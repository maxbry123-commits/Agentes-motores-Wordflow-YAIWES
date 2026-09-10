import { BrowserWindow, screen, ipcMain } from 'electron'
import { exec } from 'child_process'
import { tmpdir } from 'os'
import { join } from 'path'
import { readFileSync, unlinkSync, existsSync } from 'fs'
import { windowManager } from './windowManager'
import { createRecordingStatusWindow, createRecordingBorderWindows } from '../utils/windowCreators'
import { hideCurrentWindow, showHiddenAppWindows, createRecordingAreaSelectionHTML } from '../utils/recordingUtils'
import { compressVideo, getOptimalCompressOptions } from '../utils/videoCompress'
import type { RecordingArea } from '../types/window'

export class RecordingManager {
  private isRecording = false
  private recordingData: Buffer | null = null
  private recordingWindow: BrowserWindow | null = null
  private recordingTimer: NodeJS.Timeout | null = null
  private recordingStartTime: Date | null = null
  private currentRecordingArea: RecordingArea | null = null
  private borderAutoShowTimer: NodeJS.Timeout | null = null

  // 获取录制状态
  getIsRecording(): boolean {
    return this.isRecording
  }

  getRecordingData(): Buffer | null {
    return this.recordingData
  }

  // 显示录制状态窗口
  showRecordingStatus(type: 'screen' | 'area', area?: RecordingArea): void {
    let statusX: number | undefined
    let statusY: number | undefined

    // 如果是区域录制且提供了区域信息，则计算状态窗口位置
    if (type === 'area' && area) {
      const display = screen.getPrimaryDisplay()
      const { height: screenHeight, width: screenWidth } = display.workAreaSize
      const statusWindowHeight = 50
      const statusWindowWidth = 280
      const margin = 10 // 与边框的间距

      statusX = area.x
      statusY = area.y - statusWindowHeight - margin // 默认显示在上方

      // 如果上方空间不够，显示在下方
      if (statusY < 0) {
        statusY = area.y + area.height + margin
      }

      // 如果下方也超出屏幕，则显示在右上角
      if (statusY + statusWindowHeight > screenHeight) {
        statusX = screenWidth - statusWindowWidth - 20
        statusY = 20
      }

      // 确保状态窗口在屏幕范围内
      if (statusX + statusWindowWidth > screenWidth) {
        statusX = screenWidth - statusWindowWidth - 20
      }
      if (statusX < 0) {
        statusX = 20
      }
    }

    const recordingStatusWindow = windowManager.getRecordingStatusWindow()
    if (!recordingStatusWindow) {
      const newWindow = createRecordingStatusWindow(statusX, statusY)
      windowManager.setRecordingStatusWindow(newWindow)
    } else if (statusX !== undefined && statusY !== undefined) {
      // 如果窗口已存在但需要调整位置
      recordingStatusWindow.setPosition(statusX, statusY)
    }

    const statusWindow = windowManager.getRecordingStatusWindow()
    if (statusWindow) {
      statusWindow.show()
      statusWindow.webContents.send('start-recording-timer', type)
    }
  }

  // 隐藏录制状态窗口
  hideRecordingStatus(): void {
    const recordingStatusWindow = windowManager.getRecordingStatusWindow()
    if (recordingStatusWindow) {
      recordingStatusWindow.webContents.send('stop-recording-timer')
      recordingStatusWindow.hide()
    }
  }

  // 显示录制边框
  showRecordingBorder(area?: RecordingArea): void {
    // 先隐藏现有边框
    this.hideRecordingBorder()

    // 创建新边框
    const borderWindow = createRecordingBorderWindows(area)
    if (borderWindow) {
      windowManager.setRecordingBorderWindow(borderWindow)
      this.currentRecordingArea = area || null

      // 确保边框窗口加载完成后立即置于顶层
      borderWindow.once('ready-to-show', () => {
        if (borderWindow && !borderWindow.isDestroyed()) {
          borderWindow.show()
          // 强制置于顶层
          if (process.platform === 'darwin') {
            borderWindow.setAlwaysOnTop(true, 'screen-saver')
          } else {
            borderWindow.setAlwaysOnTop(true)
          }
          console.log('录制边框窗口已显示并置于顶层')
        }
      })

      // 监听窗口隐藏事件，在录制过程中自动重新显示
      borderWindow.on('hide', () => {
        if (this.isRecording && borderWindow && !borderWindow.isDestroyed()) {
          // 清除之前的定时器
          if (this.borderAutoShowTimer) {
            clearTimeout(this.borderAutoShowTimer)
          }

          // 10ms后自动重新显示边框窗口
          this.borderAutoShowTimer = setTimeout(() => {
            if (this.isRecording && borderWindow && !borderWindow.isDestroyed()) {
              borderWindow.show()
              // 重新显示时再次确保置于顶层
              if (process.platform === 'darwin') {
                borderWindow.setAlwaysOnTop(true, 'screen-saver')
              } else {
                borderWindow.setAlwaysOnTop(true)
              }
              console.log('录制边框窗口已自动重新显示')
            }
          }, 10)
        }
      })

      // 启动定期检查，确保边框窗口始终在顶层
      if (borderWindow && !borderWindow.isDestroyed()) {
        const borderTopMostTimer = setInterval(() => {
          if (this.isRecording && borderWindow && !borderWindow.isDestroyed()) {
            // 定期强制置顶
            if (process.platform === 'darwin') {
              borderWindow.setAlwaysOnTop(true, 'screen-saver')
            } else {
              borderWindow.setAlwaysOnTop(true)
            }
          } else {
            // 录制结束时清理定时器
            clearInterval(borderTopMostTimer)
          }
        }, 500)

        // 将定时器保存到全局变量以便清理
        global.borderTopMostTimer = borderTopMostTimer
      }
    }
  }

