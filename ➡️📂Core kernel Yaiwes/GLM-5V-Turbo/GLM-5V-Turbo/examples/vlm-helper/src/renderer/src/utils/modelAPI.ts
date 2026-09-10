import type { ModelRequest, ModelResponse } from '../types'

// 定义设置接口
interface APISettings {
  apiUrl: string
  apiKey: string
  model: string
  maxTokens: number
  temperature: number
  topP: number
  topK: number
  repetitionPenalty: number
  skipSpecialTokens: boolean
  stopTokenIds: number[]
  includeStopStrInOutput: boolean
  endpoint: string
  zhipuMaasMode: boolean
  systemPrompt: string
}

export class ModelAPI {
  async callModel(request: ModelRequest, settings: APISettings, signal?: AbortSignal): Promise<ModelResponse> {
    try {
      // 添加模型参数到请求中
      const requestWithConfig: Record<string, unknown> = {
        ...request,
        stream: false,
        temperature: settings.temperature,
        top_p: settings.topP,
        max_tokens: settings.maxTokens
      }

      // 在智谱MaaS模式下添加模型参数
      if (settings.zhipuMaasMode && settings.model) {
        requestWithConfig.model = settings.model
      }

      // 只有在非智谱MaaS模式下才添加这些参数
      if (!settings.zhipuMaasMode) {
        requestWithConfig.top_k = settings.topK
        requestWithConfig.repetition_penalty = settings.repetitionPenalty
        requestWithConfig.skip_special_tokens = settings.skipSpecialTokens
        requestWithConfig.stop_token_ids = settings.stopTokenIds
        requestWithConfig.include_stop_str_in_output = settings.includeStopStrInOutput
      }

      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      }

      if (settings.apiKey) {
        headers['Authorization'] = `Bearer ${settings.apiKey}`
      }

      const apiUrl = `${settings.apiUrl}${settings.endpoint}`
      console.log('API请求URL:', apiUrl)
      console.log('请求配置:', requestWithConfig)

      // 检查是否在Electron环境中
      if (window.api?.apiRequest) {
        return new Promise<ModelResponse>((resolve, reject) => {
          // 设置取消监听器
          if (signal) {
            signal.addEventListener('abort', () => {
              reject(new DOMException('Aborted', 'AbortError'))
            })

            if (signal.aborted) {
              reject(new DOMException('Aborted', 'AbortError'))
              return
            }
          }

          // 执行API请求
          window
            .api!.apiRequest(apiUrl, {
              method: 'POST',
              headers,
              body: JSON.stringify(requestWithConfig)
              // 注意：不传递signal，因为它无法序列化
            })
            .then(result => {
              // 再次检查是否已被取消
              if (signal && signal.aborted) {
                reject(new DOMException('Aborted', 'AbortError'))
                return
              }

              console.log(result)

              if (!result.ok) {
                console.error('API请求失败:', result)
                reject(new Error(`HTTP error! status: ${result.status}, URL: ${apiUrl}`))
                return
              }

              resolve(result.data as ModelResponse)
            })
            .catch(error => {
              // 检查是否是由于取消导致的错误
              if (signal && signal.aborted) {
                reject(new DOMException('Aborted', 'AbortError'))
              } else {
                reject(error)
              }
            })
        })
      } else {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers,
          body: JSON.stringify(requestWithConfig),
          signal // 在浏览器环境中可以直接传递 AbortSignal
        })

        if (!response.ok) {
          console.error('API请求失败:', response)
          throw new Error(`HTTP error! status: ${response.status}, URL: ${apiUrl}`)
        }

