import { BrowserWindow } from 'electron'
import type { WindowState } from '../types/window'

// 录制时窗口隐藏状态
const hiddenWindowsForRecording: WindowState[] = []

// 隐藏所有应用窗口（全屏录制时使用）
export function hideAllAppWindows(): void {
  console.log('隐藏所有应用窗口以进行录制')

  // 清空之前的记录
  hiddenWindowsForRecording.length = 0

  // 获取所有窗口
  const allWindows = BrowserWindow.getAllWindows()

  allWindows.forEach(window => {
    if (!window.isDestroyed()) {
      const wasVisible = window.isVisible()
      hiddenWindowsForRecording.push({ window, wasVisible })
      if (wasVisible) {
        window.hide()
      }
    }
  })

  console.log('已隐藏应用窗口，记录了', hiddenWindowsForRecording.length, '个窗口状态')
}

// 隐藏当前窗口（区域录制时使用）
export function hideCurrentWindow(webContents: Electron.WebContents): void {
  console.log('隐藏当前窗口以进行录制')

  // 清空之前的记录
  hiddenWindowsForRecording.length = 0

  // 找到发起请求的窗口
  const currentWindow = BrowserWindow.fromWebContents(webContents)
  if (currentWindow && !currentWindow.isDestroyed()) {
    const wasVisible = currentWindow.isVisible()
    hiddenWindowsForRecording.push({ window: currentWindow, wasVisible })
    if (wasVisible) {
      currentWindow.hide()
      console.log('已隐藏当前窗口:', currentWindow.getTitle())
    }
  } else {
    console.log('未找到当前窗口或窗口已销毁')
  }
}

// 显示之前隐藏的应用窗口（录制完成后使用）
export function showHiddenAppWindows(): void {
  console.log('恢复显示之前隐藏的应用窗口')
  console.log('hiddenWindowsForRecording:', hiddenWindowsForRecording)
  hiddenWindowsForRecording.forEach(({ window }) => {
    if (!window.isDestroyed()) {
      window.show()
      console.log('已恢复显示窗口:', window.getTitle())
    }
  })

  // 清空记录
  hiddenWindowsForRecording.length = 0
  console.log('已恢复显示所有应用窗口')
}

