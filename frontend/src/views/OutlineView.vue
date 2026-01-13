<template>
  <div class="container" style="max-width: 100%;">
    <div class="page-header" style="max-width: 1200px; margin: 0 auto 30px auto;">
      <div>
        <h1 class="page-title">编辑大纲</h1>
        <p class="page-subtitle">调整页面顺序，修改文案，打造完美内容</p>
        
        <!-- 整体生成状态提示 -->
        <div v-if="store.progress.status === 'done' && store.images.length > 0" class="overall-status success">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
          <span>所有图片生成成功！</span>
        </div>
        
        <!-- 主题编辑输入框容器，使用两列布局 -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px; max-width: 1200px;">
          <!-- 生成主题输入框 -->
          <div class="topic-edit">
            <label style="display: block; font-size: 14px; color: #333; margin-bottom: 8px; font-weight: 500;">生成主题</label>
            <el-input
              v-model="store.topic"
              placeholder="请输入生成主题"
              size="large"
              clearable
              style="width: 100%;"
            />
            <span style="font-size: 12px; color: #666; margin-top: 4px; display: block;">修改主题后，将基于新主题生成内容</span>
          </div>
          
          <!-- 总标题输入 -->
          <div class="topic-edit">
            <label style="display: block; font-size: 14px; color: #333; margin-bottom: 8px; font-weight: 500;">总标题</label>
            <el-input
              v-model="store.outline.title"
              placeholder="请输入总标题"
              size="large"
              clearable
              style="width: 100%;"
              @input="store.updateOutlineTitle(store.outline.title || '')"
            />
            <span style="font-size: 12px; color: #666; margin-top: 4px; display: block;">图文内容的总标题，用于展示在所有图片之上</span>
          </div>
          
          <!-- 总文案输入，占据两列 -->
          <div class="topic-edit" style="grid-column: 1 / -1;">
            <label style="display: block; font-size: 14px; color: #333; margin-bottom: 8px; font-weight: 500;">总文案</label>
            <el-input
              v-model="store.outline.copywriting"
              placeholder="请输入总文案，最好包含相关#话题标签"
              size="large"
              clearable
              type="textarea"
              :rows="3"
              style="width: 100%; resize: vertical; min-height: 100px;"
              @input="store.updateOutlineCopywriting(store.outline.copywriting || '')"
            />
            <span style="font-size: 12px; color: #666; margin-top: 4px; display: block;">图文内容的总文案，将与所有图片关联，建议添加相关#话题标签</span>
          </div>
        </div>
      </div>
      <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
          <div style="width: 240px;">
            <label style="display: block; font-size: 12px; color: #666; margin-bottom: 4px;">选择图片服务商</label>
            <el-select 
              v-model="imageProviderId" 
              placeholder="请选择图片服务商" 
              size="large" 
              style="width: 100%;"
              clearable
              @change="onImageProviderChange"
            >
              <el-option 
                v-for="provider in store.imageProviders.filter(p => p.enabled)" 
                :key="provider.name" 
                :label="`${provider.name} (${provider.type})`" 
                :value="provider.name" 
              >
                <template #default="{ option }">
                  <div class="option-content">
                    <div class="option-name">{{ provider.name }}</div>
                    <div class="option-desc">{{ provider.type }} - {{ provider.model }}</div>
                  </div>
                </template>
              </el-option>
            </el-select>
          </div>
          
          <div style="width: 200px;">
            <label style="display: block; font-size: 12px; color: #666; margin-bottom: 4px;">选择图片尺寸</label>
            <el-select 
              v-model="store.selectedSize" 
              placeholder="请选择图片尺寸" 
              size="large" 
              style="width: 100%;"
              clearable
            >
              <el-option 
                v-for="size in getSupportedSizes()" 
                :key="size" 
                :label="size" 
                :value="size" 
              />
            </el-select>
          </div>
          
          <!-- 参考图配置 -->
          <div v-if="getCurrentImageProvider()?.support_reference_image" style="width: 240px;">
            <label style="display: block; font-size: 12px; color: #666; margin-bottom: 4px;">参考图</label>
            <div style="display: flex; gap: 8px; align-items: center;">
              <el-switch 
                v-model="store.referenceImageEnabled" 
                size="large"
                @change="onReferenceImageToggle"
              />
              <el-dropdown trigger="click" @command="onReferenceImageOptionSelect">
                <el-button size="small" :disabled="!store.referenceImageEnabled">
                  {{ referenceImageOptionLabel }}
                  <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="upload">上传图片</el-dropdown-item>
                    <el-dropdown-item command="cover">使用封面图片</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
          
          <!-- 参考图上传 -->
          <div v-if="store.referenceImageEnabled" style="width: 240px;">
            <label style="display: block; font-size: 12px; color: #666; margin-bottom: 4px;">上传参考图</label>
            <el-upload
              v-model:file-list="referenceImageFiles"
              :action="''"
              :before-upload="handleBeforeUpload"
              :limit="getMaxReferenceImages()"
              :on-exceed="handleExceed"
              list-type="picture-card"
              :auto-upload="false"
            >
              <!-- 上传按钮插槽 -->
              <template #default>
                <el-icon><plus /></el-icon>
              </template>
              <!-- 文件列表项插槽 -->
              <template #file="{ file }">
                <el-image
                  :src="(file as UploadFile).url"
                  :alt="(file as UploadFile).name"
                  fit="cover"
                  style="width: 100%; height: 100%;"
                />
                <span class="el-upload-list__item-actions">
                  <span
                    class="el-upload-list__item-preview"
                    @click="handlePictureCardPreview(file as UploadFile)"
                  >
                    <el-icon><zoom-in /></el-icon>
                  </span>
                  <span
                    class="el-upload-list__item-delete"
                    @click="handleRemove(file as UploadFile)"
                  >
                    <el-icon><delete /></el-icon>
                  </span>
                </span>
              </template>
            </el-upload>
            <el-dialog v-model="previewVisible" title="预览" width="500px">
              <el-image
                :src="previewImage"
                fit="contain"
                style="width: 100%; height: 100%;"
              />
            </el-dialog>
          </div>
          
          <div style="width: 240px;">
            <label style="display: block; font-size: 12px; color: #666; margin-bottom: 4px;">选择视频服务商</label>
            <el-select 
              v-model="videoProviderId" 
              placeholder="请选择视频服务商" 
              size="large" 
              style="width: 100%;"
              clearable
            >
              <el-option 
                v-for="provider in store.videoProviders" 
                :key="provider.name" 
                :label="`${provider.name} (${provider.type})`" 
                :value="provider.name" 
              >
                <template #default="{ option }">
                  <div class="option-content">
                    <div class="option-name">{{ provider.name }}</div>
                    <div class="option-desc">{{ provider.type }} - {{ provider.model }}</div>
                  </div>
                </template>
              </el-option>
            </el-select>
          </div>
          <button class="btn btn-secondary" @click="goBack" style="background: white; border: 1px solid var(--border-color);">
            上一步
          </button>
          <button class="btn btn-primary" @click="startGeneration" :disabled="!imageProviderId">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path><line x1="16" y1="8" x2="2" y2="22"></line><line x1="17.5" y1="15" x2="9" y2="15"></line></svg>
            开始生成图片
          </button>
          <button class="btn btn-success" @click="startVideoGeneration" :disabled="!videoProviderId">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            开始生成视频
          </button>
        </div>
    </div>

    <div class="outline-grid">
      <div 
        v-for="(page, idx) in store.outline.pages" 
        :key="page.index"
        class="card outline-card"
        :draggable="true"
        @dragstart="onDragStart($event, idx)"
        @dragover.prevent="onDragOver($event, idx)"
        @drop="onDrop($event, idx)"
        :class="{ 'dragging-over': dragOverIndex === idx }"
      >
        <!-- 拖拽手柄 -->
        <div class="card-top-bar">
          <div class="page-info">
             <span class="page-number">P{{ idx + 1 }}</span>
             <span class="page-type" :class="page.type">{{ getPageTypeName(page.type) }}</span>
          </div>
          
          <div class="card-controls">
            <div class="drag-handle" title="拖拽排序">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="1"></circle><circle cx="9" cy="5" r="1"></circle><circle cx="9" cy="19" r="1"></circle><circle cx="15" cy="12" r="1"></circle><circle cx="15" cy="5" r="1"></circle><circle cx="15" cy="19" r="1"></circle></svg>
            </div>
            <button class="icon-btn" @click="deletePage(idx)" title="删除此页">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
        </div>

        <!-- 图片提示词输入 -->
        <div class="content-section">
          <div class="section-title">图片提示词</div>
          <textarea
            v-model="page.image_prompt"
            class="textarea-paper"
            placeholder="在此输入图片提示词..."
            @input="store.updatePage(page.index, page.image_prompt)"
            rows="5"
            style="resize: vertical; min-height: 100px; max-height: 500px;"
          />
          <div class="word-count">{{ (page.image_prompt || '').length }} 字</div>
        </div>
        

        
        <!-- 图片预览区域 -->
        <div v-if="store.images[idx]" class="image-preview-section">
          <div 
            v-if="store.images[idx].status === 'generating' || store.images[idx].status === 'retrying'"
            class="image-status generating"
          >
            <div class="spinner"></div>
            <span>{{ store.images[idx].status === 'retrying' ? '重试中...' : '生成中...' }}</span>
            <button 
              class="stop-btn"
              @click="stopSingleImageGeneration(idx)"
            >
              停止
            </button>
          </div>
          <div 
            v-else-if="store.images[idx].status === 'error'"
            class="image-status error"
          >
            <span>生成失败</span>
            <button 
              class="retry-btn"
              @click="generateSingleImage(idx)"
              :disabled="!imageProviderId"
            >
              点击重试
            </button>
            <div class="error-message">{{ store.images[idx].error }}</div>
          </div>
          <div 
            v-else-if="store.images[idx].status === 'done' && store.images[idx].url"
            class="image-preview"
          >
            <el-image
              :src="store.images[idx].url"
              :alt="`Page ${idx + 1}`"
              :preview-src-list="store.images.filter(img => img.url).map(img => img.url)"
              :initial-index="idx"
              fit="cover"
              class="preview-image"
            />
            <div class="image-actions">
              <button 
                class="retry-btn"
                @click="generateSingleImage(idx)"
                :disabled="!imageProviderId"
              >
                重新生成
              </button>
            </div>
          </div>
        </div>

        <div class="single-generate-buttons">
          <button 
            class="btn btn-small btn-primary"
            @click="generateSingleImage(idx)"
            :disabled="!imageProviderId"
          >
            生成图片
          </button>
          <button 
            class="btn btn-small btn-success"
            @click="generateSingleVideo(idx)"
            :disabled="!videoProviderId"
          >
            生成视频
          </button>
        </div>
      </div>

      <!-- 添加按钮卡片 -->
      <div class="card add-card-dashed" @click="addPage('content')">
        <div class="add-content">
          <div class="add-icon">+</div>
          <span>添加页面</span>
        </div>
      </div>
    </div>
    
    <div style="height: 100px;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
