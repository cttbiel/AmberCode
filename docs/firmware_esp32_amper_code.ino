// Amper Code - HackatOhm 2026 - Base Comunitária Móvel (Fiat Ducato / PMMG)
// Supervisor ESP32: FSM de carga solar (EFB 12 V x Li-Ion 48 V)
// Framework: Arduino (core ESP32 3.x) | Biblioteca extra: "Adafruit ADS1X15"
#include <Arduino.h>
#include <Wire.h>
#include <math.h>
#include <Adafruit_ADS1X15.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// ---------------- Pinos ----------------
#define PIN_VPV    36   // ADC1_CH0
#define PIN_T12    35   // ADC1_CH7
#define PIN_T48    32   // ADC1_CH4
#define PIN_SDA    21
#define PIN_SCL    22
#define PIN_EN12   25
#define PIN_EN48   26
#define PIN_FAN    27
#define PIN_BUZZER 18

// ---------------- Limiares (do spec) ----------------
const float VPV_MIN = 18.0f,  P_MIN = 15.0f;               // standby
const float V12_EMERG = 12.2f, V12_BAIXA = 12.4f;           // prioridade partida
const float V12_ABS = 13.6f,   I12_FLUT = 1.5f;             // flutuação
const float V48_CHEIA = 52.0f;
const float V48_RECARGA = 51.0f;                            // histerese (ajuste meu, ver notas)
const float T12_TRIP = 52.0f, T48_TRIP = 55.0f;
const float T12_REARME = 45.0f, T48_REARME = 48.0f;
const float V12_MAX = 15.5f,  V48_MAX = 54.0f;
const uint32_t TEMPO_MIN_MS = 60000UL;                      // permanência mínima
const uint32_t DEAD_MS = 100;                               // dead-time entre vias
const uint32_t RODIZIO_APOS_MS = 3UL * 3600000UL;           // 3 h EFB em carga
const uint32_t RODIZIO_DUR_MS  = 30UL * 60000UL;            // 30 min no 48 V

// ---------------- Condicionamento de sinais ----------------
const float K_VPV = 104.7f / 4.7f;        // divisor 100k/4,7k
const float K_V12 = 78.0f / 10.0f;        // divisor 68k/10k
const float K_V48 = 124.7f / 4.7f;        // divisor 120k/4,7k
const float ACS_ZERO = 2.5f;              // V do sensor com 0 A (CALIBRAR)
const float ACS_SENS = 0.100f;            // 100 mV/A (ACS712-20A)

Adafruit_ADS1115 ads;
bool adsOk = false;
BLECharacteristic *chr;

// ---------------- Temporizador "condição mantida por X ms" ----------------
struct Hold {
  uint32_t t0 = 0; bool on = false;
  bool ok(bool cond, uint32_t ms) {
    if (!cond) { on = false; return false; }
    if (!on) { on = true; t0 = millis(); }
    return millis() - t0 >= ms;
  }
};

// ---------------- Medidas ----------------
struct Medidas { float vpv, v12, v48, ipv, i12, t12 = 25, t48 = 25; bool ntc12, ntc48; };

float lerMv(int pin) {                        // média de 16 leituras
  uint32_t s = 0;
  for (int i = 0; i < 16; i++) s += analogReadMilliVolts(pin);
  return s / 16.0f;
}

bool lerNTC(int pin, float &tC) {             // pull-up 10k ao 3V3, NTC ao GND
  float v = lerMv(pin) / 1000.0f;
  if (v < 0.1f || v > 3.1f) return false;     // curto ou desconectado
  float r = 10000.0f * v / (3.3f - v);
  tC = 1.0f / (1.0f / 298.15f + logf(r / 10000.0f) / 3950.0f) - 273.15f;
  return true;
}

float adsV(uint8_t ch) { return ads.computeVolts(ads.readADC_SingleEnded(ch)); }

Medidas ler() {
  Medidas m;
  m.vpv = lerMv(PIN_VPV) / 1000.0f * K_VPV;
  m.ntc12 = lerNTC(PIN_T12, m.t12);
  m.ntc48 = lerNTC(PIN_T48, m.t48);
  m.v12 = adsV(0) * K_V12;                    // Kelvin 4 fios
  m.v48 = adsV(1) * K_V48;
  m.ipv = (adsV(2) * 2.0f - ACS_ZERO) / ACS_SENS;   // divisor 1:2 desfeito
  m.i12 = (adsV(3) * 2.0f - ACS_ZERO) / ACS_SENS;
  return m;
}

// ---------------- Saídas ----------------
enum Estado { ST_STANDBY, ST_12V, ST_48V, ST_FLOAT, ST_TRIP };
const char *NOMES[] = {"STANDBY", "CARGA12V", "CARGA48V", "FLUTUACAO", "TRIP"};
Estado estado = ST_STANDBY;
uint32_t tEstado = 0, rodizioFim = 0;
bool rodizio = false, liCheia = false;
Hold hTerm, hFrio, hVpv, hPot, hEmerg, hBaixa, hFlut;

void saidas(bool e12, bool e48) {
  digitalWrite(PIN_EN12, e12);
  digitalWrite(PIN_EN48, e48);
}

void mudar(Estado novo) {
  saidas(false, false);                       // abre as duas vias
  if (novo != ST_TRIP) delay(DEAD_MS);        // dead-time (Trip é imediato)
  estado = novo;
  tEstado = millis();
  if (novo == ST_12V || novo == ST_FLOAT) saidas(true, false);
  if (novo == ST_48V) saidas(false, true);
  if (novo == ST_TRIP) hFrio.on = false;
  Serial.printf(">> estado: %s\n", NOMES[novo]);
}

