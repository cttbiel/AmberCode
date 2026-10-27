#!/usr/bin/env python3
"""Amper Code - HackatOhm 2026 | Figura 1 (FSM) e Figura 2 (blocos) do ESP32. Saída: PNG 300 DPI."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Patch

plt.rcParams["font.family"] = "DejaVu Sans"
DPI = 300
NAVY, SLATE, INK = "#0F172A", "#334155", "#1E293B"
BLUE, GREEN, ORANGE, RED, TEAL = "#2563EB", "#16A34A", "#EA7C0A", "#DC2626", "#0D9488"
DEC_FC, DEC_EC = "#FEF9C3", "#A16207"


def box(ax, cx, cy, w, h, text, fc, ec=None, tc="white", fs=8, bold=False, lw=1.5, ls="-", z=3):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=1.2",
                                fc=fc, ec=ec or fc, lw=lw, ls=ls, zorder=z))
    ax.text(cx, cy, text, ha="center", va="center", color=tc, fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.35, zorder=z + 1)


def diamond(ax, cx, cy, w, h, text, fs=7.8):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                         closed=True, fc=DEC_FC, ec=DEC_EC, lw=1.6, zorder=3))
    ax.text(cx, cy, text, ha="center", va="center", color=INK, fontsize=fs, linespacing=1.35, zorder=4)


def path(ax, pts, color=SLATE, lw=1.7, ls="-", arrow=True):
    xs, ys = zip(*pts[:-1])
    if len(pts) > 2:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=2)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    if arrow:
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=2,
                    arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, ls=ls, shrinkA=0, shrinkB=0,
                                    mutation_scale=13))
    else:
        ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls, zorder=2)


def lab(ax, x, y, t, c=INK, fs=8, ha="center", bold=True):
    return ax.text(x, y, t, color=c, fontsize=fs, ha=ha, va="center", fontweight="bold" if bold else "normal", zorder=5)


# ============================ FIGURA 1 ============================
def figura1():
    fig, ax = plt.subplots(figsize=(16, 21))
    ax.set_xlim(-4, 124); ax.set_ylim(-21, 146); ax.axis("off")
    X = 55
    ax.text(X, 143, "FIGURA 1 — Fluxograma da lógica de controle e Máquina de Estados Finitos (FSM) do ESP32",
            ha="center", fontsize=14.5, fontweight="bold", color=NAVY)
    ax.text(X, 139.3, "Base Comunitária Móvel Off-Grid · Fiat Ducato (PMMG) · Amper Code · HackatOhm 2026",
            ha="center", fontsize=9, color=SLATE)

    box(ax, X, 134, 40, 6, "INÍCIO — ciclo de controle a cada 1 s", NAVY, fs=9, bold=True)
    box(ax, X, 124.5, 60, 9.5, "LEITURA DOS SENSORES\nV_pv, I_PV, V_12, V_48, I_12 (ADS1115 16 bits)  ·  T_12, T_48 (ADC1 interno)",
        "#E2E8F0", ec=SLATE, tc=INK, fs=8)
    path(ax, [(X, 131), (X, 129.25)])
    path(ax, [(X, 119.75), (X, 116.5)])

    ys = [108, 89, 70, 51, 32, 13]
    dw, dh = 58, 15
    texts = [
        "FALHA CRÍTICA?\nT_12 ≥ 52 °C ou T_48 ≥ 55 °C (3 s)\nV_12 > 15,5 V ou V_48 > 54 V\nNTC aberto/curto (V_pino <0,1 ou >3,1 V)",
        "SEM SOL?\nV_pv < 18 V por 60 s\nou P_sol < 15 W por 10 min",
        "EFB FRACA? (PRIORIDADE DE PARTIDA)\nV_12 < 12,2 V por 3 s\nou V_12 < 12,4 V por 10 s",
        "RODÍZIO DE SEGURANÇA?\nEFB há mais de 3 h em carga\n(comuta 30 min para o banco 48 V)",
        "Li-Ion PRECISA CARGA?\nV_12 ≥ 12,4 V  e  V_48 < 52,0 V",
        "EFB EM FLUTUAÇÃO?\nV_12 ≥ 13,6 V e I_12 ≤ 1,5 A\npor 5 min (Li-Ion cheia)",
    ]
    for y, t in zip(ys, texts):
        diamond(ax, X, y, dw, dh, t)
    for i in range(5):
        path(ax, [(X, ys[i] - dh / 2), (X, ys[i + 1] + dh / 2)])
        lab(ax, X + 2.5, (ys[i] + ys[i + 1]) / 2, "NÃO", c="#475569", fs=8, ha="left")

    # estados
    rx, rw = 104, 28
    box(ax, rx, ys[1], rw, 12, "ESTADO 0 — STANDBY\nEN_12 = 0 · EN_48 = 0\nRádio BLE ativo", BLUE, fs=8, bold=True)
    box(ax, rx, ys[2], rw, 14, "ESTADO 1 — CARGA 12 V\nPRIORIDADE ZERO (partida)\nEN_12 = 1 · EN_48 = 0\n100 % solar → bateria EFB", ORANGE, fs=8, bold=True)
    box(ax, rx, 41.5, rw, 13, "ESTADO 2 — CARGA 48 V\nOperação normal (TI)\nEN_12 = 0 · EN_48 = 1\nsolar → notebooks, CFTV, rádio", GREEN, fs=8, bold=True)
    box(ax, rx, ys[5], rw, 13, "ESTADO 3 — FLUTUAÇÃO\nEFB mantida em 13,8 V\nEN_12 = 1 · EN_48 = 0\nLi-Ion isolada", TEAL, fs=8, bold=True)
    lx, lw_ = 11.5, 22
    box(ax, lx, ys[0], lw_, 26, "ESTADO 4\nTRIP TÉRMICO /\nFALHA CRÍTICA\nEN_12 = 0 · EN_48 = 0\nTRAVADO\nCooler 100 % · Buzzer\nAlerta BLE à guarnição\nRearme: T_12 < 45 °C e\nT_48 < 48 °C por 60 s",
        RED, fs=7.2, bold=True)
    box(ax, lx, ys[5], lw_, 12, "ESTADO 1\nCARGA 12 V\n(continua absorção)\nEN_12 = 1 · EN_48 = 0", ORANGE, fs=7.4, bold=True)

    # SIM
    path(ax, [(X - dw / 2, ys[0]), (lx + lw_ / 2, ys[0])], color=RED, lw=2)
    lab(ax, 24.2, ys[0] + 2.2, "SIM", c=RED)
    path(ax, [(X + dw / 2, ys[1]), (rx - rw / 2, ys[1])], color=BLUE, lw=2); lab(ax, 88, ys[1] + 2.2, "SIM", c=BLUE)
    path(ax, [(X + dw / 2, ys[2]), (rx - rw / 2, ys[2])], color=ORANGE, lw=2); lab(ax, 88, ys[2] + 2.2, "SIM", c=ORANGE)
    path(ax, [(X + dw / 2, ys[3]), (rx, ys[3]), (rx, 41.5 + 6.5)], color=GREEN, lw=2); lab(ax, 90, ys[3] + 2.2, "SIM (30 min)", c=GREEN)
    path(ax, [(X + dw / 2, ys[4]), (rx, ys[4]), (rx, 41.5 - 6.5)], color=GREEN, lw=2); lab(ax, 90, ys[4] + 2.2, "SIM", c=GREEN)
    path(ax, [(X + dw / 2, ys[5]), (rx - rw / 2, ys[5])], color=TEAL, lw=2); lab(ax, 88, ys[5] + 2.2, "SIM", c=TEAL)
    path(ax, [(X - dw / 2, ys[5]), (lx + lw_ / 2, ys[5])], color=ORANGE, lw=2); lab(ax, 24.2, ys[5] + 2.2, "NÃO", c=ORANGE)

    # convergência -> anti-repique
    by = -5
    box(ax, X, by, 82, 9, "FILTRO ANTI-REPIQUE:  dead-time 100 ms entre vias  ·  permanência mínima 60 s em cada estado (exceto Trip)\n"
        "Aplica as saídas EN_12 · EN_48 · FAN_PWM · BUZZER   |   Fail-safe: se o ESP32 travar → saídas em 0 V (contatores abertos)",
        "#F1F5F9", ec=NAVY, tc=INK, fs=7.8, lw=1.8)
    for yy in [ys[1], ys[2], 41.5, ys[5]]:
        path(ax, [(rx + rw / 2, yy), (121, yy)], arrow=False)
    path(ax, [(121, ys[1]), (121, by), (X + 41, by)])
    path(ax, [(lx - lw_ / 2, ys[5]), (-1.5, ys[5])], arrow=False)
    path(ax, [(lx - lw_ / 2, ys[0]), (-1.5, ys[0]), (-1.5, by), (X - 41, by)], color=RED, ls="--", lw=1.8)
    lab(ax, -1.0, 55, "TRIP: corte imediato", c=RED, fs=7.5).set_rotation(90)
    path(ax, [(X, by - 4.5), (X, -13.5)])
    box(ax, X, -16.5, 44, 5, "Aguarda 1 s  ↺  volta à LEITURA DOS SENSORES", NAVY, fs=8, bold=True)

    ax.legend(handles=[Patch(fc=BLUE, label="Standby"), Patch(fc=GREEN, label="Carga 48 V (operação TI)"),
                       Patch(fc=ORANGE, label="Prioridade 12 V (partida)"), Patch(fc=TEAL, label="Flutuação"),
                       Patch(fc=RED, label="Trip / falha crítica"), Patch(fc=DEC_FC, ec=DEC_EC, label="Decisão")],
              loc="upper right", bbox_to_anchor=(1.0, 0.985), fontsize=8, frameon=True, ncol=1)
    fig.savefig("/mnt/user-data/outputs/Figura1_fluxograma_controle_ESP32.png", dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ============================ FIGURA 2 ============================
def figura2():
    fig, ax = plt.subplots(figsize=(22, 13.5))
    ax.set_xlim(0, 230); ax.set_ylim(0, 142); ax.axis("off")
    ax.text(115, 139, "FIGURA 2 — Diagrama de blocos da interface do ESP32 com o circuito de potência",
            ha="center", fontsize=16, fontweight="bold", color=NAVY)
    COND, CEC = "#E0F2FE", "#0369A1"
    ex0, ex1, ey0, ey1 = 130, 178, 22, 120

    # ESP32
    ax.add_patch(FancyBboxPatch((ex0, ey0), ex1 - ex0, ey1 - ey0, boxstyle="round,pad=0,rounding_size=2",
                                fc=NAVY, ec="#38BDF8", lw=2.5, zorder=3))
    ax.text(154, 31, "ESP32 DevKit · FSM a cada 1 s (Figura 1)\nLógica 3,3 V · somente ADC1\n(ADC2 conflita com Wi-Fi/BLE)",
            ha="center", va="center", color="white", fontsize=8.8, fontweight="bold", linespacing=1.5, zorder=4)

    # --- Entradas analógicas diretas
    rows = [
        (114, "Painel solar PV\n0–50 Vcc", "Divisor 100k/4,7k + R série 1 kΩ\nC 100 nF + clamp BAT54S (3V3/GND)", "GPIO36 · ADC1_CH0\nV_pv", "0–2,24 V"),
        (102, "NTC 10 kΩ (β≈3950)\ncarcaça bateria 12 V", "Divisor: pull-up 10 kΩ ao 3V3\n+ NTC ao GND", "GPIO35 · ADC1_CH7\nT_12", ""),
        (90, "NTC 10 kΩ (β≈3950)\ncarcaça bateria 48 V", "Divisor: pull-up 10 kΩ ao 3V3\n+ NTC ao GND", "GPIO32 · ADC1_CH4\nT_48", ""),
    ]
    for y, s, c, pin, vl in rows:
        box(ax, 18, y, 32, 9, s, SLATE, fs=7.8)
        box(ax, 66, y, 52, 9, c, COND, ec=CEC, tc=INK, fs=7.6)
        path(ax, [(34, y), (40, y)]); path(ax, [(92, y), (ex0, y)], color=CEC)
        ax.text(ex0 + 1.5, y, pin, ha="left", va="center", color="#BAE6FD", fontsize=7.6, zorder=5)
    lab(ax, 112, 116.4, "ADC1 nativo", c=CEC, fs=7.5)

    # --- ADS1115
    drows = [
        (70, "Bateria 12 V EFB\nbornes na cabine", "Divisor 68k/10k  →  canal A0\nKELVIN 4 fios: par trançado 0,5 mm² + fusível 1 A (~10 m)", True),
        (58, "Bateria 48 V Li-Ion\n(baú, via BMS)", "Divisor 120k/4,7k (60 V → 2,26 V)  →  canal A1", False),
        (46, "Hall ACS712-20A\ncorrente do painel", "Divisor 1:2 (zero 2,5 V → 0,25–2,25 V)  →  canal A2", False),
        (34, "Hall ACS712-20A\ncorrente carga 12 V", "Divisor 1:2 (zero 2,5 V → 0,25–2,25 V)  →  canal A3", False),
    ]
    for (y, s, c, kel), tag in zip(drows, ["V_12", "V_48", "I_PV", "I_12"]):
        box(ax, 18, y, 32, 9, s, SLATE, ec=ORANGE if kel else SLATE, fs=7.8, lw=2.4 if kel else 1.5)
        box(ax, 66, y, 52, 9, c, COND, ec=ORANGE if kel else CEC, tc=INK, fs=7.2, lw=2.4 if kel else 1.5)
        path(ax, [(34, y), (40, y)], color=ORANGE if kel else SLATE)
        path(ax, [(92, y), (100, y)], color=ORANGE if kel else CEC)
        ax.text(101.5, y, tag, ha="left", va="center", color="white", fontsize=7.5, fontweight="bold", zorder=6)
    box(ax, 112, 55, 24, 54, "", "#6D28D9", fs=8)
    ax.text(112, 77, "ADS1115\n16 bits · ~1 mV", ha="center", va="center", color="white", fontsize=8, fontweight="bold", zorder=6)
    ax.text(112, 31, "I²C", ha="center", color="#DDD6FE", fontsize=8, fontweight="bold", zorder=6)
    for y, t in [(62, "GPIO21 · SDA"), (56, "GPIO22 · SCL")]:
        path(ax, [(124, y), (ex0, y)], color="#6D28D9", lw=2)
        ax.text(ex0 + 1.5, y, t, ha="left", va="center", color="#DDD6FE", fontsize=7.6, zorder=5)
    ax.text(66, 77.5, "Limiares de 12 V distam < 200 mV → ADC externo (interno tem erro 1–2 %)",
            ha="center", color="#6D28D9", fontsize=7.8, fontweight="bold")

    # --- Saídas
    outs = [
        (106, 12, "GPIO25 · EN_12", GREEN, "Transistor NPN + pull-down 10 kΩ\n→ pino Enable do Buck 48V→13,8V 10 A [CV-01]"),
        (90, 15, "GPIO26 · EN_48", GREEN, "Pino de controle do MPPT ZK-SJ20 (primário)\n+ Contator CC 60 V / SSR CC (corte secundário)\ndiodo flyback 1N4007 + snubber RC"),
        (74, 12, "GPIO27 · FAN_PWM", GREEN, "MOSFET logic-level · PWM 25 kHz\n→ cooler 12 V do quadro (velocidade proporcional)"),
        (58, 11, "GPIO18 · BUZZER", RED, "Buzzer de alarme\n(falha crítica / sobreaquecimento)"),
        (42, 11, "BLE (rádio interno)", "#7C3AED", "Telemetria e alerta de emergência\n→ guarnição policial (celular/app)"),
    ]
    for y, h, pin, col, txt in outs:
        ax.text(ex1 - 1.5, y, pin, ha="right", va="center", color="#BBF7D0" if col == GREEN else "#FECACA" if col == RED else "#DDD6FE",
                fontsize=7.6, zorder=5)
        path(ax, [(ex1, y), (192, y)], color=col, lw=2.2)
        box(ax, 211, y, 38, h, txt, "#F0FDF4" if col == GREEN else "#FEF2F2" if col == RED else "#F5F3FF", ec=col, tc=INK, fs=6.8, lw=1.8)
    box(ax, 211, 28, 38, 13, "FAIL-SAFE: ESP32 travado,\nreiniciado ou sem energia ⇒ saídas\nem 0 V ⇒ vias abertas ⇒ carga\nsolar interrompida",
        "#FEE2E2", ec=RED, tc="#991B1B", fs=6.8, bold=True, lw=2)

    # --- Alimentação do ESP32 (topo)
    ax.text(2, 133.2, "ALIMENTAÇÃO DO ESP32", fontsize=8.5, fontweight="bold", color=SLATE)
    chain = [(14, 24, "Bateria 12 V\nEFB"), (48, 24, "Fusível 1 A"), (86, 34, "Diodo anti-inversão\n(1N4007/Schottky)\n+ TVS bidirecional"),
             (122, 28, "Buck 5 V\nLM2596"), (154, 24, "VIN do ESP32\n5 V")]
    for cx, w, t in chain:
        box(ax, cx, 127, w, 8, t, "#FEF3C7", ec=DEC_EC, tc=INK, fs=7.4)
    for i in range(len(chain) - 1):
        a, b = chain[i], chain[i + 1]
        path(ax, [(a[0] + a[1] / 2, 127), (b[0] - b[1] / 2, 127)], color=DEC_EC)
    path(ax, [(154, 123), (152, ey1)], color=DEC_EC)

    # --- Potência (base)
    ax.text(2, 20.8, "CIRCUITO DE POTÊNCIA  (as saídas do ESP32 só habilitam/cortam as vias; a regulação MPPT/Buck não é afetada)",
            fontsize=8.5, fontweight="bold", color=SLATE)
    P = [(16, "Painel PV\n310 Wp", SLATE, None), (48.5, "MPPT ZK-SJ20\n[CC-01]", "#B45309", "EN_48"),
         (81, "Contator CC 60 V\n/ SSR CC [corte]", "#B45309", "EN_48"), (113.5, "Barramento 48 V\n+ Bateria Li-Ion\n19,5 Ah [BAT-01]", "#065F46", None),
         (146, "Buck 48→13,8 V\n10 A [CV-01]", "#B45309", "EN_12"), (178.5, "Fusível 7,5 A\ncabo 16 mm² ~10 m", SLATE, None),
         (211, "Bateria 12 V EFB\n72 Ah (cabine)", "#065F46", None)]
    for cx, t, col, badge in P:
        box(ax, cx, 8.5, 28.5, 10.5, t, col, fs=7.6, bold=True)
        if badge:
            box(ax, cx, 16, 14, 3.4, "◄ " + badge, GREEN, fs=7.5, bold=True)
    for i in range(len(P) - 1):
        path(ax, [(P[i][0] + 14.25, 8.5), (P[i + 1][0] - 14.25, 8.5)], color=SLATE, lw=2.6)

    fig.savefig("/mnt/user-data/outputs/Figura2_diagrama_de_blocos_ESP32.png", dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    figura1(); figura2(); print("OK")
