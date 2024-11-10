const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selectDirectories: async () => ipcRenderer.invoke('select-directories')
});
