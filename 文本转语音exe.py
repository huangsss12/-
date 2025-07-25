# -*- coding: utf-8 -*-
import os
import asyncio
import edge_tts
from datetime import datetime
from moviepy.editor import AudioFileClip, ColorClip
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging

edge_tts.list_voices()
# 配置日志记录
log_file_path = "error_log.txt"
logging.basicConfig(filename=log_file_path, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义可用的音色
voices = {
"zh-CN-YunjianNeural": "男声 (Yunjian, 体育/小说, 激情)",
"zh-CN-YunxiNeural": "男声 (Yunxi, 小说, 活泼阳光)",
"zh-CN-YunxiaNeural": "男声 (Yunxia, 动漫/小说, 可爱)",
"zh-CN-YunyangNeural": "男声 (Yunyang, 新闻, 专业可靠)",
"zh-CN-XiaoxiaoNeural": "女声 (Xiaoxiao, 新闻/小说, 温暖)",
"zh-CN-XiaoyiNeural": "女声 (Xiaoyi, 动漫/小说, 活泼)",
"zh-CN-liaoning-XiaobeiNeural": "女声 (Xiaobei, 东北方言, 幽默)",
"zh-CN-shaanxi-XiaoniNeural": "女声 (Xiaoni, 陕西方言, 明亮)",
"zh-HK-HiuGaaiNeural": "女声 (HiuGaai, 粤语, 友好积极)",
"zh-HK-HiuMaanNeural": "女声 (HiuMaan, 粤语, 友好积极)",
"zh-HK-WanLungNeural": "男声 (WanLung, 粤语, 友好积极)",
"zh-TW-HsiaoChenNeural": "女声 (HsiaoChen, 台湾国语, 友好积极)",
"zh-TW-HsiaoYuNeural": "女声 (HsiaoYu, 台湾国语, 友好积极)",
"zh-TW-YunJheNeural": "男声 (YunJhe, 台湾国语, 友好积极)"
}


# 使用 edge-tts 生成音频文件
async def text_to_speech(text, output_path, voice, rate):
    try:
        # 添加语速参数
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)
    except Exception as e:
        logging.error(f"text_to_speech 函数执行出错: {e}")


def create_black_background_video(audio_path, output_video_path):
    """创建黑色背景视频并与音频合成"""
    try:
        with AudioFileClip(audio_path) as audio_clip:
            if audio_clip is None:
                raise ValueError("音频剪辑对象为 None")

            duration = audio_clip.duration
            video_clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=duration)
            final_clip = video_clip.set_audio(audio_clip)

            if final_clip is None:
                raise ValueError("最终视频剪辑对象为 None")

            final_clip.write_videofile(
                output_video_path,
                codec="libx264",
                audio_codec="aac",
                fps=24
            )
            print(f"视频合成成功：{output_video_path}")
        return True
    except Exception as e:
        logging.error(f"create_black_background_video 函数执行出错: {e}")
        print(f"视频合成失败：{str(e)}")
        return False


def on_confirm():
    user_text = text_input.get("1.0", tk.END).strip()
    if not user_text:
        messagebox.showerror("错误", "输入文本不能为空！")
        return

    output_dir = output_entry.get().strip()
    if not output_dir:
        messagebox.showerror("错误", "请指定输出路径！")
        return

    selected_voice_label = voice_combobox.get()
    if not selected_voice_label:
        messagebox.showerror("错误", "请选择音色！")
        return

    # 获取语速值（整数）
    rate_value = rate_var.get()
    # 转换为带符号的百分比字符串
    rate_str = f"{'+' if rate_value >= 0 else ''}{rate_value}%"

    # 将音色标签转换为对应的语音标识
    selected_voice = [k for k, v in voices.items() if v == selected_voice_label][0]

    today = datetime.now().strftime("%Y%m%d")
    short_text = user_text[:6].replace(" ", "_").replace("/", "_")
    filename_prefix = f"{today}_{short_text}"

    audio_filename = os.path.join(output_dir, f"{filename_prefix}.mp3")
    video_filename = os.path.join(output_dir, f"{filename_prefix}.mp4")

    # 生成音频文件
    print(f"正在生成音频... (语速: {rate_str})")
    asyncio.run(text_to_speech(user_text, audio_filename, selected_voice, rate_str))

    # 生成视频
    print("正在合成视频...")
    if create_black_background_video(audio_filename, video_filename):
        messagebox.showinfo("完成", f"任务完成！文件已保存至：\n{os.path.abspath(video_filename)}")
    else:
        messagebox.showerror("错误", "视频合成失败")


