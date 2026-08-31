export class ApiProxy {
  // 活跃的流式请求映射，用于管理和取消请求
  private activeStreams = new Map<string, AbortController>()

  // 添加API代理功能
  async proxyApiRequest(url: string, options: RequestInit): Promise<{ ok: boolean; status: number; data: unknown }> {
    try {
      console.log('主进程发起API请求:', url)
      // console.log('请求选项:', options)

      const response = await fetch(url, options)
      console.log('API响应状态:', response.status, response.statusText)

      const contentType = response.headers.get('content-type')
      let data
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
        console.log('JSON响应内容:', data.choices ? data.choices[0].message.content : data)
      } else {
        const text = await response.text()
        console.log('非JSON响应内容:', text)
        data = { error: '服务器返回非JSON格式响应', content: text }
      }

      return {
        ok: response.ok,
        status: response.status,
        data: data
      }
    } catch (error) {
      console.error('API请求失败:', error)
      throw error
    }
  }

  // 取消指定的流式请求
  cancelStream(streamId: string): void {
    const controller = this.activeStreams.get(streamId)
    if (controller) {
      console.log(`取消流式请求: ${streamId}`)
      controller.abort()
      this.activeStreams.delete(streamId)
    }
  }

  // 取消所有活跃的流式请求
  cancelAllStreams(): void {
    console.log(`取消所有活跃的流式请求 (${this.activeStreams.size} 个)`)
    for (const [, controller] of this.activeStreams) {
      controller.abort()
    }
    this.activeStreams.clear()
  }

  // 添加流式API代理功能
  async createStreamProxy(url: string, options: RequestInit, webContents: Electron.WebContents, streamId: string): Promise<{ ok: boolean; status: number }> {
    try {
      console.log('主进程发起流式API请求:', url, 'streamId:', streamId)

      const controller = new AbortController()
      this.activeStreams.set(streamId, controller)

      const requestOptions = {
        ...options,
        signal: controller.signal
      }

      const response = await fetch(url, requestOptions)
      console.log('流式API响应状态:', response.status, response.statusText)

      if (!response.ok) {
        this.activeStreams.delete(streamId)
        return { ok: false, status: response.status }
      }

      if (!response.body) {
        this.activeStreams.delete(streamId)
        throw new Error('Response body is null')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      try {
        while (true) {
          if (controller.signal.aborted) {
            console.log(`流式请求 ${streamId} 已被取消`)
            break
          }

          const { done, value } = await reader.read()

          if (done) {
            // 通知渲染进程流式响应结束
            webContents.send('stream-chunk', streamId, null, true)
            break
          }

          // 将数据块发送到渲染进程
          const chunk = decoder.decode(value, { stream: true })
          webContents.send('stream-chunk', streamId, chunk, false)
        }
      } finally {
        reader.releaseLock()
        this.activeStreams.delete(streamId)
      }

      return { ok: true, status: response.status }
    } catch (error) {
      this.activeStreams.delete(streamId)

      if (error instanceof Error && error.name === 'AbortError') {
        console.log(`流式API请求 ${streamId} 被取消:`, error.message)
        webContents.send('stream-chunk', streamId, null, true)
        return { ok: false, status: 499 } // 499 Client Closed Request
      }

      console.error('流式API请求失败:', error)
      const errorMessage = error instanceof Error ? error.message : String(error)
      webContents.send('stream-error', streamId, errorMessage)
      throw error
    }
  }
}

export const apiProxy = new ApiProxy()
