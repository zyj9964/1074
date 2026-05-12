import time
import threading
import json
import os
import ctypes
from pynput import mouse, keyboard

# --- 1. 环境适配：解决 Windows 屏幕缩放导致的坐标偏移 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# --- 2. 配置与全局状态 ---
SAVE_FILE = "macro_memory.json"
recorded_events = []
is_playing = False

def save_to_disk():
    """将内存中的动作持久化到本地 JSON"""
    try:
        serializable_data = []
        for action, params, timestamp in recorded_events:
            x, y, button = params
            # 将 Button 对象转为字符串存储
            btn_str = str(button).split('.')[-1]
            serializable_data.append([action, [x, y, btn_str], timestamp])
            
        with open(SAVE_FILE, 'w') as f:
            json.dump(serializable_data, f)
        print(f"√ 记忆已同步到磁盘: {SAVE_FILE}")
    except Exception as e:
        print(f"保存失败: {e}")

def load_from_disk():
    """启动时读取历史记录"""
    global recorded_events
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                raw_data = json.load(f)
                recorded_events = []
                for action, params, timestamp in raw_data:
                    # 还原 Button 对象
                    btn = mouse.Button[params[2]]
                    recorded_events.append((action, (params[0], params[1], btn), timestamp))
            print(f"★ 已成功载入上次录制的 {len(recorded_events)} 个动作。")
        except Exception as e:
            print(f"读取记忆失败: {e}")

def play_logic():
    """执行回放过程"""
    global is_playing
    if not recorded_events:
        print("提示：记忆库为空，请先录制！")
        return

    is_playing = True
    print(">>> 正在回放动作序列...")
    m_ctrl = mouse.Controller()
    last_time = 0
    
    try:
        for action, params, timestamp in recorded_events:
            if not is_playing: break 
            
            # 模拟真实的点击间隔
            time.sleep(timestamp - last_time)
            if action == 'click':
                m_ctrl.position = (params[0], params[1])
                m_ctrl.click(params[2])
            last_time = timestamp
    except Exception as e:
        print(f"回放中途出错: {e}")
    
    print(">>> 回放任务结束")
    is_playing = False

def start_record():
    """执行录制过程"""
    global recorded_events
    recorded_events = [] 
    start_time = time.time()
    print("● 录制中... (按 ESC 键停止录制)")

    def on_click(x, y, button, pressed):
        if pressed:
            recorded_events.append(('click', (x, y, button), time.time() - start_time))

    # 启动监听
    with mouse.Listener(on_click=on_click) as m_listener:
        with keyboard.Listener(on_press=lambda k: False if k == keyboard.Key.esc else None) as k_listener:
            k_listener.join()
        m_listener.stop()
    
    print(f"■ 录制完成，共捕获 {len(recorded_events)} 个动作。")
    save_to_disk()

def on_press(key):
    """主控热键分发中心"""
    try:
        # F12：紧急自毁退出
        if key == keyboard.Key.f12:
            print("\n!!! 触发紧急停止，进程已强制关闭")
            os._exit(0) 

        # F9：开始录制
        elif key == keyboard.Key.f9:
            if not is_playing:
                threading.Thread(target=start_record, daemon=True).start()
            else:
                print("警告：回放中无法开启录制")
        
        # F10：开始回放
        elif key == keyboard.Key.f10:
            if not is_playing:
                threading.Thread(target=play_logic, daemon=True).start()
            else:
                print("提示：已经在回放中了")

    except Exception:
        pass

if __name__ == "__main__":
    load_from_disk()
    print("-" * 35)
    print(" 自动点击助手 已就绪")
    print(" F9  - 开始录制")
    print(" F10 - 回放记忆")
    print(" F12 - 强制退出程序")
    print("-" * 35)

    with keyboard.Listener(on_press=on_press) as main_listener:
        main_listener.join()
