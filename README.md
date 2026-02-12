# Youtube_Mp3_Downloader_for_pc_ver_2

# 📖 Indonesia (Scroll for English Ver)

## 📜 Disclaimer : File ini tidak mengandung virus apapun, kalau windows mendeteksi sebagai virus cukup matikan antivirus atau pakai versi 'Portable'.

---

# 🎵 YouTube MP3 Downloader (GUI)

Simple desktop app untuk download dan convert video YouTube ke MP3 menggunakan Python + Tkinter + yt-dlp.

## ✨ Features

* GUI sederhana dan ringan
* Download audio kualitas terbaik
* Auto convert ke MP3, M4A. OPUS (192kbps)
* Bisa pilih folder download
* Tidak bikin UI freeze (pakai threading)

## 🎧 Supported Audio Formats & Quality

### 🔹 MP3

* Converted using FFmpeg
* Bitrate: **192 kbps**
* Compatible with almost all devices
* Recommended for general use

### 🔹 M4A

* Extracted from best available audio stream
* Original quality (no re-encode if possible)
* Smaller file size compared to MP3
* Recommended for Apple devices

### 🔹 OPUS

* Extracted from best available YouTube audio
* High efficiency compression
* Better quality at smaller file size
* Recommended for modern devices

---

```
Note:
Actual quality depends on the original audio quality uploaded to YouTube.
The app downloads the best available audio stream before conversion.
```

---

## ▶️ Cara run?

```bash
python main.py
```

atau

Cukup klik file .exe nya :)

---

## ▶️ Cara pakai?

### 1️⃣ Download Aplikasi

Download file:

[Quick_Audio - v2.rar](https://github.com/NabilRafa/Youtube-Music-Downloader-For-PC/releases/tag/v2.0)

### 2️⃣ Jalankan Aplikasi

Double click file `.exe`.

Jika muncul peringatan Windows:

* Klik **More Info**
* Klik **Run Anyway**

Atau matikan antivirus terlebih dulu

### 3️⃣ Download Audio

1. Paste link YouTube
2. Pilih lokasi download (opsional)
3. Klik **Download**
4. Tunggu sampai selesai

File MP3 akan otomatis tersimpan di folder pilihan Anda.

---

## 📁 Lokasi Default

Jika tidak diubah, file akan tersimpan di:

```
Downloads\YouTube_Audio
```
---


# 📖 English

## 📜 Disclaimer : This file does not contain any virus. If Windows detects it as a virus, simply disable your antivirus or use the 'Portable' version.

---

# 🎵 YouTube MP3 Downloader (GUI)

Simple desktop app to download and convert YouTube videos to MP3 using Python + Tkinter + yt-dlp.

## ✨ Features

* Simple and lightweight GUI
* Download best quality audio
* Auto convert to MP3, M4A, OPUS (192kbps)
* Choose download folder
* No UI freeze (using threading)

## 🎧 Supported Audio Formats & Quality

### 🔹 MP3

* Converted using FFmpeg
* Bitrate: **192 kbps**
* Compatible with almost all devices
* Recommended for general use

### 🔹 M4A

* Extracted from best available audio stream
* Original quality (no re-encode if possible)
* Smaller file size compared to MP3
* Recommended for Apple devices

### 🔹 OPUS

* Extracted from best available YouTube audio
* High efficiency compression
* Better quality at smaller file size
* Recommended for modern devices

---

```
Note:
Actual quality depends on the original audio quality uploaded to YouTube.
The app downloads the best available audio stream before conversion.
```

---

## ▶️ How to run?

```bash
python main.py
```

or

Just double click the `.exe` file :)

---

## ▶️ How to use?

### 1️⃣ Download the Application

Download the file:

https://github.com/NabilRafa/Youtube-Music-Downloader-For-PC/releases/tag/v2.0

### 2️⃣ Run the Application

Double click the `.exe` file.

If a Windows warning appears:

* Click **More Info**
* Click **Run Anyway**

Or temporarily disable your antivirus.

### 3️⃣ Download Audio

1. Paste the YouTube link
2. Choose download location (optional)
3. Click **Download**
4. Wait until it finishes

The MP3 file will automatically be saved to your selected folder.

---

## 📁 Default Location

If not changed, the file will be saved in:

```
Downloads\YouTube_Audio
```
---


## FOR DEVELOPMENT ONLY


---

## 🛠 Requirements

* Python 3.10+
* yt-dlp
* FFmpeg (WAJIB untuk convert ke MP3)

---

## 📦 Installation

### 1️⃣ Install dependency

```bash
pip install yt-dlp
```

### 2️⃣ Install FFmpeg

Download FFmpeg Windows build:
[https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

Tambahkan folder `bin` ke Environment Variables (PATH).

Cek instalasi:

```bash
ffmpeg -version
```

---

## 📁 Default Output Location

```
Downloads/YouTube_MP3
```

Bisa diganti langsung dari aplikasi.

---

## ⚠ Notes

* Pastikan koneksi internet stabil
* Jika error, update yt-dlp:

```bash
pip install -U yt-dlp
```