// 导入共享平台映射工具
import { loadPlatformConfig } from '../utils/platformUtils'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { ArrowDown, Plus, ZoomIn, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import { useGeneratorStore } from '../stores/generator'

const router = useRouter()
const store = useGeneratorStore()

const dragOverIndex = ref<number | null>(null)
const draggedIndex = ref<number | null>(null)// 图片服务商选择
const imageProviderId = ref<string | null>(store.imageProviderId)
const videoProviderId = ref<string | null>(store.videoProviderId)
// 请求管理对象，用于存储和取消正在进行的请求
const activeRequests = ref<Record<number, AbortController>>({})

// 参考图相关数据
const referenceImageFiles = ref<UploadFile[]>([])
const previewVisible = ref(false)
const previewImage = ref('')

// 计算属性：获取当前选中的图片提供商
const getCurrentImageProvider = () => {
  if (!imageProviderId.value) return null
  return store.imageProviders.find(p => p.name === imageProviderId.value) || null
}

// 计算属性：获取参考图选项标签
const referenceImageOptionLabel = computed(() => {
  if (store.useCoverAsReference) {
    return '使用封面图片'
  }
  return '上传图片'
})

// 获取最大参考图数量
const getMaxReferenceImages = () => {
  const provider = getCurrentImageProvider()
  if (provider?.max_reference_images) {
    return provider.max_reference_images
  }
  return provider?.support_multiple_reference_images ? 4 : 1
}

// 参考图相关方法
const onImageProviderChange = () => {
  // 重置参考图设置
  const provider = getCurrentImageProvider()
  if (!provider?.support_reference_image) {
    store.referenceImageEnabled = false
    store.referenceImages = []
    store.useCoverAsReference = false
    referenceImageFiles.value = []
  }
}

const onReferenceImageToggle = (enabled: boolean) => {
  if (!enabled) {
    store.referenceImages = []
    store.useCoverAsReference = false
    referenceImageFiles.value = []
  }
}

const onReferenceImageOptionSelect = (command: string) => {
  if (command === 'cover') {
    store.useCoverAsReference = true
    store.referenceImages = []
    referenceImageFiles.value = []
  } else {
    store.useCoverAsReference = false
  }
}

// 图片上传相关方法
const handleBeforeUpload = (rawFile: File) => {
  // 这里只是本地处理，不实际上传到服务器
  // 生成一个本地URL用于预览，同时生成base64字符串用于发送到后端
  const reader = new FileReader()
  reader.readAsDataURL(rawFile)
  reader.onload = () => {
    const base64Url = reader.result as string
    const file: UploadFile & { base64Url?: string } = {
      uid: Date.now(),
      name: rawFile.name,
      status: 'success',
      url: URL.createObjectURL(rawFile), // 使用blob URL作为预览URL
      base64Url: base64Url, // 单独保存base64字符串用于发送到后端
      raw: rawFile
    }
    referenceImageFiles.value.push(file)
    // 保存到store
    saveReferenceImagesToStore()
  }
  return false
}

const handleExceed = (files: File[], fileList: UploadFile[]) => {
  ElMessage.warning(`最多只能上传 ${getMaxReferenceImages()} 张参考图`)
}

const handleRemove = (file: UploadFile) => {
  const index = referenceImageFiles.value.findIndex(item => item.uid === file.uid)
  if (index !== -1) {
    // 释放blob URL
    if (file.url && typeof file.url === 'string' && file.url.startsWith('blob:')) {
      URL.revokeObjectURL(file.url)
    }
    referenceImageFiles.value.splice(index, 1)
    // 保存到store
    saveReferenceImagesToStore()
  }
}

const handlePictureCardPreview = (file: UploadFile) => {
  previewImage.value = file.url as string
  previewVisible.value = true
}

const saveReferenceImagesToStore = () => {
  if (store.useCoverAsReference) {
    // 使用封面图片，不需要保存上传的图片
    store.referenceImages = []
  } else {
    // 保存上传的图片到store，格式为{ file: File; url: string }
    // 注意：这里使用的是base64Url，而不是url，因为url是blob URL，无法直接发送到后端
    store.referenceImages = referenceImageFiles.value.map(file => ({
      file: file.raw as File,
      url: (file as any).base64Url as string || file.url as string
    }))
  }
}

const getPageTypeName = (type: string) => {
  const names = {
    cover: '封面',
    content: '内容',
    summary: '总结'
  }
  return names[type as keyof typeof names] || '内容'
}

// 根据选择的提供商返回支持的尺寸
const getSupportedSizes = () => {
  if (!imageProviderId.value) {
    return []
  }
  
  const provider = store.imageProviders.find(p => p.name === imageProviderId.value)
  if (!provider) {
    return []
  }
  
  // 从提供商配置中获取支持的尺寸
  let sizes = provider.supported_sizes || []
  
  // 处理supported_sizes字段，确保它是一个数组
  if (typeof sizes === 'string') {
    try {
      // 尝试解析JSON字符串
      sizes = JSON.parse(sizes)
    } catch (e) {
      console.error('解析supported_sizes失败:', e)
      sizes = []
    }
  }
  
  // 确保sizes是一个数组
  if (!Array.isArray(sizes)) {
    sizes = []
  }
  
  // 如果尺寸列表为空，使用默认尺寸
  if (sizes.length === 0) {
    // 根据提供商类型设置默认尺寸
    if (provider.type === 'siliconflow' && provider.model === 'Qwen/Qwen-Image') {
      // Qwen-Image默认尺寸
      sizes = ["1328x1328", "1664x928", "928x1664", "1472x1140", "1140x1472", "1584x1056", "1056x1584"]
    } else if (provider.type === 'siliconflow' && provider.model === 'Kwai-Kolors/Kolors') {
      // Kolors默认尺寸
      sizes = ["1024x1024", "960x1280", "768x1024", "720x1440", "720x1280"]
    } else {
      // 默认通用尺寸
      sizes = ["1024x1024", "1024x1792", "1792x1024"]
    }
  }
  
  return sizes
}

// 加载服务商数据
const loadProviders = async () => {
  try {
    // 加载图像服务商
    const imageResponse = await axios.get('/api/config/providers/image')
    if (imageResponse.data?.providers?.providers) {
      const imageProviders = Object.entries(imageResponse.data.providers.providers).map(([name, provider]: [string, any]) => ({
        name,
        type: provider.type || 'openai',
        model: provider.model,
        ...provider
      }))
      store.setImageProviders(imageProviders)
    }
    
    // 加载视频服务商
    try {
      const videoResponse = await axios.get('/api/config/providers/video')
      if (videoResponse.data?.providers?.providers) {
        const videoProviders = Object.entries(videoResponse.data.providers.providers).map(([name, provider]: [string, any]) => ({
          name,
          type: provider.type || 'openai',
          model: provider.model,
          ...provider
        }))
        store.setVideoProviders(videoProviders)
      }
    } catch (videoError: any) {
      console.error('加载视频服务商数据失败:', videoError)
      // 视频服务可能尚未实现，不影响其他功能
    }
  } catch (error: any) {
    console.error('加载服务商数据失败:', error)
  }
}

// 组件挂载时检查状态
onMounted(async () => {
  // 加载平台配置
  await loadPlatformConfig()
  
  // 检查是否有编辑的历史记录ID
  const editHistoryId = localStorage.getItem('editHistoryId')
  // 检查是否有复制的历史记录
  const copiedHistory = localStorage.getItem('copiedHistory')
  if (copiedHistory) {
    try {
      const historyData = JSON.parse(copiedHistory)
      // 清空本地存储
      localStorage.removeItem('copiedHistory')
      
      // 使用复制的历史记录数据
        if (historyData.outline) {
          store.setOutline(historyData.outline.raw, historyData.outline.pages, historyData.outline.title, historyData.outline.copywriting)
          // 如果有主题，保存到store
          if (historyData.topic) {
            store.topic = historyData.topic
          }
        // 如果有文本模型和图像模型，保存到store
        if (historyData.text_model) {
          store.textProviderId = historyData.text_model
        }
        if (historyData.image_model) {
          store.imageProviderId = historyData.image_model
        }
        // 根据是否是编辑模式设置recordId
        if (editHistoryId) {
          // 编辑模式，使用原有的历史记录ID
          store.recordId = editHistoryId
          // 清空编辑模式标记
          localStorage.removeItem('editHistoryId')
        } else {
          // 复制模式，创建新记录
          store.recordId = null
        }
      }
    } catch (e) {
      console.error('解析复制的历史记录失败:', e)
    }
  }

  if (store.outline.pages.length === 0) {
    // 如果没有大纲内容，返回首页
    ElMessage.warning('请先生成大纲')
    router.push('/')
    return
  }
  
  // 加载服务商数据
  loadProviders()
})

// 拖拽逻辑
const onDragStart = (e: DragEvent, index: number) => {
  draggedIndex.value = index
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.dropEffect = 'move'
  }
}

