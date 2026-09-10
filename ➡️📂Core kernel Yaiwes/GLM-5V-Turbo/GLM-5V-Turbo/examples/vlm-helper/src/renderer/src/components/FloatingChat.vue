<template>
  <div class="h-100vh w-full bg-black/90 rounded-lg border border-white/20 flex flex-col overflow-hidden backdrop-blur-10px shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
    <div class="drag-region bg-white/10 px-2 py-1.5 border-b border-white/15 flex justify-between items-center text-xs text-white min-h-8">
      <div class="font-semibold text-white/90">GLM-4.5V</div>
      <div class="no-drag flex gap-1">
        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="300" size="small">
          <template #trigger>
            <button class="bg-white/10 border-none rounded text-white text-2.75 cursor-pointer px-1.5 py-1 transition-all-200 min-w-5 h-5 flex items-center justify-center hover:bg-green/60" @click="startNewConversation">
              <n-icon size="12">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
                </svg>
              </n-icon>
            </button>
          </template>
          <span class="tooltip-text">新建对话 (Ctrl+Shift+N)</span>
        </n-tooltip>
        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="300" size="small">
          <template #trigger>
            <button class="border-none rounded text-white text-2.75 cursor-pointer px-1.5 py-1 transition-all-200 min-w-5 h-5 flex items-center justify-center" :class="isPinned ? 'bg-orange/60 hover:bg-orange/80' : 'bg-white/10 hover:bg-white/20'" @click="togglePin">
              <n-icon size="12">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M16,12V4H17V2H7V4H8V12L6,14V16H11.2V22H12.8V16H18V14L16,12Z" />
                </svg>
              </n-icon>
            </button>
          </template>
          <span class="tooltip-text">{{ isPinned ? '取消置顶' : '窗口置顶' }}</span>
        </n-tooltip>
        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="300" size="small">
          <template #trigger>
            <button class="bg-white/10 border-none rounded text-white text-2.75 cursor-pointer px-1.5 py-1 transition-all-200 min-w-5 h-5 flex items-center justify-center hover:bg-white/20" @click="switchToMain">⛶</button>
          </template>
          <span class="tooltip-text">切换到主窗口</span>
        </n-tooltip>
        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="300" size="small">
          <template #trigger>
            <button class="bg-white/10 border-none rounded text-white text-2.75 cursor-pointer px-1.5 py-1 transition-all-200 min-w-5 h-5 flex items-center justify-center hover:bg-red/60" @click="closeFloating">✕</button>
          </template>
          <span class="tooltip-text">关闭悬浮窗</span>
        </n-tooltip>
      </div>
    </div>

    <div class="flex-1 flex flex-col overflow-hidden p-1.5 relative" :class="{ 'drag-over': isDragOver }" @dragover="handleDragOver" @dragenter="handleDragEnter" @dragleave="handleDragLeave" @drop="handleDrop">
      <!-- 拖拽提示层 -->
      <div v-if="isDragOver" class="drag-overlay-floating">
        <div class="drag-indicator-floating">
          <div class="drag-icon-floating">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
              <circle cx="12" cy="13" r="3" />
            </svg>
          </div>
          <div class="drag-text-floating">
            <div class="drag-title-floating">释放文件上传</div>
            <div class="drag-subtitle-floating">支持图片/视频/PDF/PPT</div>
          </div>
        </div>
      </div>
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-0.5 flex flex-col gap-1 scrollbar scrollbar-w-1 scrollbar-track-white/5 scrollbar-thumb-white/20 hover:scrollbar-thumb-white/30 relative">
        <div v-for="(message, index) in chatStore.messages" :key="index" :class="[message.role === 'user' ? 'message-user' : 'message-ai']">
          <!-- 用户消息 -->
          <div v-if="message.role === 'user'" :title="'点击切换到主窗口'" @click="handleMessageClick(message)">
            <div v-if="message.image" class="mb-1 relative media-hover-container">
              <img :src="message.image" alt="截图" class="w-full h-auto rounded object-contain" />
              <!-- 媒体操作按钮 -->
              <div class="media-action-buttons">
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="reuseMedia(message.image, 'image')">
                      <n-icon size="14">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  复用图片
                </n-tooltip>
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="downloadMedia(message.image, 'image')">
                      <n-icon size="14">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  下载图片
                </n-tooltip>
              </div>
            </div>
            <div v-if="message.video" class="mb-1 relative media-hover-container">
              <VideoPlayer :src="message.video" :video-base64="message.videoBase64" class="w-full h-auto rounded object-contain" />
              <!-- 媒体操作按钮 -->
              <div class="media-action-buttons">
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="reuseMedia(message.video, 'video', message.videoBase64)">
                      <n-icon size="14">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  复用视频
                </n-tooltip>
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="downloadMedia(message.video || message.videoBase64 || '', 'video')">
                      <n-icon size="14">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  下载视频
                </n-tooltip>
              </div>
            </div>
            <div v-if="message.pdfImages && message.pdfImages.length > 0" class="mb-1 relative media-hover-container">
              <div class="bg-white/8 border border-white/15 rounded-1.5 px-2 py-1.5 flex items-center gap-2">
                <div class="w-5 h-5">
                  <img src="@renderer/assets/icons/pdf3.svg" alt="PDF" class="w-full h-full" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-white/90 text-2.75 font-medium truncate">{{ message.pdfName || 'PDF文档' }} ({{ message.pdfImages.length }}页)</div>
                </div>
              </div>
              <!-- 媒体操作按钮 -->
              <div class="media-action-buttons">
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="reuseMedia(message.pdfImages, 'pdf', undefined, message.pdfName)">
                      <n-icon size="14">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  复用PDF
                </n-tooltip>
              </div>
            </div>
            <div v-if="message.pptImages && message.pptImages.length > 0" class="mb-1 relative media-hover-container">
              <div class="bg-white/8 border border-white/15 rounded-1.5 px-2 py-1.5 flex items-center gap-2">
                <div class="w-5 h-5">
                  <img src="@renderer/assets/icons/ppt3.svg" alt="PPT" class="w-full h-full" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-white/90 text-2.75 font-medium truncate">{{ message.pptName || 'PPT文档' }} ({{ message.pptTotalPages || message.pptImages.length }}页)</div>
                </div>
              </div>
              <!-- 媒体操作按钮 -->
              <div class="media-action-buttons">
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="reuseMedia(message.pptImages, 'ppt', undefined, message.pptName, message.pptTotalPages)">
                      <n-icon size="14">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  复用PPT
                </n-tooltip>
              </div>
            </div>
            <div class="message-text">{{ message.content }}</div>
          </div>

          <!-- AI消息 -->
          <div v-else>
            <!-- 思考块 -->
            <div v-if="extractThinkContent(message.content || '')" class="mb-1.5 px-2 py-1.5 bg-white/5 rounded-1.5 border border-white/10 text-2.75">
              <div class="flex items-center gap-1 select-none">
                <span class="text-3">🤔</span>
                <span class="text-white/70 font-medium flex-1 text-2.5">思考</span>
                <button class="bg-transparent border-none text-blue/80 cursor-pointer text-2.25 px-1 py-0.5 rounded transition-all-200 hover:bg-blue/10 hover:text-blue" @click="toggleThinkExpanded(message.id || index.toString())">
                  <span v-if="isThinkExpanded(message.id || index.toString())">收起</span>
                  <span v-else>展开</span>
                </button>
              </div>
              <div v-if="isThinkExpanded(message.id || index.toString())" class="mt-1.5 pt-1.5 border-t border-white/10 text-white/60 text-2.5 leading-1.3 whitespace-pre-wrap">
                {{ extractThinkContent(message.content || '') }}
              </div>
            </div>
            <!-- AI回复内容 -->
            <div class="message-text" :title="'点击切换到主窗口并查看完整回复'" @click="handleMessageClick(message)">
              {{ formatAnswerBoxes(removeThinkContent(message.content || '')) }}
            </div>
          </div>
        </div>

        <!-- Loading 提示 -->
        <div v-if="chatStore.isLoading" class="mb-1.5 px-1.5 py-1 rounded text-2.75 bg-white/8 text-white border border-white/15 opacity-80">
          <div class="flex items-center gap-1.5">
            <div class="flex gap-0.5">
              <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both] animate-delay-[-0.32s]"></span>
              <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both] animate-delay-[-0.16s]"></span>
              <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both]"></span>
            </div>
            <div class="text-white/70 text-2.5">VLM正在思考中...</div>
          </div>
        </div>
      </div>

      <div class="pt-1 border-t border-white/10">
        <!-- 文件信息显示区域 -->
        <div v-if="chatStore.pendingMedia.image || chatStore.pendingMedia.video || (chatStore.pendingMedia.pdfImages && chatStore.pendingMedia.pdfImages.length > 0) || (chatStore.pendingMedia.pptImages && chatStore.pendingMedia.pptImages.length > 0)" class="mb-1.5">
          <div v-if="chatStore.pendingMedia.image" class="bg-white/8 border border-white/15 rounded-1.5 px-2 py-1.5 flex items-center gap-2">
            <div class="w-6 h-6">
              <img src="@renderer/assets/icons/image.svg" alt="图片" class="w-full h-full" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-white/90 text-2.75 font-medium truncate">已选择图片</div>
              <div class="text-white/60 text-2.25">点击发送按钮上传分析</div>
            </div>
            <button class="bg-red/20 border-none rounded-full w-4.5 h-4.5 flex items-center justify-center cursor-pointer text-white/80 transition-all-200 hover:bg-red/40 hover:text-white" @click="clearImageWrapper">
              <n-icon size="10">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </n-icon>
            </button>
          </div>

          <div v-if="chatStore.pendingMedia.video" class="bg-white/8 border border-white/15 rounded-1.5 px-2 py-1.5 flex items-center gap-2">
            <div class="w-6 h-6">
              <img src="@renderer/assets/icons/video.svg" alt="视频" class="w-full h-full" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-white/90 text-2.75 font-medium truncate">已选择视频</div>
              <div class="text-white/60 text-2.25">点击发送按钮上传分析</div>
            </div>
            <button class="bg-red/20 border-none rounded-full w-4.5 h-4.5 flex items-center justify-center cursor-pointer text-white/80 transition-all-200 hover:bg-red/40 hover:text-white" @click="clearVideoWrapper">
              <n-icon size="10">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </n-icon>
            </button>
          </div>

          <div v-if="chatStore.pendingMedia.pdfImages && chatStore.pendingMedia.pdfImages.length > 0" class="bg-white/8 border border-white/15 rounded-1.5 px-2 py-1.5 flex items-center gap-2">
            <div class="w-8 h-8">
              <img src="@renderer/assets/icons/pdf3.svg" alt="PDF" class="w-full h-full" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-white/90 text-2.75 font-medium truncate">{{ chatStore.pendingMedia.pdfName || 'PDF文档' }} ({{ chatStore.pendingMedia.pdfImages.length }}页)</div>
              <div class="text-white/60 text-2.25">点击发送按钮上传分析</div>
            </div>
            <button class="bg-red/20 border-none rounded-full w-4.5 h-4.5 flex items-center justify-center cursor-pointer text-white/80 transition-all-200 hover:bg-red/40 hover:text-white" @click="clearPdfWrapper">
              <n-icon size="10">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </n-icon>
            </button>
          </div>

          <div v-if="chatStore.pendingMedia.pptImages && chatStore.pendingMedia.pptImages.length > 0" class="bg-white/8 border border-white/15 rounded-1.5 px-2 py-1.5 flex items-center gap-2">
            <div class="w-7 h-7">
              <img src="@renderer/assets/icons/ppt3.svg" alt="PPT" class="w-full h-full" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-white/90 text-2.75 font-medium truncate">{{ chatStore.pendingMedia.pptName || 'PPT文档' }} ({{ chatStore.pendingMedia.pptTotalPages || chatStore.pendingMedia.pptImages.length }}页)</div>
              <div class="text-white/60 text-2.25">点击发送按钮上传分析</div>
            </div>
            <button class="bg-red/20 border-none rounded-full w-4.5 h-4.5 flex items-center justify-center cursor-pointer text-white/80 transition-all-200 hover:bg-red/40 hover:text-white" @click="clearPptWrapper">
              <n-icon size="10">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </n-icon>
            </button>
          </div>
        </div>

        <div class="flex gap-1 items-center">
          <input ref="inputRef" v-model="inputMessage" class="flex-1 bg-white/5 border border-white/10 rounded px-1.5 py-1 text-white text-2.75 outline-none h-6 leading-1.2 placeholder:text-white/50" placeholder="输入消息... 支持Ctrl+V粘贴或拖拽文件上传" @keydown="handleKeyDown" @paste="handlePasteWrapper" @focus="handleInputFocus" @blur="handleInputBlur" />

          <div class="flex gap-0.5">
            <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
              <template #trigger>
                <button class="bg-white/10 border-none rounded text-white text-2.75 cursor-pointer px-1.5 py-1 transition-all-200 min-w-6 h-6 flex items-center justify-center hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="isFileUploading" @click="uploadFile">
                  <div v-if="isFileUploading" class="flex gap-0.5 items-center">
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both] animate-delay-[-0.32s]"></span>
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both] animate-delay-[-0.16s]"></span>
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both]"></span>
                  </div>
                  <n-icon v-else size="14">
                    <Upload />
                  </n-icon>
                </button>
              </template>
              {{ isFileUploading ? '处理中...' : '上传图片/视频/PDF/PPT' }}
            </n-tooltip>
            <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
              <template #trigger>
                <button class="bg-white/10 border-none rounded text-white text-2.75 cursor-pointer px-1.5 py-1 transition-all-200 min-w-6 h-6 flex items-center justify-center hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="isAnyOperationInProgress" @click="handleScreenshot" @contextmenu.prevent="toggleScreenshotMode">
                  <div v-if="(screenshotMode === 'area' && isAreaCapturing) || (screenshotMode === 'quick' && isQuickCapturing)" class="flex gap-0.5 items-center">
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both] animate-delay-[-0.32s]"></span>
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both] animate-delay-[-0.16s]"></span>
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both]"></span>
                  </div>
                  <n-icon v-else size="14">
                    <Cut v-if="screenshotMode === 'area'" />
                    <Camera v-else />
                  </n-icon>
                </button>
              </template>
              {{ screenshotMode === 'area' ? '区域截图' : '快速截图' }} (右键切换)
            </n-tooltip>
            <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
              <template #trigger>
                <button
                  class="bg-white/10 hover:bg-white/20 border-none rounded text-white text-2.75 cursor-pointer px-1.5 py-1 transition-all-200 min-w-6 h-6 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="isAnyOperationInProgress && !isRecordingLoading && !isAreaRecordingLoading"
                  @click="toggleScreenRecording"
                  @contextmenu.prevent="toggleRecordingModeOnly">
                  <div v-if="isRecordingLoading || isAreaRecordingLoading" class="flex gap-0.5 items-center">
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both] animate-delay-[-0.32s]"></span>
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both] animate-delay-[-0.16s]"></span>
                    <span class="w-1 h-1 bg-white/60 rounded-full animate-[loading-pulse_1.4s_ease-in-out_infinite_both]"></span>
                  </div>
                  <n-icon v-else size="14">
                    <svg v-if="recordingMode === 'screen'" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="12" r="10" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="currentColor">
                      <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="4 2" />
                      <circle cx="12" cy="12" r="3" fill="currentColor" />
                    </svg>
                  </n-icon>
                </button>
              </template>
              {{ recordingMode === 'screen' ? '录制屏幕' : '录制区域' }} (右键切换)
            </n-tooltip>
            <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
              <template #trigger>
                <button class="bg-blue/60 border-none rounded text-white text-2.75 cursor-pointer px-1.5 py-1 transition-all-200 min-w-6 h-6 flex items-center justify-center hover:bg-blue/80 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="!canSend" @click="sendMessage">
                  <n-icon size="14">
                    <Send />
                  </n-icon>
                </button>
              </template>
              发送消息
            </n-tooltip>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input ref="fileInput" type="file" accept="image/*,video/*,application/pdf,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation" style="display: none" @change="handleFileSelect" />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, computed, watch } from 'vue'
