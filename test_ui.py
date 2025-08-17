#!/usr/bin/env python3
"""
Test the custom UI components
"""

import tkinter as tk
from custom_widgets import RoundedButton, RoundedFrame

def test_button_clicked():
    print("Button clicked!")

def main():
    root = tk.Tk()
    root.title("UI Test")
    root.geometry("600x400")
    root.configure(bg='#f2f1ef')
    
    # Test rounded button
    btn1 = RoundedButton(
        root,
        width=150,
        height=50,
        corner_radius=15,
        text="설치 시작",
        bg_color="#ff3d00",
        fg_color="white",
        hover_color="#e63600",
        font=('SF Pro Display', 14, 'bold'),
        command=test_button_clicked
    )
    btn1.pack(pady=20)
    
    # Test disabled button
    btn2 = RoundedButton(
        root,
        width=150,
        height=50,
        corner_radius=15,
        text="비활성 버튼",
        bg_color="#666666",
        fg_color="white",
        hover_color="#555555",
        font=('SF Pro Display', 14),
        command=test_button_clicked,
        state='disabled'
    )
    btn2.pack(pady=10)
    
    # Test rounded frame
    frame = RoundedFrame(
        root,
        width=400,
        height=150,
        corner_radius=20,
        bg_color="#ffffff",
        border_color="#e0e0e0",
        border_width=2
    )
    frame.pack(pady=20)
    
    # Add content to rounded frame
    label = tk.Label(
        frame.content_frame,
        text="둥근 모서리 프레임 테스트",
        font=('SF Pro Display', 16),
        bg="#ffffff",
        fg="#131313"
    )
    label.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()