const onDragOver = (e: DragEvent, index: number) => {
  if (draggedIndex.value === index) return
  dragOverIndex.value = index
}

const onDrop = (e: DragEvent, index: number) => {
  dragOverIndex.value = null
  if (draggedIndex.value !== null && draggedIndex.value !== index) {
    store.movePage(draggedIndex.value, index)
  }
  draggedIndex.value = null
}

const deletePage = (index: number) => {
  if (confirm('确定要删除这一页吗？')) {
    store.deletePage(index)
  }
}

const addPage = (type: 'cover' | 'content' | 'summary') => {
  store.addPage(type, '')
  // 滚动到底部
  nextTick(() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
  })
}

const goBack = () => {
  router.back()
}

const startGeneration = () => {
  if (!imageProviderId.value) {
    ElMessage.warning('请选择图片服务商')
    return
  }
  // 保存选择的图片服务商ID到状态管理
  store.setImageProviderId(imageProviderId.value)
  // 保存参考图设置
  saveReferenceImagesToStore()
  router.push('/generate')
}

const startVideoGeneration = () => {
  if (!videoProviderId.value) {
    ElMessage.warning('请选择视频服务商')
    return
  }
  // 保存选择的视频服务商ID到状态管理
  store.setVideoProviderId(videoProviderId.value)
  // 跳转到视频生成页面（假设已有该路由）
  ElMessage.info('视频生成功能正在开发中')
}