import { NTooltip, NIcon, useMessage } from 'naive-ui'
import { Send, Upload, Camera } from '@vicons/carbon'
import { Cut } from '@vicons/tabler'
import { useChatFunctions } from '../composables/useChatFunctions'
import VideoPlayer from './VideoPlayer.vue'

// 使用组合式函数
const {
  chatStore,
  extractThinkContent,
  removeThinkContent,
  formatAnswerBoxes,
  toggleThinkExpanded,
  isThinkExpanded,
  processFile,
  handlePaste,
  sendMessage: sendMessageCore,
  handleKeyDown: handleKeyDownCore,
  handleMessageClick,
  handleAreaScreenshot: handleAreaScreenshotCore,
  handleQuickScreenshot: handleQuickScreenshotCore,
  startScreenRecording,
  stopScreenRecording,
  startAreaScreenRecording,
  isRecording,
  cleanup
} = useChatFunctions((videoUrl: string, videoBase64: string) => {
  // 录制完成回调：自动将视频添加到输入框
  chatStore.setPendingMedia({
    video: videoUrl,
    videoBase64: videoBase64,
    image: undefined, // 清除已选择的图片
    pdfImages: undefined, // 清除已选择的PDF
    pdfName: undefined, // 清除PDF名称
    pptImages: undefined, // 清除已选择的PPT
    pptName: undefined // 清除PPT名称
  })
})

