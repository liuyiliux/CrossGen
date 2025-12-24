import { defineStore } from 'pinia'

/**
 * 生成器状态管理
 *
 * 功能：
 * - 管理生成主题
 * - 管理参考图片
 * - 管理生成大纲
 * - 管理生成进度
 * - 管理生成结果
 */

// 定义页面类型
interface Page {
  index: number
  type: 'cover' | 'content' | 'summary'
  content: string
  image_prompt?: string
}

// 定义生成图片类型
export interface GeneratedImage {
  index: number
  url: string
  status: 'generating' | 'done' | 'error' | 'retrying'
  error?: string
  retryable?: boolean
}

// 定义生成器状态
interface GeneratorState {
  // 当前阶段
  stage: 'input' | 'outline' | 'generating' | 'result'
  
  // 用户输入
  topic: string
  
  // 用户上传的图片（用于图片生成参考）
  userImages: File[]
  
  // 大纲数据
  outline: {
    raw: string
    title?: string        // 总标题
    copywriting?: string  // 总文案
    pages: Page[]
  }
  
  // 文本服务商ID
  textProviderId: string | null
  
  // 图像服务商ID
  imageProviderId: string | null
  
  // 可用文本服务商列表
  textProviders: any[]
  
  // 可用图像服务商列表
  imageProviders: any[]
  
  // 视频服务商ID
  videoProviderId: string | null
  
  // 可用视频服务商列表
  videoProviders: any[]
  
  // 生成进度
  progress: {
    current: number
    total: number
    status: 'idle' | 'generating' | 'done' | 'error'
  }
  
  // 生成结果
  images: GeneratedImage[]
  
  // 任务ID
  taskId: string | null
  
  // 历史记录ID
  recordId: string | null
  
  // 加载状态
  loading: boolean
  
  // 错误信息
  error: string | null
  
  // 选择的图像尺寸
  selectedSize: string | null
  
  // 选择的平台
  selectedPlatform: string | null
}

const STORAGE_KEY = 'generator-state'

// 从 localStorage 加载状态
function loadState(): Partial<GeneratorState> {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) {
    console.error('加载状态失败:', e)
  }
  return {}
}

