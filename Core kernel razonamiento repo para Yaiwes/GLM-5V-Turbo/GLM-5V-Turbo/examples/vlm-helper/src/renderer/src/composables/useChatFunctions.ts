import { nextTick, onUnmounted } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import { modelAPI } from '../utils/modelAPI'
import { useChatStore, type ChatMessage } from '../stores/chatStore'
import { useSettingsStore } from '../stores/settingsStore'
import { useTextProcessing } from './useTextProcessing'
import { useFileProcessing } from './useFileProcessing'
import { useScreenshot } from './useScreenshot'
import { useRecording } from './useRecording'
import { getUserFriendlyErrorMessage } from '../utils/errorHandler'
import { generateMessageDescription, type MediaData } from '../utils/mediaUtils'

export function useChatFunctions(onRecordingCompleted?: (videoData: string, videoBase64: string) => void): ReturnType<typeof useTextProcessing> &
  ReturnType<typeof useFileProcessing> &
  ReturnType<typeof useScreenshot> &
  ReturnType<typeof useRecording> & {
    chatStore: ReturnType<typeof useChatStore>
    sendMessage: (inputMessage: string, imageData: string | null, videoData: string | null, videoBase64: string | null, pdfImages: string[] | null, pdfName: string | null, pptImages: string[] | null, pptName: string | null, pptTotalPages: number | null, clearInputs: () => void, scrollToBottom: () => void) => Promise<void>
    handleKeyDown: (e: KeyboardEvent, sendMessageCallback: () => Promise<void>) => Promise<void>
    handleMessageClick: (message: ChatMessage) => void
    confirmClearMessages: (onClearCallback?: () => void) => void
    cleanup: () => void
    cancelCurrentRequest: () => void
  } {
  const chatStore = useChatStore()
  const settingsStore = useSettingsStore()
  const dialog = useDialog()
  const message = useMessage()

  // 获取当前 API 设置的辅助函数
  const getAPISettings = () => ({
    apiUrl: settingsStore.settings.apiUrl,
    apiKey: settingsStore.settings.apiKey,
    model: settingsStore.settings.model,
    maxTokens: settingsStore.settings.maxTokens,
    temperature: settingsStore.settings.temperature,
    topP: settingsStore.settings.topP,
    topK: settingsStore.settings.topK,
    repetitionPenalty: settingsStore.settings.repetitionPenalty,
    skipSpecialTokens: settingsStore.settings.skipSpecialTokens,
    stopTokenIds: settingsStore.settings.stopTokenIds,
    includeStopStrInOutput: settingsStore.settings.includeStopStrInOutput,
    endpoint: settingsStore.settings.endpoint,
    zhipuMaasMode: settingsStore.settings.zhipuMaasMode,
    systemPrompt: settingsStore.settings.systemPrompt
  })

  // 使用各个专门的组合函数
  const textProcessing = useTextProcessing()
  const fileProcessing = useFileProcessing()
  const screenshot = useScreenshot()
  const recording = useRecording(onRecordingCompleted)

  // 请求控制器
  let currentRequestController: AbortController | null = null

  // 监听全局取消请求事件
  const handleCancelRequest = (): void => {
    cancelCurrentRequest()
  }
  window.addEventListener('cancel-current-request', handleCancelRequest)

  // 键盘事件处理
  const handleKeyDown = async (e: KeyboardEvent, sendMessageCallback: () => Promise<void>): Promise<void> => {
    // 检查是否正在使用输入法组合输入（如中文输入法）
    // 如果 isComposing 为 true，说明用户正在输入拼音或其他组合字符，此时按回车应该是确认输入而不是发送消息
    const compositionEvent = e as KeyboardEvent & { isComposing?: boolean }
    if (e.key === 'Enter' && !e.shiftKey && !compositionEvent.isComposing) {
      e.preventDefault()
      await sendMessageCallback()
    }
  }

  // 发送消息核心逻辑
  const sendMessage = async (inputMessage: string, imageData: string | null, videoData: string | null, videoBase64: string | null, pdfImages: string[] | null, pdfName: string | null, pptImages: string[] | null, pptName: string | null, pptTotalPages: number | null, clearInputs: () => void, scrollToBottom: () => void): Promise<void> => {
    // 安全地处理当前请求控制器
    if (currentRequestController) {
      currentRequestController.abort()
    }

    // 创建新的请求控制器
    currentRequestController = new AbortController()

    const messageContent = inputMessage.trim()
    const mediaData: MediaData = {
      image: imageData || undefined,
      video: videoData || undefined,
      videoBase64: videoBase64 || undefined,
      pdfImages: pdfImages || undefined,
      pdfName: pdfName || undefined,
      pptImages: pptImages || undefined,
      pptName: pptName || undefined,
      pptTotalPages: pptTotalPages || undefined
    }

    // 生成消息描述
    const messageDescription = generateMessageDescription(messageContent, mediaData)

    chatStore.addUserMessage(messageDescription, mediaData.image, mediaData.video, mediaData.videoBase64, mediaData.pdfImages, mediaData.pdfName, mediaData.pptImages, mediaData.pptName, mediaData.pptTotalPages)

    clearInputs()
    await nextTick()
    scrollToBottom()

    chatStore.setLoading(true)
    await nextTick()
    scrollToBottom()

    try {
      let response: string

      // 安全检查：确保控制器存在且未被取消
      if (!currentRequestController || currentRequestController.signal.aborted) {
        return
      }

      // 检查是否启用流式输出（使用新的设置 Store）
      const enableStreamResponse = settingsStore.enableStreamResponse

      console.log('发送消息，流式输出:', enableStreamResponse, '，智谱MaaS模式:', settingsStore.settings.zhipuMaasMode, '，多媒体内容:', !!videoBase64, !!pdfImages, !!pptImages, !!imageData)
      console.log('当前设置:', settingsStore.settings)

      if (enableStreamResponse) {
        if (!settingsStore.settings.apiKey) {
          message.warning('API Key 未设置，无法使用流式输出模式')
          throw new Error('API Key 未设置')
        }
        console.log('使用流式输出模式 - 支持多媒体内容')
        response = await handleStreamResponse(scrollToBottom)
      } else {
        console.log('使用非流式模式 - 支持多轮对话和多媒体内容')
        response = await handleNonStreamResponse(messageContent, mediaData)
      }

      // 再次检查请求是否被取消
      if (!currentRequestController || currentRequestController.signal.aborted) {
        return
      }

      // 非流式模式下添加助手消息
      if (!enableStreamResponse) {
        chatStore.addAssistantMessage(response)

        // 非流式模式完成后，保存当前对话到历史记录
        try {
          await chatStore.saveCurrentConversationWithResponse()
          console.log('非流式模式：对话已保存到历史记录')
        } catch (error) {
          console.error('非流式模式：保存对话到历史记录失败:', error)
        }
      }

      await nextTick()
      scrollToBottom()
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('请求被取消')
        return
      }

      console.error('API请求失败:', error)
      const errorMessage = getUserFriendlyErrorMessage(error)
      chatStore.addAssistantMessage(errorMessage)
      await nextTick()
      scrollToBottom()
    } finally {
      chatStore.setLoading(false)
      currentRequestController = null
    }
  }

  // 处理流式响应
  const handleStreamResponse = async (scrollToBottom: () => void): Promise<string> => {
    const historyTurns = settingsStore.settings.historyTurns
    const historyMessages = chatStore.getHistoryForAPI(historyTurns)

    // 添加一个空的助手消息用于流式更新
    const assistantMessageId = chatStore.addAssistantMessage('')

    // 构建请求内容
    const request = buildStreamRequest(historyMessages)

    let fullResponse = ''
    let thinkingContent = ''
    let responseContent = ''
    let firstChunkReceived = false

    // 优化：使用节流来减少更新频率，但不进行存储操作
    let lastUpdateTime = 0
    const updateThrottleMs = 16 // 约60fps的更新频率
    let pendingUpdate = false

    const updateMessage = (): void => {
      const now = Date.now()
      if (now - lastUpdateTime >= updateThrottleMs || !pendingUpdate) {
        // 重新组合完整响应：思考块 + 回复内容
        fullResponse = ''
        if (thinkingContent) {
          fullResponse += `<think>${thinkingContent}</think>`
        }
        fullResponse += responseContent

        // 只更新内容，不触发存储
        chatStore.updateAssistantMessageContent(assistantMessageId, fullResponse)
        lastUpdateTime = now
        pendingUpdate = false

        // 节流滚动操作
        nextTick(() => {
          try {
            scrollToBottom()
          } catch (error) {
            console.warn('滚动操作失败:', error)
          }
        })
      } else {
        pendingUpdate = true
      }
    }

    try {
      // modelAPI 返回的是原始内容，我们使用自己构建的 fullResponse
      await modelAPI.callModelStream(
        request,
        getAPISettings(),
        (chunk: string, type?: 'reasoning' | 'content') => {
          // 检查请求是否已被取消
          if (!currentRequestController || currentRequestController.signal.aborted) {
            return
          }

          // 收到第一个chunk时，立即停止加载状态
          if (!firstChunkReceived) {
            firstChunkReceived = true
            chatStore.setLoading(false)
          }

          try {
            // 根据内容类型处理不同的显示方式
            if (type === 'reasoning') {
              thinkingContent += chunk
            } else {
              responseContent += chunk
            }

            // updateMessage() 会重新构建 fullResponse
            updateMessage()
          } catch (error) {
            console.warn('处理流式数据块失败:', error, 'chunk:', chunk)
            // 继续处理，不中断流式输出
          }
        },
        currentRequestController?.signal || new AbortController().signal
      )

      // 确保最后一次更新被应用
      if (pendingUpdate) {
        updateMessage()
      }

      // 确保最终的完整响应被正确保存到消息中
      chatStore.updateAssistantMessageContent(assistantMessageId, fullResponse)

      // 流式输出完成后，进行一次性存储保存
      console.log('流式输出完成，保存到存储，最终内容长度:', fullResponse.length)
      chatStore.saveToStorage()

      // 保存当前对话到历史记录
      try {
        await chatStore.saveCurrentConversationWithResponse()
        console.log('对话已保存到历史记录')
      } catch (error) {
        console.error('保存对话到历史记录失败:', error)
      }

      // 同步更新到其他窗口
      try {
        const syncData = {
          type: 'update',
          messageId: assistantMessageId,
          content: fullResponse,
          timestamp: Date.now()
        }

        const syncString = JSON.stringify(syncData)

        // 检查数据大小，如果太大就截断内容
        if (syncString.length > 1000000) {
          // 1MB限制
          const truncatedData = {
            ...syncData,
            content: fullResponse.substring(0, 50000) + '\n\n[内容过长，已截断...]',
            truncated: true
          }
          localStorage.setItem('vlm-chat-last-message', JSON.stringify(truncatedData))
        } else {
          localStorage.setItem('vlm-chat-last-message', syncString)
        }
      } catch (storageError) {
        console.warn('无法同步助手回复到其他窗口:', storageError)
        // 即使无法同步，也不应该影响主要功能
      }
    } catch (error) {
      console.error('流式输出失败:', error)
      throw error
    }

    return fullResponse
  }

  // 处理非流式响应
  const handleNonStreamResponse = async (messageContent: string, mediaData: MediaData): Promise<string> => {
    const historyTurns = settingsStore.settings.historyTurns
    const historyMessages = chatStore.getHistoryForAPI(historyTurns)

    if (historyMessages.length > 0) {
      // 使用带历史上下文的多媒体对话API
      return await modelAPI.chatCompletionWithHistory(historyMessages, getAPISettings(), currentRequestController!.signal)
    } else {
      // 根据内容类型选择合适的API
      return await callAppropriateAPI(messageContent, mediaData)
    }
  }

  // 构建流式请求
  const buildStreamRequest = (
    historyMessages: Array<{ role: string; content: string; image?: string; video?: string; pdfImages?: string[]; pptImages?: string[] }>
  ): {
    messages: Array<{
      role: 'user' | 'assistant' | 'system'
      content: Array<{
        type: 'text' | 'image_url' | 'video_url'
        text?: string
        image_url?: { url: string }
        video_url?: { url: string }
      }>
    }>
  } => {
    const messages: Array<{
      role: 'user' | 'assistant' | 'system'
      content: Array<{
        type: 'text' | 'image_url' | 'video_url'
        text?: string
        image_url?: { url: string }
        video_url?: { url: string }
      }>
    }> = []

    // 添加系统提示词（如果有的话）
    const systemPrompt = settingsStore.settings.systemPrompt
    if (systemPrompt.trim()) {
      messages.push({
        role: 'system',
        content: [{ type: 'text', text: systemPrompt }]
      })
    }

    if (historyMessages.length > 0) {
      // 添加历史消息
      messages.push(
        ...historyMessages.map(msg => ({
          role: msg.role as 'user' | 'assistant' | 'system',
          content: buildMessageContent(msg.content, msg.image, msg.video, msg.pdfImages, msg.pptImages)
        }))
      )
    }
    return { messages }
  }

  // 构建消息内容（支持多媒体）
  const buildMessageContent = (
    text: string,
    image?: string,
    video?: string,
    pdfImages?: string[],
    pptImages?: string[]
  ): Array<{
    type: 'text' | 'image_url' | 'video_url'
    text?: string
    image_url?: { url: string }
    video_url?: { url: string }
  }> => {
    const content: Array<{
      type: 'text' | 'image_url' | 'video_url'
      text?: string
      image_url?: { url: string }
      video_url?: { url: string }
    }> = []

    if (text) {
      content.push({ type: 'text', text })
    }

    if (image) {
      content.push({ type: 'image_url', image_url: { url: image.split(',')[1] } })
    }

    if (video) {
      content.push({ type: 'video_url', video_url: { url: video.split(',')[1] } })
    }

    pdfImages?.forEach(img => {
      content.push({ type: 'image_url', image_url: { url: img.split(',')[1] } })
    })

    pptImages?.forEach(img => {
      content.push({ type: 'image_url', image_url: { url: img.split(',')[1] } })
    })

    return content.length > 0 ? content : [{ type: 'text' as const, text: text || '请分析这个内容' }]
  }

  // 调用合适的API
  const callAppropriateAPI = async (messageContent: string, mediaData: MediaData): Promise<string> => {
    if (mediaData.videoBase64) {
      console.log('准备分析视频，数据长度:', mediaData.videoBase64.length)
      return await modelAPI.analyzeVideo(mediaData.videoBase64, messageContent || '分析这个视频', getAPISettings(), currentRequestController!.signal)
    } else if (mediaData.pdfImages && mediaData.pdfImages.length > 0) {
      return await modelAPI.analyzeImages(mediaData.pdfImages, messageContent || '分析这个PDF文档', getAPISettings(), currentRequestController!.signal)
    } else if (mediaData.pptImages && mediaData.pptImages.length > 0) {
      return await modelAPI.analyzeImages(mediaData.pptImages, messageContent || '分析这个PPT演示文稿', getAPISettings(), currentRequestController!.signal)
    } else if (mediaData.image) {
      return await modelAPI.analyzeImage(mediaData.image, messageContent || '分析这张图片', getAPISettings(), currentRequestController!.signal)
    } else {
      return await modelAPI.chatCompletion(messageContent, getAPISettings(), currentRequestController!.signal)
    }
  }

  // 消息点击处理
  const handleMessageClick = (message: ChatMessage): void => {
    if (message.role === 'assistant') {
      if (window.api?.switchToMain) {
        window.api.switchToMain()
      }

      setTimeout(() => {
        chatStore.switchToMessageAndScroll(message.id)
      }, 100)
    }
  }

  // 清空消息确认
  const confirmClearMessages = (onClearCallback?: () => void): void => {
    const isFloatingWindow = window.innerWidth < 500 || window.innerHeight < 600 || (window as unknown as { isFloatingWindow?: boolean }).isFloatingWindow

    dialog.warning({
      title: isFloatingWindow ? '清空记录' : '清空聊天记录',
      content: isFloatingWindow ? '确定清空所有记录吗？' : '确定要清空所有聊天记录吗？此操作不可撤销。',
      positiveText: '确认',
      negativeText: '取消',
      style: isFloatingWindow ? { width: '280px', fontSize: '13px' } : undefined,
      onPositiveClick: () => {
        if (onClearCallback && typeof onClearCallback === 'function') {
          onClearCallback()
        }

        chatStore.clearMessages()

        setTimeout(() => {
          chatStore.addWelcomeMessageIfNeeded()
        }, 10)

        message.success('聊天记录已清空')
      }
    })
  }

  // 取消当前请求
  const cancelCurrentRequest = (): void => {
    if (currentRequestController) {
      console.log('取消当前AI请求')
      currentRequestController.abort()
      currentRequestController = null
      chatStore.setLoading(false)
    }
  }

  // 清理函数
  const cleanup = (): void => {
    if (currentRequestController) {
      currentRequestController.abort()
      currentRequestController = null
    }

    window.removeEventListener('cancel-current-request', handleCancelRequest)
    recording.cleanup()
  }

  // 组件卸载时清理
  onUnmounted(() => {
    cleanup()
  })

  return {
    // 状态
    chatStore,
    ...textProcessing,

    // 文件处理相关
    ...fileProcessing,

    // 截图相关
    ...screenshot,

    // 录制相关
    ...recording,

    // 消息相关
    sendMessage,
    handleKeyDown,
    handleMessageClick,
    confirmClearMessages,

    // 清理
    cleanup,
    cancelCurrentRequest
  }
}
