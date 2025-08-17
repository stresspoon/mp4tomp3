#!/usr/bin/env python3
"""
Whisper 설치 UI - 사용자 친화적 설치 경험
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from whisper_manager import WhisperManager

class WhisperInstallerDialog:
    """Whisper 설치 다이얼로그"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.manager = WhisperManager()
        
        # 다이얼로그 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Whisper STT 설정")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # 색상 테마
        self.colors = {
            'bg': '#f2f1ef',
            'card': '#ffffff',
            'accent': '#ff3d00',
            'text': '#131313',
            'text_secondary': '#666666',
            'success': '#10b981'
        }
        
        self.dialog.configure(bg=self.colors['bg'])
        self.setup_ui()
        self.center_window()
        
    def center_window(self):
        """창 중앙 정렬"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
    
    def setup_ui(self):
        """UI 구성"""
        # 제목
        title_frame = tk.Frame(self.dialog, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(
            title_frame,
            text="🎤 음성 인식 설정",
            font=('SF Pro Display', 18, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack()
        
        tk.Label(
            title_frame,
            text="Whisper AI 모델을 선택하세요",
            font=('SF Pro Display', 11),
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack()
        
        # 모델 선택 카드들
        models_frame = tk.Frame(self.dialog, bg=self.colors['bg'])
        models_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.selected_model = tk.StringVar(value='tiny')
        
        model_options = [
            {
                'name': 'tiny',
                'title': '⚡ Tiny (최고속)',
                'desc': '가장 빠른 처리\n정확도: ★★☆☆☆',
                'size': '39MB',
                'color': '#10b981'
            },
            {
                'name': 'base',
                'title': '🚀 Base (빠름)',
                'desc': '빠른 처리\n정확도: ★★★☆☆',
                'size': '74MB',
                'color': '#3b82f6'
            },
            {
                'name': 'small',
                'title': '⭐ Small (추천)',
                'desc': '균형잡힌 성능\n정확도: ★★★★☆',
                'size': '244MB',
                'color': '#ff3d00'
            },
            {
                'name': 'medium',
                'title': '💎 Medium (정확)',
                'desc': '높은 정확도\n정확도: ★★★★☆',
                'size': '769MB',
                'color': '#8b5cf6'
            }
        ]
        
        for i, model in enumerate(model_options):
            self.create_model_card(models_frame, model, i)
        
        # 설치 옵션
        options_frame = tk.Frame(self.dialog, bg=self.colors['card'])
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.auto_install = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="필요한 구성 요소 자동 설치",
            variable=self.auto_install,
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(padx=10, pady=10)
        
        # 공간 정보
        info_frame = tk.Frame(self.dialog, bg=self.colors['bg'])
        info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.space_label = tk.Label(
            info_frame,
            text="",
            font=('SF Pro Display', 10),
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        )
        self.space_label.pack()
        self.update_space_info()
        
        # 진행률 표시 (숨김)
        self.progress_frame = tk.Frame(self.dialog, bg=self.colors['bg'])
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=('SF Pro Display', 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=460,
            mode='determinate'
        )
        self.progress_bar.pack(pady=5)
        
        # 버튼
        button_frame = tk.Frame(self.dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        self.install_button = tk.Button(
            button_frame,
            text="설치 시작",
            font=('SF Pro Display', 12, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.start_installation
        )
        self.install_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="나중에",
            font=('SF Pro Display', 12),
            bg=self.colors['text_secondary'],
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # STT 없이 사용 옵션
        tk.Button(
            button_frame,
            text="STT 없이 사용",
            font=('SF Pro Display', 11),
            bg=self.colors['bg'],
            fg=self.colors['text_secondary'],
            relief=tk.FLAT,
            command=self.skip_stt
        ).pack(side=tk.RIGHT)
    
    def create_model_card(self, parent, model, index):
        """모델 선택 카드 생성"""
        card = tk.Frame(
            parent,
            bg=self.colors['card'],
            highlightbackground=self.colors['card'],
            highlightthickness=2
        )
        card.pack(fill=tk.X, pady=5)
        
        # 라디오 버튼
        radio = tk.Radiobutton(
            card,
            text='',
            variable=self.selected_model,
            value=model['name'],
            bg=self.colors['card'],
            command=self.update_space_info
        )
        radio.pack(side=tk.LEFT, padx=10)
        
        # 모델 정보
        info_frame = tk.Frame(card, bg=self.colors['card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_line = tk.Frame(info_frame, bg=self.colors['card'])
        title_line.pack(fill=tk.X)
        
        tk.Label(
            title_line,
            text=model['title'],
            font=('SF Pro Display', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        # 설치 상태
        if model['name'] in self.manager.get_available_models():
            tk.Label(
                title_line,
                text="✓ 설치됨",
                font=('SF Pro Display', 10),
                bg=self.colors['card'],
                fg=self.colors['success']
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(
            info_frame,
            text=model['desc'],
            font=('SF Pro Display', 10),
            bg=self.colors['card'],
            fg=self.colors['text_secondary'],
            justify=tk.LEFT
        ).pack(anchor='w')
        
        # 크기 표시
        size_label = tk.Label(
            card,
            text=model['size'],
            font=('SF Pro Display', 11, 'bold'),
            bg=self.colors['card'],
            fg=model['color']
        )
        size_label.pack(side=tk.RIGHT, padx=15)
        
        # 호버 효과
        def on_enter(e):
            card.configure(highlightbackground=model['color'])
        
        def on_leave(e):
            card.configure(highlightbackground=self.colors['card'])
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # 클릭으로 선택
        card.bind("<Button-1>", lambda e: self.selected_model.set(model['name']))
    
    def update_space_info(self):
        """필요 공간 정보 업데이트"""
        model = self.selected_model.get()
        size_mb = self.manager.estimate_space_needed(model)
        
        if not self.manager.is_whisper_installed():
            self.space_label.config(
                text=f"💾 필요한 디스크 공간: 약 {size_mb}MB (Whisper 엔진 포함)"
            )
        else:
            model_size = self.manager.MODEL_SIZES[model]['size']
            self.space_label.config(
                text=f"💾 필요한 디스크 공간: 약 {model_size}MB"
            )
    
    def start_installation(self):
        """설치 시작"""
        self.install_button.config(state=tk.DISABLED)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=10, before=self.space_label.master)
        
        def install_thread():
            try:
                # 1. Whisper 설치 (필요시)
                if not self.manager.is_whisper_installed() and self.auto_install.get():
                    self.update_progress(0, "Whisper 엔진 설치 중...")
                    success = self.manager.install_whisper_minimal(self.update_progress)
                    if not success:
                        self.installation_failed("Whisper 설치 실패")
                        return
                
                # 2. 모델 다운로드
                model = self.selected_model.get()
                self.update_progress(0, f"{model} 모델 다운로드 중...")
                success = self.manager.download_model(model, self.update_progress)
                
                if success:
                    self.installation_complete()
                else:
                    self.installation_failed("모델 다운로드 실패")
                    
            except Exception as e:
                self.installation_failed(str(e))
        
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
    
    def update_progress(self, percent, message):
        """진행률 업데이트"""
        self.dialog.after(0, lambda: self._update_progress_ui(percent, message))
    
    def _update_progress_ui(self, percent, message):
        """UI 스레드에서 진행률 업데이트"""
        self.progress_label.config(text=message)
        self.progress_bar['value'] = percent
    
    def installation_complete(self):
        """설치 완료"""
        self.dialog.after(0, lambda: self._installation_complete_ui())
    
    def _installation_complete_ui(self):
        """UI 스레드에서 설치 완료 처리"""
        messagebox.showinfo("설치 완료", "Whisper STT가 성공적으로 설치되었습니다!")
        if self.callback:
            self.callback(True)
        self.dialog.destroy()
    
    def installation_failed(self, error):
        """설치 실패"""
        self.dialog.after(0, lambda: self._installation_failed_ui(error))
    
    def _installation_failed_ui(self, error):
        """UI 스레드에서 설치 실패 처리"""
        messagebox.showerror("설치 실패", f"설치 중 오류가 발생했습니다:\n{error}")
        self.install_button.config(state=tk.NORMAL)
        self.progress_frame.pack_forget()
    
    def skip_stt(self):
        """STT 없이 사용"""
        if self.callback:
            self.callback(False)
        self.dialog.destroy()


# 테스트용
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    def callback(installed):
        print(f"설치 결과: {installed}")
        root.quit()
    
    dialog = WhisperInstallerDialog(root, callback)
    root.mainloop()