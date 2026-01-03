<template>
  <el-container>
    <el-header class="nav-header">
      <div class="nav-container">
        <!-- 品牌标识 -->
        <div class="brand" @click="goHome">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
          </svg>
          <span class="brand-name">{{ t('navigation.brand') }}</span>
        </div>
        
        <div class="nav-right">
          <!-- 导航菜单 -->
          <el-menu 
            :default-active="activeIndex" 
            class="nav-menu" 
            mode="horizontal"
            @select="handleSelect"
            background-color="white"
            text-color="var(--el-text-color-primary)"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>{{ t('common.home') }}</span>
            </el-menu-item>
            <el-menu-item index="/config">
              <el-icon><Setting /></el-icon>
              <span>{{ t('common.config') }}</span>
            </el-menu-item>
            <el-menu-item index="/history">
              <el-icon><Clock /></el-icon>
              <span>{{ t('common.history') }}</span>
            </el-menu-item>
            <el-menu-item index="/batch">
              <el-icon><List /></el-icon>
              <span>{{ t('common.batch') }}</span>
            </el-menu-item>
          </el-menu>
          
          <!-- 语言切换 -->
          <el-dropdown @command="handleLanguageChange">
            <span class="language-trigger">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;">
                <circle cx="12" cy="12" r="10"/>
                <path d="M2 12h20"/>
                <path d="m12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1 4-10"/>
                <path d="M12 2v20"/>
              </svg>
              <span>{{ t('common.language') }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="zh-CN">{{ t('common.chinese') }}</el-dropdown-item>
                <el-dropdown-item command="en">{{ t('common.english') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { HomeFilled, Setting, Clock, List, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const { locale, t } = useI18n()

// 计算当前激活的菜单项
const activeIndex = computed(() => {
  return route.path
})

// 导航到首页
const goHome = () => {
  router.push('/')
}

// 处理菜单选择
const handleSelect = (index: string) => {
  router.push(index)
}

// 处理语言切换
const handleLanguageChange = (lang: string) => {
  locale.value = lang
  localStorage.setItem('app-language', lang)
}
</script>

<style scoped lang="scss">
// 导航栏容器 / Navigation Container
.nav-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: var(--xhs-shadow-sm);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all var(--xhs-duration-base) var(--xhs-ease-default);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--xhs-space-lg);
  height: 72px;
}

// 右侧导航区域 / Navigation Right
.nav-right {
  display: flex;
  align-items: center;
  gap: var(--xhs-space-md);
}

// 品牌标识 / Brand Identity
.brand {
  display: flex;
  align-items: center;
  gap: var(--xhs-space-sm);
  cursor: pointer;
  transition: all var(--xhs-duration-base) var(--xhs-ease-default);
  font-weight: var(--xhs-font-weight-semibold);
  color: var(--xhs-primary);
  font-size: var(--xhs-text-lg);
  padding: 8px 16px;
  border-radius: var(--xhs-radius-xl);
  background: var(--xhs-primary-soft);

  svg {
    color: var(--xhs-primary);
    transition: all var(--xhs-duration-base) var(--xhs-ease-default);
  }

  &:hover {
    transform: translateY(-2px);
    background: rgba(255, 36, 66, 0.12);
    box-shadow: var(--xhs-shadow-md);

    svg {
      transform: scale(1.1);
    }
  }

  &:active {
    transform: translateY(0);
  }
}

.brand-name {
  font-weight: var(--xhs-font-weight-bold);
  font-size: var(--xhs-text-xl);
  letter-spacing: 0.5px;
}

// 导航菜单 / Navigation Menu
.nav-menu {
  border-bottom: none;
  background: transparent;

  &:not(.el-menu--collapse) {
    width: auto;
  }

  // 菜单项样式 / Menu Item Styles
  :deep(.el-menu-item) {
    padding: 0 var(--xhs-space-md);
    margin: 0 4px;
    border-radius: var(--xhs-radius-lg);
    height: 40px;
    line-height: 40px;
    transition: all var(--xhs-duration-base) var(--xhs-ease-default);
    font-weight: var(--xhs-font-weight-medium);
    color: var(--xhs-text-secondary);

    &:hover {
      background: var(--xhs-bg-secondary);
      color: var(--xhs-primary);
    }

    &.is-active {
      background: linear-gradient(135deg, var(--xhs-primary) 0%, #FF6B9D 100%);
      color: #FFFFFF !important;
      font-weight: var(--xhs-font-weight-semibold);
      box-shadow: 0 2px 8px rgba(255, 36, 66, 0.25);
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
  }

  // 图标样式 / Icon Styles
  :deep(.el-menu-item .el-icon) {
    font-size: 18px;
    margin-right: 6px;
    transition: transform var(--xhs-duration-fast) var(--xhs-ease-default);
  }

  :deep(.el-menu-item:hover .el-icon) {
    transform: scale(1.15);
  }
}

// 语言切换触发器 / Language Trigger
.language-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 10px 16px;
  border-radius: var(--xhs-radius-lg);
  transition: all var(--xhs-duration-base) var(--xhs-ease-default);
  color: var(--xhs-text-secondary);
  background: var(--xhs-bg-secondary);
  font-weight: var(--xhs-font-weight-medium);

  svg {
    transition: transform var(--xhs-duration-fast) var(--xhs-ease-default);
  }

  &:hover {
    background: var(--xhs-primary-soft);
    color: var(--xhs-primary);
    transform: translateY(-1px);
    box-shadow: var(--xhs-shadow-sm);

    svg {
      transform: rotate(180deg);
    }
  }

  &:active {
    transform: translateY(0);
  }
}

// 响应式设计 / Responsive Design
@media (max-width: 768px) {
  .nav-container {
    padding: 0 var(--xhs-space-md);
    height: 64px;
  }

  .nav-menu {
    display: none;
  }

  .brand {
    padding: 6px 12px;
  }

  .brand-name {
    font-size: var(--xhs-text-base);
  }

  .nav-right {
    gap: var(--xhs-space-sm);
  }

  .language-trigger {
    padding: 8px 12px;

    span {
      display: none;
    }
  }
}
</style>