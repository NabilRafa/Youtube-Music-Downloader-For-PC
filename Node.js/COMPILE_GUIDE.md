# Cara Compile — YT Downloader v5.0

---

## ══ PYTHON VERSION ══

### Dependencies
```bash
pip install yt-dlp
```

### Jalankan langsung
```bash
python main.py
```

### Compile ke .exe (Windows) — pakai PyInstaller
```bash
pip install pyinstaller

# Satu file .exe
pyinstaller --onefile --windowed --name "YTDownloader" main.py

# ATAU: satu folder (load lebih cepat)
pyinstaller --onedir --windowed --name "YTDownloader" main.py
```

Output ada di folder `dist/`.

### Masukkan ffmpeg.exe
Setelah compile, taruh `ffmpeg.exe` di:
- Mode `--onefile` → folder yang sama dengan `YTDownloader.exe`
- Mode `--onedir`  → dalam folder `YTDownloader/_internal/ffmpeg.exe`

**Download ffmpeg:** https://www.gyan.dev/ffmpeg/builds/ → ambil `ffmpeg-release-essentials.zip`

### Kalau mau ikon custom
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name "YTDownloader" main.py
```

### Catatan cross-platform
- Windows: compile di Windows → hasilnya `.exe`
- macOS/Linux: compile di OS masing-masing, hasilnya binary native
- Untuk macOS: ganti `ffmpeg.exe` → `ffmpeg` (tanpa ekstensi), taruh di folder yang sama

---

## ══ NODE.JS / ELECTRON VERSION ══

### Prerequisites
Install dulu:
1. **Node.js** (v18+): https://nodejs.org
2. **yt-dlp** harus ada di PATH sistem: https://github.com/yt-dlp/yt-dlp/releases
   - Windows: download `yt-dlp.exe`, taruh di folder yang ada di PATH (misal `C:\Windows\System32\`)
   - atau taruh di `bin/yt-dlp.exe` lalu ubah `exec('yt-dlp ...')` di main.js jadi path absolut

### Struktur folder
```
ytdl_node/
├── main.js
├── preload.js
├── index.html
├── package.json
└── bin/
    └── ffmpeg.exe     ← taruh di sini
```

### Install & jalankan
```bash
cd ytdl_node
npm install
npm start
```

### Compile ke installer (.exe Windows)
```bash
npm run build
```
Output: `dist/YT Downloader Setup x.x.x.exe`

### Compile ke macOS (.dmg)
```bash
npm run build:mac
```

### Compile ke Linux (.AppImage)
```bash
npm run build:linux
```

### Catatan penting Electron
- `bin/ffmpeg.exe` otomatis ikut di-bundle karena di-define di `extraResources`
- `yt-dlp` **tidak** di-bundle — harus sudah terinstall di sistem user
- Kalau mau bundle yt-dlp juga, taruh `yt-dlp.exe` di `bin/` dan update `exec()` di `main.js` jadi:
  ```js
  const ytdlpPath = app.isPackaged
    ? path.join(process.resourcesPath, 'bin', 'yt-dlp.exe')
    : path.join(__dirname, 'bin', 'yt-dlp.exe')
  exec(`"${ytdlpPath}" --dump-json ...`)
  ```

---

## ══ PERBANDINGAN ══

| | Python (tkinter) | Node.js (Electron) |
|---|---|---|
| Ukuran bundle | ~15–30 MB | ~120–180 MB |
| UI quality | Terbatas tkinter | Full HTML/CSS/JS |
| Startup speed | Cepat | Lebih lambat (~2s) |
| Cross-platform | ✅ | ✅ |
| Distribusi | `.exe` satu file | `.exe` installer |
| Dependencies | Python + yt-dlp | Node + yt-dlp |

---

## ══ FFMPEG ══

Kedua versi butuh `ffmpeg` untuk:
- Convert ke MP3 / OPUS
- Merge video+audio (1080p/720p)
- Audio → Video conversion

**Download:** https://www.gyan.dev/ffmpeg/builds/
Ambil file `ffmpeg-release-essentials.zip`, extract, ambil `ffmpeg.exe` dari folder `bin/`.
