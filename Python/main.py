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
        self._scroll_canvases = []  # populated by _make_scrollable_panel

        # CHANGED line 59: setup_ui replaced with setup_tabs
        self.setup_tabs()

    def _on_tab_changed(self, event):
        """Bind mousewheel to the scroll canvas of the currently visible tab."""
        self.root.unbind_all("<MouseWheel>")
        try:
            current = self.notebook.nametowidget(self.notebook.select())
        except Exception:
            return
        for sc in self._scroll_canvases:
            # Check if this canvas lives inside the active tab frame
            w = sc
            while w is not None:
                if w is current:
                    self.root.bind_all("<MouseWheel>", sc._wheel_handler)
                    return
                try:
                    w = w.master
                except Exception:
                    break

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
        self.video_link_entry.bind("<FocusOut>", lambda e: self.video_get_info())
        self.setup_audio_to_video_ui()

        # Route mousewheel to whichever tab is currently active
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.root.after(100, lambda: self._on_tab_changed(None))

    def _make_scrollable_panel(self, parent):
        """Return (scroll_canvas, inner_frame) with auto-width binding.
        Mousewheel is routed via NotebookTabChanged so only the active
        tab's canvas scrolls — avoids bind_all conflicts between panels.
        """
        sc = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=sc.yview)
        inner = tk.Frame(sc)

        def _on_frame(e):
            sc.configure(scrollregion=sc.bbox("all"))
        def _on_canvas(e):
            sc.itemconfig(win_id, width=e.width)
        def _on_wheel(e):
            sc.yview_scroll(int(-1 * (e.delta / 120)), "units")

        inner.bind("<Configure>", _on_frame)
        win_id = sc.create_window((0, 0), window=inner, anchor="nw")
        sc.bind("<Configure>", _on_canvas)
        sc.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        sc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Store the wheel handler on the canvas so the tab-switch
        # callback can look it up later.
        sc._wheel_handler = _on_wheel
        self._scroll_canvases.append(sc)
        return sc, inner

    # CHANGED line 61: method renamed from setup_ui to setup_audio_ui, parent changed from self.root to self.audio_frame
    def setup_audio_ui(self):
        _, inner = self._make_scrollable_panel(self.audio_frame)
        PAD = 20

        tk.Label(inner, text="YouTube Link:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD, pady=(15, 0))

        self.link_entry = tk.Entry(inner, font=("Arial", 11))
        self.link_entry.pack(fill=tk.X, padx=PAD, pady=(5, 15))
        self.link_entry.bind("<Return>", lambda e: self.start_download())

        # ===== FORMAT OPTIONS =====
        tk.Label(inner, text="Format Audio:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD)

        self.format_var = tk.StringVar(value="m4a")

        formats = [
            ("MP3 (Best Quality)", "mp3"),
            ("M4A (Best compatibility)", "m4a"),
            ("OPUS (Opus, big size)", "opus"),
        ]

        for text, value in formats:
            tk.Radiobutton(
                inner,
                text=text,
                variable=self.format_var,
                value=value,
                font=("Arial", 10)
            ).pack(anchor=tk.W, padx=PAD)

        # ===== LOCATION =====
        tk.Label(inner, text="Download Path:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD, pady=(15, 0))

        path_frame = tk.Frame(inner)
        path_frame.pack(fill=tk.X, padx=PAD, pady=5)

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
            inner,
            text="⬇ Download Audio",
            command=self.start_download,
            bg="#1a73e8",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2
        )
        self.download_btn.pack(fill=tk.X, padx=PAD, pady=15)

        self.progress = ttk.Progressbar(inner, mode="determinate", maximum=100)
        self.progress.pack(fill=tk.X, padx=PAD)

        self.status_label = tk.Label(
            inner,
            text="Insert Link and Choose Format.",
            font=("Arial", 10),
            fg="#5f6368",
            wraplength=520,
            justify=tk.CENTER
        )
        self.status_label.pack(pady=10, padx=PAD)

    # ADDED lines below: entire video panel — new method
    def setup_video_ui(self):
        _, inner = self._make_scrollable_panel(self.video_frame)
        PAD = 20  # uniform horizontal padding for content

        # ===== LINK + GET INFO =====
        tk.Label(inner, text="YouTube Link:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD, pady=(15, 0))

        link_row = tk.Frame(inner)
        link_row.pack(fill=tk.X, padx=PAD, pady=(5, 5))

        self.video_link_entry = tk.Entry(link_row, font=("Arial", 11))
        self.video_link_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.video_link_entry.bind("<Return>", lambda e: self.video_get_info())

        self.video_info_btn = tk.Button(
            link_row,
            text="🔍 Get Info",
            command=self.video_get_info,
            bg="#34a853", fg="white",
            font=("Arial", 10, "bold")
        )
        self.video_info_btn.pack(side=tk.LEFT, padx=(5, 0))

        # ===== DURATION DISPLAY =====
        self.video_duration_label = tk.Label(
            inner,
            text="Duration: --:--:--",
            font=("Arial", 10, "bold"),
            fg="#5f6368"
        )
        self.video_duration_label.pack(anchor=tk.W, padx=PAD, pady=(2, 10))

        # ===== TRIM SECTION =====
        trim_frame = tk.LabelFrame(
            inner, text="  ✂ Trim (optional)  ",
            font=("Arial", 10, "bold"), padx=10, pady=8
        )
        trim_frame.pack(fill=tk.X, padx=PAD, pady=(0, 10))

        self.video_trim_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            trim_frame,
            text="Enable trim / partial download",
            variable=self.video_trim_var,
            font=("Arial", 10),
            command=self._video_toggle_trim
        ).pack(anchor=tk.W)

        # --- Range slider canvas ---
        self._rs_canvas = tk.Canvas(
            trim_frame, height=36, bg="#ececec",
            highlightthickness=1, highlightbackground="#cccccc",
            cursor="arrow"
        )
        self._rs_canvas.pack(fill=tk.X, pady=(10, 4))

        # --- Time inputs: [HH:MM:SS] left, [HH:MM:SS] right ---
        time_row = tk.Frame(trim_frame)
        time_row.pack(fill=tk.X, pady=(0, 4))

        self.video_start_entry = tk.Entry(
            time_row, font=("Arial", 11), width=9,
            justify=tk.CENTER, relief=tk.SOLID, bd=1
        )
        self.video_start_entry.insert(0, "00:00:00")
        self.video_start_entry.pack(side=tk.LEFT)
        self.video_start_entry.bind("<FocusOut>", lambda e: self._rs_entry_changed("start"))
        self.video_start_entry.bind("<Return>",   lambda e: self._rs_entry_changed("start"))

        tk.Frame(time_row).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.video_end_entry = tk.Entry(
            time_row, font=("Arial", 11), width=9,
            justify=tk.CENTER, relief=tk.SOLID, bd=1
        )
        self.video_end_entry.insert(0, "00:00:00")
        self.video_end_entry.pack(side=tk.RIGHT)
        self.video_end_entry.bind("<FocusOut>", lambda e: self._rs_entry_changed("end"))
        self.video_end_entry.bind("<Return>",   lambda e: self._rs_entry_changed("end"))

        # Internal state
        self._rs_start_frac = 0.0
        self._rs_end_frac   = 1.0
        self._rs_dragging   = None
        self._rs_enabled    = False
        self._rs_handle_r   = 10
        self._rs_track_h    = 6
        self._rs_pad        = 14

        self._rs_canvas.bind("<Configure>",      lambda e: self._rs_redraw())
        self._rs_canvas.bind("<ButtonPress-1>",  self._rs_mouse_press)
        self._rs_canvas.bind("<B1-Motion>",      self._rs_mouse_drag)
        self._rs_canvas.bind("<ButtonRelease-1>",self._rs_mouse_release)

        self._video_trim_widgets = [
            self._rs_canvas,
            self.video_start_entry,
            self.video_end_entry,
        ]
        self._video_toggle_trim()

        # ===== VIDEO TITLE PREVIEW =====
        self.video_title_label = tk.Label(
            inner,
            text="Title: -",
            font=("Arial", 11, "bold"),
            fg="#202124",
            wraplength=520,
            justify=tk.LEFT
        )
        self.video_title_label.pack(anchor=tk.W, padx=PAD, pady=(5,10))

        # ===== RESOLUTION OPTIONS =====
        tk.Label(inner, text="Resolution:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD)

        self.resolution_var = tk.StringVar(value="720")

        resolutions = [
            ("360p", "360"),
            ("480p", "480"),
            ("720p (HD)", "720"),
            ("1080p (Full HD)", "1080"),
        ]

        res_inner = tk.Frame(inner)
        res_inner.pack(anchor=tk.W, padx=PAD)
        for text, value in resolutions:
            tk.Radiobutton(
                res_inner,
                text=text,
                variable=self.resolution_var,
                value=value,
                font=("Arial", 10)
            ).pack(anchor=tk.W)

        # ===== VIDEO DOWNLOAD PATH =====
        tk.Label(inner, text="Download Path:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD, pady=(15, 0))

        video_path_frame = tk.Frame(inner)
        video_path_frame.pack(fill=tk.X, padx=PAD, pady=5)

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
            inner,
            text="⬇ Download Video",
            command=self.start_video_download,
            bg="#e8341a",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2
        )
        self.video_download_btn.pack(fill=tk.X, padx=PAD, pady=15)

        self.video_progress = ttk.Progressbar(inner, mode="determinate", maximum=100)
        self.video_progress.pack(fill=tk.X, padx=PAD)

        self.video_status_label = tk.Label(
            inner,
            text="Paste a link and click 🔍 Get Info, or click ⬇ Download directly.",
            font=("Arial", 10),
            fg="#5f6368",
            wraplength=520,
            justify=tk.CENTER
        )
        self.video_status_label.pack(pady=10, padx=PAD)

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

    # ===== RANGE SLIDER HELPERS =====

    def _seconds_to_hms(self, secs):
        secs = int(secs)
        return secs // 3600, (secs % 3600) // 60, secs % 60

    def _hms_to_seconds(self, h, m, s):
        return int(h) * 3600 + int(m) * 60 + int(s)

    def _parse_hms_entry(self, text):
        """Parse HH:MM:SS string to seconds. Returns 0 on error."""
        try:
            parts = text.strip().split(":")
            if len(parts) == 3:
                return self._hms_to_seconds(parts[0], parts[1], parts[2])
            elif len(parts) == 2:
                return self._hms_to_seconds(0, parts[0], parts[1])
            else:
                return int(parts[0])
        except Exception:
            return 0

    def _secs_to_entry(self, secs):
        h, m, s = self._seconds_to_hms(secs)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _video_toggle_trim(self):
        enabled = self.video_trim_var.get()
        self._rs_enabled = enabled
        state = tk.NORMAL if enabled else tk.DISABLED
        for w in self._video_trim_widgets:
            try:
                w.config(state=state)
            except Exception:
                pass
        self._rs_redraw()

    # ---- Range slider drawing ----

    def _rs_track_range(self):
        """Return (x0, x1) of drawable track area."""
        w = self._rs_canvas.winfo_width()
        if w < 2:
            w = 400
        return self._rs_pad + self._rs_handle_r, w - self._rs_pad - self._rs_handle_r

    def _rs_frac_to_x(self, frac):
        x0, x1 = self._rs_track_range()
        return x0 + frac * (x1 - x0)

    def _rs_x_to_frac(self, x):
        x0, x1 = self._rs_track_range()
        span = x1 - x0
        if span <= 0:
            return 0.0
        return max(0.0, min(1.0, (x - x0) / span))

    def _rs_redraw(self):
        c = self._rs_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 2 or h < 2:
            return

        cy = h // 2
        r  = self._rs_handle_r
        th = self._rs_track_h
        enabled = self._rs_enabled

        # Full track (grey background)
        x0, x1 = self._rs_track_range()
        c.create_rectangle(
            x0, cy - th//2, x1, cy + th//2,
            fill="#d0d0d0", outline="#bbbbbb", width=1
        )

        # Active range (blue fill)
        sx = self._rs_frac_to_x(self._rs_start_frac)
        ex = self._rs_frac_to_x(self._rs_end_frac)
        active_color = "#1a73e8" if enabled else "#90aee8"
        c.create_rectangle(
            sx, cy - th//2, ex, cy + th//2,
            fill=active_color, outline="", width=0
        )

        # Handles
        handle_fill   = "#ffffff" if enabled else "#e8e8e8"
        handle_border = "#888888" if enabled else "#bbbbbb"
        for fx in [sx, ex]:
            c.create_oval(
                fx - r, cy - r, fx + r, cy + r,
                fill=handle_fill, outline=handle_border, width=2
            )

    def _rs_mouse_press(self, event):
        if not self._rs_enabled:
            return
        sx = self._rs_frac_to_x(self._rs_start_frac)
        ex = self._rs_frac_to_x(self._rs_end_frac)
        r  = self._rs_handle_r + 4   # hit area
        dist_s = abs(event.x - sx)
        dist_e = abs(event.x - ex)
        if dist_s <= r and dist_s <= dist_e:
            self._rs_dragging = "start"
        elif dist_e <= r:
            self._rs_dragging = "end"
        else:
            self._rs_dragging = None

    def _rs_mouse_drag(self, event):
        if not self._rs_enabled or self._rs_dragging is None:
            return
        frac = self._rs_x_to_frac(event.x)
        if self._rs_dragging == "start":
            self._rs_start_frac = min(frac, self._rs_end_frac - 0.001)
        else:
            self._rs_end_frac = max(frac, self._rs_start_frac + 0.001)
        self._rs_sync_entries()
        self._rs_redraw()

    def _rs_mouse_release(self, event):
        self._rs_dragging = None

    def _rs_sync_entries(self):
        """Slider moved → update text entries."""
        dur = getattr(self, "_video_total_duration", 0)
        start_s = int(self._rs_start_frac * dur)
        end_s   = int(self._rs_end_frac   * dur)
        self.video_start_entry.delete(0, tk.END)
        self.video_start_entry.insert(0, self._secs_to_entry(start_s))
        self.video_end_entry.delete(0, tk.END)
        self.video_end_entry.insert(0, self._secs_to_entry(end_s))

    def _rs_entry_changed(self, which):
        """Text entry changed → update slider fraction."""
        dur = getattr(self, "_video_total_duration", 0)
        if dur <= 0:
            return
        if which == "start":
            secs = self._parse_hms_entry(self.video_start_entry.get())
            secs = max(0, min(secs, int(self._rs_end_frac * dur) - 1))
            self._rs_start_frac = secs / dur
            self.video_start_entry.delete(0, tk.END)
            self.video_start_entry.insert(0, self._secs_to_entry(secs))
        else:
            secs = self._parse_hms_entry(self.video_end_entry.get())
            secs = max(int(self._rs_start_frac * dur) + 1, min(secs, dur))
            self._rs_end_frac = secs / dur
            self.video_end_entry.delete(0, tk.END)
            self.video_end_entry.insert(0, self._secs_to_entry(secs))
        self._rs_redraw()

    def _get_spinbox_seconds(self, which):
        """Used by download logic to read start/end seconds."""
        try:
            if which == "start":
                return self._parse_hms_entry(self.video_start_entry.get())
            else:
                return self._parse_hms_entry(self.video_end_entry.get())
        except Exception:
            return 0

    def _update_sliders_for_duration(self, duration):
        self._video_total_duration = duration
        h, m, s = self._seconds_to_hms(duration)
        self.video_duration_label.config(
            text=f"Duration: {h:02d}:{m:02d}:{s:02d}  ({duration}s)",
            fg="#1a73e8"
        )
        self._rs_start_frac = 0.0
        self._rs_end_frac   = 1.0
        self.video_start_entry.delete(0, tk.END)
        self.video_start_entry.insert(0, "00:00:00")
        self.video_end_entry.delete(0, tk.END)
        self.video_end_entry.insert(0, self._secs_to_entry(duration))
        self._rs_redraw()

    def video_get_info(self):
        url = self.video_link_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Insert YouTube Link first!")
            return
        self.video_info_btn.config(state=tk.DISABLED)
        self.video_status_label.config(text="Fetching info...", fg="#5f6368")

        def _fetch():
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                
                self.root.after(0, lambda: self.video_title_label.config(
                    text=f"Title: {title}_{self.resolution_var.get()}p.mp4"
))
                self.root.after(0, lambda: self._update_sliders_for_duration(int(duration)))
                self.root.after(0, lambda: self.video_status_label.config(
                    text=f"📹  {title}", fg="#202124"
                ))
            except Exception as e:
                self.root.after(0, lambda: self.video_status_label.config(
                    text=f"Error: {str(e)}", fg="red"
                ))
            finally:
                self.root.after(0, lambda: self.video_info_btn.config(state=tk.NORMAL))

        threading.Thread(target=_fetch, daemon=True).start()

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

        trim_start = None
        trim_end = None
        if self.video_trim_var.get():
            trim_start = self._get_spinbox_seconds("start")
            trim_end = self._get_spinbox_seconds("end")
            if trim_end <= trim_start:
                messagebox.showwarning("Warning", "End time must be greater than Start time!")
                return

        thread = threading.Thread(
            target=self.download_video,
            args=(url, trim_start, trim_end)
        )
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

    def download_video(self, url, trim_start=None, trim_end=None):
        self.root.after(0, lambda: self.video_download_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.video_progress.config(value=0))
        self.root.after(0, lambda: self.video_status_label.config(
            text="Gathering information...", fg="#5f6368"
        ))

        try:
            resolution = self.resolution_var.get()
            resolution = self.resolution_var.get()
            res_suffix = f"_{resolution}p"
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
                'outtmpl': os.path.join(self.video_download_path, f'%(title)s{res_suffix}.%(ext)s'),
                'progress_hooks': [self.video_progress_hook],
                'quiet': False,
                'no_warnings': False,
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'ffmpeg_location': os.path.dirname(ffmpeg_path),
            }

            # ===== TRIM / PARTIAL DOWNLOAD =====
            if trim_start is not None and trim_end is not None:
                def _fmt_sec(s):
                    h, m, sec = self._seconds_to_hms(s)
                    return f"{h:02d}:{m:02d}:{sec:02d}"

                section_str = f"*{_fmt_sec(trim_start)}-{_fmt_sec(trim_end)}"
                ydl_opts['download_ranges'] = yt_dlp.utils.download_range_func(
                    [], [[trim_start, trim_end]]
                )
                ydl_opts['force_keyframes_at_cuts'] = True

                start_lbl = _fmt_sec(trim_start)
                end_lbl   = _fmt_sec(trim_end)
                self.root.after(0, lambda: self.video_status_label.config(
                    text=f"Trim mode: {start_lbl} → {end_lbl}", fg="#e8341a"
                ))

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
        _, inner = self._make_scrollable_panel(self.audio_to_video_frame)
        PAD = 20

        # --- Audio File ---
        tk.Label(inner, text="Audio File (MP3 / M4A / OPUS / WAV):", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD, pady=(15, 0))

        audio_row = tk.Frame(inner)
        audio_row.pack(fill=tk.X, padx=PAD, pady=(5, 15))

        self.av_audio_entry = tk.Entry(audio_row, font=("Arial", 10))
        self.av_audio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            audio_row, text="Browse",
            command=self.av_browse_audio
        ).pack(side=tk.LEFT, padx=5)

        # --- Background choice ---
        tk.Label(inner, text="Background:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD)

        self.av_bg_var = tk.StringVar(value="color")

        tk.Radiobutton(
            inner, text="Solid Color (black)", variable=self.av_bg_var,
            value="color", font=("Arial", 10),
            command=self._av_toggle_bg
        ).pack(anchor=tk.W, padx=PAD)

        tk.Radiobutton(
            inner, text="Custom Image (JPG/PNG)", variable=self.av_bg_var,
            value="image", font=("Arial", 10),
            command=self._av_toggle_bg
        ).pack(anchor=tk.W, padx=PAD)

        img_row = tk.Frame(inner)
        img_row.pack(fill=tk.X, padx=PAD, pady=(3, 10))

        self.av_img_entry = tk.Entry(img_row, font=("Arial", 10), state=tk.DISABLED)
        self.av_img_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.av_img_btn = tk.Button(
            img_row, text="Browse", state=tk.DISABLED,
            command=self.av_browse_image
        )
        self.av_img_btn.pack(side=tk.LEFT, padx=5)

        # --- Video Quality ---
        tk.Label(inner, text="Video Quality:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD, pady=(10, 0))

        self.av_resolution_var = tk.StringVar(value="720")

        av_resolutions = [
            ("360p", "360"),
            ("480p", "480"),
            ("720p (HD)", "720"),
            ("1080p (Full HD)", "1080"),
        ]

        res_frame = tk.Frame(inner)
        res_frame.pack(anchor=tk.W, padx=PAD, pady=(3, 10))

        for text, value in av_resolutions:
            tk.Radiobutton(
                res_frame, text=text,
                variable=self.av_resolution_var,
                value=value, font=("Arial", 10)
            ).pack(side=tk.LEFT, padx=(0, 10))

        # --- Output Path ---
        tk.Label(inner, text="Output Path:", font=("Arial", 11)).pack(
            anchor=tk.W, padx=PAD, pady=(5, 0))

        out_row = tk.Frame(inner)
        out_row.pack(fill=tk.X, padx=PAD, pady=5)

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
            inner, text="🎬 Convert Audio → Video",
            command=self.av_start_convert,
            bg="#6a1ab3", fg="white",
            font=("Arial", 12, "bold"), height=2
        )
        self.av_convert_btn.pack(fill=tk.X, padx=PAD, pady=12)

        self.av_progress = ttk.Progressbar(inner, mode="determinate", maximum=100)
        self.av_progress.pack(fill=tk.X, padx=PAD)

        self.av_status_label = tk.Label(
            inner, text="Choose an audio file to convert.",
            font=("Arial", 10), fg="#5f6368",
            wraplength=520, justify=tk.CENTER
        )
        self.av_status_label.pack(pady=8, padx=PAD)

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

        resolution = self.av_resolution_var.get()
        resolution_map = {
            "360": "640x360",
            "480": "854x480",
            "720": "1280x720",
            "1080": "1920x1080",
        }
        quality = resolution_map.get(resolution, "1280x720")

        thread = threading.Thread(
            target=self.av_convert,
            args=(audio_file, image_file, output_file, ffmpeg_path, quality)
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

    def av_convert(self, audio_file, image_file, output_file, ffmpeg_path, resolution="720"):
        resolution_map = {
            "360":  ("640",  "360"),
            "480":  ("854",  "480"),
            "720":  ("1280", "720"),
            "1080": ("1920", "1080"),
        }
        vw, vh = resolution_map.get(str(resolution), ("1280", "720"))
        quality = f"{vw}x{vh}"
        fps = "30"
        scale_filter = f"scale={vw}:{vh}:force_original_aspect_ratio=decrease,pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"

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
                    '-vf', scale_filter,
                    '-r', fps,
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
                    '-i', f'color=c=black:s={quality}:r={fps}',
                    '-i', audio_file,
                    '-r', fps,
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