// 将blob URL转换为base64字符串
const blobUrlToBase64 = async (url: string): Promise<string> => {
  try {
    const response = await fetch(url)
    const blob = await response.blob()
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  } catch (error) {
    console.error('转换blob URL为base64失败:', error)
    throw error
  }
}

// 单张生成图片
const generateSingleImage = async (index: number) => {
  if (!imageProviderId.value) {
    ElMessage.warning('请先选择图片服务商')
    return
  }
  
  // 保存选择的图片服务商ID到状态管理
  store.setImageProviderId(imageProviderId.value)
  
  // 保存参考图设置
  saveReferenceImagesToStore()
  
  // 确保images数组有足够的元素
  while (store.images.length <= index) {
    store.images.push({
      index: store.images.length,
      url: '',
      status: 'error' // 使用error状态替代idle状态，因为GeneratedImage接口不支持idle状态
    })
  }
  
  // 如果有正在进行的请求，先取消
  if (activeRequests.value[index]) {
    activeRequests.value[index].abort()
    delete activeRequests.value[index]
  }
  
  // 创建新的AbortController
  const controller = new AbortController()
  activeRequests.value[index] = controller
  
  // 设置生成状态
  store.images[index].status = 'generating'
  store.images[index].error = undefined
  
  console.group(`生成第${index + 1}页图片`)
  console.log('使用提供商:', imageProviderId.value)
  console.log('当前store中的imageProviderId:', store.imageProviderId)
  console.log('提示词:', store.outline.pages[index].content)
  console.log('参考图设置:', {
    referenceImages: store.referenceImages,
    useCoverAsReference: store.useCoverAsReference
  })
  console.log('历史记录ID:', store.recordId)
  
  try {
    // 确保使用正确的提供商ID
    if (imageProviderId.value) {
      store.imageProviderId = imageProviderId.value
      console.log('已更新store.imageProviderId为:', imageProviderId.value)
    }
    
    // 检查recordId是否为null，如果是，则创建新的历史记录
    let historyId = store.recordId
    if (!historyId) {
      try {
        // 创建新的历史记录
        console.log('准备创建新历史记录...')
        const createHistoryResponse = await axios.post('/api/history', {
          topic: store.topic,
          platform: store.selectedPlatform || 'xiaohongshu', // 使用store中的platform或默认值
          outline: {
            raw: store.outline.raw,
            title: store.outline.title,
            copywriting: store.outline.copywriting,
            pages: store.outline.pages
          },
          images: [], // 初始为空数组
          status: 'processing', // 设置初始状态
          text_model: store.textProviderId,
          image_model: store.imageProviderId
        }, {
          signal: controller.signal
        })
        
        if (createHistoryResponse.data && createHistoryResponse.data.id) {
          historyId = createHistoryResponse.data.id
          store.recordId = historyId
          console.log('创建新历史记录成功，recordId:', historyId)
        } else {
          throw new Error('创建历史记录失败: 无效的响应数据')
        }
      } catch (historyError: any) {
        console.error('创建历史记录失败:', historyError)
        console.error('历史记录创建错误详情:', historyError.response?.data || historyError.message)
        store.images[index].status = 'error'
        store.images[index].error = '创建历史记录失败，请重试'
        ElMessage.error(`创建历史记录失败: ${historyError.response?.data?.detail || historyError.message}`)
        return
      }
    }
    
    // 准备参考图数据，转换为后端期望的格式
    let referenceImagesForBackend: Array<{ type: string; image_url: string }> = []
    if (!store.useCoverAsReference && store.referenceImages.length > 0) {
      // 只有当不使用封面作为参考图时，才传递上传的参考图
      referenceImagesForBackend = await Promise.all(
        store.referenceImages.map(async img => {
          let imageUrl = img.url
          // 如果是blob URL，转换为base64字符串
          if (imageUrl.startsWith('blob:')) {
            console.log('转换blob URL为base64:', imageUrl)
            imageUrl = await blobUrlToBase64(imageUrl)
            console.log('转换成功，base64长度:', imageUrl.length)
          }
          return {
            type: "image_url",
            image_url: imageUrl
          }
        })
      )
    }

    // 调用API生成单张图片
    console.log('准备调用生成图片API...')
    const response = await axios.post('/api/generate/image', {
      history_id: historyId,
      page_index: index,
      prompt: store.outline.pages[index].image_prompt,
      image_provider: store.imageProviderId, // 使用store中的imageProviderId确保一致性
      size: store.selectedSize, // 添加用户选择的尺寸
      reference_images: referenceImagesForBackend,
      use_cover_as_reference: store.useCoverAsReference
    }, {
      signal: controller.signal
    })
    
    console.log('API响应:', response.data)
    
    if (response.data.success) {
        // 更新图片状态
        store.images[index].status = 'done'
        // 处理图片URL，确保格式正确并添加代理
        const processedUrl = store.processImageUrl(response.data.image_url)
        store.images[index].url = processedUrl
        ElMessage.success(`第${index + 1}页图片生成成功`)
        console.log('生成成功，图片URL:', response.data.image_url)
        console.log('处理后图片URL:', processedUrl)
        
        // 检查所有图片是否都已完成
        const allImagesDone = store.outline.pages.every(page => {
          const image = store.images[page.index]
          return image && image.status === 'done' && image.url
        })
        
        if (allImagesDone) {
          // 所有图片都已完成，显示整体成功状态
          ElMessage.success('所有图片生成成功！')
        }
      } else {
        // 处理生成失败
        store.images[index].status = 'error'
        store.images[index].error = response.data.error || '生成失败'
        ElMessage.error(`第${index + 1}页图片生成失败: ${response.data.error || '生成失败'}`)
        console.error('生成失败:', response.data.error)
      }
  } catch (error: any) {
    // 处理网络错误
    if (error.name === 'AbortError') {
      // 请求已取消
      console.log(`第${index + 1}页图片生成请求已取消`)
      store.images[index].status = 'error'
      store.images[index].error = '生成已取消'
      return
    }
    
    store.images[index].status = 'error'
    store.images[index].error = error.message || '网络错误，请重试'
    ElMessage.error(`第${index + 1}页图片生成失败: ${error.message || '网络错误，请重试'}`)
    console.error('网络错误:', error)
  } finally {
    // 清除请求
    delete activeRequests.value[index]
    console.groupEnd()
  }
}

