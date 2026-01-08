<template>
  <div class="container">
    <div class="page-header">
      <div>
        <h1 class="page-title">生成结果</h1>
        <p class="page-subtitle">
          <span v-if="isGenerating">正在生成第 {{ store.progress.current + 1 }} / {{ store.progress.total }} 页</span>
          <span v-else-if="hasFailedImages">{{ failedCount }} 张图片生成失败，可点击重试</span>
          <span v-else>全部 {{ store.progress.total }} 张图片生成完成</span>
        </p>
      </div>
      <div style="display: flex; gap: 10px;">
        <button
          v-if="isGenerating"
          class="btn btn-danger"
          @click="stopGeneration"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
          停止生成
        </button>
        <button
          v-else-if="hasFailedImages"
          class="btn btn-primary"
          @click="retryAllFailed"
          :disabled="isRetrying"
        >
          {{ isRetrying ? '补全中...' : '一键补全失败图片' }}
        </button>
        <button class="btn" @click="router.push('/outline')" style="border:1px solid var(--border-color)">
          返回大纲
        </button>
      </div>
    </div>

    <div class="card">
      <div style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600;">生成进度</span>
        <span style="color: var(--primary); font-weight: 600;">{{ Math.round(progressPercent) }}%</span>
      </div>
      <div class="progress-container">
        <div class="progress-bar" :style="{ width: progressPercent + '%' }" />
      </div>

      <div v-if="store.error" class="error-msg">
        {{ store.error }}
      </div>

      <div class="grid-cols-4" style="margin-top: 40px;">
        <div v-for="image in store.images" :key="image.index" class="image-card">
          <!-- 获取对应的大纲页面信息 -->
          <template v-if="store.outline.pages[image.index]">
            <!-- 大纲页面信息 -->
            <div class="outline-info">
              <div class="page-type" :class="store.outline.pages[image.index].type">
                {{ store.outline.pages[image.index].type === 'cover' ? '封面' : 
                   store.outline.pages[image.index].type === 'summary' ? '总结' : '内容页' }}
              </div>
              <div class="page-content-preview">
                {{ store.outline.pages[image.index].content }}
              </div>
            </div>
          </template>
          
          <!-- 图片展示区域 -->
          <div class="image-preview" :class="{ 'error-placeholder': image.status === 'error' }">
            <!-- 成功图片 -->
            <div v-if="image.url && image.status === 'done'" class="success-image">
              <el-image
                :src="image.url"
                :alt="`第 ${image.index + 1} 页`"
                :preview-src-list="[image.url]"
                fit="cover"
                style="width: 100%; height: 100%;"
              />
            </div>
            
            <!-- 失败图片 -->
            <div v-else-if="image.status === 'error'" class="error-image">
              <div class="error-icon">!</div>
              <div class="status-text">生成失败</div>
              <div class="error-message-container">
                <!-- 显示错误信息，支持悬停查看完整信息 -->
                <el-tooltip
                  v-if="image.error"
                  :content="image.error"
                  placement="top"
                  effect="dark"
                  :show-after="200"
                  :hide-after="5000"
                  :enterable="true"
                  trigger="hover"
                >
                  <div class="error-message" title="{{ image.error }}">{{ image.error }}</div>
                </el-tooltip>
                <div v-else class="error-message">未知错误</div>
              </div>
            </div>
            
            <!-- 生成中/重试中 -->
            <div v-else-if="image.status === 'generating' || image.status === 'retrying'" class="processing-image">
              <div class="spinner"></div>
              <div class="status-text">{{ image.status === 'retrying' ? '重试中...' : '生成中...' }}</div>
            </div>
            
            <!-- 等待中 -->
            <div v-else class="waiting-image">
              <div class="status-text">等待中</div>
            </div>
            
            <!-- 重试按钮（所有状态都显示，除了生成中/重试中） -->
            <div class="image-overlay">
              <button
                class="overlay-btn"
                @click="regenerateImage(image.index)"
                :disabled="image.status === 'generating' || image.status === 'retrying' || isRetrying"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="M23 4v6h-6"></path><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
                重新生成
              </button>
            </div>
          </div>

          <!-- 底部信息栏 -->
          <div class="image-footer">
            <span class="page-label">Page {{ image.index + 1 }}</span>
            <span class="status-badge" :class="image.status">
              {{ getStatusText(image.status) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useGeneratorStore()

const error = ref('')
const isRetrying = ref(false)
const isStopped = ref(false)
// 初始化AbortController，确保所有请求使用同一个实例
const abortController = ref<AbortController>(new AbortController())

const isGenerating = computed(() => store.progress.status === 'generating')

const progressPercent = computed(() => store.progressPercent)

const hasFailedImages = computed(() => store.hasFailedImages())

const failedCount = computed(() => store.getFailedImages().length)

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    generating: '生成中',
    done: '已完成',
    error: '失败',
    retrying: '重试中'
  }
  return texts[status] || '等待中'
}