// 消息提示
const messageApi = useMessage()

// 本地录制功能包装
const toggleScreenRecording = async (): Promise<void> => {
  try {
    isRecordingLoading.value = true
    if (isRecording.value) {
      await stopScreenRecording()
    } else {
      if (recordingMode.value === 'screen') {
        await startScreenRecording()
      } else {
        await startAreaScreenRecording()
      }
    }
  } finally {
    isRecordingLoading.value = false
  }
}

// 本地状态变量
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement>()
const inputRef = ref<HTMLInputElement>()
const fileInput = ref<HTMLInputElement>()
const isInputFocused = ref(false)
const isPinned = ref(false)
const isRecordingLoading = ref(false) // 录制loading状态
const isAreaRecordingLoading = ref(false) // 区域录制loading状态
const isFileUploading = ref(false) // 文件上传loading状态
const isQuickCapturing = ref(false) // 快速截图loading状态
const isAreaCapturing = ref(false) // 区域截图loading状态

// 拖拽相关状态
const isDragOver = ref(false)
let dragCounter = 0 // 用于处理多个拖拽事件

// 截图和录屏模式切换状态
const screenshotMode = ref<'area' | 'quick'>('area') // 截图模式：区域截图或快速截图
const recordingMode = ref<'screen' | 'area'>('screen') // 录屏模式：全屏录制或区域录制