// 停止单张图片生成
const stopSingleImageGeneration = (index: number) => {
  if (activeRequests.value[index]) {
    activeRequests.value[index].abort()
    delete activeRequests.value[index]
    store.images[index].status = 'error'
    store.images[index].error = '生成已取消'
    ElMessage.info(`第${index + 1}页图片生成已停止`)
  }
}

// 停止所有图片生成
const stopAllImageGeneration = () => {
  let stoppedCount = 0
  for (const index in activeRequests.value) {
    const numIndex = parseInt(index)
    if (activeRequests.value[numIndex]) {
      activeRequests.value[numIndex].abort()
      delete activeRequests.value[numIndex]
      store.images[numIndex].status = 'error'
      store.images[numIndex].error = '生成已取消'
      stoppedCount++
    }
  }
  
  if (stoppedCount > 0) {
    ElMessage.info(`已停止${stoppedCount}个图片生成任务`)
  } else {
    ElMessage.warning('没有正在进行的图片生成任务')
  }
}



// 单张生成视频
const generateSingleVideo = (index: number) => {
  if (!videoProviderId.value) {
    ElMessage.warning('请先选择视频服务商')
    return
  }
  // 保存选择的视频服务商ID到状态管理
  store.setVideoProviderId(videoProviderId.value)
  ElMessage.info(`正在生成第${index + 1}页的视频...`)
  // 实现单张生成视频的逻辑，这里可以调用API或其他方式
  // ...
}
</script>

