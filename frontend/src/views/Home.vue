<template>
  <div class="home-container">
    <!-- 背景图片轮播 -->
    <ShowcaseBackground />
    
    <!-- Hero Area -->
      <div class="hero-section">
        <div class="hero-content">
          <div class="brand-pill">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
            {{ t('home.brandPill') }}
          </div>
          <div class="platform-slogan">
            {{ t('home.platformSlogan') }}
          </div>
          <h1 class="page-title">{{ t('home.pageTitle') }}</h1>
          <p class="page-subtitle">{{ t('home.pageSubtitle') }}</p>
        </div>

      <!-- 主题输入组合框 -->
      <ComposerInput
        ref="composerRef"
        v-model="generatorStore.topic"
        :loading="generatorStore.loading"
        @generate="handleGenerate"
        @imagesChange="handleImagesChange"
      />
    </div>
    
    <!-- 生成结果 -->
      <el-card v-if="generateResult" shadow="hover" class="result-card" transition="el-fade-in-down">
        <template #header>
          <div class="result-header">
            <h2 class="card-title">{{ t('home.resultTitle') }}</h2>
            <div class="result-actions">
              <el-button type="success" size="small" @click="copyResult">
                <el-icon><CopyDocument /></el-icon>
                {{ t('home.copy') }}
              </el-button>
              <el-button type="info" size="small" @click="regenerate">
                <el-icon><RefreshRight /></el-icon>
                {{ t('home.regenerate') }}
              </el-button>
            </div>
          </div>
        </template>
      
      <div class="result-content">
        <!-- 平台标签 -->
        <div class="platform-info">
          <el-tag size="large" type="primary" class="platform-tag">
            {{ getPlatformLabel(generateResult.platform) }}
          </el-tag>
          <span class="generation-time">
            {{ t('home.generationTime') }}{{ generateResult.generation_time.toFixed(2) }}s
          </span>
        </div>
        
        <!-- 标题 -->
        <h3 class="result-title">{{ generateResult.title }}</h3>
        
        <!-- 正文内容 -->
        <div class="result-text">
          <el-divider content-position="left">{{ t('home.contentText') }}</el-divider>
          <div class="content-text">{{ generateResult.content }}</div>
        </div>
        
        <!-- 生成图片 -->
        <div v-if="generateResult.images.length > 0" class="result-images">
          <el-divider content-position="left">{{ t('home.generatedImages') }}</el-divider>
          <el-image-viewer
            v-if="showImageViewer"
            :url-list="generateResult.images"
            @close="showImageViewer = false"
          />
          <div class="image-grid">
            <el-image
              v-for="(image, index) in generateResult.images"
              :key="index"
              :src="image"
              :preview-src-list="generateResult.images"
              fit="cover"
              class="result-image"
              @click="showImageViewer = true"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><PictureRounded /></el-icon>
                </div>
              </template>
            </el-image>
          </div>
        </div>
        
        <!-- 生成时间 -->
        <div class="result-footer">
          <span class="create-time">
            {{ t('home.createTime') }}{{ formatTime(generateResult.created_at) }}
          </span>
        </div>
      </div>
    </el-card>
    
    <!-- 快速操作 -->
    <div class="quick-actions">
      <h3 class="section-title">{{ t('home.quickActions') }}</h3>
      <div class="action-cards">
        <el-card shadow="hover" @click="$router.push('/batch')" class="action-card">
          <div class="action-card-content">
            <div class="action-icon batch-icon">
              <el-icon><List /></el-icon>
            </div>
            <h4>{{ t('home.batchGenerate') }}</h4>
            <p>{{ t('home.batchDesc') }}</p>
            <el-button type="primary" size="small" link>{{ t('home.goTo') }}</el-button>
          </div>
        </el-card>
        
        <el-card shadow="hover" @click="$router.push('/config')" class="action-card">
          <div class="action-card-content">
            <div class="action-icon config-icon">
              <el-icon><Setting /></el-icon>
            </div>
            <h4>{{ t('home.configManagement') }}</h4>
            <p>{{ t('home.configDesc') }}</p>
            <el-button type="primary" size="small" link>{{ t('home.goTo') }}</el-button>
          </div>
        </el-card>
        
        <el-card shadow="hover" @click="$router.push('/history')" class="action-card">
          <div class="action-card-content">
            <div class="action-icon history-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <h4>{{ t('home.historyRecords') }}</h4>
            <p>{{ t('home.historyDesc') }}</p>
            <el-button type="primary" size="small" link>{{ t('home.goTo') }}</el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import { useI18n } from 'vue-i18n'
