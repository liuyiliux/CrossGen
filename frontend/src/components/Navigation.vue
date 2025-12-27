<template>
  <el-container>
    <el-header class="nav-header">
      <div class="nav-container">
        <!-- 品牌标识 -->
        <div class="brand" @click="goHome">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
          </svg>
          <span class="brand-name">{{ $t('navigation.brand') }}</span>
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
            active-text-color="var(--el-color-primary)"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>{{ $t('common.home') }}</span>
            </el-menu-item>
            <el-menu-item index="/config">
              <el-icon><Setting /></el-icon>
              <span>{{ $t('common.config') }}</span>
            </el-menu-item>
            <el-menu-item index="/history">
              <el-icon><Clock /></el-icon>
              <span>{{ $t('common.history') }}</span>
            </el-menu-item>
            <el-menu-item index="/batch">
              <el-icon><List /></el-icon>
              <span>{{ $t('common.batch') }}</span>
            </el-menu-item>
          </el-menu>
          
          <!-- 语言切换 -->
          <el-dropdown @command="handleLanguageChange">
            <span class="language-trigger">
              <el-icon><Language /></el-icon>
              <span>{{ $t('common.language') }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="zh-CN">{{ $t('common.chinese') }}</el-dropdown-item>
                <el-dropdown-item command="en">{{ $t('common.english') }}</el-dropdown-item>
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
import { HomeFilled, Setting, Clock, List, Language, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const { locale } = useI18n()

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
.nav-header {
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  color: var(--el-color-primary);
  font-size: 18px;
  
  &:hover {
    opacity: 0.8;
  }
}

.brand-name {
  font-weight: 600;
  font-size: 20px;
}

.nav-menu {
  border-bottom: none;
  
  &:not(.el-menu--collapse) {
    width: auto;
  }
}

.language-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
  color: var(--el-text-color-primary);
  
  &:hover {
    background-color: var(--el-bg-color-overlay);
    color: var(--el-color-primary);
  }
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 16px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .brand-name {
    font-size: 16px;
  }
  
  .nav-right {
    gap: 12px;
  }
  
  .language-trigger {
    padding: 6px 8px;
    
    span {
      display: none;
    }
  }
}
</style>