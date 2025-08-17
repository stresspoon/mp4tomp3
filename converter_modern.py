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
def ensure_whisper_installed(show_terminal=False):
    """Whisper가 설치되어 있지 않으면 자동으로 설치"""
    try:
        import whisper
        return True
    except ImportError:
        if show_terminal:
            return install_whisper_with_terminal()
        else:
            return install_whisper_silent()

def install_whisper_silent():
    """Silent installation with timeout"""
    try:
        print("Installing Whisper in background...")
        # Simple installation without pip upgrade to avoid hanging
        process = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "openai-whisper"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait with timeout (5 minutes)
        try:
            process.wait(timeout=300)
        except subprocess.TimeoutExpired:
            process.kill()
            print("Installation timeout - switching to terminal mode")
            return install_whisper_with_terminal()
        
        # Check if successful
        try:
            import whisper
            return True
        except ImportError:
            return False
    except Exception as e:
        print(f"Silent installation failed: {e}")
        return False

def install_whisper_with_terminal():
    """Installation with visible terminal"""
    try:
        print("Opening terminal for Whisper installation...")
        
        # Create installation script - use raw string to avoid escape issues
        install_script = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import time
import os

print("="*60)
print("Whisper STT Auto Installation")
print("="*60)
print()
print("Installing Whisper... Please wait...")
print("Press Ctrl+C to cancel if needed.")
print()

