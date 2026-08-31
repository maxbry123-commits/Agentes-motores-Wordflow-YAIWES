import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export interface AppSettings {
  // 基础设置
  starryBackground: boolean
  defaultExpandThink: boolean
  saveRecordingLocally: boolean
  zhipuMaasMode: boolean

  // API配置
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
  stopTokenIdsStr: string
  includeStopStrInOutput: boolean
  endpoint: string
  historyTurns: number
  systemPrompt: string

  // UI配置
  userMessageWidth: number
  aiMessageWidth: number
}

const DEFAULT_SETTINGS: AppSettings = {
  // 基础设置
  starryBackground: true,
  defaultExpandThink: true,
  saveRecordingLocally: false,
  zhipuMaasMode: true,

  // API配置
  apiUrl: 'https://open.bigmodel.cn',
  apiKey: '',
  model: 'glm-4.5v',
  maxTokens: 16384,
  temperature: 0.3,
  topP: 0.6,
  topK: 2,
  repetitionPenalty: 1.1,
  skipSpecialTokens: false,
  stopTokenIds: [151329, 151336],
  stopTokenIdsStr: '151329,151336',
  includeStopStrInOutput: false,
  endpoint: '/api/paas/v4/chat/completions',
  historyTurns: 4,
  systemPrompt: '',

  // UI配置
  userMessageWidth: 80,
  aiMessageWidth: 75
}

const STORAGE_KEY = 'vlm-helper-settings'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>({ ...DEFAULT_SETTINGS })

  const enableStreamResponse = computed(() => settings.value.zhipuMaasMode)

  const loadSettings = (): void => {
    try {
      const savedSettings = localStorage.getItem(STORAGE_KEY)
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings) as Partial<AppSettings>
        // 合并默认设置和保存的设置
        settings.value = { ...DEFAULT_SETTINGS, ...parsed }
        console.log('设置加载完成:', settings.value)
      }
    } catch (error) {
      console.error('加载设置失败:', error)
      settings.value = { ...DEFAULT_SETTINGS }
    }

    updateCSSVariables()
  }

  // 保存设置到本地存储
  const saveSettings = (): void => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings.value))
      console.log('设置已保存:', settings.value)

      // 保存后立即同步到 modelAPI
      updateCSSVariables()

      // 触发跨窗口同步事件
      window.dispatchEvent(
        new CustomEvent('vlm-settings-changed', {
          detail: settings.value
        })
      )
    } catch (error) {
      console.error('保存设置失败:', error)
    }
  }

  // 更新CSS变量
  const updateCSSVariables = (): void => {
    try {
      document.documentElement.style.setProperty('--user-message-width', `${settings.value.userMessageWidth}%`)
      document.documentElement.style.setProperty('--ai-message-width', `${settings.value.aiMessageWidth}%`)
    } catch (error) {
      console.error('更新CSS变量失败:', error)
    }
  }

  // 更新单个设置
  const updateSetting = <K extends keyof AppSettings>(key: K, value: AppSettings[K]): void => {
    settings.value[key] = value

    // 特殊处理：更新 stopTokenIdsStr 时同步更新 stopTokenIds
    if (key === 'stopTokenIdsStr') {
      try {
        const stopTokenIds = (value as string)
          .split(',')
          .map(id => parseInt(id.trim()))
          .filter(id => !isNaN(id))
        settings.value.stopTokenIds = stopTokenIds
      } catch (error) {
        console.error('解析 stopTokenIds 失败:', error)
      }
    }

    // 特殊处理：更新 CSS 变量相关设置时立即应用
    if (key === 'userMessageWidth') {
      document.documentElement.style.setProperty('--user-message-width', `${value}%`)
      console.log('实时更新用户消息宽度:', value)
    } else if (key === 'aiMessageWidth') {
      document.documentElement.style.setProperty('--ai-message-width', `${value}%`)
      console.log('实时更新AI回复宽度:', value)
    }

    console.log(`设置 ${key} 已更新为:`, value)
    saveSettings()
  }

  // 获取当前设置的深拷贝副本
  const getSettingsCopy = (): AppSettings => {
    return JSON.parse(JSON.stringify(settings.value))
  }

  // 从副本恢复设置
  const restoreFromCopy = (copy: AppSettings): void => {
    settings.value = { ...copy }
    updateCSSVariables()
    console.log('已从副本恢复设置:', settings.value)
  }

  // 批量更新设置
  const updateSettings = (newSettings: Partial<AppSettings>): void => {
    Object.assign(settings.value, newSettings)

    // 特殊处理 stopTokenIdsStr
    if (newSettings.stopTokenIdsStr) {
      try {
        const stopTokenIds = newSettings.stopTokenIdsStr
          .split(',')
          .map(id => parseInt(id.trim()))
          .filter(id => !isNaN(id))
        settings.value.stopTokenIds = stopTokenIds
      } catch (error) {
        console.error('解析 stopTokenIds 失败:', error)
      }
    }

    saveSettings()
  }

  // 重置为默认设置
  const resetToDefaults = (): void => {
    settings.value = { ...DEFAULT_SETTINGS }
    saveSettings()
  }

  // 监听智谱MaaS模式变化，自动切换API配置
  watch(
    () => settings.value.zhipuMaasMode,
    newValue => {
      if (newValue) {
        // 开启智谱MaaS模式时的自动配置
        console.log('开启智谱MaaS模式，自动配置API地址')
      } else {
        // 关闭智谱MaaS模式时可以选择是否恢复本地配置
        console.log('关闭智谱MaaS模式')
      }
    }
  )

  // 监听跨窗口设置变化
  const setupCrossWindowSync = (): (() => void) => {
    const handleStorageChange = (e: StorageEvent): void => {
      if (e.key === STORAGE_KEY && e.newValue) {
        try {
          const newSettings = JSON.parse(e.newValue) as AppSettings
          settings.value = { ...DEFAULT_SETTINGS, ...newSettings }
          updateCSSVariables()
          console.log('接收到跨窗口设置同步:', newSettings)
        } catch (error) {
          console.error('跨窗口设置同步失败:', error)
        }
      }
    }

    const handleCustomEvent = (e: CustomEvent): void => {
      if (e.detail) {
        settings.value = { ...DEFAULT_SETTINGS, ...e.detail }
        updateCSSVariables()
        console.log('接收到自定义设置同步事件:', e.detail)
      }
    }

    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('vlm-settings-changed', handleCustomEvent as EventListener)

    // 返回清理函数
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('vlm-settings-changed', handleCustomEvent as EventListener)
    }
  }

  return {
    settings: settings as Readonly<typeof settings>,
    enableStreamResponse,

    loadSettings,
    saveSettings,
    updateSetting,
    updateSettings,
    resetToDefaults,
    setupCrossWindowSync,
    getSettingsCopy,
    restoreFromCopy
  }
})