<style scoped lang="scss">
@use '../styles/outline-xhs-style.scss' as *;
/* 网格布局 */
.outline-grid {
  display: grid;
  /* 响应式列：最小宽度 320px，自动填充 */
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.outline-card {
  display: flex;
  flex-direction: column;
  padding: 24px;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
  border-radius: 16px;
  background: white;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  /* 保持一定的长宽比感，虽然高度自适应，但由于 flex column 和内容撑开，
     这里设置一个 min-height 让它看起来像个竖向卡片 */
  min-height: 420px;
  position: relative;
  backdrop-filter: blur(10px);
}

.outline-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.1);
  z-index: 10;
  border-color: var(--el-color-primary);
}

.outline-card.dragging-over {
  border: 2px dashed var(--el-color-primary);
  opacity: 0.8;
  background: rgba(255, 36, 66, 0.02);
}

/* 顶部栏 */
.card-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-number {
  font-size: 18px;
  font-weight: 700;
  color: var(--el-color-primary);
  font-family: 'Inter', sans-serif;
  background: rgba(255, 36, 66, 0.06);
  padding: 4px 10px;
  border-radius: 12px;
}

.page-type {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.08) 0%, rgba(255, 36, 66, 0.02) 100%);
  color: var(--el-color-primary);
  box-shadow: 0 2px 4px rgba(255, 36, 66, 0.1);
  border: 1px solid rgba(255, 36, 66, 0.15);
}

