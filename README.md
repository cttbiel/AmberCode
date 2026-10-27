# ⚡ Amper Code — Landing Page Oficial (HackatOhm 2026)
**Desafio Stellantis / Fiat — Base Comunitária Móvel Off-Grid (PMMG)**  
*Equipe Amper Code — CEFET-MG*

---

## 🌐 Deploy na Vercel (Em 1 Minuto)

Este projeto foi construído em **HTML5 moderno e Tailwind CSS puro**, sem necessidade de build complexo (`npm install`, `node_modules`, etc.). Ele roda imediatamente e pode ser hospedado gratuitamente na Vercel:

1. Acesse [vercel.com](https://vercel.com) e faça login com seu GitHub.
2. Clique em **"Add New..."** → **"Project"**.
3. Selecione o repositório `cttbiel/AmberCode`.
4. Deixe todas as configurações padrão (Framework Preset: *Other*) e clique em **"Deploy"**.
5. Em menos de 20 segundos seu site estará no ar com link público HTTPS (ex: `https://amber-code.vercel.app`)!

---

## 👩‍💻 Instruções para a Giovanna (Como Atualizar o Site)

O código foi preparado de forma muito intuitiva e modular para você adicionar novos renders, vídeos ou textos:

### 1. Adicionar Novos Renders 3D ou Fotos:
* Coloque as novas imagens dentro da pasta `assets/` (exemplo: `render_interior_van.png`).
* Abra o arquivo `index.html`.
* Vá até a seção `<!-- SEÇÃO 2: MODELAGEM 3D -->` e troque ou adicione sua imagem usando:
  ```html
  <img src="assets/render_interior_van.png" alt="Render Interior" class="w-full rounded-xl">
  ```

### 2. Adicionar o Vídeo Pitch da Equipe:
* Quando o vídeo estiver no YouTube ou Google Drive, adicione o player na seção de destaque:
  ```html
  <iframe class="w-full aspect-video rounded-2xl" src="https://www.youtube.com/embed/SEU_VIDEO_ID" frameborder="0" allowfullscreen></iframe>
  ```

### 3. Atualizar Valores ou Textos:
* Todos os textos estão comentados e organizados por seções:
  - `Hero & Visão Geral`: Métricas e apresentação da dor.
  - `Modelagem 3D`: Cards das 3 zonas (Teto, Cabine e Baú).
  - `Circuito Elétrico`: Proteções e caminho da energia.
  - `Supervisão ESP32`: Máquina de estados (FSM) e fluxograma.
  - `Orçamento BOM`: Tabela resumida e links para baixar a planilha `.xlsx` e `.csv`.
  - `Equipe`: Seus nomes, fotos e funções.

---

## 📁 Estrutura de Pastas do Repositório

```
AmberCode/
├── index.html                                                      # Landing page principal completa e responsiva
├── README.md                                                       # Este manual de instruções
├── assets/                                                         # Imagens, fluxogramas e renders 3D
│   ├── render_3d_ducato_pmmg.png                                   # Render 3D da viatura Fiat Ducato
│   ├── planta_baixa_eletrica_ducato.png                            # Planta baixa e corte lateral
│   ├── Figura1_fluxograma_controle_ESP32.png                       # Fluxograma da FSM
│   └── Figura2_diagrama_de_blocos_ESP32.png                        # Diagrama de blocos eletrônico
└── docs/                                                           # Arquivos para download do projeto
    ├── D10_AmperCode_Resumo.pdf                                    # Relatório oficial (2 páginas)
    ├── Lista_de_Materiais_Base_Comunitaria_PMMG_R2-AmperCode-Precos.xlsx # BOM R2 oficial com 3 cotações
    └── BOM_Precos_AmperCode.csv                                    # Tabela de preços em CSV
```

---

## 🏆 Equipe Amper Code
* **Nikolas Eduardo** (Líder / Engenharia Elétrica)
* **Giovanna Silva** (Modelagem 3D & Engenharia Elétrica)
* **Gabriel Carvalho** (Engenharia de Computação & Automação ESP32)
* **Lucas Chagas** (Engenharia Elétrica & Balanço Energético)
* **Orientadores:** Prof. Dr. Heros Carvalho Soares & Prof. Dr. Alexandre Zanni Hubinger
