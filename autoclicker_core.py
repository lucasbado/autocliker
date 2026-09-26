import json
import os
import time
import asyncio
import pyautogui
import winocr
from PIL import ImageGrab, ImageDraw
import uiautomation as auto
from PyQt6.QtCore import QThread, pyqtSignal

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "step1_keywords": ["Download manually", "Download Manually", "Vortex", "Download Mod", "Open", "Abrir"],
    "step1_x": 819,
    "step1_y": 568,
    "step1_timeout": 3.0,
    
    "step2_keywords": ["Slow download", "Slow Download", "Download Manual", "Download", "Baixar"],
    "step2_x": 819,
    "step2_y": 568,
    "step2_timeout": 3.0,

    "step_delay": 2.0,

    "ad_auto_close": True,
    "ad_keywords": ["✕", "Close", "Fechar", "Skip Ad", "Pular anúncio", "Dismiss", "No thanks", "Fechar propaganda"]
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                for key, val in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = val
                return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def is_point_inside_rect(x, y, rect):
    if not rect or len(rect) < 4:
        return False
    rx1, ry1, rx2, ry2 = rect
    return rx1 <= x <= rx2 and ry1 <= y <= ry2

def find_element_via_ocr(keywords, exclude_rect=None):
    """
    Captura o monitor, mascarando a região do próprio aplicativo para evitar auto-detecção,
    e utiliza a Engine de OCR nativa do Windows (Windows Media OCR) para localizar palavras-chave.
    Prioriza botões inferiores no layout da página (maior Y) para ignorar títulos superiores.
    """
    if not keywords:
        return None

    try:
        screenshot = ImageGrab.grab()

        # Mascara (pinta de preto) a área da própria janela do AutoClicker
        if exclude_rect:
            draw = ImageDraw.Draw(screenshot)
            ex1 = max(0, exclude_rect[0] - 20)
            ey1 = max(0, exclude_rect[1] - 20)
            ex2 = exclude_rect[2] + 20
            ey2 = exclude_rect[3] + 20
            draw.rectangle([ex1, ey1, ex2, ey2], fill="black")

        async def _run_ocr():
            return await winocr.recognize_pil(screenshot, 'en')

        ocr_result = asyncio.run(_run_ocr())
        if not ocr_result or not ocr_result.lines:
            return None

        candidates = []

        for line in ocr_result.lines:
            line_text = line.text.lower()

            for keyword in keywords:
                kw = keyword.strip().lower()
                if not kw:
                    continue

                # Ignora títulos superiores de cabeçalho do Nexus Mods que contenham "wait" ou "wait more"
                if "slow download" in kw and ("wait" in line_text or "more" in line_text):
                    continue

                if kw in line_text:
                    words_in_line = line.words
                    if words_in_line:
                        min_x = min(w.bounding_rect.x for w in words_in_line)
                        min_y = min(w.bounding_rect.y for w in words_in_line)
                        max_x = max(w.bounding_rect.x + w.bounding_rect.width for w in words_in_line)
                        max_y = max(w.bounding_rect.y + w.bounding_rect.height for w in words_in_line)
                        cx = int((min_x + max_x) / 2)
                        cy = int((min_y + max_y) / 2)

                        # Valida se o ponto detectado não está na região excluída do aplicativo
                        if not is_point_inside_rect(cx, cy, exclude_rect):
                            candidates.append((cy, cx, keyword.strip()))

        if candidates:
            # Ordena por Y decrescente para selecionar o BOTÃO na parte inferior da caixa/card!
            candidates.sort(key=lambda item: item[0], reverse=True)
            best_cy, best_cx, best_kw = candidates[0]
            return (best_cx, best_cy, best_kw)

    except Exception:
        pass

    return None

def find_element_on_screen(keywords, exclude_rect=None):
    """
    Combina OCR Nativo do Windows com UI Automation para máxima taxa de acerto, ignorando o próprio app.
    """
    # 1. Tenta OCR em tela (mascarando a região do AutoClicker)
    ocr_match = find_element_via_ocr(keywords, exclude_rect=exclude_rect)
    if ocr_match:
        return ocr_match

    # 2. Se o OCR não localizar, tenta UI Automation
    try:
        root = auto.GetRootControl()
        for win in root.GetChildren():
            if win.Name and "AutoClicker" in win.Name:
                continue  # Ignora a própria janela do AutoClicker

            rect = win.BoundingRectangle
            if not rect or (rect.right - rect.left) <= 0:
                continue

            for keyword in keywords:
                kw = keyword.strip()
                if not kw:
                    continue

                try:
                    ctrl = win.Control(SubName=kw)
                    if ctrl and ctrl.Exists(maxSearchSeconds=0.05):
                        c_rect = ctrl.BoundingRectangle
                        if c_rect and (c_rect.right - c_rect.left) > 5 and (c_rect.bottom - c_rect.top) > 5:
                            cx = (c_rect.left + c_rect.right) // 2
                            cy = (c_rect.top + c_rect.bottom) // 2
                            if cx > 0 and cy > 0 and not is_point_inside_rect(cx, cy, exclude_rect):
                                return (cx, cy, kw)
                except Exception:
                    pass
    except Exception:
        pass

    return None


