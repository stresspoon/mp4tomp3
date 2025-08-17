#!/usr/bin/env python3
"""
Whisper 설치 UI - 사용자 친화적 설치 경험 (Fixed version)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from whisper_manager import WhisperManager
from custom_widgets import RoundedButton

class WhisperInstallerDialog:
    """Whisper 설치 다이얼로그"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.manager = WhisperManager()
        
        # 다이얼로그 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Whisper STT 설정")
        self.dialog.geometry("500x650")
        self.dialog.resizable(False, False)
        
        # 색상 테마 (디자인 가이드 준수)
        self.colors = {
            'bg': '#f2f1ef',
            'card': '#ffffff',
            'accent': '#ff3d00',
            'text': '#131313',
            'text_secondary': '#666666',
            'border': '#e0e0e0',
            'success': '#10b981'
        }
        
        self.dialog.configure(bg=self.colors['bg'])
        self.setup_ui()
        self.center_window()
        
        # 모달 다이얼로그로 설정
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
    def center_window(self):
        """창 중앙 정렬"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"500x650+{x}+{y}")
    
    def setup_ui(self):
        """UI 구성"""
        # Main container with scrollbar
        main_frame = tk.Frame(self.dialog, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(
            title_frame,
            text="음성 인식 설정",
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
        models_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        models_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.selected_model = tk.StringVar(value='tiny')
        self.model_cards = []
        
        model_options = [
            {
                'name': 'tiny',
                'title': 'Tiny (최고속)',
                'desc': '가장 빠른 처리\n정확도: 낮음',
                'size': '39MB',
                'color': '#666666'
            },
            {
                'name': 'base',
                'title': 'Base (빠름)',
                'desc': '빠른 처리\n정확도: 보통',
                'size': '74MB',
                'color': '#666666'
            },
            {
                'name': 'small',
                'title': 'Small (추천)',
                'desc': '균형잡힌 성능\n정확도: 좋음',
                'size': '244MB',
                'color': '#ff3d00'
            },
            {
                'name': 'medium',
                'title': 'Medium (정확)',
                'desc': '높은 정확도\n정확도: 우수',
                'size': '769MB',
                'color': '#666666'
            }
        ]
        
        for i, model in enumerate(model_options):
            card = self.create_model_card(models_frame, model, i)
            self.model_cards.append(card)
        
        # 설치 옵션
        options_frame = tk.Frame(main_frame, bg=self.colors['card'], relief=tk.FLAT, bd=1)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.auto_install = tk.BooleanVar(value=True)
        check = tk.Checkbutton(
            options_frame,
            text="필요한 구성 요소 자동 설치",
            variable=self.auto_install,
            font=('SF Pro Display', 11),
            bg=self.colors['card'],
            fg=self.colors['text'],
            selectcolor=self.colors['card'],
            activebackground=self.colors['card']
        )
        check.pack(padx=10, pady=10)
        
        # 공간 정보
        info_frame = tk.Frame(main_frame, bg=self.colors['bg'])
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
        self.progress_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=('SF Pro Display', 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        self.progress_label.pack(pady=5)
        
        # 진행률 바 스타일 설정
        style = ttk.Style()
        style.configure('Custom.Horizontal.TProgressbar',
                       troughcolor=self.colors['border'],
                       background=self.colors['accent'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=460,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(pady=5)
        
        # 버튼 프레임 - 하단에 고정
        button_frame = tk.Frame(self.dialog, bg=self.colors['bg'])
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        # 버튼 컨테이너
        button_container = tk.Frame(button_frame, bg=self.colors['bg'])
        button_container.pack()
        
        # 설치 시작 버튼 - RoundedButton
        self.install_button = RoundedButton(
            button_container,
            width=180,
            height=48,
            corner_radius=14,
            text="설치 시작",
            bg_color=self.colors['accent'],
            fg_color='white',
            hover_color='#e63600',
            font=('SF Pro Display', 14, 'bold'),
            command=self.start_installation
        )
        self.install_button.grid(row=0, column=0, padx=10)
        
        # 나중에 버튼 - RoundedButton
        cancel_btn = RoundedButton(
            button_container,
            width=140,
            height=48,
            corner_radius=14,
            text="나중에",
            bg_color='#666666',
            fg_color='white',
            hover_color='#555555',
            font=('SF Pro Display', 14),
            command=self.dialog.destroy
        )
        cancel_btn.grid(row=0, column=1, padx=10)
        
        # STT 없이 사용 버튼 - RoundedButton
        skip_btn = RoundedButton(
            button_frame,
            width=160,
            height=40,
            corner_radius=10,
            text="STT 없이 사용",
            bg_color=self.colors['bg'],
            fg_color=self.colors['text_secondary'],
            hover_color='#e9e7e5',
            font=('SF Pro Display', 11),
            command=self.skip_stt
        )
        skip_btn.pack(pady=(10, 0))
    
    def create_model_card(self, parent, model, index):
        """모델 선택 카드 생성"""
        # 카드 프레임
        card = tk.Frame(
            parent,
            bg=self.colors['card'],
            highlightbackground=self.colors['border'],
            highlightthickness=1,
            bd=0,
            relief=tk.FLAT
        )
        card.pack(fill=tk.X, pady=5, padx=2)
        
        # 라디오 버튼
        radio = tk.Radiobutton(
            card,
            text='',
            variable=self.selected_model,
            value=model['name'],
            bg=self.colors['card'],
            command=lambda: self.on_model_selected(model['name'], card),
            activebackground=self.colors['card'],
            selectcolor=self.colors['card']
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
                text="[설치됨]",
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
            fg=model['color'] if model['name'] == 'small' else self.colors['text_secondary']
        )
        size_label.pack(side=tk.RIGHT, padx=15)
        
        # 호버 효과
        def on_enter(e):
            if self.selected_model.get() == model['name']:
                card.configure(highlightbackground=self.colors['accent'], highlightthickness=2)
            else:
                card.configure(highlightbackground='#999999', highlightthickness=1)
        
        def on_leave(e):
            if self.selected_model.get() == model['name']:
                card.configure(highlightbackground=self.colors['accent'], highlightthickness=2)
            else:
                card.configure(highlightbackground=self.colors['border'], highlightthickness=1)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # 클릭으로 선택
        def select_model(e):
            self.selected_model.set(model['name'])
            self.on_model_selected(model['name'], card)
        
        card.bind("<Button-1>", select_model)
        info_frame.bind("<Button-1>", select_model)
        for widget in info_frame.winfo_children():
            widget.bind("<Button-1>", select_model)
        
        # 초기 선택 상태
        if model['name'] == 'tiny':
            card.configure(highlightbackground=self.colors['accent'], highlightthickness=2)
        
        return card
    
    def on_model_selected(self, model_name, selected_card):
        """모델 선택 시 호출"""
        # 모든 카드 초기화
        for card in self.model_cards:
            card.configure(highlightbackground=self.colors['border'], highlightthickness=1)
        
        # 선택된 카드 강조
        selected_card.configure(highlightbackground=self.colors['accent'], highlightthickness=2)
        
        # 공간 정보 업데이트
        self.update_space_info()
    
    def update_space_info(self):
        """필요 공간 정보 업데이트"""
        model = self.selected_model.get()
        size_mb = self.manager.estimate_space_needed(model)
        
        if not self.manager.is_whisper_installed():
            self.space_label.config(
                text=f"필요한 디스크 공간: 약 {size_mb}MB (Whisper 엔진 포함)"
            )
        else:
            model_size = self.manager.MODEL_SIZES[model]['size']
            self.space_label.config(
                text=f"필요한 디스크 공간: 약 {model_size}MB"
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
                self.update_progress(0, f"{model.upper()} 모델 다운로드 중...")
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