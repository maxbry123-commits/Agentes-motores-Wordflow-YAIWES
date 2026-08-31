<template>
  <header class="bg-black/95 backdrop-blur-md p-3 shadow-sm border-b border-neutral-800">
    <div class="drag-region h-10 w-100% absolute top-0 lef-0 right-0"></div>
    <div class="flex justify-between items-center">
      <div class="flex-1"></div>
      <h1 class="text-xl font-bold text-white z-1000">GLM-4.5V</h1>
      <div class="flex-1 flex justify-end items-center space-x-2">
        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="500">
          <template #trigger>
            <n-button circle class="no-drag" @click="startNewConversation">
              <template #icon>
                <n-icon size="16">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
                  </svg>
                </n-icon>
              </template>
            </n-button>
          </template>
          新建对话
        </n-tooltip>
        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="500">
          <template #trigger>
            <n-button circle class="no-drag" @click="toggleHistoryPanel">
              <template #icon>
                <n-icon size="16">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z" />
                  </svg>
                </n-icon>
              </template>
            </n-button>
          </template>
          历史记录
        </n-tooltip>

        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="500">
          <template #trigger>
            <n-button circle class="no-drag" @click="openSettings">
              <template #icon>
                <n-icon size="16">
                  <Settings />
                </n-icon>
              </template>
            </n-button>
          </template>
          模型和应用设置
        </n-tooltip>
        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="500">
          <template #trigger>
            <n-button circle class="no-drag" @click="switchToFloating">
              <template #icon>
                <n-icon size="16">
                  <Launch />
                </n-icon>
              </template>
            </n-button>
          </template>
          切换到悬浮窗
        </n-tooltip>
        <n-tooltip trigger="hover" placement="bottom" :show-arrow="false" :delay="500">
          <template #trigger>
            <n-button circle class="no-drag" :type="isPinned ? 'warning' : 'default'" @click="togglePin">
              <template #icon>
                <n-icon size="16">
                  <Pin />
                </n-icon>
              </template>
            </n-button>
          </template>
          {{ isPinned ? '取消置顶' : '窗口置顶' }}
        </n-tooltip>
      </div>
    </div>

    <!-- 设置弹窗 -->
    <n-modal v-model:show="showSettings" preset="card" title="设置" class="w-200 select-none">
      <n-tabs type="segment" size="small" animated :default-value="activeTab" @update:value="activeTab = $event">
        <!-- 模型设置标签页 -->
        <n-tab-pane name="model" tab="模型设置">
          <n-form :model="localSettings" label-placement="left" label-width="200px" size="small">
            <!-- 连接设置 -->
            <div>
              <h4 class="text-sm font-semibold text-white mb-3">连接设置</h4>

              <!-- 智谱MaaS模式开关 -->
              <n-form-item>
                <template #label>
                  <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
                    <template #trigger>
                      <span>智谱MaaS模式</span>
                    </template>
                    启用后将使用智谱AI官方API地址，支持模型选择和流式输出。关闭后使用内部API，支持所有高级参数
                  </n-tooltip>
                </template>
                <n-switch v-model:value="localSettings.zhipuMaasMode" :rail-style="switchRailStyle" @update:value="updateZhipuMaasMode" />
              </n-form-item>

              <!-- 智谱MaaS模式下的模型选择 -->
              <n-form-item v-if="localSettings.zhipuMaasMode" label="模型">
                <n-input v-model:value="localSettings.model" round placeholder="如：glm-xxx" />
              </n-form-item>

              <!-- API配置 - 在所有模式下都显示 -->
              <div class="grid grid-cols-2 gap-x-0">
                <n-form-item label="API URL">
                  <n-input v-model:value="localSettings.apiUrl" round placeholder="服务器地址" />
                </n-form-item>
                <n-form-item label="Endpoint">
                  <n-input v-model:value="localSettings.endpoint" round placeholder="API端点路径" />
                </n-form-item>
              </div>

              <!-- API Key - 在所有模式下都显示，但MaaS模式下是必填的 -->
              <n-form-item :label="localSettings.zhipuMaasMode ? 'API Key（必填）' : 'API Key'">
                <n-input v-model:value="localSettings.apiKey" round type="password" :placeholder="localSettings.zhipuMaasMode ? '智谱AI API密钥（必填）' : 'API密钥（可选）'" show-password-on="click" class="mr-2" />
                <n-button v-if="localSettings.zhipuMaasMode" type="primary" ghost @click="openApiKeyPage">获取API Key</n-button>
              </n-form-item>
            </div>

            <!-- 生成参数 -->
            <div>
              <h4 class="text-sm font-semibold text-white mb-3">生成参数</h4>
              <div class="grid grid-cols-2 gap-y-0">
                <n-form-item label="max_tokens">
                  <n-input-number v-model:value="localSettings.maxTokens" round :min="1" :max="81920" class="w-full" placeholder="最大输出长度" />
                </n-form-item>
                <n-form-item label="temperature">
                  <n-input-number v-model:value="localSettings.temperature" round :min="0" :max="2" :step="0.1" class="w-full" placeholder="创造性程度" />
                </n-form-item>
                <n-form-item label="top_p">
                  <n-input-number v-model:value="localSettings.topP" round :min="0" :max="1" :step="0.1" class="w-full" placeholder="核采样概率" />
                </n-form-item>
                <n-form-item label="历史对话轮数">
                  <n-tooltip trigger="hover" placement="top" :show-arrow="false" :delay="500">
                    <template #trigger>
                      <n-input-number v-model:value="localSettings.historyTurns" round :min="0" :max="10" :step="1" class="w-full" />
                    </template>
                    控制发送给AI的历史对话轮数。为0时不携带任何历史
                  </n-tooltip>
                </n-form-item>

                <!-- 只在非MaaS模式下显示这些高级参数 -->
                <template v-if="!localSettings.zhipuMaasMode">
                  <n-form-item label="top_k">
                    <n-input-number v-model:value="localSettings.topK" round :min="1" :max="100" class="w-full" placeholder="候选词数量" />
                  </n-form-item>
                  <n-form-item label="repetition_penalty">
                    <n-input-number v-model:value="localSettings.repetitionPenalty" round :min="0.1" :max="2" :step="0.1" class="w-full" placeholder="重复惩罚" />
                  </n-form-item>
                  <n-form-item label="stop_token_ids">
                    <n-input v-model:value="localSettings.stopTokenIdsStr" round placeholder="停止词ID，逗号分隔" class="w-full" />
                  </n-form-item>
                  <n-form-item label="skip_special_tokens">
                    <n-switch v-model:value="localSettings.skipSpecialTokens" :rail-style="switchRailStyle" />
                  </n-form-item>
                  <n-form-item label="include_stop_str_in_output">
                    <n-switch v-model:value="localSettings.includeStopStrInOutput" :rail-style="switchRailStyle" />
                  </n-form-item>
                </template>
              </div>
            </div>
          </n-form>
        </n-tab-pane>

        <!-- 应用设置标签页 -->
        <n-tab-pane name="app" tab="应用设置">
          <n-form :model="localSettings" label-placement="left" size="small">
            <!-- 界面设置 -->
            <div>
              <h4 class="text-sm font-semibold text-white mb-3">通用设置</h4>
              <div class="flex flex-wrap justify-between gap-y-2 ml-8">
                <n-form-item label="默认展开思考块">
                  <n-switch v-model:value="localSettings.defaultExpandThink" :rail-style="switchRailStyle" />
                </n-form-item>
                <n-form-item label="动态背景">
                  <n-switch v-model:value="localSettings.starryBackground" :rail-style="switchRailStyle" />
                </n-form-item>
                <n-form-item label="录屏自动保存到本地">
                  <n-switch v-model:value="localSettings.saveRecordingLocally" :rail-style="switchRailStyle" />
                </n-form-item>
              </div>
              <div class="grid grid-cols-2 gap-x-4 gap-y-2 ml-8">
                <n-form-item label="用户消息宽度">
                  <n-slider v-model:value="localSettings.userMessageWidth" :min="50" :max="100" :step="5" :format-tooltip="value => `${value}%`" style="width: 100%" />
                </n-form-item>
                <n-form-item label="AI回复宽度">
                  <n-slider v-model:value="localSettings.aiMessageWidth" :min="50" :max="100" :step="5" :format-tooltip="value => `${value}%`" style="width: 100%" />
                </n-form-item>
              </div>
            </div>

            <!-- 快捷键设置 -->
            <div>
              <h4 class="text-sm font-semibold text-white mb-3">快捷键</h4>
              <div class="grid grid-cols-2 gap-x-4 gap-y-2">
                <div class="flex justify-between items-center text-sm">
                  <span>快速截图</span>
                  <n-tag size="small" type="info" class="mr-10">Cmd+Shift+S</n-tag>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span>快速切换窗口</span>
                  <n-tag size="small" type="info" class="mr-10">Cmd+Shift+C</n-tag>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span>新建对话</span>
                  <n-tag size="small" type="info" class="mr-10">Cmd+Shift+N</n-tag>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span>区域截图</span>
                  <n-tag size="small" type="info" class="mr-10">Cmd+Shift+X</n-tag>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span>打开历史</span>
                  <n-tag size="small" type="info" class="mr-10">Cmd+Shift+H</n-tag>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span>发送消息</span>
                  <n-tag size="small" type="info" class="mr-10">Enter</n-tag>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span>换行</span>
                  <n-tag size="small" type="info" class="mr-10">Shift+Enter</n-tag>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span>粘贴图片</span>
                  <n-tag size="small" type="info" class="mr-10">Cmd+V</n-tag>
                </div>
              </div>
            </div>

            <!-- 关于信息 -->
            <div>
              <h4 class="text-sm font-semibold text-white mb-3">关于</h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span>应用版本</span>
                  <span class="text-gray-500">{{ appVersion }}</span>
                </div>
              </div>
            </div>
          </n-form>
        </n-tab-pane>

        <!-- 系统提示词标签页 -->
        <n-tab-pane name="system" tab="系统提示词">
          <n-form :model="localSettings" label-placement="top" size="small">
            <n-form-item>
              <template #label>
                <div class="flex items-center mt-2">
                  <span class="text-sm font-semibold text-white">系统提示词</span>
                </div>
              </template>
              <n-input v-model:value="localSettings.systemPrompt" type="textarea" :rows="8" placeholder="请输入系统提示词，例如：你是一个专业的助手，请用简洁明了的方式回答问题..." class="w-full" clearable />
            </n-form-item>

            <div class="bg-blue-500/20 border border-blue-500/50 rounded-lg p-3">
              <div class="text-sm text-blue-300 mb-2">
                <strong>提示：</strong>
              </div>
              <ul class="text-sm text-blue-300 space-y-1">
                <li>系统提示词会影响AI的回答风格和行为模式</li>
                <li>建议保持简洁明了，过长的提示词可能影响性能</li>
                <li>修改后会立即应用到新的对话中</li>
              </ul>
            </div>
          </n-form>
        </n-tab-pane>
      </n-tabs>
      <template #footer>
        <div class="flex justify-end space-x-2 pt-0! mt-0!">
          <n-button @click="cancelSettings">取消</n-button>
          <n-button type="primary" @click="saveSettings">保存</n-button>
        </div>
      </template>
    </n-modal>

    <!-- 历史面板 -->
    <HistoryPanel :is-open="showHistoryPanel" class="z-9999" :current-conversation-id="chatStore.currentConversationId" @close="closeHistoryPanel" @load-conversation="loadHistoryConversation" @start-new-conversation="handleStartNewConversation" />
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { NButton, NIcon, NTooltip, NModal, NForm, NFormItem, NInput, NInputNumber, NSwitch, NSlider, NTabs, NTabPane, NTag, useMessage } from 'naive-ui'
import { Settings, Launch, Pin } from '@vicons/carbon'
import { useChatStore } from '../../stores/chatStore'
import { useSettingsStore, type AppSettings } from '../../stores/settingsStore'
import HistoryPanel from '../../components/HistoryPanel.vue'

