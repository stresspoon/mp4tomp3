#!/usr/bin/env python3
"""
Test Whisper installer dialog
"""

import tkinter as tk
from whisper_installer_ui import WhisperInstallerDialog

def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    def callback(installed):
        print(f"Installation result: {installed}")
        root.quit()
    
    # Open the installer dialog
    dialog = WhisperInstallerDialog(root, callback)
    
    root.mainloop()

if __name__ == "__main__":
    main()