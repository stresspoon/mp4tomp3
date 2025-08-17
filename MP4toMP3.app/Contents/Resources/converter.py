#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import os
from pathlib import Path
import sys
import time
import platform
import re
import urllib.request
import webbrowser

# Whisper 자동 설치 함수
def ensure_whisper_installed():
    """Whisper가 설치되어 있지 않으면 자동으로 설치"""
    try:
        import whisper
        return True
    except ImportError:
        print("Whisper not found. Installing automatically...")
        try:
            # pip로 자동 설치
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
            
            # 다시 import 시도
            import whisper
            print("✅ Whisper installed successfully!")
            return True
        except Exception as e:
            print(f"Failed to install Whisper: {e}")
            return False

# 앱 시작 시 Whisper 확인/설치
_WHISPER_AVAILABLE = ensure_whisper_installed()
_WHISPER_MODEL_CACHE = {}

def load_whisper_model(model_name: str):
    """Load whisper model with auto-installation"""
    global _WHISPER_MODEL_CACHE
    
    if not _WHISPER_AVAILABLE:
        if not ensure_whisper_installed():
            raise RuntimeError("Whisper 설치에 실패했습니다")
    
    device = 'cpu'
    key = f'{model_name}:{device}'
    
    if key in _WHISPER_MODEL_CACHE:
        return _WHISPER_MODEL_CACHE[key]
    
    try:
        import whisper
        print(f"Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name, device=device)
        _WHISPER_MODEL_CACHE[key] = model
        return model
    except Exception as e:
        raise RuntimeError(f'모델 로드 실패: {e}')

class ModernMP4Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 to MP3 Converter")
        self.root.geometry("800x650")
        
        # Modern color scheme
        self.colors = {
            'bg': '#0f0f0f',           # Dark background
            'card': '#1a1a1a',         # Card background
            'accent': '#3b82f6',       # Blue accent
            'accent_hover': '#2563eb', # Darker blue
            'text': '#ffffff',         # White text
            'text_secondary': '#9ca3af', # Gray text
            'success': '#10b981',      # Green
            'error': '#ef4444',        # Red
            'border': '#2d2d2d'        # Border color
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Window styling
        self.root.resizable(False, False)
        if platform.system() == 'Darwin':
            self.root.createcommand('tk::mac::ShowPreferences', lambda: None)
        
        self.files_to_convert = []
        self.current_file_index = 0
        self.start_time = None
        self.is_converting = False
        self.selected_model = 'small'
        
        self.setup_modern_ui()
        
        # Auto-install Whisper in background
        threading.Thread(target=self.check_whisper_installation, daemon=True).start()
        
    def check_whisper_installation(self):
        """Background check and install Whisper if needed"""
        try:
            global _WHISPER_AVAILABLE
            if not _WHISPER_AVAILABLE:
                self.root.after(0, lambda: self.show_installation_dialog())
                _WHISPER_AVAILABLE = ensure_whisper_installed()
                if _WHISPER_AVAILABLE:
                    self.root.after(0, lambda: self.installation_complete())
        except Exception as e:
            print(f"Whisper check error: {e}")
    
    def show_installation_dialog(self):
        """Show installation progress dialog"""
        self.install_dialog = tk.Toplevel(self.root)
        self.install_dialog.title("설치 중")
        self.install_dialog.geometry("400x150")
        self.install_dialog.configure(bg=self.colors['card'])
        self.install_dialog.transient(self.root)
        self.install_dialog.grab_set()
        
        tk.Label(
            self.install_dialog,
            text="🔄 Whisper STT 자동 설치 중...",
            font=('SF Pro Display', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        tk.Label(
            self.install_dialog,
            text="잠시만 기다려주세요 (최초 1회)",
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        ).pack()
        
        progress = ttk.Progressbar(
            self.install_dialog,
            mode='indeterminate',
            length=300
        )
        progress.pack(pady=20)
        progress.start(10)
    
    def installation_complete(self):
        """Close installation dialog"""
        if hasattr(self, 'install_dialog'):
            self.install_dialog.destroy()
            messagebox.showinfo("설치 완료", "Whisper STT가 성공적으로 설치되었습니다!")
        
    def setup_modern_ui(self):
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title section
        self.create_title_section(main_container)
        
        # Drop zone card
        self.create_drop_zone(main_container)
        
        # Options section
        self.create_options_section(main_container)
        
        # Progress section (hidden initially)
        self.create_progress_section(main_container)
        
        # Bottom buttons
        self.create_buttons_section(main_container)
        
    def create_title_section(self, parent):
        """Create modern title section"""
        title_frame = tk.Frame(parent, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # App icon and title
        title_container = tk.Frame(title_frame, bg=self.colors['bg'])
        title_container.pack()
        
        tk.Label(
            title_container,
            text="🎵",
            font=('SF Pro Display', 32),
            bg=self.colors['bg'],
            fg=self.colors['accent']
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        title_text_frame = tk.Frame(title_container, bg=self.colors['bg'])
        title_text_frame.pack(side=tk.LEFT)
        
        tk.Label(
            title_text_frame,
            text="MP4 to MP3 Converter",
            font=('SF Pro Display', 24, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        tk.Label(
            title_text_frame,
            text="with AI Speech Recognition",
            font=('SF Pro Display', 12),
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w')
    
    def create_drop_zone(self, parent):
        """Create modern drop zone"""
        # Card container
        card = tk.Frame(
            parent,
            bg=self.colors['card'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.drop_frame = tk.Frame(card, bg=self.colors['card'])
        self.drop_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Drop zone content
        drop_content = tk.Frame(self.drop_frame, bg=self.colors['card'])
        drop_content.pack(expand=True)
        
        tk.Label(
            drop_content,
            text="📁",
            font=('SF Pro Display', 48),
            bg=self.colors['card'],
            fg=self.colors['accent']
        ).pack(pady=(40, 10))
        
        self.drop_label = tk.Label(
            drop_content,
            text="드래그 앤 드롭 또는 클릭하여 파일 선택",
            font=('SF Pro Display', 14),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        self.drop_label.pack(pady=(0, 5))
        
        tk.Label(
            drop_content,
            text="MP4 파일을 MP3로 변환합니다",
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        ).pack(pady=(0, 40))
        
        # Make clickable
        self.drop_frame.bind("<Button-1>", lambda e: self.select_files())
        drop_content.bind("<Button-1>", lambda e: self.select_files())
        for widget in drop_content.winfo_children():
            widget.bind("<Button-1>", lambda e: self.select_files())
        
        # Hover effect
        def on_enter(e):
            card.configure(highlightbackground=self.colors['accent'])
        def on_leave(e):
            card.configure(highlightbackground=self.colors['border'])
        
        self.drop_frame.bind("<Enter>", on_enter)
        self.drop_frame.bind("<Leave>", on_leave)
    
    def create_options_section(self, parent):
        """Create modern options section"""
        options_frame = tk.Frame(parent, bg=self.colors['bg'])
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # STT Toggle
        stt_container = tk.Frame(options_frame, bg=self.colors['card'], highlightbackground=self.colors['border'], highlightthickness=1)
        stt_container.pack(fill=tk.X, pady=(0, 10))
        
        stt_inner = tk.Frame(stt_container, bg=self.colors['card'])
        stt_inner.pack(fill=tk.X, padx=15, pady=12)
        
        self.enable_stt = tk.BooleanVar(value=False)
        
        # Custom checkbox
        self.stt_check = tk.Checkbutton(
            stt_inner,
            text="🎤 음성을 텍스트로 변환 (STT)",
            variable=self.enable_stt,
            font=('SF Pro Display', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            selectcolor=self.colors['card'],
            activebackground=self.colors['card'],
            activeforeground=self.colors['accent'],
            command=self.toggle_stt_options
        )
        self.stt_check.pack(side=tk.LEFT)
        
        # Model selection (shown when STT is enabled)
        self.model_frame = tk.Frame(options_frame, bg=self.colors['card'], highlightbackground=self.colors['border'], highlightthickness=1)
        
        model_inner = tk.Frame(self.model_frame, bg=self.colors['card'])
        model_inner.pack(fill=tk.X, padx=15, pady=12)
        
        tk.Label(
            model_inner,
            text="AI 모델:",
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_var = tk.StringVar(value='small')
        model_buttons = [
            ('tiny', '최고속'),
            ('base', '빠름'),
            ('small', '추천'),
            ('medium', '정확'),
            ('large-v3', '최고품질')
        ]
        
        for value, label in model_buttons:
            btn = tk.Radiobutton(
                model_inner,
                text=label,
                variable=self.model_var,
                value=value,
                font=('SF Pro Display', 11),
                bg=self.colors['card'],
                fg=self.colors['text'],
                selectcolor=self.colors['accent'],
                activebackground=self.colors['card']
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def toggle_stt_options(self):
        """Show/hide STT options"""
        if self.enable_stt.get():
            self.model_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.model_frame.pack_forget()
    
    def create_progress_section(self, parent):
        """Create modern progress section"""
        self.progress_frame = tk.Frame(parent, bg=self.colors['bg'])
        
        # Progress card
        progress_card = tk.Frame(
            self.progress_frame,
            bg=self.colors['card'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        progress_card.pack(fill=tk.BOTH, expand=True)
        
        progress_inner = tk.Frame(progress_card, bg=self.colors['card'])
        progress_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Current file
        self.current_file_label = tk.Label(
            progress_inner,
            text="변환 중...",
            font=('SF Pro Display', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        self.current_file_label.pack(anchor='w', pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_inner,
            length=740,
            mode='determinate',
            style='modern.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Progress text
        self.progress_text = tk.Label(
            progress_inner,
            text="0%",
            font=('SF Pro Display', 24, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['accent']
        )
        self.progress_text.pack(pady=(10, 5))
        
        # Status
        self.status_label = tk.Label(
            progress_inner,
            text="",
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        self.status_label.pack()
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure(
            'modern.Horizontal.TProgressbar',
            troughcolor=self.colors['border'],
            background=self.colors['accent'],
            borderwidth=0,
            lightcolor=self.colors['accent'],
            darkcolor=self.colors['accent']
        )
    
    def create_buttons_section(self, parent):
        """Create modern buttons"""
        button_frame = tk.Frame(parent, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Convert button
        self.convert_button = tk.Button(
            button_frame,
            text="변환 시작",
            font=('SF Pro Display', 14, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=12,
            command=self.start_conversion,
            state=tk.DISABLED
        )
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_button = tk.Button(
            button_frame,
            text="초기화",
            font=('SF Pro Display', 14),
            bg=self.colors['card'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=12,
            command=self.clear_files,
            state=tk.DISABLED
        )
        self.clear_button.pack(side=tk.LEFT)
        
        # GitHub link
        github_label = tk.Label(
            button_frame,
            text="GitHub",
            font=('SF Pro Display', 11, 'underline'),
            bg=self.colors['bg'],
            fg=self.colors['text_secondary'],
            cursor='hand2'
        )
        github_label.pack(side=tk.RIGHT)
        github_label.bind("<Button-1>", lambda e: webbrowser.open('https://github.com/stresspoon/mp4tomp3'))
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="MP4 파일 선택",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if files:
            self.add_files(files)
    
    def add_files(self, files):
        self.files_to_convert = list(files)
        count = len(self.files_to_convert)
        
        if count > 0:
            self.drop_label.config(
                text=f"✅ {count}개 파일 선택됨",
                fg=self.colors['success']
            )
            self.convert_button.config(state=tk.NORMAL, cursor='hand2')
            self.clear_button.config(state=tk.NORMAL, cursor='hand2')
    
    def clear_files(self):
        self.files_to_convert = []
        self.drop_label.config(
            text="드래그 앤 드롭 또는 클릭하여 파일 선택",
            fg=self.colors['text']
        )
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.progress_frame.pack_forget()
        self.drop_frame.master.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    def start_conversion(self):
        if not self.files_to_convert:
            return
        
        # Check ffmpeg
        self.ffmpeg_path = self.check_ffmpeg()
        if not self.ffmpeg_path:
            messagebox.showerror("오류", "ffmpeg를 찾을 수 없습니다")
            return
        
        # UI update
        self.drop_frame.master.pack_forget()
        self.model_frame.pack_forget()
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        
        # Start conversion
        self.is_converting = True
        self.selected_model = self.model_var.get()
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
    
    def check_ffmpeg(self):
        # Check for embedded ffmpeg
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        if platform.system() == 'Darwin':
            # macOS
            possible_paths = [
                os.path.join(os.path.dirname(app_dir), 'MacOS', 'ffmpeg'),
                '/opt/homebrew/bin/ffmpeg',
                '/usr/local/bin/ffmpeg'
            ]
        else:
            # Windows
            possible_paths = [
                os.path.join(app_dir, 'ffmpeg.exe'),
                'ffmpeg.exe'
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try system ffmpeg
        try:
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def convert_files(self):
        total = len(self.files_to_convert)
        
        for i, file_path in enumerate(self.files_to_convert):
            if not self.is_converting:
                break
            
            input_path = Path(file_path)
            output_path = input_path.with_suffix('.mp3')
            
            # Update UI
            percent = int(((i + 0.5) / total) * 100)
            self.root.after(0, self.update_progress, input_path.name, percent)
            
            try:
                # Convert to MP3
                cmd = [
                    self.ffmpeg_path,
                    '-i', str(input_path),
                    '-vn',
                    '-acodec', 'libmp3lame',
                    '-ab', '192k',
                    '-y',
                    str(output_path)
                ]
                
                subprocess.run(cmd, capture_output=True)
                
                # STT if enabled
                if self.enable_stt.get():
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"🎤 음성 인식 중: {input_path.name}"
                    ))
                    
                    try:
                        model = load_whisper_model(self.selected_model)
                        result = model.transcribe(
                            str(output_path),
                            language='ko',
                            fp16=False
                        )
                        
                        text = result.get('text', '').strip()
                        if text:
                            txt_path = input_path.with_suffix('.txt')
                            with open(txt_path, 'w', encoding='utf-8') as f:
                                f.write(text)
                            
                            self.root.after(0, lambda: self.status_label.config(
                                text=f"✅ 텍스트 파일 생성: {txt_path.name}"
                            ))
                    except Exception as e:
                        print(f"STT error: {e}")
                
            except Exception as e:
                print(f"Conversion error: {e}")
        
        # Complete
        self.root.after(0, self.conversion_complete)
    
    def update_progress(self, filename, percent):
        self.current_file_label.config(text=f"변환 중: {filename}")
        self.progress_bar['value'] = percent
        self.progress_text.config(text=f"{percent}%")
    
    def conversion_complete(self):
        self.is_converting = False
        messagebox.showinfo("완료", "모든 파일 변환이 완료되었습니다!")
        self.clear_files()

def main():
    root = tk.Tk()
    app = ModernMP4Converter(root)
    root.mainloop()

if __name__ == "__main__":
    main()