  // 隐藏录制边框
  hideRecordingBorder(): void {
    // 清除自动显示定时器
    if (this.borderAutoShowTimer) {
      clearTimeout(this.borderAutoShowTimer)
      this.borderAutoShowTimer = null
    }

    // 清除定期置顶定时器
    if (global.borderTopMostTimer) {
      clearInterval(global.borderTopMostTimer)
      global.borderTopMostTimer = null
    }

    const recordingBorderWindow = windowManager.getRecordingBorderWindow()
    if (recordingBorderWindow && !recordingBorderWindow.isDestroyed()) {
      recordingBorderWindow.close()
    }

    windowManager.setRecordingBorderWindow(null)
    this.currentRecordingArea = null
  }

  // 开始屏幕录制
  async startScreenRecording(webContents: Electron.WebContents): Promise<boolean> {
    try {
      if (this.isRecording) {
        console.log('录制已在进行中')
        return false
      }

      console.log('开始屏幕录制')

      // 在开始录制前只隐藏当前窗口
      hideCurrentWindow(webContents)

      // 等待一小段时间确保窗口完全隐藏
      await new Promise(resolve => setTimeout(resolve, 300))

      this.isRecording = true
      this.recordingData = null
      this.recordingStartTime = new Date()

      // 显示录制状态窗口
      this.showRecordingStatus('screen')

      // 显示录制边框（全屏）
      this.showRecordingBorder()

      // 通知渲染进程录制状态改变
      BrowserWindow.getAllWindows().forEach(win => {
        win.webContents.send('recording-state-change', true)
      })

      // 在macOS上，使用screencapture命令来录制
      if (process.platform === 'darwin') {
        try {
          // 使用用户临时目录而不是应用目录来避免权限问题
          const tempPath = join(tmpdir(), `temp_recording_${Date.now()}.mov`)

          // 启动录制进程
          const recordingProcess = exec(`screencapture -v "${tempPath}"`)

          // 保存进程引用
          this.recordingWindow = new BrowserWindow({
            width: 1,
            height: 1,
            show: false
          })

          // 将进程信息保存到全局变量
          global.recordingProcess = recordingProcess
          global.recordingTempPath = tempPath

          console.log('macOS屏幕录制已启动')
        } catch (error) {
          console.error('启动macOS录制失败:', error)
          throw error
        }
      } else {
        // 对于其他平台，使用模拟录制
        this.recordingTimer = setInterval(() => {
          if (this.isRecording) {
            console.log('录制进行中...')
          }
        }, 1000)
      }

      return true
    } catch (error) {
      console.error('开始录制失败:', error)
      this.isRecording = false
      // 如果启动失败，恢复显示窗口
      showHiddenAppWindows()
      return false
    }
  }