const canSend = computed(() => {
  return !chatStore.isLoading && (inputMessage.value.trim() || chatStore.pendingMedia.image || chatStore.pendingMedia.video || (chatStore.pendingMedia.pdfImages && chatStore.pendingMedia.pdfImages.length > 0) || (chatStore.pendingMedia.pptImages && chatStore.pendingMedia.pptImages.length > 0))
})

// 检查是否有任何录制或截图操作正在进行
const isAnyOperationInProgress = computed(() => {
  return isQuickCapturing.value || isAreaCapturing.value || isRecordingLoading.value || isAreaRecordingLoading.value || isRecording.value
})

// 窗口控制
const switchToMain = (): void => {
  if (window.api?.switchToMain) {
    window.api.switchToMain()
  }
}

const closeFloating = (): void => {
  if (window.api?.closeFloatingWindow) {
    window.api.closeFloatingWindow()
  }
}

// 新建对话处理函数
const startNewConversation = (): void => {
  // 调用 chatStore 的新建对话功能
  chatStore.startNewConversation()

  // 清空本地状态
  inputMessage.value = ''
  // 待发送媒体在startNewConversation中清空

  messageApi.success('已开始新对话', { duration: 1500 })
}

// 包装器函数 - 适配 composable 接口
const handleAreaScreenshot = async (): Promise<void> => {
  try {
    isAreaCapturing.value = true
    await handleAreaScreenshotCore(data => {
      chatStore.setPendingMedia({
        image: data || undefined,
        video: undefined, // 清除已选择的视频
        videoBase64: undefined, // 清除视频base64
        pdfImages: undefined, // 清除已选择的PDF
        pdfName: undefined, // 清除PDF名称
        pptImages: undefined, // 清除已选择的PPT
        pptName: undefined // 清除PPT名称
      })
    })
  } finally {
    isAreaCapturing.value = false
  }
}