class AutoClickerWorker(QThread):
    status_changed = pyqtSignal(str)
    log_added = pyqtSignal(str, str)  # (type, message)
    count_updated = pyqtSignal(int)
    ad_count_updated = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = False
        self.download_count = 0
        self.ad_closed_count = 0
        self.current_step = 1  # 1 ou 2
        self.config = load_config()
        self.exclude_rect = None  # (x1, y1, x2, y2) do widget do app

    def update_config(self, new_config):
        self.config = new_config

    def set_running(self, state: bool):
        self.running = state
        if state:
            self.current_step = 1
            self.log_added.emit("INFO", "Automação Inteligente iniciada (Desambiguação de Botões Ativa).")
            self.status_changed.emit("[1/2] OCR lendo tela por Passo 1...")
        else:
            self.log_added.emit("INFO", "Automação pausada.")
            self.status_changed.emit("Parado")

    def check_and_close_ads(self) -> bool:
        if not self.config.get("ad_auto_close", True):
            return False

        ad_keywords = self.config.get("ad_keywords", DEFAULT_CONFIG["ad_keywords"])
        found_ad = find_element_on_screen(ad_keywords, exclude_rect=self.exclude_rect)

        if found_ad:
            cx, cy, matched = found_ad
            self.log_added.emit("ANTI-AD", f"🛡️ Propaganda detectada ('{matched}'). Fechando em ({cx}, {cy})!")
            pyautogui.click(cx, cy)
            self.ad_closed_count += 1
            self.ad_count_updated.emit(self.ad_closed_count)
            time.sleep(0.5)
            return True

        return False

    def run(self):
        last_step_time = time.time()
        
        while not self.isInterruptionRequested():
            if not self.running:
                time.sleep(0.3)
                continue

            self.config = load_config()
            now = time.time()
            elapsed = now - last_step_time
            step_delay = self.config.get("step_delay", 2.0)

            # Varredura por anúncios ignorando o próprio app
            if self.check_and_close_ads():
                last_step_time = time.time()
                continue

            # Respeita o delay de transição entre os passos
            if elapsed < step_delay:
                time.sleep(0.2)
                continue

            if self.current_step == 1:
                keywords = self.config.get("step1_keywords", [])
                timeout = float(self.config.get("step1_timeout", 4.0))
                remaining = max(0, int(timeout - (elapsed - step_delay)))
                self.status_changed.emit(f"[1/2] OCR Lendo Tela por Passo 1 (ou Fallback em {remaining}s)")

                # Tenta detecção dinâmica ignorando o próprio app
                found = find_element_on_screen(keywords, exclude_rect=self.exclude_rect)
                if found:
                    cx, cy, matched = found
                    self.log_added.emit("CLIQUE", f"[Passo 1/2] 👁️ OCR detectou '{matched}' em ({cx}, {cy}). Clicando!")
                    pyautogui.click(cx, cy)

                    self.current_step = 2
                    last_step_time = time.time()
                    self.status_changed.emit("[1/2] Passo 1 Concluído! Mudando para Passo 2...")
                    time.sleep(0.3)
                    continue

                # Se estourar o timeout, aciona o Fallback do Ponto 1
                if (elapsed - step_delay) >= timeout:
                    x1 = int(self.config.get("step1_x", 819))
                    y1 = int(self.config.get("step1_y", 568))

                    self.log_added.emit("FALLBACK", f"[Passo 1/2] ⚠️ Usando Fallback Ponto 1 em ({x1}, {y1})")
                    pyautogui.click(x1, y1)

                    self.current_step = 2
                    last_step_time = time.time()
                    self.status_changed.emit("[1/2] Passo 1 (Fallback) Concluído! Mudando para Passo 2...")

            elif self.current_step == 2:
                keywords = self.config.get("step2_keywords", [])
                timeout = float(self.config.get("step2_timeout", 5.0))
                remaining = max(0, int(timeout - (elapsed - step_delay)))
                self.status_changed.emit(f"[2/2] OCR Lendo Tela por Passo 2 (ou Fallback em {remaining}s)")

                # Tenta detecção dinâmica ignorando o próprio app
                found = find_element_on_screen(keywords, exclude_rect=self.exclude_rect)
                if found:
                    cx, cy, matched = found
                    self.log_added.emit("CLIQUE", f"[Passo 2/2] 👁️ OCR detectou '{matched}' no botão em ({cx}, {cy}). Clicando!")
                    pyautogui.click(cx, cy)

                    self.download_count += 1
                    self.count_updated.emit(self.download_count)
                    self.log_added.emit("SUCCESS", f"Download #{self.download_count} concluído via OCR no botão!")

                    self.current_step = 1
                    last_step_time = time.time()
                    self.status_changed.emit("[2/2] Passo 2 Concluído! Voltando para Passo 1...")
                    time.sleep(0.3)
                    continue

                # Se estourar o timeout, aciona o Fallback do Ponto 2
                if (elapsed - step_delay) >= timeout:
                    x2 = int(self.config.get("step2_x", 819))
                    y2 = int(self.config.get("step2_y", 568))

                    self.log_added.emit("FALLBACK", f"[Passo 2/2] ⚠️ Usando Fallback Ponto 2 em ({x2}, {y2})")
                    pyautogui.click(x2, y2)

                    self.download_count += 1
                    self.count_updated.emit(self.download_count)
                    self.log_added.emit("SUCCESS", f"Download #{self.download_count} concluído via Fallback!")

                    self.current_step = 1
                    last_step_time = time.time()
                    self.status_changed.emit("[2/2] Passo 2 (Fallback) Concluído! Voltando para Passo 1...")

            time.sleep(0.3)
