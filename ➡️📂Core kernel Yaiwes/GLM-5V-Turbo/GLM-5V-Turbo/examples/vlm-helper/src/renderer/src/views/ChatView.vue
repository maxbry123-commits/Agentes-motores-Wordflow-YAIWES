<template>
  <div class="flex flex-col h-full w-full overflow-hidden bg-black relative" @dragover="handleDragOver" @dragenter="handleDragEnter" @dragleave="handleDragLeave" @drop="handleDrop">
    <!-- 全局星空背景层 -->
    <div v-if="settingsStore.settings.starryBackground" class="starfield-global">
      <div class="stars"></div>
      <div class="stars2"></div>
      <div class="stars3"></div>
    </div>

    <!-- 全局拖拽提示层 -->
    <div v-if="isDragOver" class="drag-overlay-global">
      <div class="drag-indicator-global">
        <div class="drag-icon-container">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
            <polyline points="14,2 14,8 20,8" />
          </svg>
          <div class="drag-upload-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17,8 12,3 7,8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
        </div>
        <div class="drag-text">
          <div class="drag-title">释放文件以上传</div>
          <div class="drag-subtitle">支持图片、视频、PDF、PPT文件</div>
        </div>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 pb-0 bg-gradient-to-br from-neutral-950/30 to-black/20 relative z-10" :class="{ 'drag-over': isDragOver }">
      <div v-for="msg in chatStore.messages" :id="`message-${msg.id}`" :key="msg.id" class="mb-2 relative z-10 group" :class="msg.role">
        <div class="flex items-start">
          <!-- 用户消息 -->
          <div v-if="msg.role === 'user'" class="ml-auto flex flex-col items-end">
            <div v-if="msg.image" class="mb-2 flex items-center gap-2 media-container">
              <!-- 媒体操作按钮 -->
              <div class="media-action-buttons-external">
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="reuseMedia(msg.image, 'image')">
                      <n-icon size="16">
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
                    <button class="media-action-btn" @click.stop="downloadMedia(msg.image, 'image')">
                      <n-icon size="16">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  下载图片
                </n-tooltip>
              </div>
              <div class="relative media-hover-container">
                <img :src="msg.image" alt="用户上传的图片" class="max-w-300px max-h-200px rounded-lg shadow-md border border-neutral-700 cursor-pointer transition-all duration-200" @click="openPreview(msg.image, 'image')" />
                <div class="media-hover-overlay">
                  <n-icon size="24" class="eye-icon">
                    <View />
                  </n-icon>
                </div>
              </div>
            </div>
            <div v-if="msg.video" class="mb-2 flex items-center gap-2 media-container">
              <!-- 媒体操作按钮 -->
              <div class="media-action-buttons-external">
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="reuseMedia(msg.video, 'video', msg.videoBase64)">
                      <n-icon size="16">
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
                    <button class="media-action-btn" @click.stop="downloadMedia(msg.video || msg.videoBase64 || '', 'video')">
                      <n-icon size="16">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  下载视频
                </n-tooltip>
              </div>
              <div class="relative media-hover-container">
                <VideoPlayer :src="msg.video" :video-base64="msg.videoBase64" class="max-w-300px max-h-200px rounded-lg shadow-md border border-neutral-700 cursor-pointer transition-all duration-200" @click="openPreview(msg.video, 'video', msg.videoBase64)" />
                <div class="media-hover-overlay">
                  <n-icon size="24" class="eye-icon">
                    <View />
                  </n-icon>
                </div>
              </div>
            </div>
            <div v-if="msg.pdfImages && msg.pdfImages.length > 0" class="mb-2 flex items-center gap-2 media-container">
              <!-- 媒体操作按钮 -->
              <div class="media-action-buttons-external">
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="reuseMedia(msg.pdfImages, 'pdf', undefined, msg.pdfName)">
                      <n-icon size="16">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  复用PDF
                </n-tooltip>
              </div>
              <div class="bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 flex items-center space-x-2 max-w-200px">
                <div class="text-lg w-8 h-8">
                  <img src="@renderer/assets/icons/pdf3.svg" alt="PDF" class="w-full h-full" />
                </div>
                <div class="text-neutral-300 flex-1 min-w-0">
                  <div class="text-sm font-medium truncate">{{ msg.pdfName || 'PDF文档' }}</div>
                  <div class="text-xs text-neutral-400">{{ msg.pdfImages.length }}页</div>
                </div>
              </div>
            </div>
            <div v-if="msg.pptImages && msg.pptImages.length > 0" class="mb-2 flex items-center gap-2 media-container">
              <!-- 媒体操作按钮 -->
              <div class="media-action-buttons-external">
                <n-tooltip trigger="hover" placement="top" :show-arrow="false">
                  <template #trigger>
                    <button class="media-action-btn" @click.stop="reuseMedia(msg.pptImages, 'ppt', undefined, msg.pptName, msg.pptTotalPages)">
                      <n-icon size="16">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                        </svg>
                      </n-icon>
                    </button>
                  </template>
                  复用PPT
                </n-tooltip>
              </div>
              <div class="bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 flex items-center space-x-2 max-w-200px">
                <div class="text-lg w-8 h-8">
                  <img src="@renderer/assets/icons/ppt3.svg" alt="PPT" class="w-full h-full" />
                </div>
                <div class="text-neutral-300 flex-1 min-w-0">
                  <div class="text-sm font-medium truncate">{{ msg.pptName || 'PPT文档' }}</div>
                  <div class="text-xs text-neutral-400">{{ msg.pptTotalPages || msg.pptImages.length }}页</div>
                </div>
              </div>
            </div>
            <div v-if="msg.content" class="bg-neutral-800/90 backdrop-blur-sm text-white px-3 py-2 rounded-xl break-words border border-neutral-700/40">
              {{ msg.content }}
            </div>
            <!-- 用户消息时间 - 悬浮时显示 -->
            <div v-if="msg.timestamp" class="text-xs text-neutral-500 mt-1 text-right opacity-0 group-hover:opacity-100 transition-opacity duration-200" :title="formatDetailedTime(msg.timestamp)">
              {{ formatMessageTime(msg.timestamp) }}
            </div>
          </div>

          <!-- AI回复 -->
          <div v-else class="flex flex-col w-100%">
            <!-- 思考块 -->
            <div v-if="extractThinkContent(msg.content || '')" class="mb-2">
              <div class="bg-neutral-800/60 backdrop-blur-sm px-3 py-2 rounded-lg border border-neutral-700/40 think-block">
                <div class="think-header select-none">
                  <span class="think-icon">🤔</span>
                  <span class="think-label">思考过程</span>
                  <button class="think-toggle" @click="toggleThinkExpanded(msg.id)">
                    <span v-if="isThinkExpanded(msg.id)">收起</span>
                    <span v-else>展开</span>
                  </button>
                </div>
                <div v-if="isThinkExpanded(msg.id)" class="think-content">
                  <div class="prose prose-sm max-w-none prose-p:text-neutral-400 prose-p:my-1 whitespace-pre-wrap text-neutral-400 text-sm leading-5">
                    {{ extractThinkContent(msg.content || '') }}
                  </div>
                </div>
              </div>
            </div>
            <!-- AI回复内容 -->
            <div v-if="removeThinkContent(msg.content || '').trim()" class="flex items-start w-full mb-2">
              <div class="bg-neutral-900/80 backdrop-blur-sm px-3 w-full py-1 rounded-xl shadow-sm border border-neutral-800/60">
                <MarkdownRenderer
                  :content="removeAnswerBoxes(removeThinkContent(msg.content || ''))"
                  class="prose prose-sm max-w-none prose-headings:text-white prose-p:text-neutral-200 prose-code:bg-neutral-700/60 prose-code:text-neutral-100 prose-code:px-1 prose-code:rounded prose-code:break-words prose-strong:text-white prose-em:text-neutral-200 prose-p:my-2 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-li:my-0 prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline prose-blockquote:text-neutral-300 prose-blockquote:border-neutral-600 prose-hr:border-neutral-600 prose-th:text-white prose-td:text-neutral-200 prose-pre:bg-transparent prose-pre:p-0 prose-pre:m-0 ai-response" />
              </div>
            </div>
            <!-- 答案块 -->
            <div v-if="extractAnswerBoxes(msg.content || '').length > 0">
              <div v-for="(answer, index) in extractAnswerBoxes(msg.content || '')" :key="`${msg.id}-answer-${index}`" class="bg-green-800/20 backdrop-blur-sm px-3 py-2 rounded-lg border border-green-600/40 answer-block mb-2">
                <div class="answer-header select-none">
                  <span class="answer-label">答案</span>
                </div>
                <div class="answer-content">
                  <MarkdownRenderer :content="answer" class="prose prose-sm max-w-none prose-p:text-green-100 prose-p:my-1 prose-strong:text-green-100 prose-em:text-green-100 prose-headings:text-green-100 prose-code:bg-green-900/40 prose-code:text-green-100 prose-ul:text-green-100 prose-ol:text-green-100 prose-li:text-green-100 text-green-100 text-sm leading-5 font-medium" />
                </div>
              </div>
            </div>
            <!-- AI回复时间 - 悬浮时显示 -->
            <div v-if="msg.timestamp" class="text-xs text-neutral-500 mt-1 ml-0 w-[70%] opacity-0 group-hover:opacity-100 transition-opacity duration-200" :title="formatDetailedTime(msg.timestamp)">
              {{ formatMessageTime(msg.timestamp) }}
            </div>
          </div>
        </div>
      </div>
      <!-- 加载状态 -->
      <div v-if="chatStore.isLoading" class="mb-2 assistant relative z-10">
        <div class="flex items-start">
          <div class="flex items-start w-full">
            <div class="bg-neutral-900/80 backdrop-blur-sm px-3 py-2 rounded-2xl shadow-sm border border-neutral-800/60 flex items-center space-x-2 inline-flex">
              <div class="loading-indicator">
                <div class="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div class="loading-text">VLM正在思考中...</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="bg-neutral-950/90 backdrop-blur-sm border-t border-neutral-800 p-4 relative z-10 flex-shrink-0">
      <!-- 图片预览 -->
      <div v-if="chatStore.pendingMedia.image" class="relative mb-3 inline-block">
        <img :src="chatStore.pendingMedia.image" alt="待发送图片" class="max-w-200px max-h-150px rounded-lg shadow-md border border-neutral-700" />
        <n-button circle size="tiny" type="error" class="absolute -top-1 -right-1" @click="clearImageWrapper">
          <template #icon>
            <n-icon size="12">
              <Close />
            </n-icon>
          </template>
        </n-button>
      </div>

      <!-- 视频预览 -->
      <div v-if="chatStore.pendingMedia.video" class="relative mb-3 inline-block">
        <VideoPlayer :src="chatStore.pendingMedia.video" :video-base64="chatStore.pendingMedia.videoBase64" class="max-w-200px max-h-150px rounded-lg shadow-md border border-neutral-700" />
        <n-button circle size="tiny" type="error" class="absolute -top-1 -right-1" @click="clearVideoWrapper">
          <template #icon>
            <n-icon size="12">
              <Close />
            </n-icon>
          </template>
        </n-button>
      </div>

      <!-- PDF预览 -->
      <div v-if="chatStore.pendingMedia.pdfImages && chatStore.pendingMedia.pdfImages.length > 0" class="relative mb-3 inline-block">
        <div class="bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 flex items-center space-x-2">
          <div class="text-lg w-8 h-8">
            <img src="@renderer/assets/icons/pdf3.svg" alt="PDF" class="w-full h-full" />
          </div>
          <div class="text-neutral-300">
            <div class="text-sm font-medium">{{ chatStore.pendingMedia.pdfName || 'PDF文档' }}</div>
            <div class="text-xs text-neutral-400">{{ chatStore.pendingMedia.pdfImages.length }}页</div>
          </div>
        </div>
        <n-button circle size="tiny" type="error" class="absolute -top-1 -right-1" @click="clearPdfWrapper">
          <template #icon>
            <n-icon size="12">
              <Close />
            </n-icon>
          </template>
        </n-button>
      </div>

      <!-- PPT预览 -->
      <div v-if="chatStore.pendingMedia.pptImages && chatStore.pendingMedia.pptImages.length > 0" class="relative mb-3 inline-block">
        <div class="bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 flex items-center space-x-2">
          <div class="text-lg w-8 h-8">
            <img src="@renderer/assets/icons/ppt3.svg" alt="PPT" class="w-full h-full" />
          </div>
          <div class="text-neutral-300">
            <div class="text-sm font-medium">{{ chatStore.pendingMedia.pptName || 'PPT文档' }}</div>
            <div class="text-xs text-neutral-400">{{ chatStore.pendingMedia.pptTotalPages || chatStore.pendingMedia.pptImages.length }}页</div>
          </div>
        </div>
        <n-button circle size="tiny" type="error" class="absolute -top-1 -right-1" @click="clearPptWrapper">
          <template #icon>
            <n-icon size="12">
              <Close />
            </n-icon>
          </template>
        </n-button>
      </div>

      <!-- 输入框和按钮 -->
      <div class="flex items-end space-x-3">
        <div class="flex space-x-2">
          <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
            <template #trigger>
              <n-button circle :loading="isQuickCapturing" :disabled="isAnyOperationInProgress && !isQuickCapturing" @click="captureScreen">
                <template #icon>
                  <n-icon>
                    <Camera />
                  </n-icon>
                </template>
              </n-button>
            </template>
            快速截图
          </n-tooltip>

          <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
            <template #trigger>
              <n-button circle :loading="isAreaCapturing" :disabled="isAnyOperationInProgress && !isAreaCapturing" @click="captureScreenArea">
                <template #icon>
                  <n-icon>
                    <Cut />
                  </n-icon>
                </template>
              </n-button>
            </template>
            区域截图
          </n-tooltip>

          <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
            <template #trigger>
              <n-button circle :type="recordingType === 'screen' ? 'error' : 'default'" :disabled="(isAnyOperationInProgress && !isRecordingLoading) || (isRecording && recordingType !== 'screen')" :loading="isRecordingLoading" @click="toggleScreenRecording">
                <template #icon>
                  <n-icon>
                    <svg v-if="recordingType === 'screen'" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="6" y="6" width="12" height="12" rx="2" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="12" r="10" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  </n-icon>
                </template>
              </n-button>
            </template>
            {{ recordingType === 'screen' ? '停止录制' : '开始录制屏幕' }}
          </n-tooltip>

          <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
            <template #trigger>
              <n-button circle :type="recordingType === 'area' ? 'error' : 'default'" :disabled="(isAnyOperationInProgress && !isAreaRecordingLoading) || (isRecording && recordingType !== 'area')" :loading="isAreaRecordingLoading" @click="toggleAreaScreenRecording">
                <template #icon>
                  <n-icon>
                    <svg v-if="recordingType === 'area'" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="6" y="6" width="12" height="12" rx="2" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="currentColor">
                      <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="4 2" />
                      <circle cx="12" cy="12" r="3" fill="currentColor" />
                    </svg>
                  </n-icon>
                </template>
              </n-button>
            </template>
            {{ recordingType === 'area' ? '停止录制' : '区域录制屏幕' }}
          </n-tooltip>

          <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
            <template #trigger>
              <n-button circle :loading="isFileUploading" @click="uploadFile">
                <template #icon>
                  <n-icon>
                    <Upload />
                  </n-icon>
                </template>
              </n-button>
            </template>
            上传图片/视频/PDF/PPT
          </n-tooltip>
        </div>

        <n-input ref="inputRef" v-model:value="inputText" type="textarea" :autosize="{ minRows: 1, maxRows: 4 }" placeholder="输入你的问题... 支持Ctrl+V粘贴图片/视频，拖拽文件上传，或点击按钮上传PDF/PPT文档" class="flex-1" @keydown="handleKeydown" @paste="handleInputPaste" />

        <n-button type="primary" :disabled="!canSend" @click="sendMessage">
          <template v-if="chatStore.isLoading" #icon>
            <div class="send-loading">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-dasharray="15 5" />
              </svg>
            </div>
          </template>
          发送
        </n-button>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input ref="fileInput" type="file" accept="image/*,video/*,application/pdf,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation" style="display: none" @change="handleFileSelect" />

    <!-- 媒体预览Modal -->
    <div v-if="showPreview" class="media-preview-modal" @click="closePreview">
      <div class="modal-backdrop"></div>
      <div class="modal-content" @click.stop>
        <button class="modal-close-btn" @click.stop="closePreview">
          <n-icon size="16">
            <Close />
          </n-icon>
        </button>
        <div class="media-container">
          <img v-if="previewType === 'image'" :src="previewSrc" alt="预览图片" class="preview-media" />
          <VideoPlayer v-if="previewType === 'video'" :src="previewSrc" :video-base64="previewVideoBase64" class="preview-media" autoplay />
        </div>
      </div>
    </div>

    <!-- HTML预览Modal -->
    <div v-if="showHtmlPreview" class="html-preview-modal" @click="closeHtmlPreview">
      <div class="modal-backdrop"></div>
      <div class="modal-content html-preview-content" @click.stop>
        <div class="html-preview-header">
          <h3>HTML 预览</h3>
          <button class="modal-close-btn" @click.stop="closeHtmlPreview">
            <n-icon size="18">
              <Close />
            </n-icon>
          </button>
        </div>
        <div class="html-preview-container">
          <div class="rendered-content" v-html="htmlPreviewContent"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import '../assets/themes/one-dark-pro.css' // One Dark Pro
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { NInput, NButton, useMessage, NIcon, NTooltip } from 'naive-ui'
import { Camera, Close, Upload, View } from '@vicons/carbon'
import { Cut } from '@vicons/tabler'
import { useChatFunctions } from '../composables/useChatFunctions'
import { formatMessageTime, formatDetailedTime } from '../utils/timeFormat'
import VideoPlayer from '../components/VideoPlayer.vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'

