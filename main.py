# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import threading
from datetime import datetime
import customtkinter as ctk
from ai_clients import DeepseekClient, OpenAIClient, ClaudeClient
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import time
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.nl2br import Nl2BrExtension
from PIL import Image

class AIChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI 聊天助手")
        self.root.geometry("1200x800")  # 增加窗口大小
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # 加载模型标志（使用文字替代图片）
        self.model_styles = {
            "DeepSeek": {
                "text": "DeepSeek AI",
                "color": "#3B82F6",
                "font": ("Helvetica", 40, "bold")
            },
            "OpenAI": {
                "text": "ChatGPT",
                "color": "#10A37F",
                "font": ("Helvetica", 40, "bold")
            },
            "Claude": {
                "text": "Claude",
                "color": "#FF7F50",
                "font": ("Helvetica", 40, "bold")
            }
        }
        
        # 初始化历史记录
        self.history_dir = "chat_history"
        os.makedirs(self.history_dir, exist_ok=True)
        
        # 初始化 Markdown 转换器
        self.md = markdown.Markdown(extensions=[
            FencedCodeExtension(),
            TableExtension(),
            Nl2BrExtension()
        ])
        
        # 添加语言设置
        self.translations = {
            "zh": {
                "title": "AI 聊天助手",
                "input_placeholder": "输入你的问题...",
                "send": "发送",
                "settings": "API 设置",
                "history": "历史记录",
                "theme_switch": "切换主题",
                "language_switch": "Switch to English",
                "api_settings": "API 设置",
                "save": "保存",
                "settings_updated": "API 设置已更新",
                "you": "你",
                "error": "错误",
                "watermark": "Created by Travisma2233",
                "deepseek_key": "DeepSeek API 密钥",
                "openai_key": "OpenAI API 密钥",
                "claude_key": "Claude API 密钥"
            },
            "en": {
                "title": "AI Chat Assistant",
                "input_placeholder": "Type your question...",
                "send": "Send",
                "settings": "API Settings",
                "history": "History",
                "theme_switch": "Toggle Theme",
                "language_switch": "切换为中文",
                "api_settings": "API Settings",
                "save": "Save",
                "settings_updated": "API settings updated",
                "you": "You",
                "error": "Error",
                "watermark": "Created by Travisma2233",
                "deepseek_key": "DeepSeek API Key",
                "openai_key": "OpenAI API Key",
                "claude_key": "Claude API Key"
            }
        }
        
        self.current_language = "zh"
        
        # 配置界面布局
        self.create_widgets()
        
        # 初始化 AI 客户端
        self.load_config()
        self.init_ai_clients()
        
    def init_ai_clients(self):
        self.ai_clients = {
            "DeepSeek": DeepseekClient(self.config.get("deepseek_api_key", "")),
            "OpenAI": OpenAIClient(self.config.get("openai_api_key", "")),
            "Claude": ClaudeClient(self.config.get("claude_api_key", ""))
        }
        
    def create_widgets(self):
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 20))
        
        # 右侧工具按钮
        buttons_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        # 工具按钮样式
        button_style = {
            "height": 36,
            "corner_radius": 18,
            "font": ("Helvetica", 14)
        }
        
        # 语言切换按钮
        self.language_button = ctk.CTkButton(
            buttons_frame,
            text=self.translations[self.current_language]["language_switch"],
            command=self.toggle_language,
            width=120,
            **button_style
        )
        self.language_button.pack(side="left", padx=5)
        
        # 主题切换按钮
        self.theme_var = ctk.StringVar(value="dark")
        theme_button = ctk.CTkButton(
            buttons_frame,
            text="切换主题",
            command=self.toggle_theme,
            width=90,
            **button_style
        )
        theme_button.pack(side="left", padx=5)
        
        # 设置和历史记录按钮
        for text, command in [(self.translations[self.current_language]["settings"], self.show_settings), 
                            (self.translations[self.current_language]["history"], self.show_history)]:
            ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                width=90,
                **button_style
            ).pack(side="left", padx=5)
        
        # 创建中央内容区
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # 创建标志显示区
        self.logo_label = ctk.CTkLabel(
            content_frame,
            text="DeepSeek AI",
            font=self.model_styles["DeepSeek"]["font"],
            text_color=self.model_styles["DeepSeek"]["color"]
        )
        self.logo_label.pack(pady=(0, 30))
        
        # AI 模型选择
        models_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        models_frame.pack(pady=(0, 20))
        
        self.model_var = ctk.StringVar(value="DeepSeek")
        for model in ["DeepSeek", "OpenAI", "Claude"]:
            ctk.CTkRadioButton(
                models_frame,
                text=model,
                variable=self.model_var,
                value=model,
                font=("Helvetica", 14),
                command=self.update_model_logo,
                fg_color=self.model_styles[model]["color"],
                border_color=self.model_styles[model]["color"]
            ).pack(side="left", padx=20)
        
        # 创建搜索框区域
        search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=100, pady=(0, 30))
        
        # 输入框和发送按钮
        self.input_box = ctk.CTkEntry(
            search_frame,
            placeholder_text="输入你的问题...",
            font=("Helvetica", 16),
            height=50,
            corner_radius=25
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_box.bind("<Return>", lambda event: self.send_message())
        
        self.send_button = ctk.CTkButton(
            search_frame,
            text="发送",
            command=self.send_message,
            width=120,
            height=50,
            corner_radius=25,
            font=("Helvetica", 16)
        )
        self.send_button.pack(side="right")
        
        # 聊天历史区域
        self.chat_history = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=("Helvetica", 14),
            corner_radius=15,
            height=350
        )
        self.chat_history.pack(fill="both", expand=True, padx=20)
        
        # 初始化显示默认模型的标志
        self.update_model_logo()
        
        # 启用标签支持
        self.chat_history.tag_config("latex", justify="center")
        
        # 添加文本标签配置
        self.chat_history.tag_config("bold", justify="left")
        self.chat_history.tag_config("italic", justify="left")
        self.chat_history.tag_config("code", background="#2d2d2d", foreground="#e6e6e6")
        self.chat_history.tag_config("heading1", justify="left")
        self.chat_history.tag_config("heading2", justify="left")
        self.chat_history.tag_config("heading3", justify="left")
        self.chat_history.tag_config("list_item", lmargin1=20, lmargin2=40)
        
        # 使用不同的文本大小来区分标题层级
        def insert_heading1(text):
            self.chat_history.insert("end", text, ("heading1",))
            
        def insert_heading2(text):
            self.chat_history.insert("end", text, ("heading2",))
            
        def insert_heading3(text):
            self.chat_history.insert("end", text, ("heading3",))
            
        # 将这些函数保存为实例变量
        self.insert_heading1 = insert_heading1
        self.insert_heading2 = insert_heading2
        self.insert_heading3 = insert_heading3
        
        # 在底部添加水印
        watermark = ctk.CTkLabel(
            self.main_frame,
            text="Created by Travisma2233",
            font=("Helvetica", 12),
            text_color="gray60",
            cursor="hand2"  # 鼠标悬停时显示手型光标
        )
        watermark.pack(side="bottom", pady=5)
        watermark.bind("<Button-1>", lambda e: self.open_github())
        
    def update_model_logo(self):
        selected_model = self.model_var.get()
        style = self.model_styles[selected_model]
        self.logo_label.configure(
            text=style["text"],
            font=style["font"],
            text_color=style["color"]
        )

    def show_settings(self):
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title(self.translations[self.current_language]["api_settings"])
        settings_window.geometry("700x500")
        settings_window.lift()  # 将窗口提升到最上层
        settings_window.focus_force()  # 强制获取焦点
        settings_window.grab_set()  # 模态窗口，阻止与其他窗口的交互
        
        scroll_frame = ctk.CTkScrollableFrame(settings_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 使用翻译后的文本
        for name_key, key in [
            ("deepseek_key", "deepseek_api_key"),
            ("openai_key", "openai_api_key"),
            ("claude_key", "claude_api_key")
        ]:
            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                frame,
                text=self.translations[self.current_language][name_key],
                font=("Helvetica", 16)
            ).pack(padx=20, pady=5)
            
            entry = ctk.CTkEntry(
                frame,
                font=("Helvetica", 14),
                width=600,
                height=40
            )
            entry.pack(padx=20, pady=5)
            entry.insert(0, self.config.get(key, ""))
            entry.configure(show="*")  # 密码形式显示
            setattr(self, f"{key}_entry", entry)
        
        # 保存按钮
        ctk.CTkButton(
            settings_window,
            text=self.translations[self.current_language]["save"],
            command=lambda: self.save_settings(settings_window),
            width=200,
            height=40,
            font=("Helvetica", 14)
        ).pack(pady=20)

    def save_settings(self, window):
        # 保存 API 设置
        for key in ["deepseek_api_key", "openai_api_key", "claude_api_key"]:
            entry = getattr(self, f"{key}_entry")
            self.config[key] = entry.get()
        
        self.save_config()
        self.init_ai_clients()  # 重新初始化客户端
        window.destroy()
        
        # 显示保存成功消息
        self.append_message("系统", self.translations[self.current_language]["settings_updated"])

    def show_history(self):
        history_window = ctk.CTkToplevel(self.root)
        history_window.title(self.translations[self.current_language]["history"])
        history_window.geometry("800x600")
        history_window.lift()  # 将窗口提升到最上层
        history_window.focus_force()  # 强制获取焦点
        history_window.grab_set()  # 模态窗口，阻止与其他窗口的交互
        
        # 历史记录列表
        history_files = sorted(
            [f for f in os.listdir(self.history_dir) if f.endswith('.txt')],
            reverse=True
        )
        
        # 创建滚动文本框显示历史记录
        history_text = ctk.CTkTextbox(
            history_window,
            wrap="word",
            font=("Helvetica", 14)
        )
        history_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 读取最近的历史记录
        for file in history_files[:10]:  # 显示最近10条记录
            with open(os.path.join(self.history_dir, file), 'r', encoding='utf-8') as f:
                history_text.insert("end", f"=== {file[:-4]} ===\n")
                history_text.insert("end", f.read() + "\n\n")
        
        history_text.configure(state="disabled")  # 设为只读

    def save_chat_history(self, messages):
        # 保存聊天记录到文件
        filename = datetime.now().strftime("%Y%m%d_%H%M%S.txt")
        filepath = os.path.join(self.history_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(messages)

    def append_message(self, sender, message, typing_effect=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        # 翻译发送者名称
        if sender == "你" or sender == "You":
            sender = self.translations[self.current_language]["you"]
        elif sender == "错误" or sender == "Error":
            sender = self.translations[self.current_language]["error"]
            
        header = f"[{timestamp}] {sender}: "
        self.chat_history.insert("end", header)
        
        if typing_effect and sender != "你":
            segments = self.split_latex(message)
            for segment in segments:
                if any(segment.startswith(delim) for delim in ['$', '\\[']):
                    self.render_latex(segment)
                else:
                    formatted_segments = self.format_markdown(segment)
                    for tag, text in formatted_segments:
                        if tag == 'code':
                            self.chat_history.insert("end", text + "\n", "code")
                        elif tag == 'heading1':
                            self.chat_history.insert("end", text + "\n", "heading1")
                            self.chat_history.configure(font=("Helvetica", 16))  # 临时改变字体大小
                        elif tag == 'heading2':
                            self.chat_history.insert("end", text + "\n", "heading2")
                            self.chat_history.configure(font=("Helvetica", 14))  # 临时改变字体大小
                        elif tag == 'heading3':
                            self.chat_history.insert("end", text + "\n", "heading3")
                            self.chat_history.configure(font=("Helvetica", 12))  # 临时改变字体大小
                        elif tag == 'list_item':
                            self.chat_history.insert("end", text + "\n", "list_item")
                        else:
                            for char in text:
                                self.chat_history.insert("end", char)
                                self.chat_history.see("end")
                                self.root.update()
                                time.sleep(0.01)
                            
                        # 恢复默认字体大小
                        if tag in ['heading1', 'heading2', 'heading3']:
                            self.chat_history.configure(font=("Helvetica", 12))
        else:
            segments = self.split_latex(message)
            for segment in segments:
                if any(segment.startswith(delim) for delim in ['$', '\\[']):
                    self.render_latex(segment)
                else:
                    formatted_segments = self.format_markdown(segment)
                    for tag, text in formatted_segments:
                        if tag in ['heading1', 'heading2', 'heading3']:
                            self.chat_history.configure(font=("Helvetica", 16 if tag == 'heading1' else 14 if tag == 'heading2' else 12))
                        self.chat_history.insert("end", text + "\n", tag)
                        if tag in ['heading1', 'heading2', 'heading3']:
                            self.chat_history.configure(font=("Helvetica", 12))
        
        self.chat_history.insert("end", "\n")
        self.chat_history.see("end")
        
        # 保存到历史记录
        self.save_chat_history(self.chat_history.get("1.0", "end"))

    def split_latex(self, text):
        # 分割文本和各种格式的 LaTeX 公式
        patterns = [
            r'(\$\$[^$]+\$\$)',  # $$...$$
            r'(\$[^$]+\$)',      # $...$
            r'(\\\[[^\]]+\\\])', # \[...\]
            r'(\\\([^)]+\\\))'   # \(...\)
        ]
        
        segments = [text]
        for pattern in patterns:
            new_segments = []
            for segment in segments:
                if any(segment.startswith(delim) for delim in ['$', '\\[']):
                    new_segments.append(segment)
                else:
                    parts = re.split(pattern, segment)
                    for part in parts:
                        if part and not part.isspace():
                            new_segments.append(part)
            segments = new_segments
        
        return [s for s in segments if s]

    def render_latex(self, latex_code):
        try:
            # 移除外部定界符
            if latex_code.startswith('$$') and latex_code.endswith('$$'):
                latex_code = latex_code[2:-2]
            elif latex_code.startswith('$') and latex_code.endswith('$'):
                latex_code = latex_code[1:-1]
            elif latex_code.startswith('\\[') and latex_code.endswith('\\]'):
                latex_code = latex_code[2:-2]
            elif latex_code.startswith('\\(') and latex_code.endswith('\\)'):
                latex_code = latex_code[2:-2]

            # 创建图形
            is_display_math = latex_code.startswith('$$') or latex_code.startswith('\\[')
            fig = Figure(figsize=(8, 1.2 if is_display_math else 0.7))  # 增加图形大小
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            # 设置更大的边距
            fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
            
            ax.text(0.5, 0.5, f'${latex_code}$', 
                   size=16 if is_display_math else 14,  # 增加字体大小
                   ha='center', va='center')
            
            # 创建画布
            canvas = FigureCanvasTkAgg(fig, master=self.chat_frame)
            widget = canvas.get_tk_widget()
            
            # 将 LaTeX 公式插入到文本框
            self.chat_history.window_create("end", window=widget)
            canvas.draw()
            
        except Exception as e:
            # 如果渲染失败，直接显示原始文本
            self.chat_history.insert("end", latex_code)

    def load_config(self):
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
            self.save_config()
            
    def save_config(self):
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False)
    
    def send_message(self):
        message = self.input_box.get()
        if not message:
            return
            
        # 立即清除输入框
        self.input_box.delete(0, "end")
        
        # 禁用输入和发送按钮
        self.input_box.configure(state="disabled")
        self.send_button.configure(state="disabled")
        
        # 显示用户消息
        self.append_message("你", message, typing_effect=False)
        
        # 在新线程中处理 AI 响应
        def process_response():
            selected_model = self.model_var.get()
            client = self.ai_clients[selected_model]
            
            try:
                response = client.get_response(message)
                self.root.after(0, lambda: self.append_message(selected_model, response, typing_effect=True))
            except Exception as e:
                self.root.after(0, lambda: self.append_message("错误", str(e), typing_effect=False))
            finally:
                # 重新启用输入和发送按钮
                self.root.after(0, lambda: self.input_box.configure(state="normal"))
                self.root.after(0, lambda: self.send_button.configure(state="normal"))
                self.root.after(0, lambda: self.input_box.focus())
        
        threading.Thread(target=process_response, daemon=True).start()

    def format_markdown(self, text):
        # 处理代码块
        code_blocks = {}
        code_block_pattern = r'```(?:\w+)?\n(.*?)```'
        
        def replace_code_block(match):
            code = match.group(1)
            key = f"CODE_BLOCK_{len(code_blocks)}"
            code_blocks[key] = code
            return key
        
        text = re.sub(code_block_pattern, replace_code_block, text, flags=re.DOTALL)
        
        # 处理行内代码
        inline_code_blocks = {}
        inline_code_pattern = r'`([^`]+)`'
        
        def replace_inline_code(match):
            code = match.group(1)
            key = f"INLINE_CODE_{len(inline_code_blocks)}"
            inline_code_blocks[key] = code
            return key
        
        text = re.sub(inline_code_pattern, replace_inline_code, text)
        
        # 处理其他 Markdown 元素
        lines = text.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            # 处理标题
            if line.startswith('# '):
                formatted_lines.append(('heading1', line[2:]))
            elif line.startswith('## '):
                formatted_lines.append(('heading2', line[3:]))
            elif line.startswith('### '):
                formatted_lines.append(('heading3', line[4:]))
            # 处理列表
            elif line.startswith('- ') or line.startswith('* '):
                formatted_lines.append(('list_item', '• ' + line[2:]))
                in_list = True
            elif line.startswith('1. '):
                formatted_lines.append(('list_item', line))
                in_list = True
            # 处理普通文本
            else:
                if line.strip() == '' and in_list:
                    in_list = False
                formatted_lines.append(('normal', line))
        
        # 恢复代码块
        result = []
        for tag, line in formatted_lines:
            for key, code in code_blocks.items():
                if key in line:
                    result.append(('code', code))
                    break
            else:
                for key, code in inline_code_blocks.items():
                    if key in line:
                        line = line.replace(key, f'`{code}`')
                result.append((tag, line))
        
        return result

    def toggle_theme(self):
        current_theme = self.theme_var.get()
        new_theme = "light" if current_theme == "dark" else "dark"
        ctk.set_appearance_mode(new_theme)
        self.theme_var.set(new_theme)

    def toggle_language(self):
        # 切换语言
        self.current_language = "en" if self.current_language == "zh" else "zh"
        
        # 更新界面文本
        self.root.title(self.translations[self.current_language]["title"])
        self.language_button.configure(text=self.translations[self.current_language]["language_switch"])
        self.input_box.configure(placeholder_text=self.translations[self.current_language]["input_placeholder"])
        self.send_button.configure(text=self.translations[self.current_language]["send"])
        
        # 更新所有按钮文本
        for widget in self.root.winfo_children():
            self.update_widget_language(widget)
            
    def update_widget_language(self, widget):
        """递归更新所有部件的语言"""
        if isinstance(widget, ctk.CTkButton):
            for lang_key in ["settings", "history", "theme_switch"]:
                if widget.cget("text") in [self.translations["zh"][lang_key], self.translations["en"][lang_key]]:
                    widget.configure(text=self.translations[self.current_language][lang_key])
                    break
        
        # 递归处理子部件
        for child in widget.winfo_children():
            self.update_widget_language(child)

    def open_github(self):
        """打开 GitHub 个人主页"""
        import webbrowser
        webbrowser.open("https://github.com/Travisma2233")

if __name__ == "__main__":
    root = ctk.CTk()
    app = AIChatApp(root)
    root.mainloop() 