import {
  Document,
  ChatLineRound,
  MagicStick,
  Loading,
  CopyDocument,
  RefreshRight,
  PictureRounded,
  List,
  Setting,
  Clock
} from '@element-plus/icons-vue'
import axios from 'axios'
import dayjs from 'dayjs'

// 引入组件
import ShowcaseBackground from '../components/home/ShowcaseBackground.vue'
import ComposerInput from '../components/home/ComposerInput.vue'

const router = useRouter()
const { t } = useI18n()

// 表单引用
const composerRef = ref<InstanceType<typeof ComposerInput> | null>(null)

// 引入状态管理
import { useGeneratorStore } from '../stores/generator'

const generatorStore = useGeneratorStore()

// 生成状态
const showImageViewer = ref(false)
const generateResult = ref<any>(null)
const loadingProviders = ref(false)

// 加载服务商数据
const loadProviders = async () => {
  loadingProviders.value = true
  try {
    // 加载文本服务商
    const textResponse = await axios.get('/api/config/providers/text')
    if (textResponse.data?.providers?.providers) {
      const textProviders = Object.entries(textResponse.data.providers.providers).map(([name, provider]: [string, any]) => ({
        name,
        type: provider.type || 'openai',
        model: provider.model,
        ...provider
      }))
      generatorStore.setTextProviders(textProviders)
    }
    
    // 加载图像服务商
    const imageResponse = await axios.get('/api/config/providers/image')
    if (imageResponse.data?.providers?.providers) {
      const imageProviders = Object.entries(imageResponse.data.providers.providers).map(([name, provider]: [string, any]) => ({
        name,
        type: provider.type || 'openai',
        model: provider.model,
        ...provider
      }))
      generatorStore.setImageProviders(imageProviders)
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
        generatorStore.setVideoProviders(videoProviders)
      }
    } catch (videoError: any) {
      console.error('加载视频服务商数据失败:', videoError)
      // 视频服务可能尚未实现，不影响其他功能
    }
  } catch (error: any) {
    console.error('加载服务商数据失败:', error)
  } finally {
    loadingProviders.value = false
  }
}

// 导入共享平台映射工具
import { getPlatformLabel, loadPlatformConfig } from '../utils/platformUtils'

// 组件挂载时加载服务商数据和平台配置
onMounted(async () => {
  await loadPlatformConfig()
  loadProviders()
})

// 格式化时间
const formatTime = (time: string | Date) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

/**
 * 处理图片变化
 */
function handleImagesChange(images: File[]) {
  generatorStore.setUserImages(images)
}

/**
 * 开始生成
 */
const handleGenerate = async () => {
  // 防止重复提交
  if (generatorStore.loading) {
    console.log(t('home.generatingInProgress'))
    return
  }
  
  if (!generatorStore.topic.trim()) return

  generatorStore.setLoading(true)
  generatorStore.setError(null)
  
  // 创建全局加载指示器
  const loadingInstance = ElLoading.service({
    lock: true,
    text: t('home.generatingOutline'),
    background: 'rgba(255, 255, 255, 0.8)'
  })

  try {
    const imageFiles = generatorStore.userImages
    // 确保platform是string类型，使用默认值'xiaohongshu'如果为null
    const platform = generatorStore.selectedPlatform || 'xiaohongshu'

    const result = await generateOutline(
      generatorStore.topic.trim(),
      platform,
      imageFiles.length > 0 ? imageFiles : undefined
    )

    if (result.success && result.pages) {
      // 从API返回的结果中提取title和copywriting
      let title = ''
      let copywriting = ''
      const content = result.outline || ''
      
      // 查找标题
      const titleMatch = content.match(/【标题】：(.*?)\n/)
      if (titleMatch && titleMatch[1]) {
        title = titleMatch[1].trim()
      }
      
      // 查找文案
      const copywritingMatch = content.match(/【文案】：(.*?)\n【图片提示词】：/s)
      if (copywritingMatch && copywritingMatch[1]) {
        copywriting = copywritingMatch[1].trim()
      }
      
      // 使用状态管理存储结果，传递title和copywriting
      generatorStore.setOutline(content, result.pages, title, copywriting)
      
      ElMessage.success(t('home.generateSuccess'))
      
      // 清理预览
      composerRef.value?.clearPreviews()
      // 保留用户上传的图片，用于后续生成
      // generatorStore.setUserImages([])
      
      // 跳转到大纲编辑页面
      router.push('/outline')
    } else {
      generatorStore.setError(result.error || '生成失败')
      ElMessage.error(result.error || '生成失败')
    }
  } catch (err: any) {
    generatorStore.setError(err.message || '网络错误，请重试')
    ElMessage.error(err.message || '网络错误，请重试')
    console.error('生成失败:', err)
  } finally {
    generatorStore.setLoading(false)
    // 关闭全局加载指示器
    loadingInstance.close()
  }
}

