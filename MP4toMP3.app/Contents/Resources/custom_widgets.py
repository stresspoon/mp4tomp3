#!/usr/bin/env python3
"""
Custom widgets with rounded corners for modern UI
"""

import tkinter as tk
from tkinter import Canvas

class RoundedButton(tk.Canvas):
    """Custom button with rounded corners"""
    
    def __init__(self, parent, width=120, height=40, corner_radius=10, 
                 text="", bg_color="#ff3d00", fg_color="white", 
                 hover_color="#e63600", font=('SF Pro Display', 12, 'bold'),
                 command=None, state='normal', shadow=True, shadow_offset=3, shadow_color="#d9d9d9"):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bd=0)
        self.shadow = shadow
        self.shadow_offset = shadow_offset
        self.shadow_color = shadow_color
        
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.default_color = bg_color
        self.text = text
        self.font = font
        self.command = command
        self.state = state
        
        # Configure canvas background to match parent
        self.configure(bg=parent['bg'])
        
        # Draw the button
        self.draw_button()
        
        # Bind events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle"""
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.append(x)
            points.append(y)
        
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def draw_button(self):
        """Draw the button with current state"""
        self.delete("all")
        
        # Determine colors based on state
        if self.state == 'disabled':
            bg = '#cccccc'
            fg = '#999999'
        else:
            bg = self.bg_color
            fg = self.fg_color
        
        # Optional shadow
        if self.shadow:
            self.draw_rounded_rect(
                2 + self.shadow_offset, 2 + self.shadow_offset,
                self.width-2 + self.shadow_offset, self.height-2 + self.shadow_offset,
                self.corner_radius,
                fill=self.shadow_color,
                outline=""
            )
        # Draw rounded rectangle (button body)
        self.rect = self.draw_rounded_rect(
            2, 2, self.width-2, self.height-2,
            self.corner_radius,
            fill=bg,
            outline=""
        )
        
        # Draw text
        self.text_item = self.create_text(
            self.width/2, self.height/2,
            text=self.text,
            fill=fg,
            font=self.font
        )
    
    def on_click(self, event):
        """Handle click event"""
        if self.state == 'normal' and self.command:
            self.command()
    
    def on_enter(self, event):
        """Handle mouse enter"""
        if self.state == 'normal':
            self.bg_color = self.hover_color
            self.draw_button()
            self.configure(cursor='hand2')
    
    def on_leave(self, event):
        """Handle mouse leave"""
        if self.state == 'normal':
            self.bg_color = self.default_color
            self.draw_button()
            self.configure(cursor='')
    
    def config(self, **kwargs):
        """Configure button properties"""
        if 'state' in kwargs:
            self.state = kwargs['state']
            self.draw_button()
        if 'text' in kwargs:
            self.text = kwargs['text']
            self.draw_button()
        if 'bg' in kwargs:
            self.bg_color = kwargs['bg']
            self.default_color = kwargs['bg']
            self.draw_button()
        if 'command' in kwargs:
            self.command = kwargs['command']


class RoundedFrame(tk.Canvas):
    """Custom frame with rounded corners"""
    
    def __init__(self, parent, width=300, height=200, corner_radius=15,
                 bg_color="#ffffff", border_color="#e0e0e0", border_width=1):
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bd=0)
        
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        
        # Configure canvas
        self.configure(bg=parent['bg'])
        
        # Draw the frame
        self.draw_frame()
        
        # Create internal frame for content
        self.content_frame = tk.Frame(self, bg=bg_color)
        self.create_window(
            corner_radius, corner_radius,
            anchor='nw',
            window=self.content_frame,
            width=width - (corner_radius * 2),
            height=height - (corner_radius * 2)
        )
    
    def draw_frame(self):
        """Draw the rounded frame"""
        self.delete("border")
        
        # Draw border
        if self.border_width > 0:
            self.draw_rounded_rect(
                1, 1, self.width-1, self.height-1,
                self.corner_radius,
                fill=self.bg_color,
                outline=self.border_color,
                width=self.border_width,
                tags="border"
            )
        else:
            self.draw_rounded_rect(
                1, 1, self.width-1, self.height-1,
                self.corner_radius,
                fill=self.bg_color,
                outline="",
                tags="border"
            )
    
    def draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle"""
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.append(x)
            points.append(y)
        
        return self.create_polygon(points, smooth=True, **kwargs)