const message = useMessage()
const chatStore = useChatStore()
const settingsStore = useSettingsStore()

// 历史面板状态
const showHistoryPanel = ref(false)

// 应用版本号
const appVersion = ref('v1.0.1')

// Switch 开关样式
const switchRailStyle = ({ checked }: { focused: boolean; checked: boolean }): Record<string, string> => {
  const style: Record<string, string> = {}
  if (checked) {
    style.background = '#18a058' // 绿色
  } else {
    style.background = '#606266' // 灰色
  }
  return style
}

// 设置相关
const showSettings = ref(false)
const activeTab = ref('model') // 默认显示模型设置标签页
const isPinned = ref(false)

// 创建本地的设置副本，用于表单绑定
const localSettings = ref<AppSettings>({} as AppSettings)

// 保存原始设置，用于取消时恢复
const originalSettings = ref<AppSettings>({} as AppSettings)

// 打开设置时保存当前设置并创建本地副本
function openSettings(): void {
  // 获取当前设置的副本
  const currentSettings = settingsStore.getSettingsCopy()

  // 保存原始设置用于取消恢复
  originalSettings.value = JSON.parse(JSON.stringify(currentSettings))

  // 创建本地副本用于表单绑定
  localSettings.value = JSON.parse(JSON.stringify(currentSettings))

  showSettings.value = true
  console.log('打开设置，原始设置:', originalSettings.value)
  console.log('本地设置副本:', localSettings.value)
}

