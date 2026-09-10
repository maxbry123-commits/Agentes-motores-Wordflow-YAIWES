import { ipcMain, desktopCapturer, screen, clipboard, dialog, app, shell, BrowserWindow } from 'electron'
import { writeFile } from 'fs/promises'
import { join } from 'path'
import { windowManager } from './windowManager'
import { apiProxy } from './apiProxy'
import { recordingManager } from './recordingManager'
import { databaseService } from '../services/database'
import { createResponseWindow, createHtmlPreviewWindow } from '../utils/windowCreators'
import { createSelectionHTML, hideCurrentWindow } from '../utils/recordingUtils'

export class IpcHandlers {
  // 注册所有IPC处理器
  registerHandlers(): void {
    this.registerAppHandlers()
    this.registerScreenHandlers()
    this.registerApiHandlers()
    this.registerDatabaseHandlers()
    this.registerWindowHandlers()
    this.registerRecordingHandlers()
    this.registerUtilityHandlers()
  }

  // 应用相关处理器
  private registerAppHandlers(): void {
    let isFirstLaunch = true
    ipcMain.handle('is-first-launch', () => {
      const result = isFirstLaunch
      isFirstLaunch = false // 第一次调用后设为false
      return result
    })

    // 监听渲染进程初始化完成通知
    ipcMain.handle('renderer-initialization-complete', () => {
      console.log('渲染进程初始化完成，主窗口可以安全显示')
      return true
    })

    // 获取应用版本号
    ipcMain.handle('get-app-version', () => {
      return app.getVersion()
    })

    // 打开外部链接
    ipcMain.handle('open-external', async (_, url: string) => {
      try {
        await shell.openExternal(url)
      } catch (error) {
        console.error('打开外部链接失败:', error)
        throw error
      }
    })
  }

