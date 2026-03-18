const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron')
const { exec, spawn }  = require('child_process')
const path  = require('path')
const fs    = require('fs')
const os    = require('os')

let win

function createWindow() {
  win = new BrowserWindow({
    width: 680, height: 620,
    minWidth: 560, minHeight: 520,
    frame: false,
    backgroundColor: '#0d0d0d',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })
  win.loadFile('index.html')
}

app.whenReady().then(createWindow)
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit() })

// ─── FFmpeg path ────────────────────────────────────────────────
function ffmpegPath() {
  const base = app.isPackaged
    ? path.join(process.resourcesPath, 'bin')
    : path.join(__dirname, 'bin')
  const name = process.platform === 'win32' ? 'ffmpeg.exe' : 'ffmpeg'
  const p = path.join(base, name)
  return fs.existsSync(p) ? p : null
}

// ─── IPC: window controls ───────────────────────────────────────
ipcMain.on('win-minimize', () => win.minimize())
ipcMain.on('win-maximize', () => win.isMaximized() ? win.unmaximize() : win.maximize())
ipcMain.on('win-close',    () => win.close())

// ─── IPC: browse folder ─────────────────────────────────────────
ipcMain.handle('browse-folder', async (_, defaultPath) => {
  const r = await dialog.showOpenDialog(win, {
    properties: ['openDirectory'],
    defaultPath: defaultPath || os.homedir()
  })
  return r.canceled ? null : r.filePaths[0]
})

// ─── IPC: browse file ───────────────────────────────────────────
ipcMain.handle('browse-file', async (_, filters) => {
  const r = await dialog.showOpenDialog(win, {
    properties: ['openFile'],
    filters: filters
  })
  return r.canceled ? null : r.filePaths[0]
})

// ─── IPC: open folder in explorer ───────────────────────────────
ipcMain.on('open-folder', (_, p) => shell.openPath(p))

// ─── IPC: get info ──────────────────────────────────────────────
ipcMain.handle('get-info', async (_, url) => {
  return new Promise((resolve, reject) => {
    exec(`yt-dlp --dump-json --no-playlist "${url}"`, { maxBuffer: 10*1024*1024 }, (err, stdout) => {
      if (err) return reject(err.message)
      try {
        const info = JSON.parse(stdout)
        resolve({ title: info.title, duration: info.duration })
      } catch(e) { reject('Failed to parse video info') }
    })
  })
})

// ─── IPC: download audio ────────────────────────────────────────
ipcMain.handle('download-audio', async (event, { url, format, savePath }) => {
  return new Promise((resolve, reject) => {
    const ff = ffmpegPath()
    let args = ['--no-playlist', '-o', path.join(savePath, '%(title)s.%(ext)s')]

    if (format === 'm4a') {
      args.push('-f', 'bestaudio[ext=m4a]/bestaudio')
    } else {
      if (!ff) return reject('ffmpeg not found in bin/ folder')
      args.push('-f', 'bestaudio/best', '--ffmpeg-location', path.dirname(ff))
      if (format === 'mp3')  args.push('-x', '--audio-format', 'mp3', '--audio-quality', '192K')
      if (format === 'opus') args.push('-x', '--audio-format', 'opus')
    }
    args.push(url)

    const proc = spawn('yt-dlp', args)
    proc.stdout.on('data', d => {
      const line = d.toString()
      const m = line.match(/(\d+\.?\d*)%/)
      if (m) event.sender.send('progress', { type: 'audio', value: parseFloat(m[1]) })
      event.sender.send('log', { type: 'audio', text: line.trim() })
    })
    proc.stderr.on('data', d => event.sender.send('log', { type: 'audio', text: d.toString().trim() }))
    proc.on('close', code => code === 0 ? resolve('done') : reject(`yt-dlp exited with code ${code}`))
  })
})