def select_output_path():
    dir_selected = filedialog.askdirectory()
    if dir_selected:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, dir_selected)


def update_rate_label(value):
    """更新语速标签显示"""
    value = int(float(value))  # 确保是整数
    rate_str = f"{'+' if value >= 0 else ''}{value}%"
    rate_label.config(text=f"当前语速: {rate_str}")


# 创建主窗口
root = tk.Tk()
root.title("文本转语音及视频生成工具")
root.geometry("600x700")  # 调整窗口大小以容纳滑动条
root.resizable(True, True)  # 允许调整窗口大小

# 应用现代主题
style = ttk.Style()
style.theme_use("clam")  # 使用clam主题（现代感更强）

# 配置样式
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
style.configure("TButton", font=("Arial", 10), padding=5)
style.configure("TCombobox", font=("Arial", 10))
style.configure("TEntry", font=("Arial", 10))
style.configure("Horizontal.TScale", background="#f0f0f0")

# 创建主框架
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# 输入文本区域
input_frame = ttk.LabelFrame(main_frame, text="输入文本", padding=10)
input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

text_input = tk.Text(input_frame, height=10, font=("Arial", 10))
text_input.pack(fill=tk.BOTH, expand=True)
text_input.insert(tk.END, "在此输入要转换的文本...")

# 输出路径区域
output_frame = ttk.Frame(main_frame)
output_frame.pack(fill=tk.X, pady=(0, 10))

ttk.Label(output_frame, text="输出路径:").pack(side=tk.LEFT, padx=(0, 5))

output_entry = ttk.Entry(output_frame, width=40)
output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

browse_btn = ttk.Button(output_frame, text="浏览...", command=select_output_path)
browse_btn.pack(side=tk.RIGHT)

# 音色选择区域
voice_frame = ttk.Frame(main_frame)
voice_frame.pack(fill=tk.X, pady=(0, 10))

ttk.Label(voice_frame, text="选择音色:").pack(side=tk.LEFT, padx=(0, 10))

voice_combobox = ttk.Combobox(voice_frame, values=list(voices.values()), width=25)
voice_combobox.current(0)  # 设置默认选中第一个音色
voice_combobox.pack(side=tk.LEFT)

# 新增语速调整区域（使用滑动条）
rate_frame = ttk.LabelFrame(main_frame, text="语速调整", padding=10)
rate_frame.pack(fill=tk.X, pady=(10, 10))

# 创建语速变量（整数，范围-100到100）
rate_var = tk.IntVar(value=0)  # 默认正常语速

# 创建滑动条
rate_slider = ttk.Scale(
    rate_frame,
    from_=-100,
    to=100,
    orient=tk.HORIZONTAL,
    variable=rate_var,
    command=update_rate_label,
    length=400  # 设置滑动条长度
)
rate_slider.pack(fill=tk.X, padx=10, pady=(0, 5))

# 添加刻度标记
mark_frame = ttk.Frame(rate_frame)
mark_frame.pack(fill=tk.X, padx=10)

ttk.Label(mark_frame, text="-100%").pack(side=tk.LEFT)
ttk.Label(mark_frame, text="-50%").pack(side=tk.LEFT, padx=(75, 0))
ttk.Label(mark_frame, text="0%").pack(side=tk.LEFT, padx=(75, 0))
ttk.Label(mark_frame, text="+50%").pack(side=tk.LEFT, padx=(75, 0))
ttk.Label(mark_frame, text="+100%").pack(side=tk.RIGHT)

# 创建显示当前语速的标签
rate_label = ttk.Label(rate_frame, text="当前语速: 0%", font=("Arial", 10, "bold"))
rate_label.pack(pady=(5, 0))

# 添加说明
ttk.Label(rate_frame, text="提示：负值表示慢速，正值表示快速", foreground="#666666").pack(pady=(5, 0))

# 确认按钮区域
btn_frame = ttk.Frame(main_frame)
btn_frame.pack(fill=tk.X, pady=(5, 0))

confirm_btn = ttk.Button(btn_frame, text="开始生成", command=on_confirm, width=15)
confirm_btn.pack(pady=10)

# 状态栏
status_bar = ttk.Frame(root, relief=tk.SUNKEN, padding=(10, 5))
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

status_label = ttk.Label(status_bar, text="就绪", foreground="#666666")
status_label.pack(side=tk.LEFT)

root.mainloop()

