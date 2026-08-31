import { defineStore } from 'pinia'
import { ref } from 'vue'

// 生成唯一ID的函数
function generateMessageId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 消息类型定义
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  image?: string
  video?: string
  videoBase64?: string
  pdfImages?: string[]
  pdfName?: string
  pptImages?: string[]
  pptName?: string
  pptTotalPages?: number
  timestamp?: number
}

// 待发送媒体类型定义
export interface PendingMedia {
  image?: string
  video?: string
  videoBase64?: string
  pdfImages?: string[]
  pdfName?: string
  pptImages?: string[]
  pptName?: string
  pptTotalPages?: number
}

// 对话历史类型定义
export interface ConversationHistory {
  id: string
  title: string
  messages: ChatMessage[]
  timestamp: number
}

// Store ID 常量，确保所有窗口使用相同的 Store ID
const STORE_ID = 'chat'

// 本地存储键名常量
const KEYS = {
  MESSAGES: 'vlm-chat-messages',
  LOADING: 'vlm-chat-loading',
  WELCOME: 'vlm-chat-welcome-added',
  LAST_MESSAGE: 'vlm-chat-last-message',
  PENDING_MEDIA: 'vlm-chat-pending-media'
}

export const useChatStore = defineStore(STORE_ID, () => {
  // 共享的消息列表
  const messages = ref<ChatMessage[]>([])

  // 正在加载状态
  const isLoading = ref(false)

  // 欢迎消息已添加标志
  const welcomeAdded = ref(false)

  // 当前对话是否已保存标志
  const currentConversationSaved = ref(false)

  // 当前对话ID（用于更新已存在的对话）
  const currentConversationId = ref<string | null>(null)

  // 待发送的媒体状态（在窗口间同步）
  const pendingMedia = ref<PendingMedia>({})

  // 初始化时检查本地存储
  const initFromStorage = (): void => {
    try {
      const storedMessages = localStorage.getItem(KEYS.MESSAGES)
      if (storedMessages) {
        messages.value = JSON.parse(storedMessages)
      }

      // 确保加载状态的一致性
      const storedLoading = localStorage.getItem(KEYS.LOADING)
      if (storedLoading) {
        isLoading.value = JSON.parse(storedLoading)
      } else {
        // 如果没有存储的加载状态，确保默认为false
        isLoading.value = false
        localStorage.setItem(KEYS.LOADING, JSON.stringify(false))
      }

      const storedWelcomeAdded = localStorage.getItem(KEYS.WELCOME)
      if (storedWelcomeAdded) {
        welcomeAdded.value = JSON.parse(storedWelcomeAdded)
      }

      const storedPendingMedia = localStorage.getItem(KEYS.PENDING_MEDIA)
      if (storedPendingMedia) {
        pendingMedia.value = JSON.parse(storedPendingMedia)
      }
    } catch (error) {
      console.error('Error loading chat data from storage:', error)
      // 发生错误时重置为安全状态
      isLoading.value = false
      localStorage.setItem(KEYS.LOADING, JSON.stringify(false))
    }
  }

  // 添加用户消息
  function addUserMessage(content: string, image?: string, video?: string, videoBase64?: string, pdfImages?: string[], pdfName?: string, pptImages?: string[], pptName?: string, pptTotalPages?: number): void {
    const message = {
      id: generateMessageId(),
      role: 'user' as const,
      content: content || (video ? '发送了一个视频' : image ? '发送了一张图片' : pdfImages?.length ? `发送了PDF: ${pdfName || 'document.pdf'} (${pdfImages.length}页)` : pptImages?.length ? `发送了PPT: ${pptName || 'presentation.ppt'} (${pptTotalPages || pptImages.length}页)` : ''),
      image,
      video,
      videoBase64,
      pdfImages,
      pdfName,
      pptImages,
      pptName,
      pptTotalPages,
      timestamp: Date.now()
    }

    messages.value.push(message)

    // 消息发送后清空待发送媒体
    clearPendingMedia()

    // 保存到本地存储以便跨窗口同步
    saveToStorage()

    // 如果当前有对话ID，说明是在已存在的对话中添加消息，需要重置保存标志
    if (currentConversationId.value) {
      currentConversationSaved.value = false
    }

    // 通过localStorage同步消息到其他窗口（排除过大的数据）
    try {
      // 创建一个不包含大数据的简化版本用于跨窗口同步
      const syncMessage = {
        type: 'user',
        message: {
          ...message,
          // 排除可能很大的base64数据
          videoBase64: message.videoBase64 ? '[视频数据已省略]' : undefined,
          image: message.image && message.image.length > 100000 ? '[图片数据已省略]' : message.image,
          pdfImages: message.pdfImages && message.pdfImages.some(img => img.length > 50000) ? ['[PDF图片数据已省略]'] : message.pdfImages,
          pptImages: message.pptImages && message.pptImages.some(img => img.length > 50000) ? ['[PPT图片数据已省略]'] : message.pptImages
        },
        timestamp: Date.now()
      }

      const syncData = JSON.stringify(syncMessage)

      // 检查数据大小，如果仍然太大就进一步简化
      if (syncData.length > 1000000) {
        // 1MB限制
        const simplifiedMessage = {
          type: 'user',
          message: {
            id: message.id,
            role: message.role,
            content: message.content,
            timestamp: message.timestamp,
            // 只保留基本信息，不包含任何媒体数据
            hasMedia: !!(message.image || message.video || message.videoBase64 || message.pdfImages || message.pptImages)
          },
          timestamp: Date.now()
        }
        localStorage.setItem(KEYS.LAST_MESSAGE, JSON.stringify(simplifiedMessage))
      } else {
        localStorage.setItem(KEYS.LAST_MESSAGE, syncData)
      }
    } catch (error) {
      console.warn('无法同步消息到其他窗口（数据过大）:', error)
      // 如果存储失败，尝试存储一个最简化的版本
      try {
        const minimalMessage = {
          type: 'user',
          message: {
            id: message.id,
            content: message.content.substring(0, 100) + (message.content.length > 100 ? '...' : ''),
            timestamp: message.timestamp
          },
          timestamp: Date.now()
        }
        localStorage.setItem(KEYS.LAST_MESSAGE, JSON.stringify(minimalMessage))
      } catch (secondError) {
        console.error('完全无法存储消息同步数据:', secondError)
        // 即使无法同步，也不应该阻止应用继续运行
      }
    }
  }

  // 添加助手响应
  function addAssistantMessage(content: string): string {
    const message = {
      id: generateMessageId(),
      role: 'assistant' as const,
      content,
      timestamp: Date.now()
    }

    messages.value.push(message)

    // 保存到本地存储以便跨窗口同步
    saveToStorage()

    // 只有当消息内容不为空时才保存对话到历史记录（避免在流式输出开始时就保存空消息）
    if (content.trim().length > 0) {
      setTimeout(() => {
        saveCurrentConversationWithResponse()
      }, 100) // 短延迟确保消息已正确添加
    }

    // 通过localStorage同步消息到其他窗口
    localStorage.setItem(
      KEYS.LAST_MESSAGE,
      JSON.stringify({
        type: 'assistant',
        message,
        timestamp: Date.now()
      })
    )

    // 返回消息ID，用于流式更新
    return message.id
  }

  // 更新助手消息（用于流式输出）
  function updateAssistantMessage(messageId: string, content: string): void {
    const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      messages.value[messageIndex].content = content

      // 保存到本地存储
      saveToStorage()

      // 通过localStorage同步更新到其他窗口
      localStorage.setItem(
        KEYS.LAST_MESSAGE,
        JSON.stringify({
          type: 'update',
          messageId,
          content,
          timestamp: Date.now()
        })
      )
    }
  }

  // 仅更新助手消息内容
  function updateAssistantMessageContent(messageId: string, content: string): void {
    const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      messages.value[messageIndex].content = content
      // 不立即保存存储，由调用方控制何时保存
    }
  }

  // 删除消息（用于流式失败回退）
  function removeMessage(messageId: string): void {
    const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      messages.value.splice(messageIndex, 1)

      // 保存到本地存储
      saveToStorage()

      // 通过localStorage同步删除到其他窗口
      localStorage.setItem(
        KEYS.LAST_MESSAGE,
        JSON.stringify({
          type: 'remove',
          messageId,
          timestamp: Date.now()
        })
      )
    }
  }

  // 设置加载状态
  function setLoading(loading: boolean): void {
    isLoading.value = loading

    // 保存到本地存储（用于窗口间同步）
    localStorage.setItem(KEYS.LOADING, JSON.stringify(loading))
  }

  // 清空所有消息（实际上就是开始新对话）
  async function clearMessages(): Promise<void> {
    await startNewConversation()
  }

  // 添加欢迎消息
  function addWelcomeMessageIfNeeded(): void {
    if (!welcomeAdded.value && messages.value.length === 0) {
      messages.value.push({
        id: generateMessageId(),
        role: 'assistant',
        content: '你好！我是GLM-4.5V，可以帮你分析图片、视频和回答问题。你可以截图、上传图片/视频或直接输入文字与我对话。',
        timestamp: Date.now()
      })
      welcomeAdded.value = true

      // 保存到本地存储
      saveToStorage()
    }
  }

  // 保存消息到本地存储
  function saveToStorage(): void {
    try {
      // 检查消息数据的大小
      const messagesData = JSON.stringify(messages.value)

      // 如果数据过大，尝试保存一个简化版本
      if (messagesData.length > 4000000) {
        // 4MB限制
        console.warn('消息数据过大，正在保存简化版本...')

        // 创建简化版本：移除大的媒体数据
        const simplifiedMessages = messages.value.map(msg => ({
          ...msg,
          // 保留小图片，移除大图片和视频数据
          image: msg.image && msg.image.length > 100000 ? undefined : msg.image,
          video: undefined, // 移除所有视频链接
          videoBase64: undefined, // 移除所有视频base64数据
          pdfImages: msg.pdfImages && msg.pdfImages.some(img => img.length > 50000) ? undefined : msg.pdfImages,
          pptImages: msg.pptImages && msg.pptImages.some(img => img.length > 50000) ? undefined : msg.pptImages
        }))

        localStorage.setItem(KEYS.MESSAGES, JSON.stringify(simplifiedMessages))
      } else {
        localStorage.setItem(KEYS.MESSAGES, messagesData)
      }

      localStorage.setItem(KEYS.WELCOME, JSON.stringify(welcomeAdded.value))
    } catch (error) {
      console.error('保存聊天数据失败:', error)

      // 如果仍然失败，尝试保存一个最简版本（只保留文本）
      try {
        const textOnlyMessages = messages.value.map(msg => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp
        }))
        localStorage.setItem(KEYS.MESSAGES, JSON.stringify(textOnlyMessages))
        console.warn('已保存纯文本版本的聊天记录')
      } catch (secondError) {
        console.error('无法保存任何聊天数据:', secondError)
      }
    }
  }

  // 设置待发送的媒体
  function setPendingMedia(media: Partial<PendingMedia>): void {
    pendingMedia.value = { ...pendingMedia.value, ...media }

    // 保存到本地存储以便跨窗口同步
    localStorage.setItem(KEYS.PENDING_MEDIA, JSON.stringify(pendingMedia.value))
  }

  // 清空待发送的媒体
  function clearPendingMedia(): void {
    pendingMedia.value = {}
    localStorage.removeItem(KEYS.PENDING_MEDIA)
  }

  // 检查是否有待发送的媒体
  function hasPendingMedia(): boolean {
    return !!(pendingMedia.value.image || pendingMedia.value.video || (pendingMedia.value.pdfImages && pendingMedia.value.pdfImages.length > 0) || (pendingMedia.value.pptImages && pendingMedia.value.pptImages.length > 0))
  }

  // 接收来自其他窗口的消息
  function setupMessageListeners(): void {
    // 监听 localStorage 变化
    window.addEventListener('storage', event => {
      // 处理新消息同步
      if (event.key === KEYS.LAST_MESSAGE && event.newValue) {
        try {
          const data = JSON.parse(event.newValue)

          if (data.type === 'assistant' && data.message) {
            // 添加新的助手消息
            const exists = messages.value.some(msg => msg.timestamp === data.message.timestamp && msg.role === data.message.role && msg.content === data.message.content)

            if (!exists) {
              messages.value.push(data.message)
              saveToStorage()
            }
          } else if (data.type === 'update' && data.messageId && data.content !== undefined) {
            // 更新现有消息内容（流式输出）
            const messageIndex = messages.value.findIndex(msg => msg.id === data.messageId)
            if (messageIndex !== -1) {
              messages.value[messageIndex].content = data.content
              saveToStorage()
            }
          } else if (data.type === 'remove' && data.messageId) {
            // 删除消息（流式失败回退）
            const messageIndex = messages.value.findIndex(msg => msg.id === data.messageId)
            if (messageIndex !== -1) {
              messages.value.splice(messageIndex, 1)
              saveToStorage()
            }
          } else if (data && data.message) {
            // 兼容旧格式
            const exists = messages.value.some(msg => msg.timestamp === data.message.timestamp && msg.role === data.message.role && msg.content === data.message.content)

            if (!exists) {
              messages.value.push(data.message)
              saveToStorage()
            }
          }
        } catch (error) {
          console.error('Error processing message:', error)
        }
      }

      // 处理加载状态变化
      if (event.key === KEYS.LOADING && event.newValue) {
        try {
          const loading = JSON.parse(event.newValue)
          if (typeof loading === 'boolean') {
            isLoading.value = loading
          }
        } catch (error) {
          console.error('Error processing loading state:', error)
        }
      }

      // 处理消息列表直接更新（当切换对话时）
      if (event.key === KEYS.MESSAGES && event.newValue) {
        try {
          const newMessages = JSON.parse(event.newValue)
          if (Array.isArray(newMessages)) {
            // 只有当消息数量或内容不同时才更新
            if (messages.value.length !== newMessages.length || JSON.stringify(messages.value) !== JSON.stringify(newMessages)) {
              messages.value = newMessages
            }
          }
        } catch (error) {
          console.error('Error processing messages update:', error)
        }
      }

      // 处理待发送媒体变化
      if (event.key === KEYS.PENDING_MEDIA) {
        try {
          if (event.newValue) {
            const newPendingMedia = JSON.parse(event.newValue)
            if (typeof newPendingMedia === 'object') {
              pendingMedia.value = newPendingMedia
            }
          } else {
            // 当 newValue 为 null 时（调用 removeItem），清空待发送媒体
            pendingMedia.value = {}
          }
        } catch (error) {
          console.error('Error processing pending media update:', error)
        }
      }
    })
  }

  // 初始化函数
  async function initialize(): Promise<void> {
    // 加载本地存储的消息
    initFromStorage()

    // 安全检查：确保加载状态的正确性
    if (messages.value.length === 0 && isLoading.value) {
      console.warn('检测到异常状态：无消息但处于加载中，重置加载状态')
      isLoading.value = false
      localStorage.setItem(KEYS.LOADING, JSON.stringify(false))
    }

    // 设置消息监听
    setupMessageListeners()

    // 如果当前没有消息，尝试加载最新的对话
    if (messages.value.length === 0) {
      const loaded = await loadLatestConversation()
      if (!loaded) {
        // 如果没有历史对话，添加欢迎消息
        addWelcomeMessageIfNeeded()
      }
    }

    // 检查当前是哪个页面/窗口
    const isFloating = window.location.hash === '#/floating' || window.location.hash === '#floating'
    console.log(`Chat store initialized in ${isFloating ? 'floating window' : 'main window'}`)
  }

  // 加载最新的对话
  async function loadLatestConversation(): Promise<boolean> {
    try {
      // 首先尝试从数据库获取最新对话
      if (window.api?.database) {
        const conversations = await window.api.database.getConversationList()
        if (conversations.length > 0) {
          // 按时间戳降序排序，取最新的一个
          const latest = conversations.sort((a, b) => b.timestamp - a.timestamp)[0]
          console.log('自动加载最新对话:', latest.title)
          return await loadConversation(latest.id)
        }
      }

      // 回退到 localStorage
      const history: ConversationHistory[] = JSON.parse(localStorage.getItem('vlm-chat-history') || '[]')
      if (history.length > 0) {
        // 按时间戳降序排序，取最新的一个
        const latest = history.sort((a, b) => b.timestamp - a.timestamp)[0]
        console.log('从localStorage自动加载最新对话:', latest.title)
        return await loadConversation(latest.id)
      }
    } catch (error) {
      console.error('加载最新对话失败:', error)
    }
    return false
  }

  // 切换到主窗口并定位到指定消息
  function switchToMessageAndScroll(messageId: string): void {
    // 通过localStorage发送切换窗口和定位消息的事件
    localStorage.setItem(
      'vlm-chat-switch-to-message',
      JSON.stringify({
        messageId,
        timestamp: Date.now()
      })
    )
  }

  // 获取用于API的历史消息（按轮数获取，不包含当前正在发送的消息）
  function getHistoryForAPI(maxTurns: number = 4): Array<{ role: 'user' | 'assistant'; content: string; image?: string; video?: string; pdfImages?: string[]; pptImages?: string[] }> {
    // 过滤掉欢迎消息，只保留真实的对话
    const realMessages = messages.value.filter(msg => {
      // 过滤掉欢迎消息
      if (msg.role === 'assistant' && msg.content.includes('你好！我是GLM-4.5V')) {
        return false
      }
      return true
    })

    // 计算需要获取的消息条数：每轮对话包含2条消息（1条用户+1条AI回复）
    const maxMessages = maxTurns * 2 + 1 // +1是为了包含当前用户消息

    // 获取最近的历史消息（不包含当前正在发送的用户消息）
    const recentMessages = realMessages.slice(-maxMessages)

    return recentMessages.map(msg => ({
      role: msg.role,
      content: msg.content,
      image: msg.image,
      // 优先使用 videoBase64，如果不存在且 video 是 base64 格式则使用 video
      video: msg.videoBase64 || (msg.video && msg.video.startsWith('data:') ? msg.video : undefined),
      pdfImages: msg.pdfImages,
      pptImages: msg.pptImages
    }))
  }

  // 新建对话
  async function startNewConversation(): Promise<void> {
    const realMessages = messages.value.filter(msg => {
      if (msg.role === 'assistant' && msg.content.includes('你好！我是GLM-4.5V')) {
        return false
      }
      return true
    })

    // 检查是否有完整的对话（至少包含一对用户-助手消息，且助手消息不为空）
    const hasUserMessage = realMessages.some(msg => msg.role === 'user')
    const hasAssistantMessage = realMessages.some(msg => msg.role === 'assistant' && msg.content.trim().length > 0)
    const hasCompleteConversation = hasUserMessage && hasAssistantMessage

    if (hasCompleteConversation && !currentConversationSaved.value) {
      console.log('保存当前完整对话到历史记录')
      await saveCurrentConversationWithResponse()
    } else if (hasUserMessage && !hasAssistantMessage) {
      console.log('丢弃未完成的对话（只有用户消息）')
    }

    // 发布全局事件，通知所有使用chatFunctions的组件取消当前请求
    window.dispatchEvent(new CustomEvent('cancel-current-request'))

    // 取消主进程中所有活跃的流式请求
    if (window.api?.apiStreamCancelAll) {
      try {
        await window.api.apiStreamCancelAll()
        console.log('已取消所有主进程流式请求')
      } catch (error) {
        console.warn('取消主进程流式请求失败:', error)
      }
    }

    // 清空当前对话状态
    messages.value = []
    welcomeAdded.value = false
    isLoading.value = false
    currentConversationSaved.value = false
    currentConversationId.value = null

    // 清空待发送媒体
    clearPendingMedia()

    // 清理本地存储
    localStorage.removeItem(KEYS.MESSAGES)
    localStorage.setItem(KEYS.WELCOME, JSON.stringify(false))
    localStorage.setItem(KEYS.LOADING, JSON.stringify(false))

    // 添加欢迎消息
    addWelcomeMessageIfNeeded()
  }

  // 生成对话标题（基于第一条用户消息）
  function generateConversationTitle(): string {
    const firstUserMessage = messages.value.find(msg => msg.role === 'user')
    if (firstUserMessage) {
      const content = firstUserMessage.content
      if (content.length > 30) {
        return content.substring(0, 30) + '...'
      }
      return content || '新对话'
    }
    return '新对话'
  }

  // 获取历史对话列表
  function getConversationHistory(): Array<{ id: string; title: string; timestamp: number; messageCount: number }> {
    // 首先尝试从数据库获取
    if (window.api?.database) {
      return []
    }

    const history: ConversationHistory[] = JSON.parse(localStorage.getItem('vlm-chat-history') || '[]')
    return history.map((conv: ConversationHistory) => ({
      id: conv.id,
      title: conv.title,
      timestamp: conv.timestamp,
      messageCount: conv.messages?.length || 0
    }))
  }

  // 异步获取历史对话列表（从数据库）
  async function getConversationHistoryAsync(): Promise<Array<{ id: string; title: string; timestamp: number; messageCount: number }>> {
    if (window.api?.database) {
      try {
        return await window.api.database.getConversationList()
      } catch (error) {
        console.error('从数据库获取对话历史失败:', error)
      }
    }

    // 回退到 localStorage
    return getConversationHistory()
  }

  // 加载历史对话
  async function loadConversation(conversationId: string): Promise<boolean> {
    try {
      // 发布全局事件，通知所有使用chatFunctions的组件取消当前请求
      window.dispatchEvent(new CustomEvent('cancel-current-request'))

      // 取消主进程中所有活跃的流式请求
      if (window.api?.apiStreamCancelAll) {
        try {
          await window.api.apiStreamCancelAll()
          console.log('加载对话时已取消所有主进程流式请求')
        } catch (error) {
          console.warn('加载对话时取消主进程流式请求失败:', error)
        }
      }

      // 首先尝试从数据库加载
      if (window.api?.database) {
        const conversation = await window.api.database.loadConversation(conversationId)
        if (conversation) {
          // 加载选定的对话
          messages.value = conversation.messages || []
          welcomeAdded.value = messages.value.length > 0
          currentConversationSaved.value = true // 加载的对话已经保存过了
          currentConversationId.value = conversationId // 设置当前对话ID

          // 停止加载状态
          isLoading.value = false

          // 保存到当前存储
          saveToStorage()
          return true
        }
      }

      // 回退到 localStorage
      const history: ConversationHistory[] = JSON.parse(localStorage.getItem('vlm-chat-history') || '[]')
      const conversation = history.find((conv: ConversationHistory) => conv.id === conversationId)

      if (conversation) {
        // 加载选定的对话
        messages.value = conversation.messages || []
        welcomeAdded.value = messages.value.length > 0
        currentConversationSaved.value = true // 加载的对话已经保存过了
        currentConversationId.value = conversationId // 设置当前对话ID

        // 停止加载状态
        isLoading.value = false

        // 保存到当前存储
        saveToStorage()
        return true
      }
    } catch (error) {
      console.error('加载对话失败:', error)
    }
    return false
  }

  // 删除历史对话
  async function deleteConversation(conversationId: string): Promise<boolean> {
    try {
      // 首先尝试从数据库删除
      if (window.api?.database) {
        return await window.api.database.deleteConversation(conversationId)
      }

      // 回退到 localStorage
      const history: ConversationHistory[] = JSON.parse(localStorage.getItem('vlm-chat-history') || '[]')
      const filteredHistory = history.filter((conv: ConversationHistory) => conv.id !== conversationId)
      localStorage.setItem('vlm-chat-history', JSON.stringify(filteredHistory))
      return true
    } catch (error) {
      console.error('删除对话失败:', error)
      return false
    }
  }

  // 每次AI响应后保存当前对话（更保险的策略）
  async function saveCurrentConversationWithResponse(): Promise<void> {
    const realMessages = messages.value.filter(msg => {
      // 过滤掉欢迎消息
      if (msg.role === 'assistant' && msg.content.includes('你好！我是GLM-4.5V')) {
        return false
      }
      return true
    })

    // 检查是否有完整的对话（至少包含一对用户-助手消息，且助手消息不为空）
    const hasUserMessage = realMessages.some(msg => msg.role === 'user')
    const hasAssistantMessage = realMessages.some(msg => msg.role === 'assistant' && msg.content.trim().length > 0)

    // 只保存有用户消息和有实际内容的助手回复的完整对话
    if (realMessages.length > 0 && hasUserMessage && hasAssistantMessage) {
      if (!currentConversationId.value) {
        currentConversationId.value = generateMessageId()
      }

      // 清理所有消息数据
      const cleanMessages = realMessages.map(msg => ({
        id: String(msg.id || ''),
        role: (msg.role as 'user' | 'assistant') || 'user',
        content: String(msg.content || ''),
        image: msg.image ? String(msg.image) : undefined,
        video: msg.video ? String(msg.video) : undefined,
        videoBase64: msg.videoBase64 ? String(msg.videoBase64) : undefined,
        pdfImages: msg.pdfImages ? [...msg.pdfImages] : undefined,
        pdfName: msg.pdfName ? String(msg.pdfName) : undefined,
        pptImages: msg.pptImages ? [...msg.pptImages] : undefined,
        pptName: msg.pptName ? String(msg.pptName) : undefined,
        pptTotalPages: msg.pptTotalPages ? Number(msg.pptTotalPages) : undefined,
        timestamp: Number(msg.timestamp || Date.now())
      }))

      // 保存到数据库 - 保存完整对话
      if (window.api?.database) {
        try {
          // 构建完整对话对象
          const fullConversation = {
            id: currentConversationId.value,
            title: generateConversationTitle(),
            messages: cleanMessages,
            timestamp: Date.now(),
            messageCount: cleanMessages.length
          }

          // 使用增量保存方法保存完整对话
          const success = await window.api.database.saveConversationIncremental(fullConversation)

          if (success) {
            currentConversationSaved.value = true
          } else {
            console.warn('数据库保存失败，回退到 localStorage')
            // 回退到完整保存逻辑
            await saveFullConversationToLocalStorage(cleanMessages)
          }
        } catch (error) {
          console.error('AI响应后保存完整对话到数据库失败:', error)
          // 回退到完整保存逻辑
          await saveFullConversationToLocalStorage(cleanMessages)
        }
      } else {
        console.warn('数据库 API 不可用，使用 localStorage 保存')
        await saveFullConversationToLocalStorage(cleanMessages)
      }
    } else {
      console.log('跳过保存：对话不完整（缺少用户消息或助手回复）')
    }
  }

  // 完整保存到 localStorage 的辅助函数
  async function saveFullConversationToLocalStorage(realMessages: ChatMessage[]): Promise<void> {
    const cleanMessages = realMessages.map(msg => ({
      id: String(msg.id || ''),
      role: (msg.role as 'user' | 'assistant') || 'user',
      content: String(msg.content || ''),
      image: msg.image ? String(msg.image) : undefined,
      video: msg.video ? String(msg.video) : undefined,
      videoBase64: msg.videoBase64 ? String(msg.videoBase64) : undefined,
      pdfImages: msg.pdfImages ? [...msg.pdfImages] : undefined,
      pdfName: msg.pdfName ? String(msg.pdfName) : undefined,
      pptImages: msg.pptImages ? [...msg.pptImages] : undefined,
      pptName: msg.pptName ? String(msg.pptName) : undefined,
      timestamp: Number(msg.timestamp || Date.now())
    }))

    const conversationHistory = JSON.parse(
      JSON.stringify({
        id: currentConversationId.value,
        title: generateConversationTitle(),
        messages: cleanMessages,
        timestamp: Date.now(),
        messageCount: cleanMessages.length
      })
    )

    saveToLocalStorage(conversationHistory)
    currentConversationSaved.value = true
  }

  // 保存到 localStorage 的辅助函数
  function saveToLocalStorage(conversationHistory: ConversationHistory): void {
    const existingHistory = JSON.parse(localStorage.getItem('vlm-chat-history') || '[]')
    existingHistory.unshift(conversationHistory)
    if (existingHistory.length > 20) {
      existingHistory.splice(20)
    }
    localStorage.setItem('vlm-chat-history', JSON.stringify(existingHistory))
  }

  // 在 store 创建时立即调用初始化
  initialize()

  return {
    messages,
    isLoading,
    welcomeAdded,
    currentConversationId,
    pendingMedia,
    addUserMessage,
    addAssistantMessage,
    updateAssistantMessage,
    updateAssistantMessageContent,
    removeMessage,
    setLoading,
    clearMessages,
    addWelcomeMessageIfNeeded,
    saveToStorage,
    switchToMessageAndScroll,
    getHistoryForAPI,
    startNewConversation,
    getConversationHistory,
    getConversationHistoryAsync,
    loadConversation,
    deleteConversation,
    saveCurrentConversationWithResponse,
    loadLatestConversation,
    setPendingMedia,
    clearPendingMedia,
    hasPendingMedia
  }
})
