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

# Whisper Manager 통합
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from whisper_manager import WhisperManager
try:
    from custom_widgets import RoundedButton
except ImportError:
    RoundedButton = None
from whisper_installer_ui import WhisperInstallerDialog

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
        
        # Whisper Manager 초기화
        self.whisper_manager = WhisperManager()
        self.whisper_model = None
        self.whisper_available = self.whisper_manager.is_whisper_installed()
        
        self.files_to_convert = []
        self.current_file_index = 0
        self.start_time = None
        self.is_converting = False
        
        self.setup_modern_ui()
        
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
            text="MP3",
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
            text="+",
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
            text="음성을 텍스트로 변환 (STT)",
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
        
        # STT 옵션 프레임 (토글로 표시/숨김)
        self.stt_options_frame = tk.Frame(options_frame, bg=self.colors['card'])
        
        # 모델 선택 프레임
        model_select_frame = tk.Frame(self.stt_options_frame, bg=self.colors['card'])
        model_select_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            model_select_frame,
            text="모델 선택:",
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # 모델 라디오 버튼들
        self.selected_model = tk.StringVar(value='tiny')
        models = [
            ('Tiny (39MB, 빠름)', 'tiny'),
            ('Base (74MB)', 'base'),
            ('Small (244MB, 추천)', 'small'),
            ('Medium (769MB, 정확)', 'medium')
        ]
        
        for text, value in models:
            rb = tk.Radiobutton(
                model_select_frame,
                text=text,
                variable=self.selected_model,
                value=value,
                font=('SF Pro Display', 10),
                bg=self.colors['card'],
                fg=self.colors['text'],
                selectcolor=self.colors['card'],
                activebackground=self.colors['card'],
                command=self.on_model_changed
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # 설치 상태 프레임
        self.install_status_frame = tk.Frame(self.stt_options_frame, bg=self.colors['card'])
        self.install_status_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.status_label = tk.Label(
            self.install_status_frame,
            text="",
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        self.status_label.pack(side=tk.LEFT)
        
        # 설치 버튼 (필요시 표시)
        if RoundedButton:
            self.install_button = RoundedButton(
                self.install_status_frame,
                text="설치하기",
                width=100,
                height=35,
                corner_radius=8,
                bg_color=self.colors['accent'],
                fg_color='white',
                hover_color=self.colors['accent_hover'],
                font=('SF Pro Display', 11, 'bold'),
                command=self.install_whisper
            )
        else:
            self.install_button = tk.Button(
                self.install_status_frame,
                text="설치하기",
                font=('SF Pro Display', 11, 'bold'),
                bg=self.colors['accent'],
                fg='white',
                relief=tk.RAISED,
                bd=2,
                padx=20,
                pady=5,
                command=self.install_whisper,
                cursor='hand2',
                activebackground='#e63600',
                activeforeground='white'
            )
        # 초기에는 숨김
        
        # 진행률 바 (설치 중 표시)
        self.install_progress = ttk.Progressbar(
            self.stt_options_frame,
            length=400,
            mode='determinate',
            style='modern.Horizontal.TProgressbar'
        )
    
    def toggle_stt_options(self):
        """Show/hide STT options"""
        if self.enable_stt.get():
            # STT 옵션 프레임 표시
            self.stt_options_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Whisper 설치 확인
            if not self.check_whisper_ready():
                # 설치 필요 표시
                self.show_install_required()
            else:
                # 모델 정보 표시
                self.show_model_info()
        else:
            self.stt_options_frame.pack_forget()
    
    def check_whisper_ready(self):
        """Whisper와 모델이 준비되었는지 확인"""
        if not self.whisper_manager.is_whisper_installed():
            return False
        
        # 설치된 모델 확인
        installed_models = self.whisper_manager.get_available_models()
        if not installed_models:
            return False
        
        return True
    
    def show_install_required(self):
        """설치 필요 메시지 표시"""
        # 시스템 확인 및 추천
        import platform
        system = platform.system()
        machine = platform.machine()
        
        if 'arm' in machine.lower() or 'aarch' in machine.lower():
            # Apple Silicon
            recommended = 'small'  # M1/M2는 small까지 빠르게 실행
            self.status_label.config(
                text="Apple Silicon 감지: Small 모델 추천 (빠르고 정확)",
                fg=self.colors['accent']
            )
        else:
            # Intel or others
            recommended = 'tiny'  # Intel은 tiny 추천
            self.status_label.config(
                text="Whisper 설치 필요: Tiny 모델 추천 (가장 빠름)",
                fg=self.colors['text_secondary']
            )
        
        self.selected_model.set(recommended)
        self.install_button.pack(side=tk.RIGHT, padx=(10, 0))
    
    def show_model_info(self):
        """모델 정보 표시"""
        installed_models = self.whisper_manager.get_available_models()
        current = self.selected_model.get()
        
        if current in installed_models:
            self.status_label.config(
                text=f"✓ {current.upper()} 모델 설치됨",
                fg=self.colors['success']
            )
            self.install_button.pack_forget()
        else:
            self.status_label.config(
                text=f"{current.upper()} 모델 설치 필요",
                fg=self.colors['text_secondary']
            )
            self.install_button.pack(side=tk.RIGHT, padx=(10, 0))
    
    def on_model_changed(self):
        """모델 선택 변경시"""
        if self.check_whisper_ready():
            self.show_model_info()
    
    def install_whisper(self):
        """Whisper 설치"""
        self.install_button.config(state=tk.DISABLED)
        self.install_progress.pack(fill=tk.X, padx=15, pady=5)
        
        def install_thread():
            try:
                # Whisper 설치
                if not self.whisper_manager.is_whisper_installed():
                    self.update_install_progress(10, "Whisper 엔진 설치 중...")
                    success = self.whisper_manager.install_whisper_minimal(
                        lambda p, m: self.update_install_progress(p * 0.5, m)
                    )
                    if not success:
                        self.install_failed("Whisper 설치 실패")
                        return
                
                # 모델 다운로드
                model = self.selected_model.get()
                self.update_install_progress(50, f"{model.upper()} 모델 다운로드 중...")
                success = self.whisper_manager.download_model(
                    model,
                    lambda p, m: self.update_install_progress(50 + p * 0.5, m)
                )
                
                if success:
                    self.install_complete()
                else:
                    self.install_failed("모델 다운로드 실패")
                    
            except Exception as e:
                self.install_failed(str(e))
        
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
    
    def update_install_progress(self, percent, message):
        """설치 진행률 업데이트"""
        self.root.after(0, lambda: self._update_progress_ui(percent, message))
    
    def _update_progress_ui(self, percent, message):
        self.status_label.config(text=message)
        self.install_progress['value'] = percent
    
    def install_complete(self):
        """설치 완료"""
        self.root.after(0, lambda: self._install_complete_ui())
    
    def _install_complete_ui(self):
        self.install_progress.pack_forget()
        self.install_button.config(state=tk.NORMAL)
        self.whisper_available = True
        self.show_model_info()
        messagebox.showinfo("설치 완료", "Whisper STT가 성공적으로 설치되었습니다!")
    
    def install_failed(self, error):
        """설치 실패"""
        self.root.after(0, lambda: self._install_failed_ui(error))
    
    def _install_failed_ui(self, error):
        self.install_progress.pack_forget()
        self.install_button.config(state=tk.NORMAL)
        messagebox.showerror("설치 실패", f"설치 중 오류가 발생했습니다:\n{error}")
    
    
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
                text=f"{count}개 파일 선택됨",
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
        
        # STT 사용 시 모델 로드
        if self.enable_stt.get():
            model_name = self.selected_model.get()
            installed = self.whisper_manager.get_available_models()
            
            if not self.whisper_manager.is_whisper_installed() or model_name not in installed:
                messagebox.showwarning("STT 불가", f"{model_name.upper()} 모델이 설치되지 않았습니다.\nSTT 없이 변환을 진행합니다.")
                self.enable_stt.set(False)
            else:
                # 모델 미리 로드
                try:
                    self.status_label.config(text=f"{model_name.upper()} 모델 로딩 중...")
                    self.whisper_model = self.whisper_manager.load_model(model_name)
                except Exception as e:
                    messagebox.showwarning("모델 로드 실패", f"AI 모델을 로드할 수 없습니다.\n{e}")
                    self.enable_stt.set(False)
        
        # UI update
        self.drop_frame.master.pack_forget()
        self.stt_options_frame.pack_forget()
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        
        # Start conversion
        self.is_converting = True
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
    
    def get_file_duration(self, file_path):
        """Get duration of media file in seconds"""
        try:
            cmd = [
                self.ffmpeg_path or 'ffmpeg',
                '-i', file_path,
                '-f', 'null',
                '-'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse duration from stderr
            import re
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+', result.stderr)
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = int(duration_match.group(3))
                return hours * 3600 + minutes * 60 + seconds
        except:
            pass
        return 0
    
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
            
            # Get file duration first
            duration = self.get_file_duration(str(input_path))
            
            try:
                # Convert to MP3 with real-time progress
                cmd = [
                    self.ffmpeg_path,
                    '-i', str(input_path),
                    '-vn',
                    '-acodec', 'libmp3lame',
                    '-ab', '192k',
                    '-y',
                    '-progress', 'pipe:1',  # Output progress to stdout
                    str(output_path)
                ]
                
                # Use Popen for real-time progress
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                
                # Read progress
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    # Parse progress
                    if 'out_time_ms=' in line:
                        try:
                            time_ms = int(line.split('=')[1])
                            current_seconds = time_ms / 1000000
                            if duration > 0:
                                file_percent = min(int((current_seconds / duration) * 100), 100)
                                overall_percent = int(((i + file_percent/100) / total) * 100)
                                self.root.after(0, self.update_progress, input_path.name, overall_percent)
                        except:
                            pass
                
                process.wait()
                
                # STT if enabled
                if self.enable_stt.get() and self.whisper_model:
                    self.root.after(0, lambda name=input_path.name: self.status_label.config(
                        text=f"음성 인식 중: {name}"
                    ))
                    
                    try:
                        result = self.whisper_model.transcribe(
                            str(output_path),
                            language='ko',
                            fp16=False
                        )
                        
                        text = result.get('text', '').strip()
                        if text:
                            txt_path = input_path.with_suffix('.txt')
                            with open(txt_path, 'w', encoding='utf-8') as f:
                                f.write(text)
                            
                            self.root.after(0, lambda name=txt_path.name: self.status_label.config(
                                text=f"텍스트 파일 생성: {name}"
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
        self.whisper_model = None  # 모델 메모리 해제
        messagebox.showinfo("완료", "모든 파일 변환이 완료되었습니다!")
        self.clear_files()

def main():
    root = tk.Tk()
    app = ModernMP4Converter(root)
    root.mainloop()

if __name__ == "__main__":
    main()