try:
    # Show progress with real output
    print("[1/2] Installing Whisper package...")
    process = subprocess.Popen(
        [sys.executable, "-m", "pip", "install", "openai-whisper"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Show real-time output
    for line in process.stdout:
        print(line.rstrip())
    
    process.wait()
    
    if process.returncode != 0:
        raise Exception("Installation failed")
    
    # Verify installation
    print()
    print("[2/2] Verifying installation...")
    import whisper
    print()
    print("="*60)
    print("SUCCESS! Whisper installed successfully!")
    print("This window will close in 5 seconds...")
    print("="*60)
    time.sleep(5)
    
except KeyboardInterrupt:
    print("\n\nInstallation cancelled by user.")
    time.sleep(2)
except Exception as e:
    print(f"\n\nERROR: Installation failed: {e}")
    print("\nManual installation:")
    print("1. Open terminal")
    print("2. Run: pip install openai-whisper")
    print("\nPress Enter to close...")
    input()
'''.replace('\\n', '\n')
        
        # Save script temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(install_script)
            script_path = f.name
        
        # Make script executable on Unix
        if platform.system() != 'Windows':
            os.chmod(script_path, 0o755)
        
        # Run script in new terminal window
        if platform.system() == 'Darwin':  # macOS
            # Use osascript to open Terminal and run the script
            apple_script = f'''tell application "Terminal"
                activate
                do script "python3 '{script_path}'; exit"
            end tell'''
            subprocess.run(['osascript', '-e', apple_script])
        elif platform.system() == 'Windows':
            # Windows: Use start command to open new cmd window
            subprocess.Popen(
                f'start "Whisper Installation" cmd /c "python "{script_path}" & pause"',
                shell=True
            )
        else:  # Linux
            # Try different terminal emulators
            terminals = ['gnome-terminal', 'konsole', 'xterm', 'x-terminal-emulator']
            for term in terminals:
                try:
                    if term == 'gnome-terminal':
                        subprocess.Popen([term, '--', 'python3', script_path])
                    else:
                        subprocess.Popen([term, '-e', f'python3 {script_path}'])
                    break
                except:
                    continue
        
        # Wait and check if installation succeeded
        max_wait = 120  # 2 minutes
        for i in range(max_wait):
            time.sleep(1)
            try:
                # Try to import whisper
                import importlib
                importlib.invalidate_caches()
                whisper_module = importlib.import_module('whisper')
                
                # Clean up temp file
                try:
                    time.sleep(2)  # Give terminal time to finish
                    os.unlink(script_path)
                except:
                    pass
                return True
            except ImportError:
                if i == max_wait - 1:
                    # Last attempt - clean up anyway
                    try:
                        os.unlink(script_path)
                    except:
                        pass
                continue
        
        return False
        
    except Exception as e:
        print(f"Terminal installation failed: {e}")
        return False

# 앱 시작 시 Whisper 확인 (설치는 나중에)
_WHISPER_AVAILABLE = False
try:
    import whisper
    _WHISPER_AVAILABLE = True
except ImportError:
    _WHISPER_AVAILABLE = False

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
        
        # Modern color scheme from complete-guide.md
        self.colors = {
            'bg': '#f2f1ef',           # Light background
            'card': '#ffffff',         # White card background
            'accent': '#ff3d00',       # Orange accent
            'accent_hover': '#e63600', # Darker orange on hover
            'text': '#131313',         # Dark text
            'text_secondary': '#666666', # Gray text
            'success': '#10b981',      # Green
            'error': '#ef4444',        # Red
            'border': '#e0e0e0'        # Light border
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
                # Ask user immediately for installation method
                self.root.after(100, lambda: self.ask_installation_method())
        except Exception as e:
            print(f"Whisper check error: {e}")
    
    def ask_installation_method(self):
        """Ask user which installation method to use"""
        result = messagebox.askyesnocancel(
            "Whisper STT 설치 필요",
            "Whisper STT가 설치되지 않았습니다.\n\n"
            "터미널 창에서 설치를 진행하시겠습니까?\n"
            "(설치 과정을 실시간으로 확인할 수 있습니다)\n\n"
            "Yes: 터미널에서 설치\n"
            "No: 백그라운드 설치 (보이지 않음)\n"
            "Cancel: 나중에 설치"
        )
        
        global _WHISPER_AVAILABLE
        
        if result is True:  # Yes - Terminal installation
            _WHISPER_AVAILABLE = install_whisper_with_terminal()
            if _WHISPER_AVAILABLE:
                self.installation_complete()
            else:
                self.installation_failed()
        elif result is False:  # No - Background installation
            self.show_background_installation()
            # Run in thread to not block UI
            def bg_install():
                global _WHISPER_AVAILABLE
                _WHISPER_AVAILABLE = install_whisper_silent()
                if _WHISPER_AVAILABLE:
                    self.root.after(0, lambda: self.installation_complete())
                else:
                    self.root.after(0, lambda: self.installation_failed())
            threading.Thread(target=bg_install, daemon=True).start()
        # else: Cancel - do nothing
    
    def show_background_installation(self):
        """Show background installation progress"""
        self.install_dialog = tk.Toplevel(self.root)
        self.install_dialog.title("Whisper 설치 중")
        self.install_dialog.geometry("400x150")
        self.install_dialog.configure(bg=self.colors['card'])
        self.install_dialog.transient(self.root)
        
        # Center the dialog
        self.install_dialog.update_idletasks()
        x = (self.install_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.install_dialog.winfo_screenheight() // 2) - (150 // 2)
        self.install_dialog.geometry(f"400x150+{x}+{y}")
        
        tk.Label(
            self.install_dialog,
            text="🔄 Whisper STT 설치 중...",
            font=('SF Pro Display', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(pady=(30, 10))
        
        tk.Label(
            self.install_dialog,
            text="백그라운드에서 설치 중 (최대 5분)",
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        ).pack()
        
        # Progress bar
        progress = ttk.Progressbar(
            self.install_dialog,
            mode='indeterminate',
            length=300
        )
        progress.pack(pady=20)
        progress.start(10)
    
    def installation_failed(self):
        """Show installation failure message"""
        if hasattr(self, 'install_dialog'):
            self.install_dialog.destroy()
        
        messagebox.showerror(
            "설치 실패",
            "Whisper 설치에 실패했습니다.\n\n"
            "수동 설치 방법:\n"
            "1. 터미널/명령 프롬프트 열기\n"
            "2. 다음 명령어 실행:\n"
            "   pip install openai-whisper"
        )
    
    
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
        
        # Convert button with hover effect
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
            state=tk.DISABLED,
            activebackground=self.colors['accent_hover'],
            activeforeground='white'
        )
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bind hover events
        self.convert_button.bind('<Enter>', lambda e: self.convert_button.config(bg=self.colors['accent_hover']) if self.convert_button['state'] == tk.NORMAL else None)
        self.convert_button.bind('<Leave>', lambda e: self.convert_button.config(bg=self.colors['accent']) if self.convert_button['state'] == tk.NORMAL else None)
        
        # Clear button with hover effect
        self.clear_button = tk.Button(
            button_frame,
            text="초기화",
            font=('SF Pro Display', 14),
            bg=self.colors['text_secondary'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=12,
            command=self.clear_files,
            state=tk.DISABLED,
            activebackground='#555555',
            activeforeground='white'
        )
        self.clear_button.pack(side=tk.LEFT)
        
        # Bind hover events
        self.clear_button.bind('<Enter>', lambda e: self.clear_button.config(bg='#555555') if self.clear_button['state'] == tk.NORMAL else None)
        self.clear_button.bind('<Leave>', lambda e: self.clear_button.config(bg=self.colors['text_secondary']) if self.clear_button['state'] == tk.NORMAL else None)
        
        # Remove GitHub link - no replacement needed
    
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
                    # Check if Whisper is available
                    global _WHISPER_AVAILABLE
                    if not _WHISPER_AVAILABLE:
                        # Try to install if not available
                        self.root.after(0, lambda: messagebox.showwarning(
                            "Whisper 미설치",
                            "Whisper가 설치되지 않았습니다.\n"
                            "프로그램을 재시작하면 자동 설치됩니다."
                        ))
                        continue
                    
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