const message = useMessage()

import { useSettingsStore } from '../stores/settingsStore'
const settingsStore = useSettingsStore()

const {
  chatStore,
  extractThinkContent,
  removeThinkContent,
  extractAnswerBoxes,
  removeAnswerBoxes,
  toggleThinkExpanded,
  isThinkExpanded,
  processFile,
  handlePaste,
  sendMessage: sendMessageCore,
  handleKeyDown: handleKeyDownCore,
  handleQuickScreenshot: handleQuickScreenshotCore,
  handleAreaScreenshot: handleAreaScreenshotCore,
  startScreenRecording,
  stopScreenRecording,
  startAreaScreenRecording,
  isRecording,
  recordingType,
  isCompressing,
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

const inputText = ref('')
const isQuickCapturing = ref(false) // 快速截图loading状态
const isAreaCapturing = ref(false) // 区域截图loading状态
const isRecordingLoading = ref(false) // 录制loading状态
const isAreaRecordingLoading = ref(false) // 区域录制loading状态
const isFileUploading = ref(false) // 文件上传loading状态

// 拖拽相关状态
const isDragOver = ref(false)
let dragCounter = 0 // 用于处理多个拖拽事件

// 媒体预览相关
const showPreview = ref(false)
const previewSrc = ref('')
const previewType = ref<'image' | 'video'>('image')
const previewVideoBase64 = ref('')

// HTML预览相关
const showHtmlPreview = ref(false)
const htmlPreviewContent = ref('')

const messagesContainer = ref<HTMLElement>()
const fileInput = ref<HTMLInputElement>()
const inputRef = ref()

// 滚动状态
let scrollTimeout: ReturnType<typeof setTimeout> | null = null

watch(
  () => chatStore.messages.length,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  },
  { flush: 'post' }
)