const handleQuickScreenshot = async (): Promise<void> => {
  try {
    isQuickCapturing.value = true
    await handleQuickScreenshotCore(data => {
      chatStore.setPendingMedia({
        image: data || undefined,
        video: undefined, // 清除已选择的视频
        videoBase64: undefined, // 清除视频base64
        pdfImages: undefined, // 清除已选择的PDF
        pdfName: undefined, // 清除PDF名称
        pptImages: undefined, // 清除已选择的PPT
        pptName: undefined // 清除PPT名称
      })
    })
  } finally {
    isQuickCapturing.value = false
  }
}

// 截图功能 - 根据模式选择
const handleScreenshot = async (): Promise<void> => {
  if (screenshotMode.value === 'area') {
    await handleAreaScreenshot()
  } else {
    await handleQuickScreenshot()
  }
}

// 切换截图模式
const toggleScreenshotMode = (): void => {
  screenshotMode.value = screenshotMode.value === 'area' ? 'quick' : 'area'
}

// 切换录屏模式
const toggleRecordingModeOnly = (): void => {
  recordingMode.value = recordingMode.value === 'screen' ? 'area' : 'screen'
}

const processFileWrapper = async (file: File): Promise<void> => {
  await processFile(
    file,
    (data: string | null) => {
      chatStore.setPendingMedia({ image: data || undefined })
    },
    (data: string | null) => {
      chatStore.setPendingMedia({ video: data || undefined })
    },
    (data: string | null) => {
      chatStore.setPendingMedia({ videoBase64: data || undefined })
    },
    (data: string[] | null) => {
      chatStore.setPendingMedia({ pdfImages: data || undefined })
    },
    (name: string | null) => {
      chatStore.setPendingMedia({ pdfName: name || undefined })
    },
    (data: string[] | null) => {
      chatStore.setPendingMedia({ pptImages: data || undefined })
    },
    (name: string | null) => {
      chatStore.setPendingMedia({ pptName: name || undefined })
    },
    (totalPages: number | null) => {
      chatStore.setPendingMedia({ pptTotalPages: totalPages || undefined })
    }
  )
}

