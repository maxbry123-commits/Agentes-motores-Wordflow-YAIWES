/**
 * 录制功能组合函数
 */
import { ref, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useSettingsStore } from '../stores/settingsStore'
import { bufferToVideoDataUrl } from '../utils/mediaUtils'

interface RecordingResult {
  success: boolean
  filePath?: string
  fileName?: string
  data?: Buffer
  error?: string
}

export function useRecording(onRecordingCompleted?: (videoData: string, videoBase64: string) => void): {
  isRecording: ReturnType<typeof ref<boolean>>
  recordingType: ReturnType<typeof ref<'screen' | 'area' | null>>
  recordingDuration: ReturnType<typeof ref<string>>
  isCompressing: ReturnType<typeof ref<boolean>>
  startScreenRecording: () => Promise<boolean>
  stopScreenRecording: () => Promise<boolean>
  startAreaScreenRecording: () => Promise<boolean>
  toggleScreenRecording: () => void
  toggleAreaScreenRecording: () => void
  saveRecordingToFile: () => Promise<boolean>
  cleanup: () => void
} {
  const message = useMessage()
  const settingsStore = useSettingsStore()

  // 录制状态
  const isRecording = ref(false)
  const recordingType = ref<'screen' | 'area' | null>(null)
  const recordingStartTime = ref<Date | null>(null)
  const recordingDuration = ref<string>('00:00')
  const isCompressing = ref(false) // 新增：压缩状态
  let recordingData: Buffer | null = null
  let recordingTimer: NodeJS.Timeout | null = null

  // 记录监听器引用，避免重复注册
  let recordingStateChangeListener: ((recording: boolean) => void) | null = null
  let recordingCompletedListener: ((result: RecordingResult) => void) | null = null

  // 更新录制持续时间
  const updateRecordingDuration = (): void => {
    if (recordingStartTime.value) {
      const now = new Date()
      const diff = now.getTime() - recordingStartTime.value.getTime()
      const seconds = Math.floor(diff / 1000)
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      recordingDuration.value = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
    }
  }

  // 开始录制计时器
  const startRecordingTimer = (): void => {
    recordingStartTime.value = new Date()
    recordingDuration.value = '00:00'
    recordingTimer = setInterval(updateRecordingDuration, 1000)
  }

  // 停止录制计时器
  const stopRecordingTimer = (): void => {
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
    recordingStartTime.value = null
  }

  // 设置录制状态变化监听器（只注册一次）
  if (window.api?.onRecordingStateChange && !recordingStateChangeListener) {
    recordingStateChangeListener = (recording: boolean) => {
      console.log('录制状态变化:', recording)
      isRecording.value = recording
      if (!recording) {
        recordingType.value = null
        stopRecordingTimer() // 录制停止时停止计时
      }
    }
    window.api.onRecordingStateChange(recordingStateChangeListener)
  }

  // 设置压缩状态监听器
  const apiWithCompress = window.api as typeof window.api & {
    onRecordingCompressStart?: (callback: () => void) => void
    onRecordingCompressEnd?: (callback: () => void) => void
  }

  if (apiWithCompress?.onRecordingCompressStart) {
    apiWithCompress.onRecordingCompressStart(() => {
      console.log('开始压缩视频')
      isCompressing.value = true
      message.info('正在压缩视频，请稍候...', { duration: 0, closable: true })
    })
  }

  if (apiWithCompress?.onRecordingCompressEnd) {
    apiWithCompress.onRecordingCompressEnd(() => {
      console.log('视频压缩完成')
      isCompressing.value = false
      message.destroyAll() // 关闭所有压缩提示消息
    })
  }

  // 设置录制完成监听器（只注册一次）
  if (window.api && 'onRecordingCompleted' in window.api && onRecordingCompleted && !recordingCompletedListener) {
    recordingCompletedListener = async (result: RecordingResult) => {
      console.log('录制完成事件:', result)

      if (result.success && result.data) {
        // 检查是否需要自动保存到本地
        try {
          const shouldSaveLocally = settingsStore.settings.saveRecordingLocally || false

          // 智能选择保存窗口：优先使用主窗口，如果没有主窗口则使用当前窗口
          const isMainWindow = !window.location.hash.includes('floating')

          // 使用更可靠的互斥锁机制
          const saveKey = 'vlm-recording-save-lock'
          const currentTime = Date.now()

          // 如果启用了本地保存，使用智能保存策略
          if (shouldSaveLocally && window.api?.saveRecordingToFile) {
            let shouldSave = false

            // 尝试获取保存锁
            const existingLock = localStorage.getItem(saveKey)
            const lockTimeout = 10000 // 10秒超时

            if (!existingLock || currentTime - parseInt(existingLock) > lockTimeout) {
              // 没有锁或锁已过期，尝试获取锁
              localStorage.setItem(saveKey, currentTime.toString())

              // 短暂延迟后再次检查，确保没有竞争条件
              await new Promise(resolve => setTimeout(resolve, 50))
              const recheckLock = localStorage.getItem(saveKey)

              if (recheckLock === currentTime.toString()) {
                // 成功获取锁
                shouldSave = true
                console.log(`${isMainWindow ? '主窗口' : '悬浮窗口'}获取保存锁成功，执行自动保存录制文件`)
              } else {
                console.log(`${isMainWindow ? '主窗口' : '悬浮窗口'}获取保存锁失败，其他窗口正在处理`)
              }
            } else {
              console.log(`${isMainWindow ? '主窗口' : '悬浮窗口'}跳过自动保存，保存锁被占用`)
            }

            if (shouldSave) {
              try {
                const saveResult = await window.api.saveRecordingToFile(result.data)
                if (saveResult.success) {
                  message.success(`${saveResult.message}`, { duration: 3000 })
                } else {
                  message.error(`保存失败: ${saveResult.message}`, { duration: 3000 })
                }
              } finally {
                // 释放保存锁
                const currentLock = localStorage.getItem(saveKey)
                if (currentLock === currentTime.toString()) {
                  localStorage.removeItem(saveKey)
                  console.log('保存锁已释放')
                }
              }
            }
          }
        } catch (error) {
          console.error('处理录屏保存设置失败:', error)
        }

        // 统一使用 MP4 格式以确保更好的兼容性
        const videoMimeType = 'video/mp4'

        // 验证录制数据有效性
        if (!result.data || result.data.byteLength === 0) {
          console.error('录制数据为空或无效')
          message.error('录制数据无效，请重试')
          return
        }

        console.log('录制完成，数据大小:', result.data.byteLength, 'bytes, 统一格式为:', videoMimeType)

        // 显示录制完成和压缩信息
        const sizeMB = (result.data.byteLength / 1024 / 1024).toFixed(2)
        if (result.data.byteLength > 1024 * 1024) {
          // 大于1MB
          console.log(`录制视频已自动压缩处理，当前大小: ${sizeMB}MB`)
        }

        const videoBase64 = bufferToVideoDataUrl(result.data, videoMimeType)

        console.log('视频处理完成，Base64 大小:', videoBase64.length, 'chars')

        // 调用回调函数
        onRecordingCompleted(videoBase64, videoBase64)
      } else if (!result.success && result.error && !result.error.includes('取消')) {
        // 只在非取消情况下显示错误消息，避免重复显示取消消息
        console.log('录制未成功完成:', result.error || '未知错误')
        message.error(result.error || '录制失败')
      }
      // 对于取消情况，不显示任何消息，让用户知道是正常取消
    }

    if (recordingCompletedListener) {
      ;(window.api as unknown as { onRecordingCompleted: (callback: (result: RecordingResult) => void) => void }).onRecordingCompleted(recordingCompletedListener)
    }
  }

  // 屏幕录制相关函数
  const startScreenRecording = async (): Promise<boolean> => {
    try {
      if (!window.api?.startScreenRecording) {
        message.error('录制功能不可用')
        return false
      }

      const success = await window.api.startScreenRecording()
      if (success) {
        isRecording.value = true
        recordingType.value = 'screen'
        startRecordingTimer() // 开始计时

        // 显示录制状态窗口
        if (window.api && 'showRecordingStatus' in window.api) {
          await (window.api as { showRecordingStatus: (type: 'screen' | 'area') => Promise<void> }).showRecordingStatus('screen')
        }

        message.success('开始录制屏幕')
      } else {
        message.error('录制启动失败')
      }
      return success
    } catch (error) {
      console.error('开始录制失败:', error)
      message.error('录制启动失败')
      return false
    }
  }

  const stopScreenRecording = async (): Promise<boolean> => {
    try {
      // 先检查是否正在录制
      if (!isRecording.value) {
        console.log('当前没有进行录制，无需停止')
        return false
      }

      if (!window.api?.stopScreenRecording) {
        message.error('录制功能不可用')
        return false
      }

      const data = await window.api.stopScreenRecording()
      if (data) {
        recordingData = data
        stopRecordingTimer() // 停止计时

        // 隐藏录制状态窗口
        if (window.api && 'hideRecordingStatus' in window.api) {
          await (window.api as { hideRecordingStatus: () => Promise<void> }).hideRecordingStatus()
        }

        return true
      } else {
        // 如果返回null，可能是因为没有正在进行的录制
        console.log('停止录制返回null，可能录制已被取消或未在进行中')
        // 确保状态正确重置
        isRecording.value = false
        recordingType.value = null
        stopRecordingTimer()
        return false
      }
    } catch (error) {
      console.error('停止录制失败:', error)
      // 确保状态正确重置
      isRecording.value = false
      recordingType.value = null
      stopRecordingTimer()

      // 只有在真正的错误情况下才显示错误消息
      if (error instanceof Error && !error.message.includes('当前没有进行录制')) {
        message.error('录制停止失败')
      }
      return false
    }
  }

  const saveRecordingToFile = async (): Promise<boolean> => {
    try {
      if (!recordingData) {
        message.error('没有录制数据')
        return false
      }

      const result = await window.api?.saveRecordingToFile(recordingData)
      if (result?.success) {
        message.success(result.message)
        recordingData = null // 保存成功后清理本地数据
        return true
      } else {
        message.error(result?.message || '保存文件失败')
        return false
      }
    } catch (error) {
      console.error('保存文件失败:', error)
      message.error('保存文件失败')
      return false
    }
  }

  // 区域录屏功能
  const startAreaScreenRecording = async (): Promise<boolean> => {
    try {
      if (!(window.api as typeof window.api & { hideAppWindows?: () => Promise<boolean> })?.hideAppWindows || !window.api?.selectRecordingArea || !window.api?.startAreaScreenRecording) {
        message.error('区域录制功能不可用')
        return false
      }

      // 点击按钮的那一刻立即隐藏应用窗口
      await (window.api as typeof window.api & { hideAppWindows: () => Promise<boolean> }).hideAppWindows()
      // 然后选择录制区域
      const area = await window.api.selectRecordingArea()
      if (!area || area.width < 20 || area.height < 20) {
        message.warning('录制区域太小，请选择更大的区域')
        return false
      }

      // 开始区域录制
      const success = await window.api.startAreaScreenRecording(area)
      if (success) {
        isRecording.value = true
        recordingType.value = 'area'
        startRecordingTimer() // 开始计时

        // 显示录制状态窗口
        if (window.api && 'showRecordingStatus' in window.api) {
          await (window.api as { showRecordingStatus: (type: 'screen' | 'area') => Promise<void> }).showRecordingStatus('area')
        }

        message.success('区域录制已开始', { duration: 1000 })
      } else {
        message.error('区域录制启动失败')
      }
      return success
    } catch (error) {
      console.error('开始区域录制失败:', error)

      if (error instanceof Error && error.message.includes('取消')) {
        message.info('已取消区域选择')
      } else {
        message.error('区域录制启动失败')
      }
      return false
    }
  }

  // 切换屏幕录制
  const toggleScreenRecording = (): void => {
    if (isRecording.value && recordingType.value === 'screen') {
      stopScreenRecording()
    } else {
      startScreenRecording()
    }
  }

  // 切换区域录制
  const toggleAreaScreenRecording = (): void => {
    if (isRecording.value && recordingType.value === 'area') {
      stopScreenRecording() // 区域录制也使用stopScreenRecording
    } else {
      startAreaScreenRecording()
    }
  }

  // 清理函数
  const cleanup = (): void => {
    // 清理录制计时器
    stopRecordingTimer()

    // 清理录制状态监听
    if (window.api?.offRecordingStateChange && recordingStateChangeListener) {
      window.api.offRecordingStateChange(recordingStateChangeListener)
      recordingStateChangeListener = null
    }

    // 清理录制完成监听
    if (window.api && 'offRecordingCompleted' in window.api && recordingCompletedListener) {
      ;(window.api as { offRecordingCompleted: (callback: (result: RecordingResult) => void) => void }).offRecordingCompleted(recordingCompletedListener)
      recordingCompletedListener = null
    }
  }

  // 组件卸载时清理
  onUnmounted(() => {
    cleanup()
  })

  return {
    isRecording,
    recordingType,
    recordingDuration,
    isCompressing,
    startScreenRecording,
    stopScreenRecording,
    startAreaScreenRecording,
    toggleScreenRecording,
    toggleAreaScreenRecording,
    saveRecordingToFile,
    cleanup
  }
}