// 取消设置时恢复原始设置
function cancelSettings(): void {
  // 恢复到原始设置
  settingsStore.restoreFromCopy(originalSettings.value)

  // 同步更新本地设置副本，确保界面显示正确
  localSettings.value = JSON.parse(JSON.stringify(originalSettings.value))

  showSettings.value = false
  console.log('取消设置，已恢复到:', originalSettings.value)
  console.log('本地设置副本已同步:', localSettings.value)
}

// 设置相关功能
function loadSettings(): void {
  try {
    // 使用设置 Store 自动加载设置
    settingsStore.loadSettings()
    console.log('设置加载完成')
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

function saveSettings(): void {
  try {
    // 先将本地设置副本的更改同步到设置存储
    settingsStore.updateSettings(localSettings.value)

    // 然后保存设置
    settingsStore.saveSettings()
    message.success('设置已保存并立即生效', { duration: 2000 })
    showSettings.value = false
    console.log('设置已保存:', localSettings.value)
  } catch (error) {
    console.error('保存设置失败:', error)
    message.error('保存设置失败')
  }
}

// 通用的设置更新方法 - 直接使用 settingsStore.updateSetting
// 不再需要单独的更新函数，直接在模板中使用 @update:value="settingsStore.updateSetting"

// 智谱MaaS模式需要特殊处理，因为需要立即生效
function updateZhipuMaasMode(value: boolean): void {
  // 同时更新本地副本和 store（立即生效）
  localSettings.value.zhipuMaasMode = value
  settingsStore.updateSetting('zhipuMaasMode', value)
  console.log('智谱MaaS模式设置已实时更新:', value)
}

async function startNewConversation(): Promise<void> {
  // 调用新建对话功能
  await chatStore.startNewConversation()
  message.success('已开始新对话', { duration: 1500 })
}

// 打开智谱AI API Key获取页面
async function openApiKeyPage(): Promise<void> {
  try {
    if (window.api?.openExternal) {
      await window.api.openExternal('https://bigmodel.cn/usercenter/proj-mgmt/apikeys')
    } else {
      // 备用方案：尝试使用window.open
      window.open('https://bigmodel.cn/usercenter/proj-mgmt/apikeys', '_blank')
    }
  } catch (error) {
    console.error('打开API Key页面失败:', error)
    message.error('无法打开浏览器页面')
  }
}

// 切换历史面板
function toggleHistoryPanel(): void {
  console.log('toggleHistoryPanel called, current value:', showHistoryPanel.value)
  showHistoryPanel.value = !showHistoryPanel.value
  console.log('showHistoryPanel new value:', showHistoryPanel.value)
}

// 关闭历史面板
function closeHistoryPanel(): void {
  showHistoryPanel.value = false
}

// 加载历史对话
async function loadHistoryConversation(conversationId: string): Promise<void> {
  try {
    const success = await chatStore.loadConversation(conversationId)
    if (success) {
      // 成功加载后关闭历史面板
      showHistoryPanel.value = false
      message.success('历史对话已加载', { duration: 1500 })
    } else {
      message.error('加载历史对话失败', { duration: 2000 })
    }
  } catch (error) {
    console.error('加载历史对话失败:', error)
    message.error('加载历史对话失败', { duration: 2000 })
  }
}

// 处理删除当前对话后开始新对话
async function handleStartNewConversation(): Promise<void> {
  try {
    await chatStore.startNewConversation()
    showHistoryPanel.value = false
  } catch (error) {
    console.error('开始新对话失败:', error)
    message.error('开始新对话失败', { duration: 2000 })
  }
}

function switchToFloating(): void {
  if (window.api?.switchToFloating) {
    window.api.switchToFloating()
  }
}

// 置顶功能
async function togglePin(): Promise<void> {
  try {
    if (window.api?.toggleAlwaysOnTop) {
      // 记录当前状态，用于显示正确的操作提示
      const currentPinState = isPinned.value
      const newState = await window.api.toggleAlwaysOnTop()
      isPinned.value = newState

      // 根据用户执行的操作显示消息（而不是结果状态）
      if (currentPinState) {
        message.success('已取消置顶', { duration: 1500 })
      } else {
        message.success('窗口已置顶', { duration: 1500 })
      }
    }
  } catch (error) {
    console.error('切换置顶状态失败:', error)
    message.error('操作失败')
  }
}

// 获取当前置顶状态
async function checkPinStatus(): Promise<void> {
  try {
    if (window.api?.getAlwaysOnTopStatus) {
      isPinned.value = await window.api.getAlwaysOnTopStatus()
    }
  } catch (error) {
    console.error('获取置顶状态失败:', error)
  }
}

// 监听置顶状态刷新请求
function setupPinStatusListener(): void {
  if (window.api?.onRefreshPinStatus) {
    window.api.onRefreshPinStatus(async () => {
      // 当收到刷新请求时，重新查询自己的置顶状态
      await checkPinStatus()
    })
  }
}

// 清理置顶状态监听器
function cleanupPinStatusListener(): void {
  if (window.api?.offRefreshPinStatus) {
    window.api.offRefreshPinStatus(() => {})
  }
}

// 获取应用版本号
async function loadAppVersion(): Promise<void> {
  try {
    const windowWithApi = window as { api?: { getAppVersion?: () => Promise<string> } }
    if (windowWithApi.api?.getAppVersion) {
      const version = await windowWithApi.api.getAppVersion()
      appVersion.value = `v${version}`
    }
  } catch (error) {
    console.error('获取应用版本失败:', error)
    // 保持默认版本号
  }
}

// 监听来自悬浮窗的历史面板显示请求
function setupHistoryPanelListener(): void {
  window.addEventListener('storage', event => {
    if (event.key === 'vlm-show-history-panel' && event.newValue) {
      try {
        const data = JSON.parse(event.newValue)
        if (data.show) {
          showHistoryPanel.value = true
        }
      } catch (error) {
        console.error('解析历史面板显示请求失败:', error)
      }
    }
  })
}

// 监听全局快捷键事件
function setupGlobalShortcutListeners(): void {
  // 使用 IPC 事件监听
  if (window.electron?.ipcRenderer) {
    window.electron.ipcRenderer.on('trigger-new-conversation', () => {
      startNewConversation()
    })

    window.electron.ipcRenderer.on('trigger-history-panel', () => {
      toggleHistoryPanel()
    })
  }
}

// 清理全局快捷键监听器
function cleanupGlobalShortcutListeners(): void {
  if (window.electron?.ipcRenderer) {
    window.electron.ipcRenderer.removeAllListeners('trigger-new-conversation')
    window.electron.ipcRenderer.removeAllListeners('trigger-history-panel')
    window.electron.ipcRenderer.removeAllListeners('trigger-quick-screenshot')
  }
}

onMounted(() => {
  loadSettings()
  loadAppVersion()
  checkPinStatus()
  setupPinStatusListener()
  setupHistoryPanelListener()
  setupGlobalShortcutListeners()
})

onUnmounted(() => {
  cleanupPinStatusListener()
  cleanupGlobalShortcutListeners()
})
</script>

<style scoped>
.drag-region {
  -webkit-app-region: drag;
}

/* 确保按钮等交互元素可以点击 */
.drag-region button,
.drag-region input,
.drag-region select,
.drag-region textarea,
.no-drag {
  -webkit-app-region: no-drag;
}

/* 紧凑的表单样式 */
:deep(.n-form-item) {
  margin-bottom: 2px !important;
}

:deep(.n-form-item:last-child) {
  margin-bottom: 0 !important;
}

/* 进一步减少网格布局中的间距 */
:deep(.grid .n-form-item) {
  margin-bottom: 1px !important;
}

/* 减少模态框内容与底部的间距 */
:deep(.n-card__content) {
  padding-bottom: 8px !important;
}
</style>