const clearImageWrapper = (): void => {
  chatStore.setPendingMedia({
    image: undefined,
    video: chatStore.pendingMedia.video,
    videoBase64: chatStore.pendingMedia.videoBase64,
    pdfImages: chatStore.pendingMedia.pdfImages,
    pdfName: chatStore.pendingMedia.pdfName,
    pptImages: chatStore.pendingMedia.pptImages,
    pptName: chatStore.pendingMedia.pptName,
    pptTotalPages: chatStore.pendingMedia.pptTotalPages
  })
}

const clearVideoWrapper = (): void => {
  chatStore.setPendingMedia({
    image: chatStore.pendingMedia.image,
    video: undefined,
    videoBase64: undefined,
    pdfImages: chatStore.pendingMedia.pdfImages,
    pdfName: chatStore.pendingMedia.pdfName,
    pptImages: chatStore.pendingMedia.pptImages,
    pptName: chatStore.pendingMedia.pptName,
    pptTotalPages: chatStore.pendingMedia.pptTotalPages
  })
}

const clearPdfWrapper = (): void => {
  chatStore.setPendingMedia({
    image: chatStore.pendingMedia.image,
    video: chatStore.pendingMedia.video,
    videoBase64: chatStore.pendingMedia.videoBase64,
    pdfImages: undefined,
    pdfName: undefined,
    pptImages: chatStore.pendingMedia.pptImages,
    pptName: chatStore.pendingMedia.pptName,
    pptTotalPages: chatStore.pendingMedia.pptTotalPages
  })
}

const clearPptWrapper = (): void => {
  chatStore.setPendingMedia({
    image: chatStore.pendingMedia.image, // 保留其他媒体
    video: chatStore.pendingMedia.video,
    videoBase64: chatStore.pendingMedia.videoBase64,
    pdfImages: chatStore.pendingMedia.pdfImages,
    pdfName: chatStore.pendingMedia.pdfName,
    pptImages: undefined,
    pptName: undefined,
    pptTotalPages: undefined
  })
}

const uploadFile = (): void => {
  fileInput.value?.click()
}

const handleFileSelect = async (event: Event): Promise<void> => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    isFileUploading.value = true
    await processFileWrapper(file)
  } catch (error) {
    console.error('文件处理失败:', error)
  } finally {
    isFileUploading.value = false
    target.value = ''
  }
}

const handleInputFocus = (): void => {
  isInputFocused.value = true
}

const handleInputBlur = (): void => {
  isInputFocused.value = false
}

const handleKeyDown = async (e: KeyboardEvent): Promise<void> => {
  await handleKeyDownCore(e, sendMessage)
}

// 复用媒体到输入框
const reuseMedia = (mediaData: string | string[], mediaType: 'image' | 'video' | 'pdf' | 'ppt', videoBase64?: string, fileName?: string, totalPages?: number): void => {
  try {
    // 清除当前所有选择的媒体
    chatStore.clearPendingMedia()

    // 根据媒体类型设置相应的数据
    switch (mediaType) {
      case 'image':
        if (typeof mediaData === 'string') {
          chatStore.setPendingMedia({ image: mediaData })
          messageApi.success('图片已添加到输入框', { duration: 1500 })
        }
        break
      case 'video':
        if (typeof mediaData === 'string') {
          chatStore.setPendingMedia({
            video: mediaData,
            videoBase64: videoBase64 || undefined
          })
          messageApi.success('视频已添加到输入框', { duration: 1500 })
        }
        break
      case 'pdf':
        if (Array.isArray(mediaData)) {
          chatStore.setPendingMedia({
            pdfImages: mediaData,
            pdfName: fileName || 'PDF文档'
          })
          messageApi.success('PDF已添加到输入框', { duration: 1500 })
        }
        break
      case 'ppt':
        if (Array.isArray(mediaData)) {
          chatStore.setPendingMedia({
            pptImages: mediaData,
            pptName: fileName || 'PPT文档',
            pptTotalPages: totalPages
          })
          messageApi.success('PPT已添加到输入框', { duration: 1500 })
        }
        break
    }
  } catch (error) {
    console.error('复用媒体失败:', error)
    messageApi.error('复用媒体失败，请重试')
  }
}