watch(
  () => chatStore.messages,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  },
  { deep: true, immediate: true, flush: 'post' }
)

watch(
  () => chatStore.isLoading,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  },
  { flush: 'post' }
)

const canSend = computed(() => {
  return (inputText.value.trim() || chatStore.pendingMedia.image || chatStore.pendingMedia.video || (chatStore.pendingMedia.pdfImages && chatStore.pendingMedia.pdfImages.length > 0) || (chatStore.pendingMedia.pptImages && chatStore.pendingMedia.pptImages.length > 0)) && !chatStore.isLoading && !isRecording.value
})

const isAnyOperationInProgress = computed(() => {
  return isQuickCapturing.value || isAreaCapturing.value || isRecordingLoading.value || isAreaRecordingLoading.value || isRecording.value || isCompressing.value
})

async function handleInputPaste(event: ClipboardEvent): Promise<void> {
  await handlePaste(event, (file: File) => {
    processFile(
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
  })
}

// 处理滚动条显示/隐藏
function handleScroll(): void {
  const container = messagesContainer.value
  if (!container) return

  // 添加滚动中的类
  container.classList.add('scrolling')

  // 清除之前的定时器
  if (scrollTimeout) {
    clearTimeout(scrollTimeout)
  }

  // 设置新的定时器，滚动停止后隐藏滚动条
  scrollTimeout = setTimeout(() => {
    container.classList.remove('scrolling')
  }, 200) // 0.2秒后开始淡退
}

onMounted(() => {
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', handleScroll)
  }

  document.addEventListener('keydown', handleGlobalKeydown)

  window.electron.ipcRenderer.on('trigger-quick-screenshot', () => {
    captureScreen()
  })

  window.electron.ipcRenderer.on('trigger-area-screenshot', () => {
    captureScreenArea()
  })

  window.addEventListener('storage', handleStorageClearEvent)

  if ((window.api as any)?.onRecordingStopLoadingStart) {
    ;(window.api as any).onRecordingStopLoadingStart(() => {
      if (recordingType.value === 'area') {
        isAreaRecordingLoading.value = true
      } else {
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

  // 添加欢迎消息
  chatStore.addWelcomeMessageIfNeeded()

  // 确保在组件完全加载和消息渲染后滚动到底部
  nextTick().then(() => {
    // 延迟一点时间确保所有内容都已渲染
    setTimeout(() => {
      scrollToBottom()
    }, 300)
  })

  // 添加全局复制代码函数
  ;(window as unknown as Record<string, unknown>).copyCode = (codeId: string) => {
    const codeElement = document.getElementById(codeId)
    if (codeElement) {
      const text = codeElement.textContent || ''
      navigator.clipboard
        .writeText(text)
        .then(() => {
          message.success('代码已复制到剪贴板', { duration: 1500 })
        })
        .catch(() => {
          message.error('复制失败')
        })
    }
  }

  // 添加全局HTML预览函数
  ;(window as unknown as Record<string, unknown>).openHtmlPreview = (codeId: string) => {
    openHtmlPreview(codeId)
  }

  // 添加localStorage监听器来处理切换到指定消息的事件
  window.addEventListener('storage', e => {
    if (e.key === 'vlm-chat-switch-to-message' && e.newValue) {
      handleSwitchToMessage()
    }
  })

  // 页面加载时检查是否有待处理的消息定位请求
  handleSwitchToMessage()
}) // 全局键盘事件处理
function handleGlobalKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    if (showHtmlPreview.value) {
      closeHtmlPreview()
    } else if (showPreview.value) {
      closePreview()
    }
  }
}

// 处理切换到指定消息的事件
function handleSwitchToMessage(): void {
  const switchData = localStorage.getItem('vlm-chat-switch-to-message')
  if (switchData) {
    try {
      const { messageId } = JSON.parse(switchData)
      // 清除事件数据
      localStorage.removeItem('vlm-chat-switch-to-message')

      // 多次尝试定位，确保DOM已完全渲染和消息已加载
      const attemptScroll = (attempts = 0): void => {
        const messageElement = document.getElementById(`message-${messageId}`)
        if (messageElement && messagesContainer.value) {
          // 确保滚动容器已渲染并且有内容
          if (messagesContainer.value.scrollHeight > 0) {
            messageElement.scrollIntoView({
              behavior: 'smooth',
              block: 'center'
            })

            // 添加更明显的高亮效果
            messageElement.style.transition = 'all 0.2s ease'
            messageElement.style.backgroundColor = 'rgba(59, 130, 246, 0.3)'
            messageElement.style.boxShadow = '0 0 0 2px rgba(59, 130, 246, 0.5)'
            messageElement.style.borderRadius = '8px'

            setTimeout(() => {
              messageElement.style.transition = 'all 0.5s ease'
              messageElement.style.backgroundColor = ''
              messageElement.style.boxShadow = ''
              messageElement.style.borderRadius = ''
            }, 1500)
          } else if (attempts < 10) {
            // 如果滚动容器还没有内容，继续重试
            setTimeout(() => attemptScroll(attempts + 1), 100)
          }
        } else if (attempts < 10) {
          // 如果消息元素还没找到，继续重试
          setTimeout(() => attemptScroll(attempts + 1), 100)
        }
      }

      // 使用 nextTick 确保 Vue 渲染完成，然后开始定位尝试
      nextTick(() => {
        setTimeout(() => attemptScroll(), 50)
      })
    } catch (error) {
      console.error('解析切换消息数据失败:', error)
    }
  }
}

// 组件卸载时清理
onUnmounted(() => {
  if (messagesContainer.value) {
    messagesContainer.value.removeEventListener('scroll', handleScroll)
  }
  if (scrollTimeout) {
    clearTimeout(scrollTimeout)
  }

  document.removeEventListener('keydown', handleGlobalKeydown)
  window.removeEventListener('trigger-quick-screenshot', () => {})
  window.removeEventListener('trigger-area-screenshot', () => {})
  window.removeEventListener('storage', handleStorageClearEvent)

  if (window.api?.offRecordingStopLoadingStart) {
    window.api.offRecordingStopLoadingStart(() => {})
  }
  if (window.api?.offRecordingStopLoadingEnd) {
    window.api.offRecordingStopLoadingEnd(() => {})
  }

  document.body.style.overflow = 'auto'
  cleanup()
})

// 截图功能包装函数
async function captureScreen(): Promise<void> {
  try {
    isQuickCapturing.value = true
    await handleQuickScreenshotCore((data: string | null) => {
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

// 录制功能包装函数
async function toggleScreenRecording(): Promise<void> {
  try {
    isRecordingLoading.value = true
    if (isRecording.value) {
      await stopScreenRecording()
    } else {
      await startScreenRecording()
    }
  } finally {
    isRecordingLoading.value = false
  }
}

// 区域录制功能包装函数
async function toggleAreaScreenRecording(): Promise<void> {
  try {
    isAreaRecordingLoading.value = true
    if (isRecording.value) {
      await stopScreenRecording()
    } else {
      await startAreaScreenRecording()
    }
  } finally {
    isAreaRecordingLoading.value = false
  }
}

// 区域截图功能包装函数
async function captureScreenArea(): Promise<void> {
  try {
    isAreaCapturing.value = true
    await handleAreaScreenshotCore((data: string | null) => {
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

// 上传文件（图片或视频）
function uploadFile(): void {
  fileInput.value?.click()
}

async function handleFileSelect(event: Event): Promise<void> {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  // 检查文件大小限制 (50MB)
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    message.error('文件大小超过限制（50MB），请选择更小的文件')
    ;(event.target as HTMLInputElement).value = ''
    return
  }

  try {
    // 开始上传loading状态
    isFileUploading.value = true

    if (file.type.startsWith('image/')) {
      // 检查图片大小限制 (10MB)
      const imageMaxSize = 10 * 1024 * 1024 // 10MB
      if (file.size > imageMaxSize) {
        message.error('图片文件大小超过限制（10MB），请选择更小的图片')
        ;(event.target as HTMLInputElement).value = ''
        return
      }

      // 图片直接使用base64
      const reader = new FileReader()
      reader.onload = e => {
        chatStore.setPendingMedia({
          image: e.target?.result as string,
          video: undefined,
          videoBase64: undefined,
          pdfImages: undefined,
          pdfName: undefined,
          pptImages: undefined,
          pptName: undefined
        })
        message.success('图片上传成功')
      }
      reader.readAsDataURL(file)
    } else if (file.type.startsWith('video/')) {
      // 检查视频大小限制 (20MB)
      const videoMaxSize = 20 * 1024 * 1024 // 20MB
      if (file.size > videoMaxSize) {
        message.error('视频文件大小超过限制（20MB），请选择更小的视频或进行压缩')
        ;(event.target as HTMLInputElement).value = ''
        return
      }

      // 直接使用 base64 data URL，更简单可靠
      const reader = new FileReader()
      reader.onload = e => {
        const result = e.target?.result as string
        chatStore.setPendingMedia({
          video: result,
          videoBase64: result,
          image: undefined,
          pdfImages: undefined,
          pdfName: undefined,
          pptImages: undefined,
          pptName: undefined
        })
        message.success('视频上传成功')
      }
      reader.readAsDataURL(file)
    } else if (file.type === 'application/pdf' || file.type === 'application/vnd.ms-powerpoint' || file.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation') {
      // 使用processFile函数处理PDF和PPT
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
    } else {
      message.error('不支持的文件类型，请选择图片、视频、PDF或PPT文件')
      ;(event.target as HTMLInputElement).value = ''
    }
  } catch (error) {
    console.error('文件上传处理失败:', error)
    message.error('文件处理失败，请重试')
    ;(event.target as HTMLInputElement).value = ''
  } finally {
    // 结束loading状态
    isFileUploading.value = false
  }
}

// 清除图片的包装函数
function clearImageWrapper(): void {
  chatStore.setPendingMedia({ image: undefined })
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 清除视频的包装函数
function clearVideoWrapper(): void {
  if (chatStore.pendingMedia.video && chatStore.pendingMedia.video.startsWith('blob:')) {
    URL.revokeObjectURL(chatStore.pendingMedia.video)
  }
  chatStore.setPendingMedia({ video: undefined, videoBase64: undefined })
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 清除PDF的包装函数
function clearPdfWrapper(): void {
  chatStore.setPendingMedia({ pdfImages: undefined, pdfName: undefined })
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 清除PPT的包装函数
function clearPptWrapper(): void {
  chatStore.setPendingMedia({ pptImages: undefined, pptName: undefined, pptTotalPages: undefined })
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 复用媒体到输入框
function reuseMedia(mediaData: string | string[], mediaType: 'image' | 'video' | 'pdf' | 'ppt', videoBase64?: string, fileName?: string, totalPages?: number): void {
  try {
    // 清除当前所有选择的媒体
    chatStore.clearPendingMedia()

    // 根据媒体类型设置相应的数据
    switch (mediaType) {
      case 'image':
        if (typeof mediaData === 'string') {
          chatStore.setPendingMedia({ image: mediaData })
          message.success('图片已添加到输入框')
        }
        break
      case 'video':
        if (typeof mediaData === 'string') {
          chatStore.setPendingMedia({
            video: mediaData,
            videoBase64: videoBase64 || undefined
          })
          message.success('视频已添加到输入框')
        }
        break
      case 'pdf':
        if (Array.isArray(mediaData)) {
          chatStore.setPendingMedia({
            pdfImages: mediaData,
            pdfName: fileName || 'PDF文档'
          })
          message.success('PDF已添加到输入框')
        }
        break
      case 'ppt':
        if (Array.isArray(mediaData)) {
          chatStore.setPendingMedia({
            pptImages: mediaData,
            pptName: fileName || 'PPT文档',
            pptTotalPages: totalPages
          })
          message.success('PPT已添加到输入框')
        }
        break
    }
  } catch (error) {
    console.error('复用媒体失败:', error)
    message.error('复用媒体失败，请重试')
  }
}

// 下载媒体文件
function downloadMedia(mediaData: string, mediaType: 'image' | 'video'): void {
  try {
    if (!mediaData) {
      message.error('无效的媒体数据')
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
      message.error('不支持的媒体格式')
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
    message.error('下载失败，请重试')
  }
}

// 拖拽处理函数
function handleDragEnter(event: DragEvent): void {
  event.preventDefault()
  event.stopPropagation()

  // 检查是否包含文件
  if (event.dataTransfer?.types.includes('Files')) {
    dragCounter++
    isDragOver.value = true
  }
}

function handleDragOver(event: DragEvent): void {
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

function handleDragLeave(event: DragEvent): void {
  event.preventDefault()
  event.stopPropagation()

  dragCounter--
  if (dragCounter <= 0) {
    dragCounter = 0
    isDragOver.value = false
  }
}

async function handleDrop(event: DragEvent): Promise<void> {
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
    message.error('不支持的文件类型，请拖入图片、视频、PDF或PPT文件')
    return
  }

  // 显示上传中状态
  isFileUploading.value = true

  try {
    // 创建一个模拟的文件选择事件
    const mockEvent = {
      target: {
        files: [file],
        value: ''
      }
    } as unknown as Event

    await handleFileSelect(mockEvent)
  } catch (error) {
    console.error('拖拽文件处理失败:', error)
    message.error('文件处理失败，请重试')
  } finally {
    isFileUploading.value = false
  }
}

// 发送消息的包装函数
async function sendMessage(): Promise<void> {
  if (!canSend.value) return

  await sendMessageCore(
    inputText.value.trim(),
    chatStore.pendingMedia.image || '',
    chatStore.pendingMedia.video || '', // 用于显示
    chatStore.pendingMedia.videoBase64 || '', // 使用base64数据发送给API
    chatStore.pendingMedia.pdfImages || [], // PDF图片数组
    chatStore.pendingMedia.pdfName || '', // PDF文件名
    chatStore.pendingMedia.pptImages || [], // PPT图片数组
    chatStore.pendingMedia.pptName || '', // PPT文件名
    chatStore.pendingMedia.pptTotalPages || null, // PPT总页数
    () => {
      // 清空本地状态的回调函数
      inputText.value = ''
      // 清空待发送媒体在store的addUserMessage中处理
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    },
    scrollToBottom
  )
}

// 处理键盘事件的包装函数
async function handleKeydown(event: KeyboardEvent): Promise<void> {
  await handleKeyDownCore(event, sendMessage)
}

// 滚动到底部
function scrollToBottom(): void {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 媒体预览功能
function openPreview(src: string, type: 'image' | 'video', videoBase64?: string): void {
  previewSrc.value = src
  previewType.value = type
  previewVideoBase64.value = videoBase64 || ''
  showPreview.value = true
  // 阻止页面滚动
  document.body.style.overflow = 'hidden'
}

function closePreview(): void {
  console.log('closePreview called') // 调试用
  showPreview.value = false
  previewSrc.value = ''
  // 恢复页面滚动
  document.body.style.overflow = 'auto'
}

// HTML预览功能
function openHtmlPreview(codeId: string): void {
  const codeElement = document.getElementById(codeId)
  if (codeElement) {
    const htmlCode = codeElement.textContent || ''

    // 使用主进程的独立窗口
    if (window.api && (window.api as typeof window.api & { showHtmlPreview?: (html: string) => Promise<void> }).showHtmlPreview) {
      ;(window.api as typeof window.api & { showHtmlPreview: (html: string) => Promise<void> })
        .showHtmlPreview(htmlCode)
        .then(() => {
          console.log('HTML预览窗口已打开')
        })
        .catch((error: Error) => {
          console.error('打开HTML预览窗口失败:', error)
          // 回退到内联模态窗口
          fallbackToInlinePreview(htmlCode)
        })
    } else {
      // 回退到内联模态窗口
      fallbackToInlinePreview(htmlCode)
    }
  }
}

// 回退的内联预览功能
function fallbackToInlinePreview(htmlCode: string): void {
  htmlPreviewContent.value = htmlCode
  showHtmlPreview.value = true
  document.body.style.overflow = 'hidden'
}

function closeHtmlPreview(): void {
  showHtmlPreview.value = false
  htmlPreviewContent.value = ''
  // 恢复页面滚动
  document.body.style.overflow = 'auto'
}

// 处理来自其他窗口的清空事件
function handleStorageClearEvent(event: StorageEvent): void {
  if (event.key === 'vlm-chat-messages-cleared' && event.newValue) {
    // 清空本地状态
    inputText.value = ''
    chatStore.clearPendingMedia()
  }
}
</script>

<style scoped>
/* 确保没有白边 - 全局重置 */
:global(html),
:global(body) {
  margin: 0 !important;
  padding: 0 !important;
  background-color: #000000 !important;
  overflow: hidden;
}

:global(#app) {
  margin: 0 !important;
  padding: 0 !important;
  background-color: #000000 !important;
}

/* 消息宽度控制 */
.user {
  max-width: var(--user-message-width, 80%);
  margin-left: auto;
  margin-right: 0;
}

.assistant {
  max-width: var(--ai-message-width, 75%);
  margin-left: 0;
  margin-right: auto;
}

/* 滚动条样式 - 只在滚动时显示，带淡退效果 */

/* 消息容器滚动条 - 默认完全隐藏 */
.flex-1.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.flex-1.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.flex-1.overflow-y-auto::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 3px;
  transition: background 0.5s ease-out;
}

/* 只有在滚动时才显示滚动条 */
.flex-1.overflow-y-auto.scrolling::-webkit-scrollbar-thumb {
  background: rgba(64, 64, 64, 0.7);
  transition: background 0.2s ease-in;
}

.flex-1.overflow-y-auto.scrolling::-webkit-scrollbar-thumb:hover {
  background: rgba(82, 82, 82, 0.8);
}

/* AI回复文本颜色修复 */
.ai-response {
  color: #e5e7eb !important;
}

/* 只对非代码元素应用继承颜色，避免影响代码高亮 */
.ai-response p,
.ai-response span:not(.hljs *),
.ai-response div:not(.code-block-wrapper):not(.code-header):not(.hljs) {
  color: inherit !important;
}

.ai-response h1,
.ai-response h2,
.ai-response h3,
.ai-response h4,
.ai-response h5,
.ai-response h6 {
  color: #ffffff !important;
  margin-top: 1em !important;
  margin-bottom: 0.5em !important;
}

.ai-response p {
  color: #e5e7eb !important;
  margin: 0.5em 0 !important;
}

.ai-response code:not(.hljs) {
  color: #f3f4f6 !important;
  background-color: rgba(75, 85, 99, 0.6) !important;
  padding: 2px 4px !important;
  border-radius: 3px !important;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
  word-wrap: break-word !important;
  word-break: break-all !important;
  white-space: pre-wrap !important;
  display: inline !important;
  max-width: 100% !important;
}

/* KaTeX 数学公式样式 - 确保不被行内代码样式影响 */
.ai-response .katex {
  font-family: KaTeX_Main, 'Times New Roman', serif !important;
  font-size: 1.1em !important;
  color: #e5e7eb !important;
  background: none !important;
  padding: 0 !important;
  border-radius: 0 !important;
  word-wrap: normal !important;
  word-break: normal !important;
  white-space: nowrap !important;
  display: inline !important;
  max-width: none !important;
}

.ai-response .katex-display {
  display: block !important;
  text-align: center !important;
  margin: 1em 0 !important;
  white-space: normal !important;
}

/* 确保 KaTeX 内部元素不被代码样式影响 */
.ai-response .katex * {
  font-family: inherit !important;
  color: inherit !important;
  background: none !important;
  padding: 0 !important;
  border-radius: 0 !important;
  word-wrap: normal !important;
  word-break: normal !important;
  white-space: normal !important;
}

/* 重置代码块的 prose 样式 */
.ai-response pre {
  background: none !important;
  border: none !important;
  border-radius: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

.ai-response pre code {
  color: inherit !important;
  background: none !important;
  padding: 0 !important;
  border-radius: 0 !important;
  display: block !important;
}

/* 确保代码块容器样式 */
.ai-response .code-block-wrapper {
  margin: 1em 0 !important;
  border: 1px solid #404040 !important;
  border-radius: 6px !important;
  background: #1e1e1e !important;
  overflow: hidden !important;
  max-width: 100% !important;
  width: 100% !important;
}

.ai-response .code-header {
  background: #2d2d30 !important;
  border-bottom: 1px solid #404040 !important;
  padding: 8px 16px !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
}

.ai-response .language-label {
  color: #cccccc !important;
  font-weight: 500 !important;
  font-size: 12px !important;
}

/* 代码操作按钮样式 */
.ai-response .code-actions {
  display: flex !important;
  gap: 8px !important;
}

.ai-response .copy-button,
.ai-response .preview-button {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 4px !important;
  padding: 4px 6px !important;
  color: #cccccc !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  display: flex !important;
  align-items: center !important;
  font-size: 11px !important;
}

.ai-response .copy-button:hover,
.ai-response .preview-button:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  color: #ffffff !important;
}

/* 确保代码高亮样式优先级 */
.ai-response .hljs {
  background: #1e1e1e !important;
  color: #d4d4d4 !important;
  padding: 1em !important;
  border-radius: 0 0 6px 6px !important;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  display: block !important;
  overflow-x: auto !important;
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  word-break: break-all !important;
}

/* 代码块滚动条样式 */
.ai-response .hljs::-webkit-scrollbar {
  height: 2px !important;
}

.ai-response .hljs::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05) !important;
  border-radius: 2px !important;
}

.ai-response .hljs::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2) !important;
  border-radius: 2px !important;
}

.ai-response .hljs::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3) !important;
}

/* 确保语法高亮颜色正确应用 - 提高优先级 */
.ai-response .hljs .hljs-keyword,
.ai-response .hljs .hljs-selector-tag,
.ai-response .hljs .hljs-literal,
.ai-response .hljs .hljs-section,
.ai-response .hljs .hljs-link {
  color: #569cd6 !important;
}

.ai-response .hljs .hljs-string,
.ai-response .hljs .hljs-title,
.ai-response .hljs .hljs-name,
.ai-response .hljs .hljs-type,
.ai-response .hljs .hljs-attribute,
.ai-response .hljs .hljs-symbol,
.ai-response .hljs .hljs-bullet,
.ai-response .hljs .hljs-addition,
.ai-response .hljs .hljs-variable,
.ai-response .hljs .hljs-template-tag,
.ai-response .hljs .hljs-template-variable {
  color: #ce9178 !important;
}

.ai-response .hljs .hljs-comment,
.ai-response .hljs .hljs-quote,
.ai-response .hljs .hljs-deletion,
.ai-response .hljs .hljs-meta {
  color: #6a9955 !important;
}

.ai-response .hljs .hljs-number,
.ai-response .hljs .hljs-literal {
  color: #b5cea8 !important;
}

.ai-response .hljs .hljs-function {
  color: #dcdcaa !important;
}

.ai-response .hljs .hljs-built_in {
  color: #4ec9b0 !important;
}

.ai-response .hljs .hljs-class .hljs-title {
  color: #4ec9b0 !important;
}

.ai-response .hljs .hljs-tag {
  color: #569cd6 !important;
}

.ai-response .hljs .hljs-tag .hljs-name {
  color: #569cd6 !important;
}

.ai-response .hljs .hljs-tag .hljs-attr {
  color: #92c5f8 !important;
}

.ai-response strong,
.ai-response b {
  color: #ffffff !important;
}

.ai-response em,
.ai-response i {
  color: #e5e7eb !important;
}

.ai-response ul,
.ai-response ol {
  margin: 0.5em 0 !important;
  padding-left: 1.5em !important;
}

.ai-response ul li,
.ai-response ol li {
  color: #e5e7eb !important;
  margin: 0.25em 0 !important;
}

.ai-response a {
  color: #60a5fa !important;
}

.ai-response blockquote {
  color: #d1d5db !important;
  border-left: 4px solid #6b7280 !important;
  padding-left: 1em !important;
  margin: 1em 0 !important;
  font-style: italic !important;
}

.ai-response hr {
  border: none !important;
  border-top: 1px solid #6b7280 !important;
  margin: 2em 0 !important;
}

.ai-response table {
  border-collapse: collapse !important;
  width: 100% !important;
  margin: 1em 0 !important;
}

.ai-response table th {
  color: #ffffff !important;
  background-color: rgba(75, 85, 99, 0.3) !important;
  border: 1px solid #6b7280 !important;
  padding: 8px 12px !important;
}

.ai-response table td {
  color: #e5e7eb !important;
  border: 1px solid #6b7280 !important;
  padding: 8px 12px !important;
}

/* 媒体hover效果 */
.media-hover-container {
  position: relative;
  display: inline-block;
}

.media-hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.media-hover-container:hover .media-hover-overlay {
  opacity: 1;
}

.eye-icon {
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
}

/* 媒体操作按钮 */
.media-action-buttons {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
  z-index: 10;
}

.media-hover-container:hover .media-action-buttons {
  opacity: 1;
  pointer-events: auto;
}

/* 外部媒体操作按钮 */
.media-action-buttons-external {
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.media-container:hover .media-action-buttons-external {
  opacity: 1;
  pointer-events: auto;
}

.media-action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
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

/* 媒体预览Modal样式 */
.media-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease-out;
  -webkit-app-region: no-drag;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: scaleIn 0.2s ease-out;
  -webkit-app-region: no-drag;
}

.modal-close-btn {
  position: absolute;
  top: -12px;
  right: -12px;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 10001;
  -webkit-app-region: no-drag;
  pointer-events: auto;
  user-select: none;
  -webkit-user-select: none;
}

.modal-close-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  border-color: rgba(255, 255, 255, 0.8);
  transform: scale(1.05);
}

.media-container {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.preview-media {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* HTML预览Modal样式 */
.html-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease-out;
  -webkit-app-region: no-drag;
}

.html-preview-modal .modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.html-preview-content {
  position: relative;
  width: 90vw;
  height: 90vh;
  background: white;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: scaleIn 0.2s ease-out;
  -webkit-app-region: no-drag;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.html-preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  border-radius: 12px 12px 0 0;
}

.html-preview-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.html-preview-container {
  flex: 1;
  overflow: auto;
  background: white;
}

.rendered-content {
  padding: 20px;
  min-height: 100%;
}

/* 确保HTML预览中的样式正常工作 */
.rendered-content * {
  max-width: 100%;
  word-wrap: break-word;
}

/* 发送按钮 loading 样式 */
.send-loading {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 6px;
}

.send-loading svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* HTML 预览样式 */
.html-preview {
  border-top: 1px solid #404040;
  background: #f5f5f5;
  margin: 0;
}

.preview-header {
  background: #e5e5e5;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 500;
  color: #333;
  border-bottom: 1px solid #d0d0d0;
}

.preview-content {
  padding: 16px;
  background: white;
  color: #333;
  min-height: 100px;
  max-height: 400px;
  overflow: auto;
}

/* 确保预览内容中的样式正常工作 */
.preview-content * {
  color: inherit !important;
}

/* 思考块样式 */
.think-block {
  font-size: 0.875rem;
  position: relative;
}

.think-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 0;
  font-size: 0.8rem;
}

.think-icon {
  font-size: 14px;
}

.think-label {
  color: rgb(156, 163, 175);
  font-weight: 500;
  flex: 1;
}

.think-toggle {
  background: none;
  border: none;
  color: rgb(96, 165, 250);
  cursor: pointer;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
}

.think-toggle:hover {
  background: rgba(96, 165, 250, 0.1);
  color: rgb(147, 197, 253);
}

.think-content {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(115, 115, 115, 0.3);
}

.think-content .prose {
  font-size: 0.8rem;
  line-height: 1.4;
}

/* 答案块样式 */
.answer-block {
  font-size: 0.875rem;
  position: relative;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 0;
  font-size: 0.8rem;
}

.answer-icon {
  font-size: 14px;
}

.answer-label {
  color: rgb(34, 197, 94);
  font-weight: 500;
  flex: 1;
}

.answer-content {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(34, 197, 94, 0.2);
}

.answer-content .prose {
  font-size: 0.8rem;
  line-height: 1.4;
}

/* 录制状态动画 */
.recording-status {
  animation: recordingPulse 2s infinite;
}

@keyframes recordingPulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }

  50% {
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1);
  }
}

.recording-dot {
  animation: recordingDotPulse 1s infinite;
}

@keyframes recordingDotPulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
}

/* 拖拽样式 */
.drag-over {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(37, 99, 235, 0.04)) !important;
  position: relative;
}

/* 全局星空背景效果 */
.starfield-global {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}

/* 星空背景效果 */
.starfield {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
  pointer-events: none;
}

.stars,
.stars2,
.stars3 {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
}

.stars {
  background-image:
    radial-gradient(2px 2px at 15px 25px, rgba(255, 255, 255, 0.8), transparent), radial-gradient(1px 1px at 35px 65px, rgba(255, 255, 255, 0.6), transparent), radial-gradient(1px 1px at 75px 35px, rgba(255, 255, 255, 0.9), transparent), radial-gradient(1px 1px at 95px 75px, rgba(255, 255, 255, 0.7), transparent), radial-gradient(2px 2px at 115px 25px, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 25px 55px, rgba(255, 255, 255, 0.4), transparent), radial-gradient(1px 1px at 65px 15px, rgba(255, 255, 255, 0.6), transparent), radial-gradient(2px 2px at 105px 55px, rgba(255, 255, 255, 0.5), transparent);
  background-repeat: repeat;
  background-size: 120px 160px;
  animation: move-stars 10s linear infinite;
}

.stars2 {
  background-image:
    radial-gradient(1px 1px at 30px 50px, rgba(255, 255, 255, 0.4), transparent), radial-gradient(1px 1px at 90px 20px, rgba(255, 255, 255, 0.6), transparent), radial-gradient(1px 1px at 60px 80px, rgba(255, 255, 255, 0.3), transparent), radial-gradient(1px 1px at 10px 30px, rgba(255, 255, 255, 0.5), transparent), radial-gradient(1px 1px at 80px 60px, rgba(255, 255, 255, 0.4), transparent),
    radial-gradient(1px 1px at 50px 10px, rgba(255, 255, 255, 0.3), transparent);
  background-repeat: repeat;
  background-size: 100px 140px;
  animation: move-stars 15s linear infinite;
}

.stars3 {
  background-image:
    radial-gradient(1px 1px at 45px 15px, rgba(255, 255, 255, 0.2), transparent), radial-gradient(1px 1px at 75px 45px, rgba(255, 255, 255, 0.4), transparent), radial-gradient(1px 1px at 20px 70px, rgba(255, 255, 255, 0.3), transparent), radial-gradient(1px 1px at 95px 25px, rgba(255, 255, 255, 0.2), transparent), radial-gradient(1px 1px at 125px 55px, rgba(255, 255, 255, 0.3), transparent),
    radial-gradient(1px 1px at 5px 45px, rgba(255, 255, 255, 0.25), transparent);
  background-repeat: repeat;
  background-size: 140px 120px;
  animation: move-stars 20s linear infinite;
}

@keyframes move-stars {
  0% {
    transform: translateY(0);
  }

  100% {
    transform: translateY(-160px);
  }
}

.drag-overlay {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  bottom: 16px;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border: 2px dashed rgba(59, 130, 246, 0.6);
  border-radius: 12px;
  animation: dragOverlay 0.2s ease-out;
}

.drag-overlay-global {
  position: fixed;
  top: 70px;
  left: 10px;
  right: 10px;
  bottom: 65px;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  border: 3px dashed rgba(59, 130, 246, 0.8);
  border-radius: 20px;
  animation: dragOverlay 0.2s ease-out;
  pointer-events: none;
}

.drag-indicator {
  text-align: center;
  color: #60a5fa;
}

.drag-indicator-global {
  text-align: center;
  color: #60a5fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.drag-icon-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: dragIconBounce 1s ease-in-out infinite alternate;
}

.drag-upload-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(59, 130, 246, 0.2);
  border-radius: 50%;
  padding: 8px;
  animation: dragUploadIconPulse 1.5s ease-in-out infinite;
}

@keyframes dragIconBounce {
  0% {
    transform: translateY(0px);
  }
  100% {
    transform: translateY(-10px);
  }
}

@keyframes dragUploadIconPulse {
  0%,
  100% {
    opacity: 0.7;
    transform: translate(-50%, -50%) scale(1);
  }

  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

.drag-text {
  user-select: none;
}

.drag-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #60a5fa;
}

.drag-subtitle {
  font-size: 14px;
  color: #94a3b8;
  opacity: 0.9;
}

@keyframes dragOverlay {
  from {
    opacity: 0;
    transform: scale(0.95);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* KaTeX 数学公式样式 */
.katex-display {
  text-align: center;
  margin: 1em 0;
  overflow-x: auto;
  overflow-y: hidden;
}

/* 确保 KaTeX 公式在深色主题下正确显示 */
.katex .base,
.katex .mord,
.katex .mrel,
.katex .mbin,
.katex .mop,
.katex .mopen,
.katex .mclose,
.katex .mpunct {
  color: inherit;
}
</style>