// ─── IPC: download video ────────────────────────────────────────
ipcMain.handle('download-video', async (event, { url, resolution, savePath, trimStart, trimEnd }) => {
  return new Promise((resolve, reject) => {
    const ff = ffmpegPath()
    if (!ff) return reject('ffmpeg not found in bin/ folder')

    const fmt = `bestvideo[height<=${resolution}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=${resolution}]+bestaudio/best`
    let args = [
      '--no-playlist',
      '-f', fmt,
      '--merge-output-format', 'mp4',
      '--ffmpeg-location', path.dirname(ff),
      '-o', path.join(savePath, `%(title)s_${resolution}p.%(ext)s`),
    ]

    if (trimStart !== null && trimEnd !== null) {
      args.push('--download-sections', `*${trimStart}-${trimEnd}`, '--force-keyframes-at-cuts')
    }
    args.push(url)

    const proc = spawn('yt-dlp', args)
    proc.stdout.on('data', d => {
      const line = d.toString()
      const m = line.match(/(\d+\.?\d*)%/)
      if (m) event.sender.send('progress', { type: 'video', value: parseFloat(m[1]) })
      event.sender.send('log', { type: 'video', text: line.trim() })
    })
    proc.stderr.on('data', d => event.sender.send('log', { type: 'video', text: d.toString().trim() }))
    proc.on('close', code => code === 0 ? resolve('done') : reject(`yt-dlp exited with code ${code}`))
  })
})

// ─── IPC: audio → video ─────────────────────────────────────────
ipcMain.handle('av-convert', async (event, { audioFile, imageFile, outputFile, resolution }) => {
  return new Promise((resolve, reject) => {
    const ff = ffmpegPath()
    if (!ff) return reject('ffmpeg not found in bin/ folder')

    const resMap = { '360':'640:360','480':'854:480','720':'1280:720','1080':'1920:1080' }
    const [vw,vh] = (resMap[resolution] || '1280:720').split(':')
    const sf = `scale=${vw}:${vh}:force_original_aspect_ratio=decrease,pad=${vw}:${vh}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30`

    let args
    if (imageFile) {
      args = ['-loop','1','-i',imageFile,'-i',audioFile,
              '-c:v','libx264','-tune','stillimage','-vf',sf,
              '-r','30','-c:a','aac','-b:a','192k','-pix_fmt','yuv420p','-shortest','-y',outputFile]
    } else {
      args = ['-f','lavfi','-i',`color=c=black:s=${vw}x${vh}:r=30`,
              '-i',audioFile,'-r','30','-c:v','libx264','-tune','stillimage',
              '-c:a','aac','-b:a','192k','-pix_fmt','yuv420p','-shortest','-y',outputFile]
    }

    // probe duration for progress
    exec(`"${ff}" -i "${audioFile}" 2>&1`, (_, out) => {
      const dm = out.match(/Duration:\s*(\d{2}):(\d{2}):(\d{2})/)
      const dur = dm ? (+dm[1]*3600 + +dm[2]*60 + +dm[3]) : 0

      const proc = spawn(ff, args)
      proc.stdout.on('data', d => {
        const line = d.toString()
        const tm = line.match(/time=(\d{2}):(\d{2}):(\d{2})/)
        if (tm && dur > 0) {
          const cur = +tm[1]*3600 + +tm[2]*60 + +tm[3]
          event.sender.send('progress', { type: 'av', value: Math.min(cur/dur*100,100) })
        }
      })
      proc.stderr.on('data', d => {
        const line = d.toString()
        const tm = line.match(/time=(\d{2}):(\d{2}):(\d{2})/)
        if (tm && dur > 0) {
          const cur = +tm[1]*3600 + +tm[2]*60 + +tm[3]
          event.sender.send('progress', { type: 'av', value: Math.min(cur/dur*100,100) })
        }
      })
      proc.on('close', code => code === 0 ? resolve('done') : reject('FFmpeg conversion failed'))
    })
  })
})

// ─── IPC: ffmpeg check ──────────────────────────────────────────
ipcMain.handle('check-ffmpeg', () => !!ffmpegPath())

// ─── IPC: default paths ─────────────────────────────────────────
ipcMain.handle('get-defaults', () => ({
  audio: path.join(os.homedir(), 'Downloads', 'YT_Audio'),
  video: path.join(os.homedir(), 'Downloads', 'YT_Video'),
}))
