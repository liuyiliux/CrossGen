<template>
  <div class="container">
    <div class="page-header">
      <div>
        <h1 class="page-title">创作完成</h1>
        <p class="page-subtitle">恭喜！你的{{ getPlatformLabel(store.selectedPlatform) }}图文已生成完毕，共 {{ store.images.length }} 张</p>
      </div>
      <div style="display: flex; gap: 12px;">
        <button class="btn" @click="startOver" style="background: white; border: 1px solid var(--el-border-color);">
          再来一篇
        </button>
        <button class="btn btn-primary" @click="downloadAll">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          一键下载
        </button>
      </div>
    </div>

    <div class="card">
      <div class="grid-cols-4">
        <div v-for="image in store.images" :key="image.index" class="image-card group">
          <!-- Image Area -->
          <div 
            v-if="image.url" 
            style="position: relative; aspect-ratio: 3/4; overflow: hidden; cursor: pointer;" 
            @click="viewImage(image.url)"
          >
            <img
              :src="image.url"
              :alt="`第 ${image.index + 1} 页`"
              style="width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s;"
            />
            <!-- Regenerating Overlay -->
            <div v-if="regeneratingIndex === image.index" style="position: absolute; inset: 0; background: rgba(255,255,255,0.8); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10;">
               <div class="spinner" style="width: 24px; height: 24px; border-width: 2px; border-color: var(--el-color-primary); border-top-color: transparent;"></div>
               <span style="font-size: 12px; color: var(--el-color-primary); margin-top: 8px; font-weight: 600;">重绘中...</span>
            </div>
            
            <!-- Hover Overlay -->
            <div v-else style="position: absolute; inset: 0; background: rgba(0,0,0,0.3); opacity: 0; transition: opacity 0.2s; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;" class="hover-overlay">
              预览大图
            </div>
          </div>
          
          <!-- Action Bar -->
          <div style="padding: 12px; border-top: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 12px; color: var(--el-text-color-secondary);">Page {{ image.index + 1 }}</span>
            <div style="display: flex; gap: 8px;">
              <button 
                style="border: none; background: none; color: var(--el-text-color-secondary); cursor: pointer; display: flex; align-items: center;"
                title="重新生成此图"
                @click="handleRegenerate(image)"
                :disabled="regeneratingIndex === image.index"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
              </button>
              <button 
                style="border: none; background: none; color: var(--el-color-primary); cursor: pointer; font-size: 12px;"
                @click="downloadOne(image)"
              >
                下载
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: var(--el-text-color-primary);
}

.page-subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--el-color-primary);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.grid-cols-4 {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.image-card {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.image-card:hover .hover-overlay {
  opacity: 1;
}

.image-card:hover img {
  transform: scale(1.05);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--el-color-primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'
import { ElMessage } from 'element-plus'
import axios from 'axios'
// 导入共享平台映射工具
import { getPlatformLabel, loadPlatformConfig } from '../utils/platformUtils'

const router = useRouter()
const store = useGeneratorStore()
const regeneratingIndex = ref<number | null>(null)

// 加载平台配置
onMounted(async () => {
  await loadPlatformConfig()
})

const viewImage = (url: string) => {
  const baseUrl = url.split('?')[0]
  window.open(baseUrl + '?thumbnail=false', '_blank')
}

const startOver = () => {
  store.reset()
  router.push('/')
}

const downloadOne = (image: any) => {
  if (image.url) {
    const link = document.createElement('a')
    // 使用后端图片代理下载API
    link.href = `http://localhost:8000/api/image/download?url=${encodeURIComponent(image.url)}`
    link.download = `yiliu_page_${image.index + 1}.png`
    link.click()
    ElMessage.success('图片下载开始')
  }
}

const downloadAll = () => {
  // 收集所有图片URL
  const imageUrls = store.images.filter(img => img.url).map(img => img.url);
  
  if (imageUrls.length === 0) {
    ElMessage.warning('没有可下载的图片')
    return
  }
  
  // 调用后端打包API
  const link = document.createElement('a')
  link.href = `http://localhost:8000/api/image/download-all?image_urls=${encodeURIComponent(JSON.stringify(imageUrls))}`
  link.download = `yiliu_images.zip`
  link.click()
  ElMessage.success('开始打包下载所有图片')
}

const handleRegenerate = async (image: any) => {
  if (!store.taskId || regeneratingIndex.value !== null) return

  regeneratingIndex.value = image.index
  try {
    // TODO: 实现重新生成图片的API调用
    console.log('重新生成图片:', image.index)
    
    // 模拟API调用
    setTimeout(() => {
      const newUrl = 'https://picsum.photos/800/1200?random=' + Date.now()
      store.updateImage(image.index, newUrl)
      regeneratingIndex.value = null
      ElMessage.success('图片重新生成成功')
    }, 1500)
  } catch (e: any) {
    ElMessage.error('重绘失败: ' + e.message)
    regeneratingIndex.value = null
  }
}
</script>