// ---------------- Lógica de decisão (prioridades da Figura 1) ----------------
Estado decidir(const Medidas &m) {
  bool vpvBaixo = hVpv.ok(m.vpv < VPV_MIN, 60000);
  if (estado == ST_STANDBY) hPot.on = false;
  bool potBaixa = hPot.ok(m.vpv * m.ipv < P_MIN, 600000);
  bool emerg = hEmerg.ok(m.v12 < V12_EMERG, 3000);
  bool baixa = hBaixa.ok(m.v12 < V12_BAIXA, 10000);
  bool flut  = hFlut.ok(m.v12 >= V12_ABS && m.i12 <= I12_FLUT, 300000);

  if (m.v48 >= V48_CHEIA) liCheia = true;
  else if (m.v48 < V48_RECARGA) liCheia = false;

  // Sem sol -> standby (saindo do standby: basta Vpv voltar acima de 18 V)
  if (estado == ST_STANDBY ? m.vpv < VPV_MIN : (vpvBaixo || potBaixa)) return ST_STANDBY;

  // Rodízio: EFB mais de 3 h em carga -> 30 min no 48 V
  if (estado == ST_12V && millis() - tEstado >= RODIZIO_APOS_MS) { rodizio = true; rodizioFim = millis() + RODIZIO_DUR_MS; }
  if (rodizio && millis() >= rodizioFim) rodizio = false;
  if (rodizio) return ST_48V;

  if (emerg || baixa) return ST_12V;          // prioridade zero: partida da viatura
  if (!liCheia) return ST_48V;                // operação normal TI
  return flut ? ST_FLOAT : ST_12V;            // Li-Ion cheia: flutua EFB / continua absorção
}

// ---------------- Ciclo de 1 s ----------------
void ciclo() {
  Medidas m = ler();
  bool sensorFalha = !m.ntc12 || !m.ntc48 || !adsOk;
  bool sobreV = m.v12 > V12_MAX || m.v48 > V48_MAX;
  bool termico = hTerm.ok(m.t12 >= T12_TRIP || m.t48 >= T48_TRIP, 3000);
  Estado novo = decidir(m);                   // sempre roda, p/ manter os temporizadores

  if (estado == ST_TRIP) {                    // travado até resfriar
    bool frio = hFrio.ok(m.t12 < T12_REARME && m.t48 < T48_REARME, 60000);
    if (!sensorFalha && !sobreV && frio) mudar(ST_STANDBY);
  } else if (sensorFalha || sobreV || termico) {
    mudar(ST_TRIP);
  } else if (novo != estado && millis() - tEstado >= TEMPO_MIN_MS) {
    mudar(novo);
  }

  // Cooler: 0% abaixo de 30 °C, 20% a 30 °C até 100% a 50 °C; Trip = 100%
  float tmax = max(m.t12, m.t48);
  int duty = (estado == ST_TRIP || tmax >= 50) ? 100 : (tmax < 30 ? 0 : (int)(20 + (tmax - 30) * 4));
  ledcWrite(PIN_FAN, duty * 255 / 100);

  // Telemetria (serial + BLE)
  char buf[140];
  snprintf(buf, sizeof(buf), "E=%s;Vpv=%.1f;Ipv=%.1f;V12=%.2f;I12=%.1f;V48=%.1f;T12=%.0f;T48=%.0f",
           NOMES[estado], m.vpv, m.ipv, m.v12, m.i12, m.v48, m.t12, m.t48);
  Serial.println(buf);
  chr->setValue(String(buf));
  chr->notify();
}

// ---------------- BLE ----------------
#define SVC_UUID  "6f1a0001-5a2b-4c3d-9e8f-a1b2c3d4e5f6"
#define CHR_UUID  "6f1a0002-5a2b-4c3d-9e8f-a1b2c3d4e5f6"
class Cb : public BLEServerCallbacks {
  void onDisconnect(BLEServer *) override { BLEDevice::startAdvertising(); }
};

void setup() {
  pinMode(PIN_EN12, OUTPUT); pinMode(PIN_EN48, OUTPUT); pinMode(PIN_BUZZER, OUTPUT);
  saidas(false, false);                       // fail-safe: tudo desligado desde o boot
  digitalWrite(PIN_BUZZER, LOW);
  Serial.begin(115200);

  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  ledcAttach(PIN_FAN, 25000, 8);              // PWM 25 kHz, 8 bits
  ledcWrite(PIN_FAN, 0);

  Wire.begin(PIN_SDA, PIN_SCL);
  adsOk = ads.begin(0x48, &Wire);             // se falhar, o sistema fica em TRIP
  ads.setGain(GAIN_ONE);                      // +-4,096 V
  ads.setDataRate(RATE_ADS1115_128SPS);

  BLEDevice::init("AmperCode-Base");
  BLEServer *srv = BLEDevice::createServer();
  srv->setCallbacks(new Cb());
  BLEService *svc = srv->createService(SVC_UUID);
  chr = svc->createCharacteristic(CHR_UUID, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  chr->addDescriptor(new BLE2902());
  svc->start();
  BLEDevice::getAdvertising()->addServiceUUID(SVC_UUID);
  BLEDevice::startAdvertising();

  tEstado = millis() - TEMPO_MIN_MS;          // permite sair do standby no 1º ciclo
}

void loop() {
  static uint32_t ult = 0;
  if (millis() - ult >= 1000) { ult = millis(); ciclo(); }
  digitalWrite(PIN_BUZZER, estado == ST_TRIP && ((millis() / 400) % 2));   // apita no Trip
  delay(10);
}