.page-type.cover { 
  color: #FF4D4F; 
  background: #FFF1F0; 
  border-color: #FFCCC7;
}
.page-type.content { 
  color: #1890FF; 
  background: #E6F7FF; 
  border-color: #91D5FF;
}
.page-type.summary { 
  color: #52C41A; 
  background: #F6FFED; 
  border-color: #B7EB8F;
}

.card-controls {
  display: flex;
  gap: 10px;
  opacity: 0.6;
  transition: all 0.3s ease;
  background: #fafafa;
  padding: 6px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.outline-card:hover .card-controls { 
  opacity: 1;
  background: #ffffff;
  border-color: var(--el-color-primary);
}

.drag-handle {
  cursor: grab;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.drag-handle:hover {
  background: rgba(255, 36, 66, 0.1);
  color: var(--el-color-primary);
}

.drag-handle:active { 
  cursor: grabbing;
  background: rgba(255, 36, 66, 0.15);
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 6px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.icon-btn:hover { 
  color: #FF4D4F;
  background: rgba(255, 77, 79, 0.1);
}

.icon-btn:active { 
  background: rgba(255, 77, 79, 0.15);
}

/* 文本区域 - 核心 */
.textarea-paper {
  flex: 1; /* 占据剩余空间 */
  width: 100%;
  border: 1px solid #f0f0f0;
  background: #fafafa;
  padding: 16px;
  font-size: 16px; /* 更大的字号 */
  line-height: 1.7; /* 舒适行高 */
  color: #333;
  resize: none; /* 禁止手动拉伸，保持卡片整体感 */
  font-family: inherit;
  margin-bottom: 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
  /* 添加 placeholder 样式 */
}

.textarea-paper::placeholder {
  color: #bdbdbd;
  font-style: italic;
}

.textarea-paper:focus {
  outline: none;
  border-color: var(--el-color-primary);
  background: #ffffff;
  box-shadow: 0 0 0 2px rgba(255, 36, 66, 0.1);
}

.word-count {
  text-align: right;
  font-size: 12px;
  color: #9e9e9e;
  margin-top: auto;
  margin-bottom: 16px;
  font-weight: 500;
}

/* 图片预览区域 */
.image-preview-section {
  margin-top: 12px;
  margin-bottom: 8px;
  border: 1px solid #f5f5f5;
  border-radius: 6px;
  overflow: hidden;
}

/* 图片预览 */
.image-preview {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  background: #f9f9f9;
  overflow: hidden;
  cursor: pointer;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-preview:hover .preview-image {
  transform: scale(1.05);
}

/* 图片操作按钮 */
.image-actions {
  position: absolute;
  bottom: 8px;
  right: 8px;
  display: flex;
  gap: 8px;
}

.retry-btn {
  padding: 4px 8px;
  font-size: 11px;
  background: white;
  border: 1px solid var(--el-color-primary);
  color: var(--el-color-primary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  background: var(--el-color-primary);
  color: white;
}

.retry-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 停止按钮样式 */
.stop-btn {
  padding: 4px 8px;
  font-size: 11px;
  background: white;
  border: 1px solid var(--el-color-danger);
  color: var(--el-color-danger);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}

.stop-btn:hover {
  background: var(--el-color-danger);
  color: white;
}

/* 生成状态 */
.image-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 3/4;
  padding: 12px;
  text-align: center;
}

.image-status.generating {
  background: #f0f8ff;
  color: var(--el-color-primary);
  gap: 8px;
}

.image-status.error {
  background: #fff2f0;
  color: var(--el-color-danger);
  gap: 8px;
}

/* 错误信息 */
.error-message {
  font-size: 11px;
  color: var(--el-color-danger);
  margin-top: 4px;
  line-height: 1.4;
  word-break: break-word;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* 加载动画 */
.spinner {
  width: 20px;
  height: 20px;
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

/* 单张生成按钮 */
.single-generate-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.btn-small {
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
}

.btn-primary {
  background: var(--el-color-primary);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
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

.btn-success {
  background: var(--el-color-success);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-success:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-success:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 添加卡片 */
.add-card-dashed {
  border: 2px dashed #e0e0e0;
  background: #fafafa;
  box-shadow: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 400px;
  color: #9e9e9e;
  transition: all 0.2s;
}

.add-card-dashed:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background: rgba(255, 36, 66, 0.02);
}

.add-content {
  text-align: center;
}

.add-icon {
  font-size: 40px;
  font-weight: 300;
  margin-bottom: 12px;
  line-height: 1;
}

/* 整体生成状态 */
.overall-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  margin: 12px 0;
}

.overall-status.success {
  background: #F6FFED;
  color: #52C41A;
  border: 1px solid #B7EB8F;
}

.overall-status.processing {
  background: #E6F7FF;
  color: #1890FF;
  border: 1px solid #91D5FF;
}

.overall-status.error {
  background: #FFF1F0;
  color: #FF4D4F;
  border: 1px solid #FFCCC7;
}

/* 页面头部 */
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
  padding: 24px 0;
  border-bottom: 1px solid #e8e8e8;
  flex-wrap: wrap;
  gap: 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 30px;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  color: var(--el-text-color-primary);
  line-height: 1.2;
}

.page-subtitle {
  margin: 12px 0 0 0;
  font-size: 16px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: var(--el-color-primary);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.3);
}

.btn-secondary {
  background: white;
  color: var(--el-text-color-primary);
  border: 1px solid var(--el-border-color);
}

.btn-secondary:hover {
  background: #f9f9f9;
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn:disabled:hover {
  background: var(--el-color-primary);
  border-color: var(--el-border-color);
  color: white;
}
</style>