        return await response.json()
      }
    } catch (error) {
      console.error('模型调用失败:', error)
      throw error
    }
  }

  // 流式调用方法，支持实时响应回调
  async callModelStream(request: ModelRequest, settings: APISettings, onChunk: (chunk: string, type?: 'reasoning' | 'content') => void, signal?: AbortSignal): Promise<string> {
    try {
      // 添加流式响应强制启用，并根据 zhipuMaasMode 决定是否包含智谱AI不支持的参数
      const requestWithConfig: Record<string, unknown> = {
        ...request,
        stream: true,
        temperature: settings.temperature,
        top_p: settings.topP,
        max_tokens: settings.maxTokens
      }

      // 在智谱MaaS模式下添加模型参数
      if (settings.zhipuMaasMode && settings.model) {
        requestWithConfig.model = settings.model
      }

      // 只有在非智谱MaaS模式下才添加这些参数
      if (!settings.zhipuMaasMode) {
        requestWithConfig.top_k = settings.topK
        requestWithConfig.repetition_penalty = settings.repetitionPenalty
        requestWithConfig.skip_special_tokens = settings.skipSpecialTokens
        requestWithConfig.stop_token_ids = settings.stopTokenIds
        requestWithConfig.include_stop_str_in_output = settings.includeStopStrInOutput
      }

      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      }

      // 如果有API密钥，添加到请求头
      if (settings.apiKey) {
        headers['Authorization'] = `Bearer ${settings.apiKey}`
      }

      const apiUrl = `${settings.apiUrl}${settings.endpoint}`
      console.log('API流式请求URL:', apiUrl)
      console.log('请求配置:', requestWithConfig)

      // 检查是否有主进程代理可用
      if (window.api?.apiStreamRequest) {
        // 使用主进程的流式代理，支持所有模式
        console.log('使用主进程流式代理发送API请求')

        const streamId = `stream_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        let fullContent = ''
        let buffer = ''

        return new Promise<string>((resolve, reject) => {
          let streamChunkWrapper: ((event: Electron.IpcRendererEvent, ...args: unknown[]) => void) | null = null
          let streamErrorWrapper: ((event: Electron.IpcRendererEvent, ...args: unknown[]) => void) | null = null

          // 设置流数据处理器
          const handleStreamChunk = (id: string, chunk: string | null, isDone: boolean): void => {
            if (id !== streamId) return

            if (isDone) {
              // 流式响应结束
              console.log('主进程流式输出结束')
              if (streamChunkWrapper && window.api?.offStreamChunk) {
                window.api.offStreamChunk(streamChunkWrapper)
              }
              if (streamErrorWrapper && window.api?.offStreamError) {
                window.api.offStreamError(streamErrorWrapper)
              }

              // 处理缓冲区中剩余的不完整数据
              if (buffer.trim()) {
                console.warn('Stream ended with incomplete data in buffer:', buffer)
              }

              resolve(fullContent)
              return
            }

            if (chunk) {
              // 将新数据添加到缓冲区
              buffer += chunk

              // 按行处理数据
              const lines = buffer.split('\n')

              // 保留最后一行（可能不完整）
              buffer = lines.pop() || ''

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  const data = line.slice(6).trim()

                  // 智谱AI流式结束标志
                  if (data === '[DONE]') {
                    console.log('智谱AI流式输出结束')
                    continue
                  }

                  if (!data) continue // 跳过空数据

                  try {
                    const parsed = JSON.parse(data)

                    if (settings.zhipuMaasMode) {
                      // 智谱AI流式响应格式处理
                      const delta = parsed.choices?.[0]?.delta
                      if (delta) {
                        // 处理普通内容
                        const content = delta.content || ''
                        // 处理思考块内容（智谱AI特有）
                        const reasoningContent = delta.reasoning_content || ''

                        // 如果有思考块内容，标记为reasoning类型
                        if (reasoningContent) {
                          console.log('思考块', reasoningContent)

                          fullContent += reasoningContent
                          try {
                            onChunk(reasoningContent, 'reasoning')
                          } catch (callbackError) {
                            console.warn('回调处理reasoning内容失败:', callbackError)
                          }
                        }

                        // 如果有普通内容，标记为content类型
                        if (content) {
                          console.log('普通块:', content)
                          fullContent += content
                          try {
                            onChunk(content, 'content')
                          } catch (callbackError) {
                            console.warn('回调处理content内容失败:', callbackError)
                          }
                        }
                      }
                    } else {
                      // 标准流式响应格式处理
                      const content = parsed.choices?.[0]?.delta?.content || ''
                      if (content) {
                        fullContent += content
                        try {
                          onChunk(content)
                        } catch (callbackError) {
                          console.warn('回调处理内容失败:', callbackError)
                        }
                      }
                    }
                  } catch (parseError) {
                    // 忽略JSON解析错误，但输出调试信息
                    console.warn('Failed to parse SSE data:', data, 'Error:', parseError)
                    // 继续处理下一行，不中断流式输出
                  }
                }
              }
            }
          }

          // 设置错误处理器
          const handleStreamError = (id: string, error: string): void => {
            if (id !== streamId) return

            console.error('主进程流式请求失败:', error)
            if (streamChunkWrapper && window.api?.offStreamChunk) {
              window.api.offStreamChunk(streamChunkWrapper)
            }
            if (streamErrorWrapper && window.api?.offStreamError) {
              window.api.offStreamError(streamErrorWrapper)
            }
            reject(new Error(error))
          }

          // 注册事件监听器并获取包装器
          if (window.api?.onStreamChunk) {
            streamChunkWrapper = window.api.onStreamChunk(handleStreamChunk)
          }
          if (window.api?.onStreamError) {
            streamErrorWrapper = window.api.onStreamError(handleStreamError)
          }

          // 发起流式API请求
          if (window.api?.apiStreamRequest) {
            window.api
              .apiStreamRequest(
                apiUrl,
                {
                  method: 'POST',
                  headers,
                  body: JSON.stringify(requestWithConfig)
                },
                streamId
              )
              .catch(error => {
                console.error('发起主进程流式请求失败:', error)
                if (streamChunkWrapper && window.api?.offStreamChunk) {
                  window.api.offStreamChunk(streamChunkWrapper)
                }
                if (streamErrorWrapper && window.api?.offStreamError) {
                  window.api.offStreamError(streamErrorWrapper)
                }
                reject(error)
              })
          } else {
            reject(new Error('流式API不可用'))
          }

          // 处理取消信号
          if (signal) {
            signal.addEventListener('abort', () => {
              console.log(`取消流式请求: ${streamId}`)
              // 通知主进程取消流式请求
              if (window.api?.apiStreamCancel) {
                window.api.apiStreamCancel(streamId).catch(error => {
                  console.error('通知主进程取消流式请求失败:', error)
                })
              }
              if (streamChunkWrapper && window.api?.offStreamChunk) {
                window.api.offStreamChunk(streamChunkWrapper)
              }
              if (streamErrorWrapper && window.api?.offStreamError) {
                window.api.offStreamError(streamErrorWrapper)
              }
              reject(new DOMException('Aborted', 'AbortError'))
            })
          }
        })
      } else if (settings.zhipuMaasMode) {
        console.warn('智谱MaaS模式: 主进程代理不可用，使用浏览器fetch')
        // 使用浏览器fetch，处理SSE流
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers,
          body: JSON.stringify(requestWithConfig),
          signal
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        if (!response.body) {
          throw new Error('Response body is null')
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let fullContent = ''
        let buffer = '' // 用于处理不完整的 chunk

        try {
          while (true) {
            const { done, value } = await reader.read()

            if (done) break

            // 将新数据添加到缓冲区
            buffer += decoder.decode(value, { stream: true })

            // 按行处理数据
            const lines = buffer.split('\n')

            // 保留最后一行（可能不完整）
            buffer = lines.pop() || ''

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6).trim()

                // 智谱AI流式结束标志
                if (data === '[DONE]') {
                  console.log('智谱AI流式输出结束')
                  continue
                }

                if (!data) continue // 跳过空数据

                try {
                  const parsed = JSON.parse(data)

                  // 智谱AI流式响应格式处理
                  const delta = parsed.choices?.[0]?.delta
                  if (delta) {
                    // 处理普通内容
                    const content = delta.content || ''
                    // 处理思考块内容（智谱AI特有）
                    const reasoningContent = delta.reasoning_content || ''

                    // 如果有思考块内容，标记为reasoning类型
                    if (reasoningContent) {
                      fullContent += reasoningContent
                      try {
                        onChunk(reasoningContent, 'reasoning')
                      } catch (callbackError) {
                        console.warn('回调处理reasoning内容失败:', callbackError)
                      }
                    }

                    // 如果有普通内容，标记为content类型
                    if (content) {
                      fullContent += content
                      try {
                        onChunk(content, 'content')
                      } catch (callbackError) {
                        console.warn('回调处理content内容失败:', callbackError)
                      }
                    }
                  }
                } catch (parseError) {
                  // 忽略JSON解析错误，但输出调试信息
                  console.warn('Failed to parse SSE data:', data, 'Error:', parseError)
                  // 继续处理下一行，不中断流式输出
                }
              }
            }
          }

          // 处理缓冲区中剩余的不完整数据
          if (buffer.trim()) {
            console.warn('Stream ended with incomplete data in buffer:', buffer)
          }
        } finally {
          reader.releaseLock()
        }

        return fullContent
      } else {
        console.log('在Electron环境中使用模拟流式输出')
        // 非MaaS模式且在Electron环境中，使用模拟流式输出
        if (!window.api?.apiRequest) {
          throw new Error('Electron API 不可用')
        }

        const result = await window.api.apiRequest(apiUrl, {
          method: 'POST',
          headers,
          body: JSON.stringify(requestWithConfig)
        })

        if (!result.ok) {
          throw new Error(`HTTP error! status: ${result.status}`)
        }

        const response = result.data as ModelResponse
        const content = response.choices[0]?.message?.content || ''

        // 模拟流式输出
        const words = content.split('')

        for (let i = 0; i < words.length; i++) {
          if (signal && signal.aborted) {
            throw new DOMException('Aborted', 'AbortError')
          }

          onChunk(words[i])

          // 添加小延迟来模拟流式效果
          if (i % 5 === 0) {
            await new Promise(resolve => setTimeout(resolve, 20))
          }
        }

        return content
      }
    } catch (error) {
      console.error('流式模型调用失败:', error)
      throw error
    }
  }

  async analyzeImage(imageBase64: string, prompt: string, settings: APISettings, signal?: AbortSignal): Promise<string> {
    const messages: Array<{
      role: 'user' | 'system'
      content: Array<{
        type: 'text' | 'image_url'
        text?: string
        image_url?: { url: string }
      }>
    }> = []

    // 添加系统提示词（如果有的话）
    if (settings.systemPrompt.trim()) {
      messages.push({
        role: 'system',
        content: [{ type: 'text', text: settings.systemPrompt }]
      })
    }

    // 添加用户消息
    messages.push({
      role: 'user',
      content: [
        {
          type: 'text',
          text: prompt
        },
        {
          type: 'image_url',
          image_url: {
            url: imageBase64
          }
        }
      ]
    })

    const request: ModelRequest = {
      messages
    }

    const response = await this.callModel(request, settings, signal)
    return response.choices[0]?.message?.content || '无法获取分析结果'
  }

  async analyzeImages(images: string[], prompt: string, settings: APISettings, signal?: AbortSignal): Promise<string> {
    const content: Array<{
      type: 'text' | 'image_url'
      text?: string
      image_url?: { url: string }
    }> = [
        {
          type: 'text',
          text: prompt
        }
      ]

    // 添加所有图片
    images.forEach(image => {
      content.push({
        type: 'image_url',
        image_url: {
          url: image
        }
      })
    })

    const messages: Array<{
      role: 'user' | 'system'
      content: Array<{
        type: 'text' | 'image_url'
        text?: string
        image_url?: { url: string }
      }>
    }> = []

    // 添加系统提示词（如果有的话）
    if (settings.systemPrompt.trim()) {
      messages.push({
        role: 'system',
        content: [{ type: 'text', text: settings.systemPrompt }]
      })
    }

    // 添加用户消息
    messages.push({
      role: 'user',
      content
    })

    const request: ModelRequest = {
      messages
    }

    const response = await this.callModel(request, settings, signal)
    return response.choices[0]?.message?.content || '无法获取分析结果'
  }

  async analyzeVideo(videoBase64: string, prompt: string, settings: APISettings, signal?: AbortSignal): Promise<string> {
    const messages: Array<{
      role: 'user' | 'system'
      content: Array<{
        type: 'text' | 'video_url'
        text?: string
        video_url?: { url: string }
      }>
    }> = []

    // 添加系统提示词（如果有的话）
    if (settings.systemPrompt.trim()) {
      messages.push({
        role: 'system',
        content: [{ type: 'text', text: settings.systemPrompt }]
      })
    }

    // 添加用户消息
    messages.push({
      role: 'user',
      content: [
        {
          type: 'text',
          text: prompt
        },
        {
          type: 'video_url',
          video_url: {
            url: videoBase64
          }
        }
      ]
    })

    const request: ModelRequest = {
      messages
    }

    const response = await this.callModel(request, settings, signal)
    return response.choices[0]?.message?.content || '无法获取分析结果'
  }

  async analyzeText(text: string, settings: APISettings, signal?: AbortSignal): Promise<string> {
    const request: ModelRequest = {
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: text
            }
          ]
        }
      ]
    }

    const response = await this.callModel(request, settings, signal)
    return response.choices[0]?.message?.content || '无法获取分析结果'
  }

  async chatCompletion(message: string, settings: APISettings, signal?: AbortSignal): Promise<string> {
    const request: ModelRequest = {
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: message
            }
          ]
        }
      ]
    }

    const response = await this.callModel(request, settings, signal)
    return response.choices[0]?.message?.content || '无法获取回复'
  }

  // 带历史上下文的对话完成
  async chatCompletionWithHistory(messages: Array<{ role: 'user' | 'assistant'; content: string; image?: string; video?: string; pdfImages?: string[]; pptImages?: string[] }>, settings: APISettings, signal?: AbortSignal): Promise<string> {
    // 构建符合API格式的消息数组
    const apiMessages: Array<{ role: 'user' | 'assistant' | 'system'; content: Array<{ type: 'text' | 'image_url' | 'video_url'; text?: string; image_url?: { url: string }; video_url?: { url: string } }> }> = []

    if (settings.systemPrompt.trim()) {
      apiMessages.push({
        role: 'system',
        content: [{ type: 'text', text: settings.systemPrompt }]
      })
    }

    // 添加历史消息
    apiMessages.push(
      ...messages.map(msg => {
        const content: Array<{ type: 'text' | 'image_url' | 'video_url'; text?: string; image_url?: { url: string }; video_url?: { url: string } }> = []

        if (msg.content) {
          content.push({
            type: 'text',
            text: msg.content
          })
        }

        if (msg.image) {
          content.push({
            type: 'image_url',
            image_url: { url: msg.image }
          })
        }

        if (msg.video) {
          content.push({
            type: 'video_url',
            video_url: { url: msg.video }
          })
        }

        if (msg.pdfImages && msg.pdfImages.length > 0) {
          msg.pdfImages.forEach(image => {
            content.push({
              type: 'image_url',
              image_url: { url: image }
            })
          })
        }

        if (msg.pptImages && msg.pptImages.length > 0) {
          msg.pptImages.forEach(image => {
            content.push({
              type: 'image_url',
              image_url: { url: image }
            })
          })
        }

        return {
          role: msg.role,
          content
        }
      })
    )

    const request: ModelRequest = {
      messages: apiMessages
    }

    const response = await this.callModel(request, settings, signal)
    return response.choices[0]?.message?.content || '无法获取回复'
  }
}

export const modelAPI = new ModelAPI()