/**
 * 调用大纲生成API
 */
const generateOutline = async (topic: string, platform: string, imageFiles?: File[]) => {
  try {
    const formData = new FormData()
    formData.append('topic', topic)
    formData.append('platform', platform) // 使用选择的平台
    
    // 添加文本服务商参数
    if (generatorStore.textProviderId) {
      formData.append('text_provider', generatorStore.textProviderId)
    }
    
    // 添加图像服务商参数
    if (generatorStore.imageProviderId) {
      formData.append('image_provider', generatorStore.imageProviderId)
    }
    
    // 添加图片文件
    if (imageFiles && imageFiles.length > 0) {
      imageFiles.forEach((file, index) => {
        formData.append('images', file, file.name)
      })
    }
    
    const response = await axios.post('/api/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data?.success && response.data?.results?.length > 0) {
      // 获取第一个结果
      const firstResult = response.data.results[0]
      // 从结果中提取页面信息
      let pages = []
      
      // 检查是否有拆分后的页面信息
      if (firstResult.metadata && firstResult.metadata.pages) {
        // 使用后端拆分的页面信息
        pages = firstResult.metadata.pages.map((page, index) => ({
          index,
          type: 'content',
          content: page.content,
          image_prompt: page.content  // 将content复制到image_prompt
        }))
      } else {
        // 没有拆分的页面信息，返回失败
        console.error('API返回成功但没有页面信息')
        return {
          success: false,
          error: '生成失败：未获取到有效的页面信息'
        }
      }
      
      // 保存历史记录ID到store
      if (response.data.history_id) {
        generatorStore.setRecordId(response.data.history_id)
      } else {
        // 如果API没有返回history_id，创建历史记录
        await createHistoryRecord(
          generatorStore.topic.trim(),
          platform,
          { raw: firstResult.content, pages },
          [],
          'success' // 大纲生成成功，状态为success
        )
      }
      
      return {
        success: true,
        outline: firstResult.content,
        pages: pages
      }
    } else {
      // 处理API返回的错误
      const errorMsg = response.data?.message || response.data?.detail || '生成失败'
      console.error('API返回错误:', errorMsg)
      return {
        success: false,
        error: errorMsg
      }
    }
  } catch (error: any) {
    // 处理网络错误、超时等
    console.error('生成大纲失败:', error)
    let errorMsg = '网络错误，请重试'
    
    if (error.code === 'ECONNABORTED') {
      errorMsg = '请求超时，请检查网络连接后重试'
    } else if (error.response) {
      // 服务器返回错误状态码
      errorMsg = error.response.data?.message || error.response.data?.detail || `服务器错误 (${error.response.status})`
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorMsg = '服务器无响应，请检查网络连接或稍后重试'
    }
    
    return {
      success: false,
      error: errorMsg
    }
  }
}

// 复制结果
const copyResult = () => {
  if (!generateResult.value) return
  
  const resultText = `${generateResult.value.title}\n\n${generateResult.value.content}`
  navigator.clipboard.writeText(resultText)
    .then(() => {
      ElMessage.success(t('home.copySuccess'))
    })
    .catch(() => {
      ElMessage.error(t('home.copyFailed'))
    })
}

// 重新生成
const regenerate = () => {
  if (!generateResult.value) return
  handleGenerate(generateResult.value.platform)
}

/**
 * 创建历史记录
 */
async function createHistoryRecord(
  topic: string,
  platform: string,
  outline: any,
  images: any[],
  status: string
) {
  try {
    // 获取文本提供商信息
    const textProvider = generatorStore.textProviders.find(p => p.name === generatorStore.textProviderId)
    // 获取图像提供商信息
    const imageProvider = generatorStore.imageProviders.find(p => p.name === generatorStore.imageProviderId)
    
    const response = await axios.post('/api/history', {
      topic,
      platform,
      outline,
      images,
      status,
      // 保存完整的文本提供商名称和模型信息
      text_model: textProvider ? `${textProvider.name} (${textProvider.model})` : generatorStore.textProviderId || '默认模型',
      // 保存完整的图像提供商名称和模型信息
      image_model: imageProvider ? `${imageProvider.name} (${imageProvider.model})` : generatorStore.imageProviderId || '默认模型'
    })
    
    if (response.data?.id) {
      generatorStore.setRecordId(response.data.id)
      console.log('历史记录创建成功:', response.data.id)
    }
  } catch (error: any) {
    console.error('创建历史记录失败:', error)
  }
}
</script>