// 下载媒体文件
const downloadMedia = (mediaData: string, mediaType: 'image' | 'video'): void => {
  try {
    if (!mediaData) {
      messageApi.error('无效的媒体数据')
      return
    }

    const link = document.createElement('a')
    link.style.display = 'none'

    if (mediaData.startsWith('data:')) {
      // base64数据，直接下载
      link.href = mediaData
    } else if (mediaData.startsWith('blob:')) {
      // blob URL，直接下载
      link.href = mediaData
    } else {
      messageApi.error('不支持的媒体格式')
      return
    }

    // 设置文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const extension = mediaType === 'image' ? 'png' : 'mp4'
    link.download = `media_${timestamp}.${extension}`

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('下载失败:', error)
    messageApi.error('下载失败，请重试')
  }
}

const handlePasteWrapper = async (event: ClipboardEvent): Promise<void> => {
  // 粘贴文件时也要显示loading状态
  const originalCallback = processFileWrapper
  const wrappedCallback = async (file: File): Promise<void> => {
    try {
      isFileUploading.value = true
      await originalCallback(file)
    } catch (error) {
      console.error('粘贴文件处理失败:', error)
    } finally {
      isFileUploading.value = false
    }
  }
  await handlePaste(event, wrappedCallback)
}

const sendMessage = async (): Promise<void> => {
  if (!canSend.value) return

  const clearInputs = (): void => {
    inputMessage.value = ''
    // 待发送媒体在store的addUserMessage中清空
  }

  await sendMessageCore(inputMessage.value, chatStore.pendingMedia.image || '', chatStore.pendingMedia.video || '', chatStore.pendingMedia.videoBase64 || '', chatStore.pendingMedia.pdfImages || [], chatStore.pendingMedia.pdfName || '', chatStore.pendingMedia.pptImages || [], chatStore.pendingMedia.pptName || '', chatStore.pendingMedia.pptTotalPages || null, clearInputs, scrollToBottom)
}

const scrollToBottom = (): void => {
  if (messagesContainer.value) {
    setTimeout(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }, 10)
  }
}

// 置顶功能
const togglePin = async (): Promise<void> => {
  try {
    if (window.api?.toggleAlwaysOnTop) {
      const newState = await window.api.toggleAlwaysOnTop()
      isPinned.value = newState
    }
  } catch (error) {
    console.error('切换置顶状态失败:', error)
  }
}

// 获取当前置顶状态
const checkPinStatus = async (): Promise<void> => {
  try {
    if (window.api?.getAlwaysOnTopStatus) {
      isPinned.value = await window.api.getAlwaysOnTopStatus()
    }
  } catch (error) {
    console.error('获取置顶状态失败:', error)
  }
}

// 监听置顶状态刷新请求
const setupPinStatusListener = (): void => {
  if (window.api?.onRefreshPinStatus) {
    window.api.onRefreshPinStatus(async () => {
      // 当收到刷新请求时，重新查询自己的置顶状态
      await checkPinStatus()
    })
  }
}

// 清理置顶状态监听器
const cleanupPinStatusListener = (): void => {
  if (window.api?.offRefreshPinStatus) {
    window.api.offRefreshPinStatus(() => {})
  }
}

