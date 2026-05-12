import time
import threading
import json
import os
import ctypes
import customtkinter as ctk
from pynput import mouse, keyboard

# DPI 适配
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

SAVE_FILE = "macro_memory.json"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GoldBankApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("鲟鱼黄金银行 - 自动化助手")
        self.geometry("400x450")
        
        self.recorded_events = []
        self.is_playing = False
        self.load_from_disk()

        # UI 布局
        self.label = ctk.CTkLabel(self, text="OPERATIONAL PANEL", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)

        self.status_box = ctk.CTkTextbox(self, width=300, height=150)
        self.status_box.pack(pady=10)
        self.log("系统就绪。等待指令...")

        self.record_btn = ctk.CTkButton(self, text="开始录制 (F9)", fg_color="#d35400", command=self.start_record_thread)
        self.record_btn.pack(pady=10)

        self.play_btn = ctk.CTkButton(self, text="回放记忆 (F10)", fg_color="#27ae60", command=self.start_play_thread)
        self.play_btn.pack(pady=10)

        self.info = ctk.CTkLabel(self, text="F12: 强制退出 | ESC: 停止录制", font=ctk.CTkFont(size=12))
        self.info.pack(side="bottom", pady=10)

        # 启动后台全局热键监听
        threading.Thread(target=self.global_hotkey_listener, daemon=True).start()

    def log(self, msg):
        self.status_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.status_box.see("end")

    def save_to_disk(self):
        try:
            data = [[a, [p[0], p[1], str(p[2]).split('.')[-1]], t] for a, p, t in self.recorded_events]
            with open(SAVE_FILE, 'w') as f: json.dump(data, f)
            self.log("√ 记忆已同步至磁盘")
        except Exception as e: self.log(f"保存失败: {e}")

    def load_from_disk(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    raw = json.load(f)
                    self.recorded_events = [ (a, (p[0], p[1], mouse.Button[p[2]]), t) for a, p, t in raw ]
            except: pass

    def start_record_thread(self):
        if not self.is_playing:
            threading.Thread(target=self.record_logic, daemon=True).start()

    def record_logic(self):
        self.recorded_events = []
        start_time = time.time()
        self.log("● 录制中... 按 ESC 停止")
        
        def on_click(x, y, button, pressed):
            if pressed: self.recorded_events.append(('click', (x, y, button), time.time() - start_time))

        with mouse.Listener(on_click=on_click) as m_l:
            with keyboard.Listener(on_press=lambda k: False if k == keyboard.Key.esc else None) as k_l:
                k_l.join()
            m_l.stop()
        
        self.log(f"■ 录制完成 ({len(self.recorded_events)} 动作)")
        self.save_to_disk()

    def start_play_thread(self):
        if not self.is_playing:
            threading.Thread(target=self.play_logic, daemon=True).start()

    def play_logic(self):
        if not self.recorded_events:
            self.log("错误：没有记忆可回放")
            return
        self.is_playing = True
        self.log(">>> 开始回放...")
        m_ctrl = mouse.Controller()
        last_t = 0
        for action, params, t in self.recorded_events:
            if not self.is_playing: break
            time.sleep(max(0, t - last_t))
            m_ctrl.position = (params[0], params[1])
            m_ctrl.click(params[2])
            last_t = t
        self.log(">>> 回放完毕")
        self.is_playing = False

    def global_hotkey_listener(self):
        def on_press(key):
            if key == keyboard.Key.f12: os._exit(0)
            elif key == keyboard.Key.f9: self.start_record_thread()
            elif key == keyboard.Key.f10: self.start_play_thread()
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

if __name__ == "__main__":
    app = GoldBankApp()
    app.mainloop()