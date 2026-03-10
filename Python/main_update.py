"""
YouTube Audio & Video Downloader - Unified Version
Support Audio: M4A, OPUS (WebM), MP3
Support Video: MP4 (360p, 480p, 720p, 1080p)
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
    y = (screen_height // 2) - (height // 2) - 35
    root.geometry(f"{width}x{height}+{x}+{y}")

# CHANGED line 47: class name updated, title updated, window height increased
class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        # CHANGED line 50: title updated to reflect both audio & video
        self.root.title("YouTube Downloader - v4.0")
        center_window(self.root, 620, 550)
        self.root.resizable(True, True)

        self.download_path = str(Path.home() / "Downloads" / "YouTube_Audio")
        os.makedirs(self.download_path, exist_ok=True)

        self.video_duration = 0

        # CHANGED line 59: setup_ui replaced with setup_tabs
        self.setup_tabs()

    # ADDED: new method to create notebook/tab container
    def setup_tabs(self):
        # ADDED lines 63-72: header frame (same as original)
        header = tk.Frame(self.root, bg="#1a73e8", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🎵🎬 YouTube Downloader",
            font=("Arial", 18, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack(pady=15)

        # ADDED lines 75-80: notebook widget for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ADDED: Audio tab frame
        self.audio_frame = tk.Frame(self.notebook, padx=20, pady=20)
        self.notebook.add(self.audio_frame, text="🎵  Audio")

        # ADDED: Video tab frame
        self.video_frame = tk.Frame(self.notebook, padx=20, pady=20)
        self.notebook.add(self.video_frame, text="🎬  Video")

        # ADDED: Audio to Video converter tab frame
        self.audio_to_video_frame = tk.Frame(self.notebook, padx=20, pady=20)
        self.notebook.add(self.audio_to_video_frame, text="🔄  Audio → Video")

        # ADDED: call all panel setup methods
        self.setup_audio_ui()
        self.setup_video_ui()
        self.setup_audio_to_video_ui()

    # CHANGED line 61: method renamed from setup_ui to setup_audio_ui, parent changed from self.root to self.audio_frame
    def setup_audio_ui(self):
        main = self.audio_frame

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
            text="⬇ Download Audio",
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

    # ADDED lines below: entire video panel — new method
    def setup_video_ui(self):
        main = self.video_frame

        tk.Label(main, text="YouTube Link:", font=("Arial", 11)).pack(anchor=tk.W)

        self.video_link_entry = tk.Entry(main, font=("Arial", 11))
        self.video_link_entry.pack(fill=tk.X, pady=(5, 15))
        self.video_link_entry.bind("<Return>", lambda e: self.start_video_download())

        # ===== RESOLUTION OPTIONS =====
        tk.Label(main, text="Resolution:", font=("Arial", 11)).pack(anchor=tk.W)

        self.resolution_var = tk.StringVar(value="720")

        resolutions = [
            ("360p", "360"),
            ("480p", "480"),
            ("720p (HD)", "720"),
            ("1080p (Full HD)", "1080"),
        ]

        for text, value in resolutions:
            tk.Radiobutton(
                main,
                text=text,
                variable=self.resolution_var,
                value=value,
                font=("Arial", 10)
            ).pack(anchor=tk.W)

        # ===== VIDEO DOWNLOAD PATH =====
        tk.Label(main, text="Download Path:", font=("Arial", 11)).pack(anchor=tk.W, pady=(15, 0))

        video_path_frame = tk.Frame(main)
        video_path_frame.pack(fill=tk.X, pady=5)

        self.video_download_path = str(Path.home() / "Downloads" / "YouTube_Video")
        os.makedirs(self.video_download_path, exist_ok=True)

        self.video_path_entry = tk.Entry(video_path_frame, font=("Arial", 10))
        self.video_path_entry.insert(0, self.video_download_path)
        self.video_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            video_path_frame,
            text="Browse",
            command=self.browse_video_folder
        ).pack(side=tk.LEFT, padx=5)

        # ===== VIDEO DOWNLOAD BUTTON =====
        self.video_download_btn = tk.Button(
            main,
            text="⬇ Download Video",
            command=self.start_video_download,
            bg="#e8341a",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2
        )
        self.video_download_btn.pack(fill=tk.X, pady=15)

        self.video_progress = ttk.Progressbar(main, mode='determinate', maximum=100)
        self.video_progress.pack(fill=tk.X)

        self.video_status_label = tk.Label(
            main,
            text="Insert Link and Choose Resolution.",
            font=("Arial", 10),
            fg="#5f6368",
            wraplength=550,
            justify=tk.LEFT
        )
        self.video_status_label.pack(anchor=tk.W, pady=10)

    # ===== AUDIO METHODS (unchanged from original) =====

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

    # ===== VIDEO METHODS (all new) =====

    def browse_video_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.video_download_path = folder
            self.video_path_entry.delete(0, tk.END)
            self.video_path_entry.insert(0, folder)

    def start_video_download(self):
        url = self.video_link_entry.get().strip()

        if not url:
            messagebox.showwarning("Warning", "Insert YouTube Link!")
            return

        self.video_download_path = self.video_path_entry.get()

        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()

    def video_progress_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').strip()
            try:
                percent_value = float(percent_str.replace('%', ''))
                self.root.after(0, lambda v=percent_value: self.video_progress.config(value=v))
            except:
                pass
            self.root.after(0, lambda s=percent_str: self.video_status_label.config(
                text=f"Downloading... {s}", fg="#e8341a"
            ))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.video_progress.config(value=100))
            self.root.after(0, lambda: self.video_status_label.config(
                text="Processing / Merging...", fg="#e8341a"
            ))

    def download_video(self, url):
        self.root.after(0, lambda: self.video_download_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.video_progress.config(value=0))
        self.root.after(0, lambda: self.video_status_label.config(
            text="Gathering information...", fg="#5f6368"
        ))

        try:
            resolution = self.resolution_var.get()
            ffmpeg_path = get_ffmpeg_path()

            if not ffmpeg_path:
                messagebox.showerror(
                    "FFmpeg Cannot Be Found",
                    "Video download needs ffmpeg.exe in the application folder.\n"
                    "Video (best quality) + Audio are merged using FFmpeg."
                )
                return

            # Format: best video at chosen resolution + best audio, merged to mp4
            fmt = (
                f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height<={resolution}]+bestaudio/"
                f"best[height<={resolution}]/best"
            )

            ydl_opts = {
                'format': fmt,
                'outtmpl': os.path.join(self.video_download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.video_progress_hook],
                'quiet': False,
                'no_warnings': False,
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'ffmpeg_location': os.path.dirname(ffmpeg_path),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')

                self.root.after(0, lambda t=title: self.video_status_label.config(
                    text=f"Downloading: {t}", fg="#e8341a"
                ))

                ydl.download([url])

            self.root.after(0, lambda: self.video_status_label.config(
                text="Finish!", fg="green"
            ))
            self.root.after(0, lambda: self.video_progress.config(value=100))
            messagebox.showinfo("Success", f"Video Downloaded:\n{title}")

        except Exception as e:
            self.root.after(0, lambda: self.video_status_label.config(
                text=f"Error: {str(e)}", fg="red"
            ))
            messagebox.showerror("Error", str(e))

        finally:
            self.root.after(0, lambda: self.video_download_btn.config(state=tk.NORMAL))


    # ===== AUDIO → VIDEO PANEL =====

    def setup_audio_to_video_ui(self):
        main = self.audio_to_video_frame

        # --- Audio File ---
        tk.Label(main, text="Audio File (MP3 / M4A / OPUS / WAV):", font=("Arial", 11)).pack(anchor=tk.W)

        audio_row = tk.Frame(main)
        audio_row.pack(fill=tk.X, pady=(5, 15))

        self.av_audio_entry = tk.Entry(audio_row, font=("Arial", 10))
        self.av_audio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            audio_row, text="Browse",
            command=self.av_browse_audio
        ).pack(side=tk.LEFT, padx=5)

        # --- Background choice ---
        tk.Label(main, text="Background:", font=("Arial", 11)).pack(anchor=tk.W)

        self.av_bg_var = tk.StringVar(value="color")

        tk.Radiobutton(
            main, text="Solid Color (black)", variable=self.av_bg_var,
            value="color", font=("Arial", 10),
            command=self._av_toggle_bg
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            main, text="Custom Image (JPG/PNG)", variable=self.av_bg_var,
            value="image", font=("Arial", 10),
            command=self._av_toggle_bg
        ).pack(anchor=tk.W)

        img_row = tk.Frame(main)
        img_row.pack(fill=tk.X, pady=(3, 10))

        self.av_img_entry = tk.Entry(img_row, font=("Arial", 10), state=tk.DISABLED)
        self.av_img_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.av_img_btn = tk.Button(
            img_row, text="Browse", state=tk.DISABLED,
            command=self.av_browse_image
        )
        self.av_img_btn.pack(side=tk.LEFT, padx=5)

        # --- Output Path ---
        tk.Label(main, text="Output Path:", font=("Arial", 11)).pack(anchor=tk.W, pady=(5, 0))

        out_row = tk.Frame(main)
        out_row.pack(fill=tk.X, pady=5)

        self.av_out_path = str(Path.home() / "Downloads" / "YouTube_Audio")
        self.av_out_entry = tk.Entry(out_row, font=("Arial", 10))
        self.av_out_entry.insert(0, self.av_out_path)
        self.av_out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            out_row, text="Browse",
            command=self.av_browse_out_folder
        ).pack(side=tk.LEFT, padx=5)

        # --- Convert Button ---
        self.av_convert_btn = tk.Button(
            main, text="🎬 Convert Audio → Video",
            command=self.av_start_convert,
            bg="#6a1ab3", fg="white",
            font=("Arial", 12, "bold"), height=2
        )
        self.av_convert_btn.pack(fill=tk.X, pady=12)

        self.av_progress = ttk.Progressbar(main, mode='determinate', maximum=100)
        self.av_progress.pack(fill=tk.X)

        self.av_status_label = tk.Label(
            main, text="Choose an audio file to convert.",
            font=("Arial", 10), fg="#5f6368",
            wraplength=550, justify=tk.LEFT
        )
        self.av_status_label.pack(anchor=tk.W, pady=8)

    def _av_toggle_bg(self):
        if self.av_bg_var.get() == "image":
            self.av_img_entry.config(state=tk.NORMAL)
            self.av_img_btn.config(state=tk.NORMAL)
        else:
            self.av_img_entry.config(state=tk.DISABLED)
            self.av_img_btn.config(state=tk.DISABLED)

    def av_browse_audio(self):
        f = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.m4a *.opus *.wav *.ogg *.flac"), ("All Files", "*.*")]
        )
        if f:
            self.av_audio_entry.delete(0, tk.END)
            self.av_audio_entry.insert(0, f)

    def av_browse_image(self):
        f = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png"), ("All Files", "*.*")]
        )
        if f:
            self.av_img_entry.delete(0, tk.END)
            self.av_img_entry.insert(0, f)

    def av_browse_out_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.av_out_path = folder
            self.av_out_entry.delete(0, tk.END)
            self.av_out_entry.insert(0, folder)

    def av_start_convert(self):
        audio_file = self.av_audio_entry.get().strip()
        if not audio_file or not os.path.exists(audio_file):
            messagebox.showwarning("Warning", "Please select a valid audio file!")
            return

        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            messagebox.showerror(
                "FFmpeg Not Found",
                "ffmpeg.exe is required for Audio → Video conversion.\n"
                "Place ffmpeg.exe in the application folder."
            )
            return

        bg_mode = self.av_bg_var.get()
        image_file = None
        if bg_mode == "image":
            image_file = self.av_img_entry.get().strip()
            if not image_file or not os.path.exists(image_file):
                messagebox.showwarning("Warning", "Please select a valid image file!")
                return

        out_folder = self.av_out_entry.get().strip() or self.av_out_path
        os.makedirs(out_folder, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = os.path.join(out_folder, base_name + ".mp4")

        thread = threading.Thread(
            target=self.av_convert,
            args=(audio_file, image_file, output_file, ffmpeg_path)
        )
        thread.daemon = True
        thread.start()

    def av_ffmpeg_progress_hook(self, line, duration):
        time_match = re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line)
        if time_match and duration > 0:
            current_time = self.parse_time_to_seconds(time_match.group(1))
            progress = min((current_time / duration) * 100, 100)
            self.root.after(0, lambda p=progress: self.av_progress.config(value=p))
            self.root.after(0, lambda p=progress: self.av_status_label.config(
                text=f"Converting... {p:.1f}%", fg="#6a1ab3"
            ))

    def av_convert(self, audio_file, image_file, output_file, ffmpeg_path):
        self.root.after(0, lambda: self.av_convert_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.av_progress.config(value=0))
        self.root.after(0, lambda: self.av_status_label.config(
            text="Reading audio duration...", fg="#5f6368"
        ))

        try:
            # Get audio duration via ffprobe (ffmpeg can do it too)
            duration = 0
            probe_cmd = [
                ffmpeg_path, '-i', audio_file
            ]
            probe_proc = subprocess.run(
                probe_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            dur_match = re.search(r'Duration:\s*(\d{2}:\d{2}:\d{2}\.\d{2})', probe_proc.stdout)
            if dur_match:
                duration = self.parse_time_to_seconds(dur_match.group(1))

            self.root.after(0, lambda: self.av_status_label.config(
                text="Converting...", fg="#6a1ab3"
            ))

            if image_file:
                # Use provided image as static background
                cmd = [
                    ffmpeg_path,
                    '-loop', '1',
                    '-i', image_file,
                    '-i', audio_file,
                    '-c:v', 'libx264',
                    '-tune', 'stillimage',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    '-shortest',
                    '-y',
                    output_file
                ]
            else:
                # Black background 1280x720
                cmd = [
                    ffmpeg_path,
                    '-f', 'lavfi',
                    '-i', 'color=c=black:s=1280x720:r=1',
                    '-i', audio_file,
                    '-c:v', 'libx264',
                    '-tune', 'stillimage',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    '-shortest',
                    '-y',
                    output_file
                ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            for line in process.stdout:
                self.av_ffmpeg_progress_hook(line, duration)

            process.wait()

            if process.returncode == 0 and os.path.exists(output_file):
                self.root.after(0, lambda: self.av_progress.config(value=100))
                self.root.after(0, lambda: self.av_status_label.config(
                    text="Finish!", fg="green"
                ))
                messagebox.showinfo("Success", f"Video saved:\n{output_file}")
            else:
                raise Exception("FFmpeg conversion failed. Check if the audio format is supported.")

        except Exception as e:
            self.root.after(0, lambda: self.av_status_label.config(
                text=f"Error: {str(e)}", fg="red"
            ))
            messagebox.showerror("Error", str(e))

        finally:
            self.root.after(0, lambda: self.av_convert_btn.config(state=tk.NORMAL))


# CHANGED line 359: class name updated
def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()