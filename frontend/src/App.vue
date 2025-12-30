<template>
  <div id="app">
    <el-config-provider :locale="elementPlusLocale">
      <!-- 导航栏，首页隐藏，其他页面显示 -->
      <Navigation v-if="$route.path !== '/'" />
      <!-- 主内容区域 -->
      <main class="main-content" :class="{ 'has-navigation': $route.path !== '/' }">
        <router-view />
      </main>
    </el-config-provider>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Navigation from './components/Navigation.vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'

const { locale } = useI18n()

// 根据当前语言获取Element Plus的locale
const elementPlusLocale = computed(() => {
  return locale.value === 'zh-CN' ? zhCn : en
})
</script>

<style lang="scss">
// ============================================
// 应用根样式 / App Root Styles
// 小红书风格 - 沉浸式体验
// ============================================

#app {
  font-family: var(--xhs-font-display), var(--xhs-font-body), -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: relative;

  // 添加背景渐变
  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--xhs-gradient-bg-1);
    z-index: -1;
    pointer-events: none;
  }

  // 添加装饰性背景元素
  &::after {
    content: '';
    position: fixed;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 100%;
    background: var(--xhs-gradient-bg-2);
    z-index: -1;
    pointer-events: none;
    animation: floatBg 20s ease-in-out infinite;
  }
}

// 全局重置
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: transparent;
  overflow: hidden;
}

// 主内容区域样式
.main-content {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  z-index: 1;

  // 首页不需要顶部边距
  padding-top: 0;

  // 非首页页面，当导航栏显示时，添加顶部边距
  &.has-navigation {
    padding-top: 72px;
  }

  // 添加底部装饰性渐变
  &::after {
    content: '';
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: linear-gradient(to top, var(--xhs-bg-primary) 0%, transparent 100%);
    z-index: -1;
    pointer-events: none;
  }
}

// 背景浮动动画
@keyframes floatBg {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

// 暗色主题适配
.dark #app {
  &::before {
    background: linear-gradient(180deg, #1A1A1A 0%, #2D2D2D 50%, #1A1A2E 100%);
  }

  &::after {
    background: radial-gradient(ellipse at top right, rgba(255, 36, 66, 0.12) 0%, transparent 50%);
  }
}
</style>