  // 开始区域录制
  async startAreaRecording(webContents: Electron.WebContents, area: RecordingArea): Promise<boolean> {
    try {
      if (this.isRecording) {
        console.log('录制已在进行中')
        return false
      }

      console.log('开始区域屏幕录制，接收到的区域:', area)

      // 在开始录制前隐藏当前窗口（发起请求的窗口）
      hideCurrentWindow(webContents)

      // 等待一小段时间确保窗口完全隐藏
      await new Promise(resolve => setTimeout(resolve, 300))

      this.isRecording = true
      this.recordingData = null
      this.recordingStartTime = new Date()
      this.currentRecordingArea = area

      // 显示录制状态窗口
      this.showRecordingStatus('area', area)

      // 显示录制边框（指定区域）
      console.log('显示录制边框，区域:', area)
      this.showRecordingBorder(area)

      // 通知渲染进程录制状态改变
      BrowserWindow.getAllWindows().forEach(win => {
        win.webContents.send('recording-state-change', true)
      })

      // 在macOS上，使用screencapture命令录制指定区域
      if (process.platform === 'darwin') {
        try {
          // 使用用户临时目录而不是应用目录来避免权限问题
          const tempPath = join(tmpdir(), `temp_area_recording_${Date.now()}.mov`)

          // 获取主显示器信息
          const display = screen.getPrimaryDisplay()
          console.log('主显示器信息:', {
            bounds: display.bounds,
            workArea: display.workArea,
            scaleFactor: display.scaleFactor
          })

          // 在 macOS 中，screencapture 和 Electron 的坐标系统存在差异
          const menuBarHeight = display.workArea.y - display.bounds.y
          const dockHeight = display.bounds.height - display.workArea.height - menuBarHeight

          console.log('系统 UI 元素高度:', {
            menuBarHeight,
            dockHeight,
            screenHeight: display.bounds.height,
            workAreaHeight: display.workArea.height
          })

          // 录制区域保持不变
          const adjustedArea = {
            x: area.x,
            y: area.y,
            width: area.width,
            height: area.height
          }

          console.log('坐标调整结果:', {
            原始区域: area,
            调整后区域: adjustedArea
          })

          // 构建区域录制命令：-R x,y,width,height
          const areaParam = `${adjustedArea.x},${adjustedArea.y},${adjustedArea.width},${adjustedArea.height}`

          console.log('screencapture 录制命令参数:', areaParam)

          const recordingProcess = exec(`screencapture -v -R ${areaParam} "${tempPath}"`)

          // 保存进程引用
          this.recordingWindow = new BrowserWindow({
            width: 1,
            height: 1,
            show: false
          })

          // 将进程信息保存到全局变量
          global.recordingProcess = recordingProcess
          global.recordingTempPath = tempPath

          console.log(`macOS区域屏幕录制已启动，区域: ${areaParam}`)
        } catch (error) {
          console.error('启动macOS区域录制失败:', error)
          throw error
        }
      } else {
        // 对于其他平台，使用模拟录制
        this.recordingTimer = setInterval(() => {
          if (this.isRecording) {
            console.log('区域录制进行中...', area)
          }
        }, 1000)
      }

      return true
    } catch (error) {
      console.error('开始区域录制失败:', error)
      this.isRecording = false
      // 如果启动失败，恢复显示窗口
      showHiddenAppWindows()
      return false
    }
  }

  // 停止录制
  async stopRecording(): Promise<Buffer | null> {
    try {
      if (!this.isRecording) {
        console.log('当前没有进行录制')
        return null
      }

      console.log('停止屏幕录制')

      // 先隐藏边框，避免被录制进去
      this.hideRecordingBorder()

      this.isRecording = false
      this.recordingStartTime = null

      // 隐藏录制状态窗口
      this.hideRecordingStatus()

      // 清理定时器
      if (this.recordingTimer) {
        clearInterval(this.recordingTimer)
        this.recordingTimer = null
      }

      // 处理macOS录制
      if (process.platform === 'darwin' && global.recordingProcess) {
        try {
          // 终止录制进程
          global.recordingProcess.kill('SIGINT')

          // 等待录制进程完全退出
          await new Promise<void>(resolve => {
            if (global.recordingProcess) {
              global.recordingProcess.on('exit', () => {
                setTimeout(resolve, 200)
              })
              setTimeout(resolve, 2000)
            } else {
              resolve()
            }
          })

          // 读取录制文件
          if (global.recordingTempPath) {
            try {
              if (!existsSync(global.recordingTempPath)) {
                console.error('录制文件不存在:', global.recordingTempPath)
                this.recordingData = Buffer.from('录制文件不存在')
              } else {
                const recordingBuffer = readFileSync(global.recordingTempPath)

                if (recordingBuffer.length === 0) {
                  console.error('录制文件为空')
                  this.recordingData = Buffer.from('录制文件为空')
                } else {
                  this.recordingData = recordingBuffer
                  console.log('录制文件已读取，大小:', recordingBuffer.length, 'bytes')
                }

                // 清理临时文件
                try {
                  unlinkSync(global.recordingTempPath)
                  console.log('临时录制文件已删除')
                } catch (deleteError) {
                  console.error('删除临时录制文件失败:', deleteError)
                }
              }
            } catch (fileError) {
              console.error('读取录制文件失败:', fileError)
              this.recordingData = Buffer.from('录制文件读取失败')
            }
          }

          // 清理全局变量
          global.recordingProcess = null
          global.recordingTempPath = null
        } catch (error) {
          console.error('停止macOS录制失败:', error)
          this.recordingData = Buffer.from('录制停止失败')
        }
      } else {
        // 创建一个示例录制数据
        this.recordingData = Buffer.from('Mock video data - 这是示例录制数据')
      }

      if (this.recordingWindow) {
        this.recordingWindow.close()
        this.recordingWindow = null
      }

      // 通知渲染进程录制状态改变
      BrowserWindow.getAllWindows().forEach(win => {
        win.webContents.send('recording-state-change', false)
      })

      // 录制完成后恢复显示所有应用窗口
      showHiddenAppWindows()

      // 返回录制数据，但不清空 recordingData，以便后续保存使用
      return this.recordingData
    } catch (error) {
      console.error('停止录制失败:', error)
      // 出错时也要恢复显示窗口
      showHiddenAppWindows()
      return null
    }
  }