<style scoped lang="scss">
// 使用小红书风格设计变量
.home-container {
  padding: var(--xhs-space-md);
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  background: var(--xhs-gradient-bg-1);
  position: relative;
  overflow-x: hidden;
  
  // 添加动态光效背景
  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--xhs-gradient-bg-2);
    pointer-events: none;
    z-index: 0;
    animation: backgroundPulse 8s ease-in-out infinite;
  }
  
  &::after {
    content: '';
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60vh;
    background: var(--xhs-gradient-bg-3);
    pointer-events: none;
    z-index: 0;
    animation: backgroundFloat 12s ease-in-out infinite;
  }
}

/* Hero Section - 首页主区域 */
.hero-section {
  position: relative;
  text-align: center;
  margin-bottom: var(--xhs-space-2xl);
  padding: var(--xhs-space-3xl) var(--xhs-space-md);
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--xhs-radius-3xl);
  box-shadow: var(--xhs-shadow-xl);
  backdrop-filter: blur(20px);
  animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
  overflow: hidden;
  
  // 添加装饰性渐变
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: var(--xhs-gradient-warm);
    opacity: 0.05;
    animation: gradientRotate 20s linear infinite;
    pointer-events: none;
  }
}

.hero-content {
  position: relative;
  margin-bottom: var(--xhs-space-xl);
  z-index: 1;
}

.brand-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 20px;
  background: var(--xhs-primary-soft);
  color: var(--xhs-primary);
  border-radius: var(--xhs-radius-button);
  font-size: var(--xhs-text-sm);
  font-weight: var(--xhs-font-weight-semibold);
  margin-bottom: var(--xhs-space-lg);
  letter-spacing: 0.5px;
  border: 1px solid rgba(255, 36, 66, 0.1);
  animation: fadeIn 1s ease-out 0.2s both;
  
  svg {
    animation: sparkle 2s ease-in-out infinite;
  }
}

.platform-slogan {
  font-size: var(--xhs-text-xl);
  font-weight: var(--xhs-font-weight-medium);
  color: var(--xhs-text-primary);
  margin-bottom: var(--xhs-space-md);
  line-height: 1.6;
  letter-spacing: 0.5px;
  animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
  background: var(--xhs-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-title {
  margin: 0 0 var(--xhs-space-md) 0;
  font-size: var(--xhs-text-4xl);
  font-weight: var(--xhs-font-weight-bold);
  color: var(--xhs-text-primary);
  line-height: 1.2;
  letter-spacing: -0.5px;
  animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

.page-subtitle {
  margin: 0;
  font-size: var(--xhs-text-base);
  color: var(--xhs-text-secondary);
  line-height: 1.8;
  animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both;
}

/* 生成结果样式 - 卡片化设计 */
.result-card {
  position: relative;
  margin: 0 auto var(--xhs-space-xl);
  border-radius: var(--xhs-radius-2xl);
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  max-width: 1200px;
  z-index: 1;
  overflow: hidden;
  
  // 添加微妙的渐变背景
  background: linear-gradient(145deg, #FFFFFF 0%, #FAFAFA 100%);
  border: 1px solid rgba(255, 36, 66, 0.06);
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.06),
    0 0 0 1px rgba(255, 36, 66, 0.02);
  
  &:hover {
    box-shadow: 
      0 8px 24px rgba(0, 0, 0, 0.1),
      0 0 0 1px rgba(255, 36, 66, 0.04);
    transform: translateY(-2px);
  }
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--xhs-space-md) var(--xhs-space-lg);
  border-bottom: 1px solid var(--xhs-bg-tertiary);
}

.result-actions {
  display: flex;
  gap: var(--xhs-space-sm);
}

.result-content {
  padding: var(--xhs-space-md) var(--xhs-space-lg);
}

.platform-info {
  display: flex;
  align-items: center;
  gap: var(--xhs-space-md);
  margin-bottom: var(--xhs-space-lg);
  
  .platform-tag {
    margin: 0;
    padding: 6px 16px;
    font-weight: var(--xhs-font-weight-semibold);
  }
  
  .generation-time {
    font-size: var(--xhs-text-sm);
    color: var(--xhs-text-tertiary);
  }
}

.result-title {
  font-size: var(--xhs-text-xl);
  font-weight: var(--xhs-font-weight-bold);
  color: var(--xhs-text-primary);
  margin: 0 0 var(--xhs-space-md) 0;
  line-height: 1.4;
  letter-spacing: -0.3px;
}

.result-text {
  margin-bottom: var(--xhs-space-lg);
  
  .content-text {
    font-size: var(--xhs-text-base);
    line-height: 1.9;
    color: var(--xhs-text-secondary);
    white-space: pre-wrap;
  }
}

.result-images {
  margin-bottom: var(--xhs-space-lg);
  
  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--xhs-space-md);
    
    @media (max-width: 768px) {
      grid-template-columns: repeat(2, 1fr);
      gap: var(--xhs-space-sm);
    }
  }
  
  .result-image {
    width: 100%;
    height: 200px;
    border-radius: var(--xhs-radius-lg);
    cursor: pointer;
    transition: var(--xhs-transition-default);
    border: 2px solid transparent;
    
    &:hover {
      transform: scale(1.03);
      box-shadow: var(--xhs-shadow-hover);
      border-color: var(--xhs-primary-soft);
    }
  }
  
  .image-error {
    width: 100%;
    height: 200px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: var(--xhs-bg-secondary);
    border-radius: var(--xhs-radius-lg);
    
    .el-icon {
      font-size: 48px;
      color: var(--xhs-text-placeholder);
    }
  }
}