  // 屏幕相关处理器
  private registerScreenHandlers(): void {
    ipcMain.handle('get-screen-sources', async () => {
      try {
        const sources = await desktopCapturer.getSources({
          types: ['window', 'screen'],
          thumbnailSize: { width: 320, height: 180 }
        })
        return sources.map(source => ({
          id: source.id,
          name: source.name,
          thumbnail: source.thumbnail.toDataURL()
        }))
      } catch (error) {
        console.error('Error getting screen sources:', error)
        return []
      }
    })

    ipcMain.handle('get-clipboard-image', () => {
      try {
        const image = clipboard.readImage()
        if (image.isEmpty()) {
          return null
        }
        return image.toDataURL()
      } catch (error) {
        console.error('读取粘贴板图片失败:', error)
        return null
      }
    })

    // 快速全屏截图
    ipcMain.handle('quick-screenshot', async () => {
      try {
        const allWindows = BrowserWindow.getAllWindows()
        const windowsVisibility = allWindows.map(win => win.isVisible())

        allWindows.forEach(win => {
          if (win.isVisible()) {
            win.hide()
          }
        })

        // 给系统一点时间来完成窗口隐藏
        await new Promise(resolve => setTimeout(resolve, 200))

        const display = screen.getPrimaryDisplay()
        const { width, height } = display.size

        const sources = await desktopCapturer.getSources({
          types: ['screen'],
          thumbnailSize: { width, height }
        })

        // 恢复窗口可见状态
        allWindows.forEach((win, index) => {
          if (windowsVisibility[index]) {
            win.show()
          }
        })

        if (sources.length === 0) {
          throw new Error('无法获取屏幕截图')
        }

        return sources[0].thumbnail.toDataURL()
      } catch (error) {
        // 发生错误时确保窗口恢复显示
        BrowserWindow.getAllWindows().forEach(win => win.show())
        console.error('快速截图失败:', error)
        throw error
      }
    })

    ipcMain.handle('get-primary-display', () => {
      return screen.getPrimaryDisplay().bounds
    })

    // 添加快速截图功能
    ipcMain.handle('capture-screen', async () => {
      try {
        // 保存当前所有窗口的可见状态
        const allWindows = BrowserWindow.getAllWindows()
        const windowsVisibility = allWindows.map(win => win.isVisible())

        // 隐藏所有窗口
        allWindows.forEach(win => {
          if (win.isVisible()) {
            win.hide()
          }
        })

        // 给系统一点时间来完成窗口隐藏
        await new Promise(resolve => setTimeout(resolve, 200))

        const sources = await desktopCapturer.getSources({
          types: ['screen'],
          thumbnailSize: { width: 1920, height: 1080 }
        })

        // 恢复窗口可见状态
        allWindows.forEach((win, index) => {
          if (windowsVisibility[index]) {
            win.show()
          }
        })

        if (sources.length > 0) {
          // 返回第一个屏幕的截图（主屏幕）
          return sources[0].thumbnail.toDataURL()
        }
        throw new Error('No screen sources available')
      } catch (error) {
        // 发生错误时确保窗口恢复显示
        BrowserWindow.getAllWindows().forEach(win => win.show())
        console.error('Error capturing screen:', error)
        throw error
      }
    })

    // 添加区域截图功能
    ipcMain.handle('capture-screen-area', async () => {
      try {
        return new Promise((resolve, reject) => {
          // 获取所有窗口和当前活动窗口
          const windows = BrowserWindow.getAllWindows()
          const activeWindow = BrowserWindow.getFocusedWindow()

          // 隐藏所有窗口
          windows.forEach(win => {
            win.hide()
          })

          // 等待窗口隐藏完成
          setTimeout(async () => {
            try {
              // 获取屏幕截图作为参考
              const display = screen.getPrimaryDisplay()
              const { width, height } = display.size

              const sources = await desktopCapturer.getSources({
                types: ['screen'],
                thumbnailSize: { width, height }
              })

              if (sources.length === 0) {
                throw new Error('无法获取屏幕截图')
              }

              const fullImage = sources[0].thumbnail.toDataURL()

              // 创建全屏透明选择窗口
              const selectionWindow = new BrowserWindow({
                width,
                height,
                x: 0,
                y: 0,
                frame: false,
                transparent: true,
                alwaysOnTop: true,
                skipTaskbar: true,
                resizable: false,
                movable: false,
                webPreferences: {
                  nodeIntegration: true,
                  contextIsolation: false
                }
              })

              // 设置选择窗口始终在最顶层
              selectionWindow.setAlwaysOnTop(true, 'screen-saver')

              // 加载选择界面HTML
              const selectionHtml = createSelectionHTML()
              selectionWindow.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(selectionHtml))

              // 监听选择结果
              const handleAreaSelected = async (_, area: { x: number; y: number; width: number; height: number }): Promise<void> => {
                selectionWindow.close()

                try {
                  // 获取选择窗口的位置，将相对坐标转换为绝对坐标
                  const windowBounds = selectionWindow.getBounds()
                  const absoluteArea = {
                    x: area.x + windowBounds.x,
                    y: area.y + windowBounds.y,
                    width: area.width,
                    height: area.height
                  }

                  console.log('=== 截图区域坐标调试 (绝对坐标转换) ===')
                  console.log('选择窗口位置:', windowBounds)
                  console.log('原始相对坐标:', area)
                  console.log('转换后绝对坐标:', absoluteArea)

                  // 只恢复原来活动的窗口
                  if (activeWindow && !activeWindow.isDestroyed()) {
                    activeWindow.show()
                    activeWindow.focus()
                  }
                  // 使用转换后的绝对坐标进行截图裁剪
                  resolve({ fullImage, area: absoluteArea })
                } catch (error) {
                  // 如果原窗口有问题，恢复所有窗口
                  windows.forEach(win => {
                    if (!win.isDestroyed()) win.show()
                  })
                  reject(error)
                }
              }

              const handleSelectionCancelled = (): void => {
                selectionWindow.close()
                // 只恢复原来活动的窗口
                if (activeWindow && !activeWindow.isDestroyed()) {
                  activeWindow.show()
                  activeWindow.focus()
                }
                reject(new Error('用户取消了区域选择'))
              }

              // 注册事件监听器
              ipcMain.once('area-selected', handleAreaSelected)
              ipcMain.once('area-selection-cancelled', handleSelectionCancelled)

              // 窗口关闭时清理
              selectionWindow.on('closed', () => {
                ipcMain.removeListener('area-selected', handleAreaSelected)
                ipcMain.removeListener('area-selection-cancelled', handleSelectionCancelled)
                // 只恢复原来活动的窗口
                if (activeWindow && !activeWindow.isDestroyed()) {
                  activeWindow.show()
                  activeWindow.focus()
                }
              })
            } catch (error) {
              // 出错时恢复所有窗口
              windows.forEach(win => {
                if (!win.isDestroyed()) win.show()
              })
              reject(error)
            }
          }, 300)
        })
      } catch (error) {
        console.error('区域截图失败:', error)
        throw error
      }
    })
  }

  // API相关处理器
  private registerApiHandlers(): void {
    // 添加API代理处理器
    ipcMain.handle('api-request', async (_, url: string, options: RequestInit) => {
      return await apiProxy.proxyApiRequest(url, options)
    })

    // 添加流式API代理处理器
    ipcMain.handle('api-stream-request', async (event, url: string, options: RequestInit, streamId: string) => {
      return await apiProxy.createStreamProxy(url, options, event.sender, streamId)
    })

    // 取消流式请求处理器
    ipcMain.handle('api-stream-cancel', async (_, streamId: string) => {
      console.log('收到取消流式请求:', streamId)
      apiProxy.cancelStream(streamId)
    })

    // 取消所有流式请求处理器
    ipcMain.handle('api-stream-cancel-all', async () => {
      console.log('收到取消所有流式请求')
      apiProxy.cancelAllStreams()
    })
  }

  // 数据库相关处理器
  private registerDatabaseHandlers(): void {
    ipcMain.handle('db-save-conversation', (_, conversation) => {
      return databaseService.saveConversation(conversation)
    })

    ipcMain.handle('db-save-conversation-incremental', (_, conversation) => {
      return databaseService.saveConversationIncremental(conversation)
    })

    ipcMain.handle('db-save-message', (_, conversationId: string, message) => {
      return databaseService.saveMessage(conversationId, message)
    })

    ipcMain.handle('db-save-or-update-conversation', (_, conversationId: string, title: string, timestamp: number, messageCount: number) => {
      return databaseService.saveOrUpdateConversation(conversationId, title, timestamp, messageCount)
    })

    ipcMain.handle('db-get-conversation-list', () => {
      return databaseService.getConversationList()
    })

    ipcMain.handle('db-load-conversation', (_, conversationId: string) => {
      return databaseService.loadConversation(conversationId)
    })

    ipcMain.handle('db-delete-conversation', (_, conversationId: string) => {
      return databaseService.deleteConversation(conversationId)
    })

    ipcMain.handle('db-search-conversations', (_, keyword: string) => {
      return databaseService.searchConversations(keyword)
    })

    ipcMain.handle('db-get-stats', () => {
      return databaseService.getStats()
    })

    ipcMain.handle('db-cleanup', (_, keepRecentCount: number = 100) => {
      return databaseService.cleanup(keepRecentCount)
    })

    ipcMain.handle('db-cleanup-duplicates', () => {
      return databaseService.cleanupDuplicateMessages()
    })
  }

  // 窗口相关处理器
  private registerWindowHandlers(): void {
    // 窗口模式切换
    ipcMain.handle('switch-to-floating', () => {
      const mainWindow = windowManager.getMainWindow()
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.hide()
      }

      // 创建或显示悬浮窗，保持其原有的置顶状态
      windowManager.createFloatingWindow(true) // 用户主动切换时显示

      return true
    })

    ipcMain.handle('switch-to-main', () => {
      const floatingWindow = windowManager.getFloatingWindow()
      if (floatingWindow && !floatingWindow.isDestroyed()) {
        floatingWindow.hide() // 隐藏而不是关闭，保持窗口状态
      }

      // 显示主窗口，保持其原有的置顶状态
      const mainWindow = windowManager.getMainWindow()
      if (mainWindow) {
        mainWindow.show()
        mainWindow.focus()
      } else {
        windowManager.createMainWindow()
      }

      return true
    })

    // 关闭悬浮窗
    ipcMain.on('close-floating-window', () => {
      const floatingWindow = windowManager.getFloatingWindow()
      if (floatingWindow) {
        floatingWindow.close()
        windowManager.setFloatingWindow(null)
      }
    })

    // 显示响应窗口
    ipcMain.handle('show-response-window', (_, response: string) => {
      // 如果已经有响应窗口，先关闭它
      const existingResponseWindow = windowManager.getResponseWindow()
      if (existingResponseWindow && !existingResponseWindow.isDestroyed()) {
        existingResponseWindow.close()
        windowManager.setResponseWindow(null)
      }

      const floatingWindow = windowManager.getFloatingWindow()
      const responseWindow = createResponseWindow(response, floatingWindow || undefined)
      windowManager.setResponseWindow(responseWindow)

      // 添加一个定时器，如果窗口长时间未关闭，自动关闭（5分钟）
      const autoCloseTimer = setTimeout(
        () => {
          if (responseWindow && !responseWindow.isDestroyed()) {
            console.log('自动关闭长时间未关闭的响应窗口')
            responseWindow.close()
            windowManager.setResponseWindow(null)
          }
        },
        5 * 60 * 1000
      )

      // 窗口关闭时清理
      responseWindow.on('closed', () => {
        clearTimeout(autoCloseTimer)
        windowManager.setResponseWindow(null)
      })

      return true
    })

    // 关闭响应窗口
    ipcMain.on('close-response-window', () => {
      const responseWindow = windowManager.getResponseWindow()
      if (responseWindow && !responseWindow.isDestroyed()) {
        try {
          responseWindow.close()
        } catch (error) {
          console.error('关闭响应窗口失败:', error)
          // 强制销毁
          if (responseWindow && !responseWindow.isDestroyed()) {
            responseWindow.destroy()
          }
        } finally {
          windowManager.setResponseWindow(null)
        }
      }
    })

    // 显示HTML预览窗口
    ipcMain.handle('show-html-preview', (_, htmlContent: string) => {
      // 如果已经有HTML预览窗口，先关闭它
      const existingHtmlPreviewWindow = windowManager.getHtmlPreviewWindow()
      if (existingHtmlPreviewWindow && !existingHtmlPreviewWindow.isDestroyed()) {
        existingHtmlPreviewWindow.close()
        windowManager.setHtmlPreviewWindow(null)
      }

      const htmlPreviewWindow = createHtmlPreviewWindow(htmlContent)
      windowManager.setHtmlPreviewWindow(htmlPreviewWindow)

      // 窗口关闭时清理
      htmlPreviewWindow.on('closed', () => {
        windowManager.setHtmlPreviewWindow(null)
      })

      return true
    })

    // 关闭HTML预览窗口
    ipcMain.on('close-html-preview', () => {
      const htmlPreviewWindow = windowManager.getHtmlPreviewWindow()
      if (htmlPreviewWindow && !htmlPreviewWindow.isDestroyed()) {
        htmlPreviewWindow.close()
        windowManager.setHtmlPreviewWindow(null)
      }
    })

    // 窗口置顶功能
    ipcMain.handle('toggle-always-on-top', event => {
      // 根据发送请求的窗口来处理置顶
      const senderWindow = BrowserWindow.fromWebContents(event.sender)
      if (!senderWindow) return false

      const isAlwaysOnTop = senderWindow.isAlwaysOnTop()
      senderWindow.setAlwaysOnTop(!isAlwaysOnTop)

      return !isAlwaysOnTop
    })

    ipcMain.handle('get-always-on-top-status', event => {
      // 根据发送请求的窗口来获取状态
      const senderWindow = BrowserWindow.fromWebContents(event.sender)
      if (!senderWindow) return false

      return senderWindow.isAlwaysOnTop()
    })
  }

  // 录制相关处理器
  private registerRecordingHandlers(): void {
    // 屏幕录制功能
    ipcMain.handle('start-screen-recording', async event => {
      return await recordingManager.startScreenRecording(event.sender)
    })

    ipcMain.handle('stop-screen-recording', async () => {
      return await recordingManager.stopRecording()
    })

    ipcMain.handle('start-area-screen-recording', async (event, area: { x: number; y: number; width: number; height: number }) => {
      return await recordingManager.startAreaRecording(event.sender, area)
    })

    // 保存录制文件
    ipcMain.handle('save-recording-to-file', async (_, recordingBuffer: Buffer) => {
      try {
        if (!recordingBuffer) {
          console.log('没有录制数据可保存')
          return { success: false, message: '没有录制数据' }
        }

        // 验证录制数据是否有效
        if (recordingBuffer.length < 100) {
          console.log('录制数据太小，可能无效')
          return { success: false, message: '录制数据无效' }
        }

        // 获取下载目录
        const downloadsPath = app.getPath('downloads')

        // 生成文件名：包含时间戳，统一使用 MP4 格式
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
        const fileName = `screen-recording-${timestamp}.mp4`
        const filePath = join(downloadsPath, fileName)

        await writeFile(filePath, recordingBuffer)
        console.log('录制文件已保存:', filePath)

        return { success: true, filePath, message: `录制已保存到: ${fileName}` }
      } catch (error) {
        console.error('保存录制文件失败:', error)
        return { success: false, message: '保存文件失败' }
      }
    })

    // 手动清理录制数据
    ipcMain.handle('clear-recording-data', () => {
      recordingManager.clearRecordingData()
      return true
    })

    // 隐藏应用窗口功能 - 用于录屏前隐藏
    ipcMain.handle('hide-app-windows', event => {
      try {
        // 隐藏发起请求的当前窗口
        const webContents = event.sender
        hideCurrentWindow(webContents)
        return true
      } catch (error) {
        console.error('隐藏应用窗口失败:', error)
        return false
      }
    })

    // 录制状态窗口相关处理器
    ipcMain.on('stop-recording-from-status', async () => {
      await recordingManager.handleStopRecordingFromStatus()
    })

    // 取消录制处理器 - 不保存录制内容
    ipcMain.on('cancel-recording-from-status', async event => {
      await recordingManager.handleCancelRecordingFromStatus(event.sender)
    })

    ipcMain.on('hide-recording-status', () => {
      recordingManager.hideRecordingStatus()
    })

    ipcMain.handle('show-recording-status', (_, type: 'screen' | 'area', area?: { x: number; y: number; width: number; height: number }) => {
      recordingManager.showRecordingStatus(type, area)
      return true
    })

    // 显示应用窗口功能 - 用于录屏后恢复
    ipcMain.handle('show-app-windows', () => {
      return true
    })

    // 区域选择功能 - 用于录屏前选择区域
    ipcMain.handle('select-recording-area', async () => {
      return await recordingManager.selectRecordingArea()
    })
  }

  // 工具相关处理器
  private registerUtilityHandlers(): void {
    // 显示保存文件对话框
    ipcMain.handle('show-save-dialog', async (_, options) => {
      try {
        const result = await dialog.showSaveDialog(options)
        return result
      } catch (error) {
        console.error('显示保存对话框失败:', error)
        return { canceled: true }
      }
    })

    // IPC test
    ipcMain.on('ping', () => console.log('pong'))
  }
}

export const ipcHandlers = new IpcHandlers()