  // 取消录制
  async cancelRecording(): Promise<void> {
    if (!this.isRecording) {
      console.log('当前没有进行录制')
      return
    }

    console.log('取消屏幕录制 - 不保存录制内容')

    // 先隐藏边框
    this.hideRecordingBorder()

    this.isRecording = false
    this.recordingStartTime = null

    // 隐藏录制状态窗口
    this.hideRecordingStatus()

    // 清理定时器
    if (this.recordingTimer) {
      clearInterval(this.recordingTimer)
      this.recordingTimer = null
    }

    // 处理macOS录制进程 - 直接终止不保存
    if (process.platform === 'darwin' && global.recordingProcess) {
      try {
        // 终止录制进程
        global.recordingProcess.kill('SIGINT')

        // 等待录制进程完全退出
        await new Promise<void>(resolve => {
          if (global.recordingProcess) {
            global.recordingProcess.on('exit', () => {
              resolve()
            })
            setTimeout(resolve, 1000)
          } else {
            resolve()
          }
        })

        // 清理临时文件（如果存在）
        if (global.recordingTempPath) {
          try {
            unlinkSync(global.recordingTempPath)
            console.log('临时录制文件已删除')
          } catch (fileError) {
            console.error('删除临时录制文件失败:', fileError)
          }
        }

        // 清理全局变量
        global.recordingProcess = null
        global.recordingTempPath = null
      } catch (error) {
        console.error('取消macOS录制失败:', error)
      }
    }

    if (this.recordingWindow) {
      this.recordingWindow.close()
      this.recordingWindow = null
    }

    // 清理录制数据，不保存
    this.recordingData = null

    // 通知所有窗口录制状态改变
    BrowserWindow.getAllWindows().forEach(win => {
      win.webContents.send('recording-state-change', false)
    })

    // 恢复显示之前隐藏的应用窗口
    showHiddenAppWindows()

    console.log('录制已取消，未保存任何内容')
  }

  // 选择录制区域
  async selectRecordingArea(): Promise<RecordingArea> {
    try {
      return new Promise((resolve, reject) => {
        try {
          // 获取屏幕尺寸 - 使用绝对屏幕坐标系统
          const display = screen.getPrimaryDisplay()
          const { width, height, x: screenX, y: screenY } = display.bounds

          console.log('创建区域选择窗口 - 绝对屏幕坐标:', display.bounds)

          // 创建全屏透明选择窗口
          const selectionWindow = new BrowserWindow({
            width,
            height,
            x: screenX,
            y: screenY,
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

          // 加载区域选择界面HTML
          const selectionHtml = createRecordingAreaSelectionHTML()
          selectionWindow.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(selectionHtml))

          // 监听选择结果
          const handleAreaSelected = async (_, area: RecordingArea): Promise<void> => {
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

              console.log('=== 录制区域坐标调试 (绝对坐标转换) ===')
              console.log('选择窗口位置:', windowBounds)
              console.log('原始相对坐标:', area)
              console.log('转换后绝对坐标:', absoluteArea)

              resolve(absoluteArea)
            } catch (error) {
              reject(error)
            }
          }

          const handleSelectionCancelled = (): void => {
            selectionWindow.close()
            reject(new Error('用户取消了区域选择'))
          }

          // 注册事件监听器
          ipcMain.once('recording-area-selected', handleAreaSelected)
          ipcMain.once('recording-area-selection-cancelled', handleSelectionCancelled)

          // 窗口关闭时清理
          selectionWindow.on('closed', () => {
            ipcMain.removeListener('recording-area-selected', handleAreaSelected)
            ipcMain.removeListener('recording-area-selection-cancelled', handleSelectionCancelled)
          })
        } catch (error) {
          reject(error)
        }
      })
    } catch (error) {
      console.error('区域选择失败:', error)
      throw error
    }
  }

