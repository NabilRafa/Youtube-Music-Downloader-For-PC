"""
YouTube Audio Downloader - Unified Version
Support: M4A, OPUS (WebM), MP3
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import subprocess
import os
from pathlib import Path
import threading
import sys

try:
    import yt_dlp
except ImportError:
    print("yt-dlp not installed! pip install yt-dlp")
    exit()


# ===== OPTIONAL FFMPEG DETECTION =====
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.join(os.path.dirname(sys.executable), '_internal')

    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    ffmpeg_path = os.path.join(base_path, "ffmpeg.exe")
    return ffmpeg_path if os.path.exists(ffmpeg_path) else None

# ===== CENTER WINDOW =====
def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

#Title & Version
class YouTubeAudioDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Audio Downloader - v2.1")
        center_window(self.root, 600, 490)
        self.root.resizable(True, True)

        self.download_path = str(Path.home() / "Downloads" / "YouTube_Audio")
        os.makedirs(self.download_path, exist_ok=True)

        self.video_duration = 0

        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#1a73e8", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🎵 YouTube Audio Downloader",
            font=("Arial", 18, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack(pady=15)

        main = tk.Frame(self.root, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(main, text="YouTube Link:", font=("Arial", 11)).pack(anchor=tk.W)

        self.link_entry = tk.Entry(main, font=("Arial", 11))
        self.link_entry.pack(fill=tk.X, pady=(5, 15))
        self.link_entry.bind("<Return>", lambda e: self.start_download())

        # ===== FORMAT OPTIONS =====
        tk.Label(main, text="Format Audio:", font=("Arial", 11)).pack(anchor=tk.W)

        self.format_var = tk.StringVar(value="m4a")

        formats = [
            ("MP3 (Best Quality)", "mp3"),
            ("M4A (Best compatibility)", "m4a"),
            ("OPUS (Opus, big size)", "opus"),
        ]

        for text, value in formats:
            tk.Radiobutton(
                main,
                text=text,
                variable=self.format_var,
                value=value,
                font=("Arial", 10)
            ).pack(anchor=tk.W)

        # ===== LOCATION =====
        tk.Label(main, text="Download Path:", font=("Arial", 11)).pack(anchor=tk.W, pady=(15,0))

        path_frame = tk.Frame(main)
        path_frame.pack(fill=tk.X, pady=5)

        self.path_entry = tk.Entry(path_frame, font=("Arial", 10))
        self.path_entry.insert(0, self.download_path)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            path_frame,
            text="Browse",
            command=self.browse_folder
        ).pack(side=tk.LEFT, padx=5)

        # ===== DOWNLOAD BUTTON =====
        self.download_btn = tk.Button(
            main,
            text="⬇ Download",
            command=self.start_download,
            bg="#1a73e8",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2
        )
        self.download_btn.pack(fill=tk.X, pady=15)

        self.progress = ttk.Progressbar(main, mode='determinate', maximum=100)
        self.progress.pack(fill=tk.X)

        self.status_label = tk.Label(
            main,
            text="Insert Link and Choose Format.",
            font=("Arial", 10),
            fg="#5f6368",
            wraplength=550,
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W, pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path = folder
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def start_download(self):
        url = self.link_entry.get().strip()

        if not url:
            messagebox.showwarning("Warning", "Insert YouTube Link!")
            return

        self.download_path = self.path_entry.get()

        thread = threading.Thread(target=self.download_audio, args=(url,))
        thread.daemon = True
        thread.start()

    def parse_time_to_seconds(self, time_str):
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = parts
                total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                return total_seconds
            elif len(parts) == 2:
                minutes, seconds = parts
                total_seconds = int(minutes) * 60 + float(seconds)
                return total_seconds
            else:
                return float(time_str)
        except:
            return 0

    def ffmpeg_progress_hook(self, line, duration):
        time_match = re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line)
        if time_match and duration > 0:
            current_time = self.parse_time_to_seconds(time_match.group(1))
            progress = min((current_time / duration) * 100, 100)
            
            self.root.after(0, lambda: self.progress.config(value=progress))
            self.root.after(0, lambda: self.status_label.config(
                text=f"Converting... {progress:.1f}%",
                fg="#1a73e8"
            ))

    def manual_convert(self, input_file, output_format, ffmpeg_path):
        output_file = os.path.splitext(input_file)[0] + f'.{output_format}'
        
        if output_format == "mp3":
            cmd = [
                ffmpeg_path,
                '-i', input_file,
                '-vn',
                '-ar', '44100',
                '-ac', '2',
                '-b:a', '192k',
                '-y',
                output_file
            ]
        elif output_format == "opus":
            cmd = [
                ffmpeg_path,
                '-i', input_file,
                '-vn',
                '-c:a', 'libopus',
                '-b:a', '192k',
                '-y',
                output_file
            ]
        
        self.root.after(0, lambda: self.status_label.config(text="Converting...", fg="#1a73e8"))
        self.root.after(0, lambda: self.progress.config(value=0))
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            for line in process.stdout:
                if self.video_duration > 0:
                    self.ffmpeg_progress_hook(line, self.video_duration)
            
            process.wait()
            
            if process.returncode == 0 and os.path.exists(output_file):
                try:
                    os.remove(input_file)
                except:
                    pass
                
                self.root.after(0, lambda: self.status_label.config(text="Selesai!", fg="green"))
                self.root.after(0, lambda: self.progress.config(value=100))
            else:
                raise Exception("FFmpeg conversion failed")
                
        except Exception as e:
            raise Exception(f"Conversion error: {str(e)}")

    def download_audio(self, url):
        self.download_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_label.config(text="Gathering information...")

        try:
            selected_format = self.format_var.get()

            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': False,
                'no_warnings': False,   
                'noplaylist': True,
            }

            # ===== FORMAT LOGIC =====

            if selected_format == "m4a":
                ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio'
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    self.video_duration = info.get('duration', 0)

                    self.status_label.config(text=f"Downloading: {title}")
                    ydl.download([url])

            elif selected_format == "opus":
                ffmpeg_path = get_ffmpeg_path()

                if not ffmpeg_path:
                    messagebox.showerror(
                        "FFmpeg Cannot Be Found",
                        "OPUS need ffmpeg.exe in application folder."
                    )
                    return

                ydl_opts['format'] = 'bestaudio/best'
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    self.video_duration = info.get('duration', 0)

                    self.status_label.config(text=f"Downloading: {title}")
                    
                    result = ydl.extract_info(url, download=True)
                    downloaded_file = ydl.prepare_filename(result)

                self.manual_convert(downloaded_file, selected_format, ffmpeg_path)

            elif selected_format == "mp3":
                ffmpeg_path = get_ffmpeg_path()

                if not ffmpeg_path:
                    messagebox.showerror(
                        "FFmpeg Cannot Be Found",
                        "MP3 need ffmpeg.exe in application folder."
                    )
                    return

                ydl_opts['format'] = 'bestaudio/best'
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    self.video_duration = info.get('duration', 0)

                    self.status_label.config(text=f"Downloading: {title}")
                    
                    result = ydl.extract_info(url, download=True)
                    downloaded_file = ydl.prepare_filename(result)

                self.manual_convert(downloaded_file, selected_format, ffmpeg_path)

            self.status_label.config(
                text="Finish!",
                fg="green"
            )

            messagebox.showinfo("Succes", f"Download Finished:\n{title}")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", str(e))

        finally:
            self.download_btn.config(state=tk.NORMAL)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').strip()
            try:
                percent_value = float(percent_str.replace('%', ''))
                self.progress['value'] = percent_value
            except:
                pass
            
            self.status_label.config(text=f"Downloading... {percent_str}", fg="#1a73e8")
        elif d['status'] == 'finished':
            self.progress['value'] = 100
            selected_format = self.format_var.get()
            if selected_format == "m4a":
                self.status_label.config(text="Finish!", fg="green")
            else:
                self.status_label.config(text="Processing...", fg="#1a73e8")


def main():
    root = tk.Tk()
    app = YouTubeAudioDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()