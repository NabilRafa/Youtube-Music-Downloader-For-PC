# Youtube_Mp3_Downloader_for_pc_ver_2

Gue bakal kasih lo README yang rapi, profesional, dan layak masuk GitHub.
Ada dua versi: 🇮🇩 Indonesia dan 🇬🇧 English.

---

# 🇮🇩 README – Versi Bahasa Indonesia

# 🎵 YouTube MP3 Downloader (GUI)

Aplikasi sederhana berbasis GUI untuk mengunduh video YouTube dan mengonversinya secara otomatis ke format MP3 (192 kbps).

---

## ✨ Fitur

* Download video YouTube dengan kualitas audio terbaik
* Otomatis convert ke MP3 (192 kbps)
* Tampilan GUI sederhana & mudah digunakan
* Bisa memilih lokasi penyimpanan file
* Progress indicator saat download
* Tidak membuat UI freeze (menggunakan threading)

---

## 📋 Persyaratan

### 1️⃣ Python 3.7 atau lebih baru

Download dari:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

Pastikan centang **“Add Python to PATH”** saat instalasi.

---

### 2️⃣ FFmpeg (Wajib untuk konversi MP3)

**Windows:**

1. Download dari [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract file ZIP
3. Tambahkan folder `bin` ke PATH

Cek instalasi dengan:

```
ffmpeg -version
```

---

### 3️⃣ Library Python

Install yt-dlp:

```
pip install yt-dlp
```

---

## 🚀 Cara Menjalankan

Jalankan file berikut:

```
python youtube_mp3_downloader_gui.py
```

Atau di Windows:

```
py youtube_mp3_downloader_gui.py
```

---

## 💻 Cara Menggunakan

1. Masukkan link YouTube ke kolom input
2. (Opsional) Pilih lokasi download dengan tombol **Browse**
3. Klik tombol **Download & Convert ke MP3**
4. Tunggu proses selesai
5. File MP3 akan tersimpan di folder yang dipilih

Secara default file disimpan di:

```
C:\Users\[Username]\Downloads\YouTube_MP3
```

---

## ⚠️ Troubleshooting

### ❌ yt-dlp belum terinstall

```
pip install yt-dlp
```

### ❌ FFmpeg tidak ditemukan

Pastikan sudah install dan ada di PATH.

### ❌ Python tidak dikenali

Gunakan:

```
py youtube_mp3_downloader_gui.py
```

---

## ⚖️ Legal Notice

Program ini ditujukan untuk penggunaan personal dan edukasi.
Pastikan Anda memiliki hak untuk mengunduh konten yang digunakan.
Jangan gunakan untuk melanggar hak cipta.

---

## 🔧 Technical Details

* Language: Python 3
* GUI: Tkinter
* Downloader Engine: yt-dlp
* Converter: FFmpeg
* Output Format: MP3 (192 kbps)

---

---

# 🇬🇧 README – English Version

# 🎵 YouTube MP3 Downloader (GUI)

A simple GUI-based application to download YouTube videos and automatically convert them into MP3 format (192 kbps).

---

## ✨ Features

* Download YouTube videos with best available audio quality
* Automatic MP3 conversion (192 kbps)
* Simple and user-friendly GUI
* Custom download location selection
* Download progress indicator
* Non-blocking UI (uses threading)

---

## 📋 Requirements

### 1️⃣ Python 3.7 or newer

Download from:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

Make sure to check **“Add Python to PATH”** during installation.

---

### 2️⃣ FFmpeg (Required for MP3 conversion)

**Windows:**

1. Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the ZIP file
3. Add the `bin` folder to PATH

Verify installation:

```
ffmpeg -version
```

---

### 3️⃣ Python Library

Install yt-dlp:

```
pip install yt-dlp
```

---

## 🚀 How to Run

Run:

```
python youtube_mp3_downloader_gui.py
```

On Windows you can also use:

```
py youtube_mp3_downloader_gui.py
```

---

## 💻 How to Use

1. Paste a valid YouTube link into the input field
2. (Optional) Choose a download location using the **Browse** button
3. Click **Download & Convert to MP3**
4. Wait for the process to complete
5. The MP3 file will be saved in the selected folder

Default save location:

```
C:\Users\[Username]\Downloads\YouTube_MP3
```

---

## ⚠️ Troubleshooting

### ❌ yt-dlp not installed

```
pip install yt-dlp
```

### ❌ FFmpeg not found

Make sure FFmpeg is installed and added to PATH.

### ❌ Python not recognized

Try:

```
py youtube_mp3_downloader_gui.py
```

---

## ⚖️ Legal Notice

This program is intended for personal and educational use only.
Ensure you have the rights to download the content you use.
Do not use this software for copyright infringement.

---

## 🔧 Technical Details

* Language: Python 3
* GUI Framework: Tkinter
* Downloader Engine: yt-dlp
* Audio Converter: FFmpeg
* Output Format: MP3 (192 kbps)

---

Contact Me : 
Email : nabilr.athy@gmail.com
IG : @nabilr.a95