// 重试单张图片（异步并发执行，不阻塞）
async function retrySingleImage(index: number) {
  // 如果没有图像提供商ID或已经停止，不允许重试
  if (!store.imageProviderId || isStopped.value) {
    console.log('重试失败：缺少图像提供商或已停止')
    return
  }

  const page = store.outline.pages.find(p => p.index === index)
  if (!page) return

  // 创建新的AbortController用于重试请求
  const retryController = new AbortController()
  
  // 立即设置为重试状态
  store.setImageRetrying(index)

  try {
    // 调用API生成图片
    console.log(`重试生成第${index + 1}页图片`)
    console.log('使用提供商:', store.imageProviderId)
    console.log('提示词:', page.content)
    console.log('尺寸:', store.selectedSize)
    
    // 准备参考图数据，转换为后端期望的格式
    let referenceImagesForBackend: Array<{ type: string; image_url: string }> = []
    if (!store.useCoverAsReference && store.referenceImages.length > 0) {
      // 只有当不使用封面作为参考图时，才传递上传的参考图
      referenceImagesForBackend = store.referenceImages.map(img => ({
        type: "image_url",
        image_url: img.url
      }))
    }

    const response = await axios.post('/api/generate/image', {
      history_id: store.recordId,
      page_index: index,
      prompt: page.content,
      image_provider: store.imageProviderId,
      size: store.selectedSize,
      reference_images: referenceImagesForBackend,
      use_cover_as_reference: store.useCoverAsReference
    }, {
      signal: retryController.signal
    })
    
    console.log('API响应:', response.data)
    
    if (response.data.success && response.data.image_url) {
      // 更新图片状态为成功
      store.updateProgress(index, 'done', response.data.image_url)
    } else {
      // 更新图片状态为失败
      store.updateProgress(index, 'error', undefined, response.data.error || '生成失败')
    }
  } catch (error: any) {
    console.error(`重试生成第${index + 1}页图片失败:`, error)
    // 检查是否是取消请求导致的错误
    if (error.name !== 'AbortError') {
      store.updateProgress(index, 'error', undefined, error.response?.data?.detail || error.message || '生成失败')
    }
  } finally {
    // 重试完成后，检查是否所有图片都已处理
    checkAndUpdateGenerationStatus()
  }
}

// 检查并更新生成状态
function checkAndUpdateGenerationStatus() {
  // 检查是否所有图片都生成完成（包括重试成功的情况）
  const allImagesProcessed = store.images.every(img => 
    img.status === 'done' || img.status === 'error'
  );
  
  // 检查是否所有图片都生成成功
  const allImagesSuccessful = store.images.every(img => img.status === 'done');
  
  // 如果所有图片都已处理，更新状态为完成
  if (allImagesProcessed && store.progress.status === 'generating') {
    // 所有图片都已处理，更新生成状态为完成
    store.progress.status = 'done'
  }
  
  // 无论当前状态如何，只要所有图片都生成成功，就更新历史记录并跳转
  if (allImagesSuccessful) {
    // 强制更新store的进度状态为done
    store.progress.status = 'done'
    
    // 更新历史记录
    updateHistoryAfterGeneration()
  }
}

// 重新生成图片（成功的也可以重新生成，立即返回不等待）
function regenerateImage(index: number) {
  retrySingleImage(index)
}