// 保存状态到 localStorage
function saveState(state: GeneratorState) {
  try {
    // 只保存关键数据，不保存 userImages（文件对象无法序列化）
    const toSave = {
      stage: state.stage,
      topic: state.topic,
      outline: state.outline,
      progress: state.progress,
      images: state.images,
      taskId: state.taskId,
      recordId: state.recordId,
      textProviderId: state.textProviderId,
      imageProviderId: state.imageProviderId,
      videoProviderId: state.videoProviderId,
      selectedSize: state.selectedSize,
      selectedPlatform: state.selectedPlatform
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
  } catch (e) {
    console.error('保存状态失败:', e)
  }
}

export const useGeneratorStore = defineStore('generator', {
  state: (): GeneratorState => {
      const saved = loadState()
      return {
        // 当前阶段
        stage: saved.stage || 'input',
        
        // 用户输入
        topic: saved.topic || '',
        
        // 用户上传的图片
        userImages: [],
        
        // 大纲数据
        outline: saved.outline || {
          raw: '',
          title: '',
          copywriting: '',
          pages: []
        },
        
        // 文本服务商ID
        textProviderId: saved.textProviderId || null,
        
        // 图像服务商ID
        imageProviderId: saved.imageProviderId || null,
        
        // 选择的图像尺寸
        selectedSize: saved.selectedSize || null,
        
        // 选择的平台
        selectedPlatform: saved.selectedPlatform || null,
        
        // 视频服务商ID
        videoProviderId: saved.videoProviderId || null,
        
        // 可用文本服务商列表
        textProviders: [],
        
        // 可用图像服务商列表
        imageProviders: [],
        
        // 可用视频服务商列表
        videoProviders: [],
        
        // 生成进度
        progress: saved.progress || {
          current: 0,
          total: 0,
          status: 'idle'
        },
        
        // 生成结果
        images: saved.images || [],
        
        // 任务ID
        taskId: saved.taskId || null,
        
        // 历史记录ID
        recordId: saved.recordId || null,
        
        // 加载状态
        loading: false,
        
        // 错误信息
        error: null
      }
    },

  actions: {
    /**
     * 设置生成主题
     */
    setTopic(topic: string) {
      this.topic = topic
    },

    /**
     * 设置用户上传的图片
     */
    setUserImages(images: File[]) {
      this.userImages = images
    },



    /**
     * 设置文本服务商ID
     */
    setTextProviderId(providerId: string | null) {
      this.textProviderId = providerId
    },

    /**
     * 设置图像服务商ID
     */
    setImageProviderId(providerId: string | null) {
      this.imageProviderId = providerId
    },

    /**
     * 设置选择的图像尺寸
     */
    setSelectedSize(size: string | null) {
      this.selectedSize = size
    },
    
    /**
     * 设置选择的平台
     */
    setSelectedPlatform(platform: string | null) {
      this.selectedPlatform = platform
    },

    /**
     * 设置可用文本服务商列表
     */
    setTextProviders(providers: any[]) {
      this.textProviders = providers
    },

    /**
     * 设置可用图像服务商列表
     */
    setImageProviders(providers: any[]) {
      this.imageProviders = providers
    },

    /**
     * 设置视频服务商ID
     */
    setVideoProviderId(providerId: string | null) {
      this.videoProviderId = providerId
    },

    /**
     * 设置可用视频服务商列表
     */
    setVideoProviders(providers: any[]) {
      this.videoProviders = providers
    },

    /**
     * 设置大纲
     */
    setOutline(raw: string, pages: Page[], title?: string, copywriting?: string) {
      this.outline.raw = raw
      this.outline.title = title
      this.outline.copywriting = copywriting
      
      // 确保每个页面的image_prompt字段被正确设置
      this.outline.pages = pages.map(page => ({
        ...page,
        image_prompt: page.image_prompt || page.content  // 如果image_prompt为空，使用content作为默认值
      }))
      
      this.stage = 'outline'
      // 清空图片数组，避免自动生成图像
      this.images = []
      // 不再清空recordId，保留API返回的history_id
      // 确保大纲生成和图片生成使用同一个历史记录ID
    },

    /**
     * 更新页面内容
     */
    updatePage(index: number, content: string) {
      const page = this.outline.pages.find(p => p.index === index)
      if (page) {
        page.content = content
        page.image_prompt = content  // 同时更新image_prompt
        // 同步更新 raw 文本
        this.syncRawFromPages()
      }
    },
    
    /**
     * 更新大纲标题
     */
    updateOutlineTitle(title: string) {
      this.outline.title = title
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    /**
     * 更新大纲文案
     */
    updateOutlineCopywriting(copywriting: string) {
      this.outline.copywriting = copywriting
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    /**
     * 根据 pages 和大纲信息重新生成 raw 文本
     */
    syncRawFromPages() {
      let raw = ''
      
      // 添加标题
      if (this.outline.title) {
        raw += `【标题】：${this.outline.title}\n\n`
      }
      
      // 添加文案
      if (this.outline.copywriting) {
        raw += `【文案】：${this.outline.copywriting}\n\n`
      }
      
      // 添加图片提示词
      for (const page of this.outline.pages) {
        if (page.image_prompt) {
          raw += `【图片提示词】：${page.image_prompt}\n\n`
        } else {
          raw += `【图片提示词】：${page.content}\n\n`
        }
        
        // 添加<page>标签分隔（除了最后一页）
        if (page.index < this.outline.pages.length - 1) {
          raw += '<page>\n\n'
        }
      }
      
      this.outline.raw = raw.trim()
    },

    /**
     * 删除页面
     */
    deletePage(index: number) {
      this.outline.pages = this.outline.pages.filter(p => p.index !== index)
      // 重新索引
      this.outline.pages.forEach((page, idx) => {
        page.index = idx
      })
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    /**
     * 添加页面
     */
    addPage(type: 'cover' | 'content' | 'summary', content: string = '') {
      const newPage: Page = {
        index: this.outline.pages.length,
        type,
        content
      }
      this.outline.pages.push(newPage)
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    /**
     * 移动页面 (拖拽排序)
     */
    movePage(fromIndex: number, toIndex: number) {
      const pages = [...this.outline.pages]
      const [movedPage] = pages.splice(fromIndex, 1)
      pages.splice(toIndex, 0, movedPage)

      // 重新索引
      pages.forEach((page, idx) => {
        page.index = idx
      })

      this.outline.pages = pages
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    /**
     * 开始生成
     */
    startGeneration() {
      this.stage = 'generating'
      this.progress.total = this.outline.pages.length
      this.progress.status = 'generating'
      
      // 计算已完成的图片数量
      let completedCount = 0
      
      // 保留已生成成功的图片，只创建或重置其他图片
      const updatedImages: GeneratedImage[] = []
      
      for (const page of this.outline.pages) {
        // 查找是否已有该页面的图片
        const existingImage = this.images.find(img => img.index === page.index)
        
        if (existingImage && existingImage.status === 'done' && existingImage.url) {
          // 保留已生成成功的图片
          updatedImages.push(existingImage)
          completedCount++
        } else {
          // 创建新图片或重置失败/生成中的图片
          updatedImages.push({
            index: page.index,
            url: '',
            status: 'generating'
          })
        }
      }
      
      this.images = updatedImages
      this.progress.current = completedCount
    },

    /**
     * 更新生成进度
     */
    updateProgress(index: number, status: 'generating' | 'done' | 'error', url?: string, error?: string) {
      const image = this.images.find(img => img.index === index)
      if (image) {
        image.status = status
        if (url) image.url = url
        if (error) image.error = error
      }
      if (status === 'done') {
        this.progress.current++
      }
    },

    /**
     * 更新图片
     */
    updateImage(index: number, newUrl: string) {
      const image = this.images.find(img => img.index === index)
      if (image) {
        const timestamp = Date.now()
        image.url = `${newUrl}?t=${timestamp}`
        image.status = 'done'
        delete image.error
      }
    },

    /**
     * 完成生成
     */
    finishGeneration(taskId: string) {
      this.taskId = taskId
      this.stage = 'result'
      this.progress.status = 'done'
    },

    /**
     * 设置单个图片为重试中状态
     */
    setImageRetrying(index: number) {
      const image = this.images.find(img => img.index === index)
      if (image) {
        image.status = 'retrying'
      }
    },

    /**
     * 获取失败的图片列表
     */
    getFailedImages() {
      return this.images.filter(img => img.status === 'error')
    },

    /**
     * 获取失败图片对应的页面
     */
    getFailedPages() {
      const failedIndices = this.images
        .filter(img => img.status === 'error')
        .map(img => img.index)
      return this.outline.pages.filter(page => failedIndices.includes(page.index))
    },

    /**
     * 检查是否有失败的图片
     */
    hasFailedImages() {
      return this.images.some(img => img.status === 'error')
    },

    /**
     * 设置记录ID
     */
    setRecordId(id: string | null) {
      this.recordId = id
    },

    /**
     * 设置加载状态
     */
    setLoading(loading: boolean) {
      this.loading = loading
    },

    /**
     * 设置错误信息
     */
    setError(error: string | null) {
      this.error = error
    },

    /**
     * 重置状态
     */
    reset() {
      this.stage = 'input'
      this.topic = ''
      this.userImages = []
      this.outline = {
        raw: '',
        pages: []
      }
      this.progress = {
        current: 0,
        total: 0,
        status: 'idle'
      }
      this.images = []
      this.taskId = null
      this.recordId = null
      this.error = null
      this.loading = false
      // 清除 localStorage
      localStorage.removeItem(STORAGE_KEY)
    },

    /**
     * 保存当前状态
     */
    saveToStorage() {
      saveState(this)
    }
  },

  getters: {
    /**
     * 获取是否有生成结果
     */
    hasResults: (state) => state.images.some(img => img.status === 'done'),

    /**
     * 获取总页数
     */
    totalPages: (state) => state.outline.pages.length,

    /**
     * 获取已上传图片数量
     */
    imageCount: (state) => state.userImages.length,

    /**
     * 获取当前进度百分比
     */
    progressPercent: (state) => {
      if (state.progress.total === 0) return 0
      return Math.round((state.progress.current / state.progress.total) * 100)
    }
  }
})

// 监听状态变化并自动保存（使用 watch）
import { watch } from 'vue'

export function setupAutoSave() {
  const store = useGeneratorStore()

  // 监听关键字段变化并自动保存
  watch(
    () => ({
      stage: store.stage,
      topic: store.topic,
      outline: store.outline,
      textProviderId: store.textProviderId,
      imageProviderId: store.imageProviderId,
      progress: store.progress,
      images: store.images,
      taskId: store.taskId,
      recordId: store.recordId
    }),
    () => {
      store.saveToStorage()
    },
    { deep: true }
  )
}
