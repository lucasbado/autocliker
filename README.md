# ⚡ AutoClicker PC Modpack (Vortex & Nexus Mods)

Um **AutoClicker Inteligente para Windows PC** desenvolvido em Python/PyQt6 com **Leitura Visual de Tela via OCR Nativo**, projetado para automatizar os downloads de modpacks no **Vortex** e no **Nexus Mods** (Opera, Chrome, Edge, Firefox, Brave).

Disponível como **executável portátil `.exe` para Windows** (sem necessidade de instalar o Python) e como código fonte.

---

## 🚀 Como Executar no Windows PC

### Método 1: Executável Portátil `.exe` (Sem Instalação)
Basta dar um duplo clique no arquivo executável gerado:
```
AutoClicker_PC.exe
```
*(Não precisa de Python nem de terminal para rodar!)*

### Método 2: Via Script `.bat`
```
run_autoclicker.bat
```

### Método 3: Código Fonte (Python 3.10+)
```cmd
pip install -r requirements.txt
python main.py
```

### ⚙️ Como Gerar um Novo Arquivo Executável `.exe`
Se você modificar o código e desejar empacotar novamente em um arquivo `.exe`:
```
build_exe.bat
```
*(O novo executável será gerado e atualizado na raiz do projeto e na pasta `dist/`)*.

---

## ✨ Recursos Principais

- 👁️ **Leitura de Tela por OCR Nativo do Windows (`winocr`)**:
  Captura o monitor e utiliza a engine de OCR nativa do Windows 10/11 para ler palavras diretamente dos pixels da imagem. Funciona com 100% de precisão no **Opera**, **Vortex (Electron)**, **Chrome** e **Firefox**, encontrando automaticamente os botões *"Download manually"* e *"Slow download"*, mesmo que mude de posição na tela ou role a página.

- 🎯 **Automação em 2 Passos com Desambiguação Inteligente**:
  - **Passo 1/2**: Identifica e clica no aviso/notificação do Vortex ou botão inicial.
  - **Passo 2/2**: Identifica e clica no botão *"Slow download"* na página do Nexus Mods.
  - **Filtro de Desambiguação**: Diferencia automaticamente títulos informativos superiores (ex: *"Slow download. Wait more."*) do **botão real clicável na parte inferior do card**.

- 🛡️ **Fechamento Automático de Anúncios (Anti-Ad)**:
  Varre preventivamente a tela procurando por popups e botões de fechar propaganda (`"✕"`, `"Close"`, `"Fechar"`, `"Skip Ad"`, `"Dismiss"`, `"No thanks"`), fechando o anúncio automaticamente para evitar travamentos no fluxo de download.

- 📍 **Calibração Livre de 2 Pontos (`pynput`)**:
  Permite clicar em **qualquer lugar da tela ou em qualquer aplicativo do seu PC** para definir as coordenadas de Fallback do Ponto 1 (Vortex) e Ponto 2 (Navegador).

- 🪟 **Painel Flutuante Sempre no Topo (Always-On-Top)**:
  Interface gráfica em `PyQt6` translúcida e arrastável que fica fixada sobre os navegadores com status em tempo real, contador de downloads concluídos, contador de anúncios fechados e feed de logs ao vivo.

- 🚫 **Mascaramento Anti-Auto-Detecção**:
  A área da própria janela flutuante é pintada de preto nas capturas de tela internas do OCR, garantindo que o aplicativo **nunca leia ou clique nos seus próprios botões**.

---

## 💻 Passo a Passo de Uso

1. **Abra o aplicativo**: Execute o `AutoClicker_PC.exe` ou `run_autoclicker.bat`. A janela flutuante aparecerá no canto superior direito da tela.
2. **Calibrar as Coordenadas de Fallback**:
   - Clique em **"Calibrar 2 Pontos"**.
   - Dê o **1º Clique** no botão/notificação do Vortex na sua tela (Ponto 1).
   - Dê o **2º Clique** no botão *"Slow download"* no seu navegador (Ponto 2).
3. **Iniciar a Automação**:
   - Clique no botão **"Iniciar"** no painel flutuante.
   - Abra a fila de modpack no Vortex e o aplicativo gerenciará os cliques e o fechamento de anúncios automaticamente!

---

## 📂 Estrutura do Projeto PC

```
├── AutoClicker_PC.exe        # Executável portátil standalone para Windows PC
├── main.py                   # Ponto de entrada da aplicação PyQt6
├── autoclicker_core.py       # Engine de cliques, OCR nativo winocr e máquina de 2 passos
├── floating_widget.py        # Janela flutuante Always-On-Top e diálogo de configurações
├── calibration_overlay.py    # Sistema de calibração livre com listener global do mouse (pynput)
├── test_autoclicker_core.py  # Suíte de testes unitários
├── requirements.txt          # Dependências do Python (PyQt6, pyautogui, pynput, winocr, pillow)
├── run_autoclicker.bat       # Script de execução rápida
├── build_exe.bat             # Script para empacotar em arquivo .exe (PyInstaller)
├── config.json               # Arquivo de configuração gerado localmente (ignorado pelo git)
└── .gitignore                # Regras de exclusão para repositório do Git
```

---

## 🧪 Testes Unitários

Para rodar os testes unitários do motor de automação e OCR:
```cmd
python -m unittest test_autoclicker_core.py
```

---