// 批量重试所有失败的图片
async function retryAllFailed() {
  // 如果正在生成或已经停止，不允许批量重试
  if (!store.imageProviderId || isGenerating.value || isStopped.value) {
    console.log('批量重试失败：当前正在生成或已停止')
    return
  }

  const failedImages = store.getFailedImages()
  if (failedImages.length === 0) return

  isRetrying.value = true
  
  // 创建新的AbortController用于批量重试请求
  const retryController = new AbortController()

  try {
    // 并行重试所有失败的图片
    await Promise.all(failedImages.map(async (image) => {
      const page = store.outline.pages.find(p => p.index === image.index)
      if (!page) return

      // 设置为重试状态
      store.setImageRetrying(image.index)

      try {
        // 调用API生成图片
        console.log(`批量重试生成第${image.index + 1}页图片`)
        console.log('使用提供商:', store.imageProviderId)
        console.log('提示词:', page.content)
        console.log('尺寸:', store.selectedSize)
        
        // 准备参考图数据，转换为后端期望的格式
        let referenceImagesForBackend: Array<{ type: string; image_url: string }> = []
        if (!store.useCoverAsReference && store.referenceImages.length > 0) {
          // 只有当不使用封面作为参考图时，才传递上传的参考图
          referenceImagesForBackend = store.referenceImages.map(img => ({
            type: "image_url",
            image_url: img.url
          }))
        }

        const response = await axios.post('/api/generate/image', {
          history_id: store.recordId,
          page_index: image.index,
          prompt: page.content,
          image_provider: store.imageProviderId,
          size: store.selectedSize,
          reference_images: referenceImagesForBackend,
          use_cover_as_reference: store.useCoverAsReference
        }, {
          signal: retryController.signal
        })
        
        console.log('API响应:', response.data)
        
        if (response.data.success && response.data.image_url) {
          // 更新图片状态为成功
          store.updateProgress(image.index, 'done', response.data.image_url)
        } else {
          // 更新图片状态为失败
          store.updateProgress(image.index, 'error', undefined, response.data.error || '生成失败')
        }
      } catch (error: any) {
        console.error(`批量重试生成第${image.index + 1}页图片失败:`, error)
        // 检查是否是取消请求导致的错误
        if (error.name !== 'AbortError') {
          store.updateProgress(image.index, 'error', undefined, error.response?.data?.detail || error.message || '生成失败')
        }
      }
    }))
  } finally {
    isRetrying.value = false
    // 批量重试完成后，检查是否所有图片都已处理
    checkAndUpdateGenerationStatus()
  }
}

// 更新历史记录
async function updateHistoryAfterGeneration() {
  // 获取当前选择的文本和图像模型
  const textModel = store.textProviders.find(p => p.name === store.textProviderId)?.model || ''
  const imageModel = store.imageProviders.find(p => p.name === store.imageProviderId)?.model || ''
  
  // 更新历史记录状态
  if (store.recordId) {
    try {
      // 构建完整的历史记录更新数据，确保大纲和图片都被正确更新
      await axios.put(`/api/history/${store.recordId}`, {
        status: hasFailedImages.value ? 'success' : 'success', // 即使有失败图片，也标记为success，因为生成过程已结束
        outline: {
          raw: store.outline.raw,
          pages: store.outline.pages
        },
        images: store.images.map(img => ({
          index: img.index,
          url: img.url || '',
          status: img.status,
          error: img.error
        })),
        text_model: textModel,
        image_model: imageModel
      }, {
        signal: abortController.value.signal
      })
      console.log('历史记录更新成功，包含完整的大纲和图片信息')
    } catch (error: any) {
      console.error('更新历史记录失败:', error)
      // 检查是否是取消请求导致的错误
      if (error.name !== 'AbortError') {
        console.error('更新历史记录失败:', error)
      }
    }
  }
  
  // 完成生成
  store.finishGeneration('task-' + Date.now())
  
  // 如果没有失败的，跳转到结果页
  if (!hasFailedImages.value) {
    setTimeout(() => {
      router.push('/result')
    }, 1000)
  }
}

