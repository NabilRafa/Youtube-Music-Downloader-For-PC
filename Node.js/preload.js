const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('api', {
  // Window controls
  minimize:    ()    => ipcRenderer.send('win-minimize'),
  maximize:    ()    => ipcRenderer.send('win-maximize'),
  close:       ()    => ipcRenderer.send('win-close'),
  openFolder:  (p)   => ipcRenderer.send('open-folder', p),

  // Dialogs
  browseFolder: (def) => ipcRenderer.invoke('browse-folder', def),
  browseFile:   (f)   => ipcRenderer.invoke('browse-file', f),

  // Core actions
  getInfo:       (url)    => ipcRenderer.invoke('get-info', url),
  downloadAudio: (opts)   => ipcRenderer.invoke('download-audio', opts),
  downloadVideo: (opts)   => ipcRenderer.invoke('download-video', opts),
  avConvert:     (opts)   => ipcRenderer.invoke('av-convert', opts),
  checkFfmpeg:   ()       => ipcRenderer.invoke('check-ffmpeg'),
  getDefaults:   ()       => ipcRenderer.invoke('get-defaults'),

  // Events
  onProgress: (cb) => ipcRenderer.on('progress', (_, d) => cb(d)),
  onLog:      (cb) => ipcRenderer.on('log',      (_, d) => cb(d)),
  removeAllListeners: (ch) => ipcRenderer.removeAllListeners(ch),
})
