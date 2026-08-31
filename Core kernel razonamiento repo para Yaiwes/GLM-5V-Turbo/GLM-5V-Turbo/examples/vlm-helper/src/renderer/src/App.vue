<template>
  <ThemeProvider>
    <div v-if="isFloatingMode">
      <FloatingChat />
    </div>
    <AppLayout v-else>
      <ChatView />
    </AppLayout>
  </ThemeProvider>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeMount, nextTick } from 'vue'
import ThemeProvider from './components/ThemeProvider.vue'
import AppLayout from './layouts/AppLayout.vue'
import ChatView from './views/ChatView.vue'
import FloatingChat from './components/FloatingChat.vue'
import { useSettingsInit } from './composables/useSettingsInit'

const isFloatingMode = ref(false)

// 初始化设置
const { settingsStore } = useSettingsInit()

// 检查是否为悬浮窗模式
const checkMode = (): void => {
  const hash = window.location.hash
  isFloatingMode.value = hash === '#/floating' || hash === '#floating'
}

// 隐藏全局loading（仅在应用真正启动时延迟显示）
const hideGlobalLoading = (): void => {
  const globalLoading = document.getElementById('global-loading')
  const appElement = document.getElementById('app')

  if (globalLoading && appElement) {
    appElement.classList.add('loaded')
    globalLoading.classList.add('fade-out')

    // 动画完成后移除loading元素
    setTimeout(() => {
      if (globalLoading.parentNode) {
        globalLoading.parentNode.removeChild(globalLoading)
      }
    }, 500)
  }
}

onBeforeMount(() => {
  // 确保模式检查在所有初始化之前完成
  checkMode()
})

onMounted(async () => {
  // 监听哈希变化
  window.addEventListener('hashchange', checkMode)

  // 简化等待逻辑，只等待下一个tick
  await nextTick()

  // 检查是否是应用的首次启动（通过主进程判断）
  try {
    const windowWithApi = window as { api?: { isFirstLaunch?: () => Promise<boolean>; rendererInitializationComplete?: () => Promise<boolean> } }
    const isFirstLaunch = await windowWithApi.api?.isFirstLaunch?.()

    const delay = isFirstLaunch ? 600 : 100
    setTimeout(async () => {
      hideGlobalLoading()

      // 通知主进程渲染进程初始化完成
      try {
        await windowWithApi.api?.rendererInitializationComplete?.()
        console.log('已通知主进程：渲染进程初始化完成')
      } catch (error) {
        console.error('通知主进程初始化完成失败:', error)
      }
    }, delay)
  } catch (error) {
    console.error('检查启动状态失败:', error)
    setTimeout(() => {
      hideGlobalLoading()
    }, 100)
  }
})
</script>