// 停止生成
const stopGeneration = () => {
  // 显示停止操作正在进行中的提示
  ElMessage.info('正在停止生成...')
  
  // 设置停止标志
  isStopped.value = true
  
  // 设置生成状态为完成
  store.progress.status = 'done'
  
  // 更新所有生成中的图片状态为已取消
  store.images.forEach(img => {
    if (img.status === 'generating' || img.status === 'retrying') {
      img.status = 'error'
      img.error = '生成已取消'
    }
  })
  
  // 取消所有正在进行的请求
  abortController.value.abort()
  console.log('已取消所有正在进行的请求')
  
  // 计算已生成的图片数量
  const generatedCount = store.images.filter(img => img.status === 'done').length
  
  // 显示停止成功的提示信息
  ElMessage.success(`生成已停止，共生成了${generatedCount}张图片`)
  
  // 添加一个短暂的延迟，确保所有请求都已被取消
  setTimeout(() => {
    // 跳转到大纲页面
    router.push('/outline')
  }, 500)
  
  // 重置 AbortController，准备下次生成
  abortController.value = new AbortController()
}

// 添加组件销毁时的清理逻辑
onUnmounted(() => {
  // 组件销毁时取消所有正在进行的请求
  if (abortController.value) {
    abortController.value.abort()
    console.log('组件销毁，已取消所有正在进行的请求')
  }
})

onMounted(async () => {
  if (store.outline.pages.length === 0) {
    router.push('/')
    return
  }

  // 重置AbortController，确保每次生成都有独立的控制器
  abortController.value = new AbortController()

  try {
    // 获取当前选择的文本和图像模型
    const textModel = store.textProviders.find(p => p.name === store.textProviderId)?.model || ''
    const imageModel = store.imageProviders.find(p => p.name === store.imageProviderId)?.model || ''
    
    // 更新历史记录，不管是否已经有recordId
    if (store.recordId) {
      // 更新现有历史记录
      console.log('更新现有历史记录:', store.recordId)
      
      // 调用API更新历史记录
      await axios.put(`/api/history/${store.recordId}`, {
        status: 'processing',
        images: store.images.map(img => ({
          index: img.index,
          url: img.url || '',
          status: img.status,
          error: img.error
        })),
        text_model: textModel,
        image_model: imageModel,
        // 确保大纲信息也被更新
        outline: {
          raw: store.outline.raw,
          pages: store.outline.pages
        }
      }, {
        signal: abortController.value.signal
      })
      
      console.log('历史记录更新成功')
    } else {
      // 如果没有recordId，创建新的历史记录
      console.log('创建新的历史记录')
      
      // 调用API创建历史记录
      const createResponse = await axios.post('/api/history', {
        topic: store.topic,
        platform: 'xiaohongshu', // 这里应该根据实际选择的平台来设置
        outline: {
          raw: store.outline.raw,
          pages: store.outline.pages
        },
        images: store.images.map(img => ({
          index: img.index,
          url: img.url || '',
          status: img.status,
          error: img.error
        })),
        status: 'processing',
        text_model: textModel,
        image_model: imageModel
      }, {
        signal: abortController.value.signal
      })
      
      console.log('历史记录创建成功:', createResponse.data)
      store.setRecordId(createResponse.data.id)
    }
  } catch (error: any) {
    console.error('创建/更新历史记录失败:', error)
    // 检查是否是取消请求导致的错误
    if (error.name === 'AbortError') {
      console.log('创建/更新历史记录请求已取消')
      return
    }
  }

  store.startGeneration()

  console.log('开始生成图片')
  
  // 遍历所有页面，批量生成图片
    for (let index = 0; index < store.outline.pages.length; index++) {
      // 检查是否已停止生成
      if (store.progress.status !== 'generating' || isStopped.value) {
        console.log('生成已停止')
        break
      }

      const image = store.images[index]
      // 如果图片已经生成成功，跳过
      if (image && image.status === 'done' && image.url) {
        console.log(`跳过第${index + 1}页，图片已生成`)
        continue
      }
      
      // 获取当前页面内容
      const page = store.outline.pages[index]
      if (!page) continue
      
      // 设置生成状态
      store.updateProgress(index, 'generating')
      
      try {
        // 检查是否已停止生成
        if (store.progress.status !== 'generating' || isStopped.value) {
          console.log('生成已停止，跳过第', index + 1, '页')
          break
        }
        
        // 调用API生成图片
        console.log(`生成第${index + 1}页图片`)
        console.log('使用提供商:', store.imageProviderId)
        console.log('提示词:', page.content)
        console.log('尺寸:', store.selectedSize)
        
        const response = await axios.post('/api/generate/image', {
          history_id: store.recordId,
          page_index: index,
          prompt: page.content,
          image_provider: store.imageProviderId,
          size: store.selectedSize
        }, {
          signal: abortController.value.signal
        })
        
        // 检查是否已停止生成
        if (store.progress.status !== 'generating' || isStopped.value) {
          console.log('生成已停止，忽略第', index + 1, '页结果')
          break
        }
        
        console.log('API响应:', response.data)
        
        if (response.data.success && response.data.image_url) {
          // 更新图片状态为成功
          store.updateProgress(index, 'done', response.data.image_url)
        } else {
          // 更新图片状态为失败
          store.updateProgress(index, 'error', undefined, response.data.error || '生成失败')
        }
      } catch (error: any) {
        // 检查是否已停止生成
        if (store.progress.status !== 'generating' || isStopped.value) {
          console.log('生成已停止，忽略第', index + 1, '页错误')
          break
        }
        
        console.error(`生成第${index + 1}页图片失败:`, error)
        // 检查是否是取消请求导致的错误
        if (error.name === 'AbortError') {
          console.log('第', index + 1, '页生成请求已取消')
          break
        }
        
        store.updateProgress(index, 'error', undefined, error.response?.data?.detail || error.message || '生成失败')
      }
      
      // 等待500毫秒再生成下一张，避免请求过于频繁，同时提高生成速度
      await new Promise(resolve => setTimeout(resolve, 500))
    }
    
    // 生成循环结束后，无论是否有失败的图片，都检查并更新生成状态
    checkAndUpdateGenerationStatus()
})
</script>

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
  color: var(--text-primary);
}

