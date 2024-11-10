const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false, // Best practice for security
      contextIsolation: true, // Enable context isolation
      preload: path.join(__dirname, 'preload.js') // Load the preload script
    }
  });

  win.loadURL('http://localhost:3000'); // Load the React app during development
}

// Handle directory selection
ipcMain.handle('select-directories', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory', 'multiSelections']
  });
  return result.filePaths; // Return the selected directory paths to the renderer process
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