  // 处理来自录制状态窗口的停止录制请求
  async handleStopRecordingFromStatus(): Promise<void> {
    if (!this.isRecording) {
      console.log('当前没有进行录制')
      return
    }

    console.log('停止屏幕录制')

    // 先隐藏边框，避免被录制进去
    this.hideRecordingBorder()

    // 通知所有窗口开始loading状态
    BrowserWindow.getAllWindows().forEach(win => {
      win.webContents.send('recording-stop-loading-start')
    })

    // 停止录制
    await this.stopRecording()

    // 通知所有窗口停止loading状态
    BrowserWindow.getAllWindows().forEach(win => {
      win.webContents.send('recording-stop-loading-end')
    })

    // 在发送给前端之前先压缩视频
    if (this.recordingData && this.recordingData.length > 0) {
      try {
        // 检查是否为示例数据，跳过压缩
        const isExampleData = this.recordingData.toString().includes('Mock video data')

        if (!isExampleData) {
          console.log('开始压缩录制视频...')

          // 通知所有窗口开始压缩状态
          BrowserWindow.getAllWindows().forEach(win => {
            win.webContents.send('recording-compress-start')
          })

          // 获取最佳压缩设置
          const compressOptions = getOptimalCompressOptions(this.recordingData.length)

          // 压缩视频
          const compressResult = await compressVideo(this.recordingData, compressOptions)

          // 通知所有窗口压缩结束
          BrowserWindow.getAllWindows().forEach(win => {
            win.webContents.send('recording-compress-end')
          })

          if (compressResult.success && compressResult.compressedBuffer) {
            const originalSizeMB = (this.recordingData.length / 1024 / 1024).toFixed(2)
            const compressedSizeMB = (compressResult.compressedBuffer.length / 1024 / 1024).toFixed(2)

            if (compressResult.error && compressResult.error.includes('FFmpeg not available')) {
              console.log(`FFmpeg 不可用，跳过压缩，保持原始大小: ${originalSizeMB}MB`)
            } else {
              console.log(`视频压缩成功，大小从 ${originalSizeMB}MB 减少到 ${compressedSizeMB}MB`)
            }

            this.recordingData = compressResult.compressedBuffer
          } else {
            console.warn('视频压缩失败，使用原始录制数据:', compressResult.error)
          }
        } else {
          console.log('跳过示例数据的压缩')
        }
      } catch (compressionError) {
        console.error('压缩过程出错，使用原始录制数据:', compressionError)
        // 压缩出错时也要通知压缩结束
        BrowserWindow.getAllWindows().forEach(win => {
          win.webContents.send('recording-compress-end')
        })
      }
    }

    // 通知前端录制完成，由前端根据设置决定是否保存
    if (this.recordingData) {
      // 只通知主窗口录制完成，避免多个窗口重复保存文件
      const mainWindow = windowManager.getMainWindow()
      const mainWin = mainWindow || BrowserWindow.getAllWindows()[0]
      if (mainWin) {
        mainWin.webContents.send('recording-completed', {
          success: true,
          data: this.recordingData
        })
      }
    } else {
      // 录制失败，通知所有窗口
      BrowserWindow.getAllWindows().forEach(win => {
        win.webContents.send('recording-completed', {
          success: false,
          error: '录制数据为空'
        })
      })
    }
  }

  // 处理来自录制状态窗口的取消录制请求
  async handleCancelRecordingFromStatus(webContents: Electron.WebContents): Promise<void> {
    if (!this.isRecording) {
      console.log('当前没有进行录制')
      return
    }

    // 通知所有窗口开始loading状态
    BrowserWindow.getAllWindows().forEach(win => {
      win.webContents.send('recording-cancel-loading-start')
    })

    // 取消录制
    await this.cancelRecording()

    // 通知所有窗口取消loading状态
    BrowserWindow.getAllWindows().forEach(win => {
      win.webContents.send('recording-cancel-loading-end')
    })

    // 只向发起者窗口发送取消完成事件（避免重复消息）
    const senderWindow = BrowserWindow.fromWebContents(webContents)
    if (senderWindow) {
      senderWindow.webContents.send('recording-completed', {
        success: false,
        error: '用户取消录制'
      })
    }
  }

  // 清理录制数据
  clearRecordingData(): void {
    this.recordingData = null
    console.log('录制数据已清理')
  }
}

export const recordingManager = new RecordingManager()