.page-subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: var(--text-sub);
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
  background: var(--primary);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.progress-container {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 20px;
}

.progress-bar {
  height: 100%;
  background: var(--primary);
  transition: width 0.3s ease;
}

.error-msg {
  color: #ff4d4f;
  font-size: 14px;
  margin-bottom: 20px;
  padding: 12px;
  background: #fff5f5;
  border-radius: 6px;
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

.image-preview {
  aspect-ratio: 3/4;
  overflow: hidden;
  position: relative;
  flex: 1;
  min-height: 240px;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.image-preview.error-placeholder {
  background: #fff5f5;
}

.success-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-image {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
}

.processing-image,
.waiting-image {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.overlay-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.2s;
}

.overlay-btn:hover {
  background: var(--primary);
  color: white;
}

.overlay-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.error-message {
  font-size: 12px;
  color: #FF4D4F;
  text-align: center;
  padding: 0 20px;
  margin: 5px 0;
  line-height: 1.4;
  max-height: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  width: 100%;
  word-break: break-word;
  cursor: pointer;
}

/* 自定义tooltip样式 */
:deep(.error-tooltip) {
  max-width: 500px !important;
  word-break: break-all;
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 13px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.85) !important;
  border-radius: 6px !important;
  z-index: 9999 !important;
}

.error-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #ff4d4f;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.outline-info {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.page-type {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-type.cover {
  background: #FFE8E8;
  color: #FF4D4F;
}

.page-type.content {
  background: #E6F7FF;
  color: #1890FF;
}

.page-type.summary {
  background: #F6FFED;
  color: #52C41A;
}

.page-content-preview {
  font-size: 12px;
  color: var(--text-primary);
  line-height: 1.4;
  max-height: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  word-break: break-word;
}

.image-footer {
  padding: 12px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-label {
  font-size: 12px;
  color: var(--text-sub);
}

.status-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-badge.done {
  background: #E6F7ED;
  color: #52C41A;
}

.status-badge.generating,
.status-badge.retrying {
  background: #E6F4FF;
  color: #1890FF;
}

.status-badge.error {
  background: #FFF1F0;
  color: #FF4D4F;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--primary);
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
