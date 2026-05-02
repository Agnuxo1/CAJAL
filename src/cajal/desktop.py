#!/usr/bin/env python3
"""
CAJAL Desktop — Cross-platform system tray application
Provides quick access to CAJAL-4B AI assistant

Usage:
    python -m cajal.desktop
    cajal-desktop

Requirements:
    pip install pystray pillow requests
"""

import io
import json
import os
import sys
import threading
import webbrowser

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pathlib import Path

import requests

from cajal.config import get_config

CAJAL_VERSION = "1.0.0"
ICON_SVG = b"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<rect width="100" height="100" rx="15" fill="#0d2137"/>
<circle cx="50" cy="35" r="20" fill="none" stroke="#1e3a5f" stroke-width="3"/>
<circle cx="50" cy="35" r="8" fill="#f4a261"/>
<line x1="50" y1="55" x2="50" y2="85" stroke="#f4a261" stroke-width="3"/>
<line x1="50" y1="65" x2="30" y2="75" stroke="#f4a261" stroke-width="2"/>
<line x1="50" y1="65" x2="70" y2="75" stroke="#f4a261" stroke-width="2"/>
<line x1="50" y1="75" x2="35" y2="90" stroke="#f4a261" stroke-width="2"/>
<line x1="50" y1="75" x2="65" y2="90" stroke="#f4a261" stroke-width="2"/>
</svg>"""

def create_icon_image():
    """Create icon from SVG or fallback to a simple PIL image."""
    try:
        from PIL import Image, ImageDraw
        # Try to use cairosvg if available
        try:
            import cairosvg
            png = cairosvg.svg2png(bytestring=ICON_SVG, output_width=64, output_height=64)
            from PIL import Image
            return Image.open(io.BytesIO(png))
        except ImportError:
            pass
        
        # Fallback: draw a simple icon
        img = Image.new('RGBA', (64, 64), (13, 33, 55, 255))
        draw = ImageDraw.Draw(img)
        # Circle head
        draw.ellipse([22, 8, 42, 28], outline=(30, 58, 95, 255), width=2)
        draw.ellipse([28, 14, 36, 22], fill=(244, 162, 97, 255))
        # Body lines
        draw.line([(32, 28), (32, 52)], fill=(244, 162, 97, 255), width=2)
        draw.line([(32, 36), (18, 44)], fill=(244, 162, 97, 255), width=2)
        draw.line([(32, 36), (46, 44)], fill=(244, 162, 97, 255), width=2)
        draw.line([(32, 44), (20, 56)], fill=(244, 162, 97, 255), width=2)
        draw.line([(32, 44), (44, 56)], fill=(244, 162, 97, 255), width=2)
        return img
    except ImportError:
        return None

def check_ollama():
    cfg = get_config()
    try:
        r = requests.get(f"{cfg.get('ollama_host', 'http://localhost:11434')}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

def open_chat_window():
    """Open a simple chat window."""
    try:
        import tkinter as tk
        from tkinter import scrolledtext, ttk
    except ImportError:
        print("GUI not available. Use 'cajal chat' in terminal.")
        return
    
    cfg = get_config()
    host = cfg.get('ollama_host', 'http://localhost:11434')
    model = cfg.get('model', 'cajal-4b')
    
    root = tk.Tk()
    root.title("CAJAL Chat")
    root.geometry("600x500")
    root.configure(bg='#0d1117')
    
    # Header
    header = tk.Frame(root, bg='#1e3a5f', height=50)
    header.pack(fill='x')
    header_label = tk.Label(header, text="🧠 CAJAL — P2PCLAW AI", 
                           bg='#1e3a5f', fg='#f4a261', font=('Segoe UI', 14, 'bold'))
    header_label.pack(pady=10)
    
    # Chat area
    chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg='#0d1117', 
                                          fg='#c9d1d9', font=('Consolas', 11),
                                          insertbackground='#c9d1d9')
    chat_area.pack(padx=10, pady=10, fill='both', expand=True)
    chat_area.config(state='disabled')
    
    messages = []
    
    def add_message(role, text):
        chat_area.config(state='normal')
        tag = 'user' if role == 'user' else 'assistant'
        chat_area.insert('end', f"\n{'You' if role == 'user' else 'CAJAL'}:\n", tag)
        chat_area.insert('end', f"{text}\n", 'text')
        chat_area.config(state='disabled')
        chat_area.see('end')
    
    chat_area.tag_config('user', foreground='#58a6ff', font=('Segoe UI', 10, 'bold'))
    chat_area.tag_config('assistant', foreground='#f4a261', font=('Segoe UI', 10, 'bold'))
    chat_area.tag_config('text', foreground='#c9d1d9')
    
    # Input area
    input_frame = tk.Frame(root, bg='#0d1117')
    input_frame.pack(fill='x', padx=10, pady=10)
    
    input_box = tk.Entry(input_frame, bg='#161b22', fg='#c9d1d9', 
                        insertbackground='#c9d1d9', font=('Consolas', 11),
                        relief='flat', highlightthickness=1, 
                        highlightcolor='#f4a261', highlightbackground='#30363d')
    input_box.pack(side='left', fill='x', expand=True, ipady=8)
    
    def send_message():
        text = input_box.get().strip()
        if not text:
            return
        input_box.delete(0, 'end')
        add_message('user', text)
        messages.append({'role': 'user', 'content': text})
        
        # Async response
        def get_response():
            try:
                system_prompt = """You are CAJAL, a distinguished scientist at the P2PCLAW laboratory. Be concise and helpful."""
                response = requests.post(
                    f'{host}/api/chat',
                    json={
                        'model': model,
                        'messages': [
                            {'role': 'system', 'content': system_prompt},
                            *messages[-6:]
                        ],
                        'stream': False,
                        'options': {'temperature': 0.7, 'num_ctx': 4096}
                    },
                    timeout=300
                )
                data = response.json()
                reply = data['message']['content']
                root.after(0, lambda: add_message('assistant', reply))
                messages.append({'role': 'assistant', 'content': reply})
            except Exception as e:
                root.after(0, lambda: add_message('assistant', f'Error: {str(e)}'))
        
        threading.Thread(target=get_response, daemon=True).start()
    
    send_btn = tk.Button(input_frame, text='Send', bg='#f4a261', fg='#0d1117',
                        font=('Segoe UI', 10, 'bold'), relief='flat',
                        command=send_message, cursor='hand2')
    send_btn.pack(side='right', padx=(8, 0), ipadx=15, ipady=5)
    
    input_box.bind('<Return>', lambda e: send_message())
    
    # Welcome message
    add_message('assistant', 'Hello! I am CAJAL. How can I help you today?')
    
    input_box.focus()
    root.mainloop()

def main():
    try:
        import pystray
    except ImportError:
        print("pystray not installed. Install with: pip install pystray pillow")
        print("Falling back to direct chat window...")
        open_chat_window()
        return
    
    icon_image = create_icon_image()
    if not icon_image:
        print("Could not create icon. Please install Pillow: pip install pillow")
        return
    
    def on_chat(icon, item):
        threading.Thread(target=open_chat_window, daemon=True).start()
    
    def on_status(icon, item):
        if check_ollama():
            icon.notify("CAJAL is online! Ollama is running.", "CAJAL Status")
        else:
            icon.notify("CAJAL is offline. Start Ollama first.", "CAJAL Status")
    
    def on_settings(icon, item):
        config_path = Path.home() / ".cajal" / "config.json"
        if sys.platform == "win32":
            os.startfile(str(config_path))
        elif sys.platform == "darwin":
            os.system(f'open "{config_path}"')
        else:
            os.system(f'xdg-open "{config_path}"')
    
    def on_docs(icon, item):
        webbrowser.open("https://github.com/Agnuxo1/CAJAL")
    
    def on_p2pclaw(icon, item):
        webbrowser.open("https://p2pclaw.com/silicon")
    
    def on_exit(icon, item):
        icon.stop()
    
    menu = pystray.Menu(
        pystray.MenuItem("🧠 Open Chat", on_chat),
        pystray.MenuItem("📊 Check Status", on_status),
        pystray.MenuItem("⚙️ Settings", on_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("📚 Documentation", on_docs),
        pystray.MenuItem("🌐 P2PCLAW Platform", on_p2pclaw),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Exit", on_exit)
    )
    
    icon = pystray.Icon("cajal", icon_image, "CAJAL AI", menu)
    
    print("🧠 CAJAL Desktop started")
    print("   Right-click the tray icon to interact")
    print("   Press Ctrl+C to exit\n")
    
    icon.run()

if __name__ == "__main__":
    main()