.result-footer {
  text-align: right;
  
  .create-time {
    font-size: var(--xhs-text-xs);
    color: var(--xhs-text-tertiary);
  }
}

/* 快速操作样式 - 卡片网格 */
.quick-actions {
  position: relative;
  margin-top: var(--xhs-space-2xl);
  z-index: 1;
  
  .section-title {
    margin: 0 0 var(--xhs-space-md) 0;
    font-size: var(--xhs-text-2xl);
    font-weight: var(--xhs-font-weight-bold);
    color: var(--xhs-text-primary);
    animation: fadeIn 0.6s ease-out 0.6s both;
  }
  
  .action-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: var(--xhs-space-lg);
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
      gap: var(--xhs-space-md);
    }
  }
  
  .action-card {
    cursor: pointer;
    transition: var(--xhs-transition-default);
    border-radius: var(--xhs-radius-2xl);
    position: relative;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(255, 36, 66, 0.06);
    box-shadow: var(--xhs-shadow-sm);
    
    &:hover {
      transform: translateY(-6px);
      box-shadow: var(--xhs-shadow-hover);
      border-color: rgba(255, 36, 66, 0.12);
    }
    
    // 添加悬浮光效
    &::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255, 36, 66, 0.03) 0%, transparent 70%);
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
    }
    
    &:hover::before {
      opacity: 1;
    }
    
    .action-card-content {
      display: flex;
      flex-direction: column;
      gap: var(--xhs-space-sm);
      padding: var(--xhs-space-xl);
      position: relative;
      z-index: 1;
      
      h4 {
        margin: 0;
        font-size: var(--xhs-text-lg);
        font-weight: var(--xhs-font-weight-bold);
        color: var(--xhs-text-primary);
      }
      
      p {
        margin: 0;
        color: var(--xhs-text-secondary);
        line-height: 1.7;
        font-size: var(--xhs-text-sm);
      }
    }
    
    .action-icon {
      width: 72px;
      height: 72px;
      border-radius: var(--xhs-radius-xl);
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 36px;
      margin-bottom: var(--xhs-space-sm);
      transition: var(--xhs-transition-default);
      
      &.batch-icon {
        background: linear-gradient(135deg, rgba(255, 36, 66, 0.12) 0%, rgba(255, 107, 157, 0.12) 100%);
        color: var(--xhs-primary);
      }
      
      &.config-icon {
        background: linear-gradient(135deg, rgba(0, 200, 83, 0.12) 0%, rgba(76, 175, 80, 0.12) 100%);
        color: var(--xhs-success);
      }
      
      &.history-icon {
        background: linear-gradient(135deg, rgba(255, 160, 0, 0.12) 0%, rgba(245, 124, 0, 0.12) 100%);
        color: var(--xhs-warning);
      }
    }
    
    &:hover .action-icon {
      transform: scale(1.08) rotate(3deg);
    }
  }
}

/* 动画定义 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes backgroundPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes backgroundFloat {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-20px) scale(1.05);
  }
}

@keyframes gradientRotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes sparkle {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: scale(1.2) rotate(180deg);
    opacity: 0.7;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-container {
    padding: var(--xhs-space-sm);
  }
  
  .hero-section {
    padding: var(--xhs-space-2xl) var(--xhs-space-sm);
    margin-bottom: var(--xhs-space-xl);
  }
  
  .page-title {
    font-size: var(--xhs-text-3xl);
  }
  
  .platform-slogan {
    font-size: var(--xhs-text-lg);
  }
  
  .result-card {
    border-radius: var(--xhs-radius-xl);
  }
}
</style>