// 创建选择界面HTML
export function createSelectionHTML(): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        body {
          width: 100vw;
          height: 100vh;
          background: rgba(0, 0, 0, 0.3);
          cursor: crosshair;
          user-select: none;
          overflow: hidden;
        }
        .selection {
          position: absolute;
          border: 2px solid #007ACC;
          background: rgba(0, 122, 204, 0.1);
          display: none;
          z-index: 1000;
        }
        .instructions {
          position: absolute;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 12px 24px;
          border-radius: 6px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          font-size: 14px;
          z-index: 1001;
        }
      </style>
    </head>
    <body>
      <div class="instructions">拖拽选择截图区域，ESC取消</div>
      <div class="selection" id="selection"></div>
      <script>
        const { ipcRenderer } = require('electron');
        let isSelecting = false;
        let startX, startY;
        const selection = document.getElementById('selection');

        document.addEventListener('mousedown', (e) => {
          if (e.button === 0) {
            isSelecting = true;
            startX = e.clientX;
            startY = e.clientY;
            selection.style.left = startX + 'px';
            selection.style.top = startY + 'px';
            selection.style.width = '0px';
            selection.style.height = '0px';
            selection.style.display = 'block';
          }
        });

        document.addEventListener('mousemove', (e) => {
          if (isSelecting) {
            const currentX = e.clientX;
            const currentY = e.clientY;
            const left = Math.min(startX, currentX);
            const top = Math.min(startY, currentY);
            const width = Math.abs(currentX - startX);
            const height = Math.abs(currentY - startY);

            selection.style.left = left + 'px';
            selection.style.top = top + 'px';
            selection.style.width = width + 'px';
            selection.style.height = height + 'px';
          }
        });

        document.addEventListener('mouseup', (e) => {
          if (e.button === 0 && isSelecting) {
            isSelecting = false;
            const currentX = e.clientX;
            const currentY = e.clientY;
            const left = Math.min(startX, currentX);
            const top = Math.min(startY, currentY);
            const width = Math.abs(currentX - startX);
            const height = Math.abs(currentY - startY);

            if (width > 10 && height > 10) {
              ipcRenderer.send('area-selected', { x: left, y: top, width, height });
            } else {
              ipcRenderer.send('area-selection-cancelled');
            }
          }
        });

        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape') {
            ipcRenderer.send('area-selection-cancelled');
          }
        });

        document.addEventListener('contextmenu', (e) => {
          e.preventDefault();
          ipcRenderer.send('area-selection-cancelled');
        });
      </script>
    </body>
    </html>
  `
}

// 创建录屏区域选择界面HTML
export function createRecordingAreaSelectionHTML(): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        body {
          width: 100vw;
          height: 100vh;
          background: transparent;
          cursor: crosshair;
          user-select: none;
          overflow: hidden;
          position: relative;
        }
        .overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.3);
          pointer-events: none;
        }
        .selection {
          position: absolute;
          border: 2px solid #FF4444;
          background: rgba(255, 68, 68, 0.2);
          display: none;
          z-index: 1000;
          box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.3);
        }
        .instructions {
          position: absolute;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 12px 24px;
          border-radius: 6px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          font-size: 14px;
          z-index: 1001;
          text-align: center;
        }
        .recording-indicator {
          position: absolute;
          top: 60px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(255, 68, 68, 0.9);
          color: white;
          padding: 8px 16px;
          border-radius: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          font-size: 12px;
          font-weight: 600;
          z-index: 1001;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .recording-dot {
          width: 8px;
          height: 8px;
          background: white;
          border-radius: 50%;
          animation: pulse 1s infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      </style>
    </head>
    <body>
      <div class="overlay"></div>
      <div class="instructions">拖拽选择录屏区域，ESC取消</div>
      <div class="recording-indicator">
        <div class="recording-dot"></div>
        准备录制
      </div>
      <div class="selection" id="selection"></div>
      <script>
        const { ipcRenderer } = require('electron');
        let isSelecting = false;
        let startX, startY;
        const selection = document.getElementById('selection');

        document.addEventListener('mousedown', (e) => {
          if (e.button === 0) {
            isSelecting = true;
            startX = e.clientX;
            startY = e.clientY;
            selection.style.left = startX + 'px';
            selection.style.top = startY + 'px';
            selection.style.width = '0px';
            selection.style.height = '0px';
            selection.style.display = 'block';

            // 更新指示器
            const indicator = document.querySelector('.recording-indicator');
            indicator.textContent = '拖拽选择区域...';
            indicator.style.background = 'rgba(255, 165, 0, 0.9)';
          }
        });

        document.addEventListener('mousemove', (e) => {
          if (isSelecting) {
            const currentX = e.clientX;
            const currentY = e.clientY;
            const left = Math.min(startX, currentX);
            const top = Math.min(startY, currentY);
            const width = Math.abs(currentX - startX);
            const height = Math.abs(currentY - startY);

            selection.style.left = left + 'px';
            selection.style.top = top + 'px';
            selection.style.width = width + 'px';
            selection.style.height = height + 'px';

            // 更新指示器显示尺寸
            const indicator = document.querySelector('.recording-indicator');
            indicator.innerHTML = \`
              <div class="recording-dot"></div>
              区域: \${width} × \${height}
            \`;
          }
        });

        document.addEventListener('mouseup', (e) => {
          if (e.button === 0 && isSelecting) {
            isSelecting = false;
            const currentX = e.clientX;
            const currentY = e.clientY;
            const left = Math.min(startX, currentX);
            const top = Math.min(startY, currentY);
            const width = Math.abs(currentX - startX);
            const height = Math.abs(currentY - startY);

            if (width > 20 && height > 20) {
              // 考虑设备像素比（Retina 显示器）
              const devicePixelRatio = window.devicePixelRatio || 1;
              console.log('选择区域:', { x: left, y: top, width, height, devicePixelRatio });

              // 对于 macOS Retina 显示器，可能需要调整坐标
              // 但 screencapture 命令通常使用逻辑坐标，所以暂时不缩放
              ipcRenderer.send('recording-area-selected', {
                x: Math.round(left),
                y: Math.round(top),
                width: Math.round(width),
                height: Math.round(height)
              });
            } else {
              ipcRenderer.send('recording-area-selection-cancelled');
            }
          }
        });

        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape') {
            ipcRenderer.send('recording-area-selection-cancelled');
          }
        });

        document.addEventListener('contextmenu', (e) => {
          e.preventDefault();
          ipcRenderer.send('recording-area-selection-cancelled');
        });
      </script>
    </body>
    </html>
  `
}
