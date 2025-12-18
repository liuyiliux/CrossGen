<template>
  <el-container>
    <el-header class="nav-header">
      <div class="nav-container">
        <!-- 品牌标识 -->
        <div class="brand" @click="goHome">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
          </svg>
          <span class="brand-name">逸流</span>
        </div>
        
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
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/config">
            <el-icon><Setting /></el-icon>
            <span>配置管理</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><Clock /></el-icon>
            <span>历史记录</span>
          </el-menu-item>
          <el-menu-item index="/batch">
            <el-icon><List /></el-icon>
            <span>批量生成</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, Setting, Clock, List } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

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
}
</style>