watch(
  () => chatStore.messages.length,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

onMounted(() => {
  scrollToBottom()
  checkPinStatus()
  setupPinStatusListener()

  // 添加新建对话快捷键监听器
  if (window.electron?.ipcRenderer) {
    window.electron.ipcRenderer.on('trigger-new-conversation', () => {
      startNewConversation()
    })
    window.electron.ipcRenderer.on('trigger-quick-screenshot', () => {
      handleQuickScreenshot()
    })
    window.electron.ipcRenderer.on('trigger-area-screenshot', () => {
      handleAreaScreenshot()
    })
  }

  // 添加录制停止loading状态监听器
  if ((window.api as any)?.onRecordingStopLoadingStart) {
    ;(window.api as any).onRecordingStopLoadingStart(() => {
      if (isRecording.value) {
        // 根据当前录制类型设置对应的loading状态
        isAreaRecordingLoading.value = true
        isRecordingLoading.value = true
      }
    })
  }

  if ((window.api as any)?.onRecordingStopLoadingEnd) {
    ;(window.api as any).onRecordingStopLoadingEnd(() => {
      isAreaRecordingLoading.value = false
      isRecordingLoading.value = false
    })
  }
})

onUnmounted(() => {
  // 清理新建对话快捷键监听器
  if (window.electron?.ipcRenderer) {
    window.electron.ipcRenderer.removeAllListeners('trigger-new-conversation')
    window.electron.ipcRenderer.removeAllListeners('trigger-quick-screenshot')
    window.electron.ipcRenderer.removeAllListeners('trigger-area-screenshot')
  }

  // 清理录制loading状态监听器
  if ((window.api as any)?.offRecordingStopLoadingStart) {
    ;(window.api as any).offRecordingStopLoadingStart(() => {})
  }
  if ((window.api as any)?.offRecordingStopLoadingEnd) {
    ;(window.api as any).offRecordingStopLoadingEnd(() => {})
  }

  cleanupPinStatusListener()
  cleanup()
})

// 拖拽处理函数
const handleDragEnter = (event: DragEvent): void => {
  event.preventDefault()
  event.stopPropagation()

  // 检查是否包含文件
  if (event.dataTransfer?.types.includes('Files')) {
    dragCounter++
    isDragOver.value = true
  }
}

const handleDragOver = (event: DragEvent): void => {
  event.preventDefault()
  event.stopPropagation()

  // 检查是否包含文件
  if (event.dataTransfer?.types.includes('Files')) {
    // 设置拖拽效果
    event.dataTransfer.dropEffect = 'copy'
    if (!isDragOver.value) {
      dragCounter++
      isDragOver.value = true
    }
  }
}

const handleDragLeave = (event: DragEvent): void => {
  event.preventDefault()
  event.stopPropagation()

  dragCounter--
  if (dragCounter <= 0) {
    dragCounter = 0
    isDragOver.value = false
  }
}

const handleDrop = async (event: DragEvent): Promise<void> => {
  event.preventDefault()
  event.stopPropagation()

  dragCounter = 0
  isDragOver.value = false

  const files = event.dataTransfer?.files
  if (!files || files.length === 0) return

  const file = files[0]

  // 检查文件类型
  const allowedTypes = ['image/', 'video/', 'application/pdf', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']

  const isAllowedType = allowedTypes.some(type => file.type.startsWith(type) || file.type === type)

  if (!isAllowedType) {
    // 在悬浮窗中使用更简洁的错误提示
    console.warn('不支持的文件类型')
    return
  }

  // 显示上传中状态
  isFileUploading.value = true

  try {
    await processFileWrapper(file)

    // 显示简洁的成功提示
    console.log('文件拖拽上传成功')
  } catch (error) {
    console.error('拖拽文件处理失败:', error)
  } finally {
    isFileUploading.value = false
  }
}
</script>

<style scoped>
/* 拖拽区域 */
.drag-region {
  -webkit-app-region: drag;
}

.no-drag {
  -webkit-app-region: no-drag;
}

/* 加载动画 */
@keyframes loading-pulse {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }

  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 滚动条自定义样式（UnoCSS 无法完全覆盖 webkit 滚动条） */
.scrollbar::-webkit-scrollbar {
  width: 4px;
}

.scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
}

.scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 拖拽样式 - 悬浮窗适配 */
.drag-over {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(37, 99, 235, 0.06)) !important;
  position: relative;
}

.drag-overlay-floating {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.88);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border: 1px dashed rgba(59, 130, 246, 0.7);
  border-radius: 8px;
  animation: dragOverlayFloating 0.2s ease-out;
}

.drag-indicator-floating {
  text-align: center;
  color: #60a5fa;
  /* 移除跳动动画 */
}

.drag-icon-floating {
  margin: 0 auto 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.2);
  border-radius: 50%;
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.drag-text-floating {
  user-select: none;
}

.drag-title-floating {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #60a5fa;
}

.drag-subtitle-floating {
  font-size: 11px;
  color: #94a3b8;
  opacity: 0.9;
}

@keyframes dragOverlayFloating {
  from {
    opacity: 0;
    transform: scale(0.98);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 媒体hover效果 */
.media-hover-container {
  position: relative;
  display: inline-block;
}

/* 媒体操作按钮 */
.media-action-buttons {
  position: absolute;
  top: 4px;
  left: 4px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
  z-index: 10;
}

.media-hover-container:hover .media-action-buttons {
  opacity: 1;
  pointer-events: auto;
}

.media-action-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.media-action-btn:hover {
  background: rgba(0, 0, 0, 0.8);
  border-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.media-action-btn:active {
  transform: scale(0.95);
}
</style>
