<template>
  <div class="inspiration-container">
    <!-- Hero区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">
          <el-icon><EditPen /></el-icon>
          <span>{{ t('inspiration.title') }}</span>
        </div>
        <h1 class="hero-title">{{ t('inspiration.subtitle') }}</h1>
        <p class="hero-subtitle">{{ t('inspiration.searchHint') }}</p>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <el-card class="search-card" shadow="hover">
        <div class="card-header-actions">
          <el-button type="text" class="settings-btn" @click="openSettings">
            <el-icon><Setting /></el-icon> {{ t('inspiration.settings') }}
          </el-button>
        </div>
        <el-tabs v-model="activeTab" class="search-tabs" @tab-change="handleTabChange">
          <!-- 关键词搜索 -->
          <el-tab-pane :label="t('inspiration.searchTab')" name="search">
            <div class="search-input-wrapper">
              <el-input
                v-model="keyword"
                size="large"
                :placeholder="t('inspiration.keywordPlaceholder')"
                clearable
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button
                type="primary"
                size="large"
                :loading="searching"
                @click="handleSearch"
                class="search-button"
              >
                {{ searching ? t('inspiration.searching') : t('inspiration.searchButton') }}
              </el-button>
            </div>
          </el-tab-pane>

          <!-- 链接解析 -->
          <el-tab-pane :label="t('inspiration.parseTab')" name="parse">
            <div class="search-input-wrapper">
              <el-input
                v-model="noteUrl"
                size="large"
                :placeholder="t('inspiration.urlPlaceholder')"
                clearable
                @keyup.enter="handleParse"
              >
                <template #prefix>
                  <el-icon><Link /></el-icon>
                </template>
              </el-input>
              <el-button
                type="primary"
                size="large"
                :loading="parsing"
                @click="handleParse"
                class="search-button"
              >
                {{ parsing ? t('inspiration.parsing') : t('inspiration.parseButton') }}
              </el-button>
            </div>
            <div class="input-helper" style="margin-top: 8px; font-size: 13px; color: #909399;">
              <el-button link type="primary" size="small" @click="fillExampleUrl">
                <el-icon style="margin-right: 4px"><Link /></el-icon>
                {{ t('inspiration.tryExample') }}
              </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- 搜索历史和热门推荐 (仅在关键词搜索Tab显示) -->
        <div v-if="activeTab === 'search'" class="search-extras">
          <!-- 搜索历史 -->
          <div v-if="searchHistory.length > 0" class="history-section">
            <div class="section-header">
              <span class="section-label">
                <el-icon><Clock /></el-icon> {{ t('inspiration.history') }}
              </span>
              <el-button type="text" class="clear-btn" @click="clearHistory">
                <el-icon><Delete /></el-icon> {{ t('inspiration.clearHistory') }}
              </el-button>
            </div>
            <div class="tags-wrapper">
              <el-tag
                v-for="kw in searchHistory"
                :key="kw"
                class="history-tag"
                closable
                @click="handleQuickSearch(kw)"
                @close="deleteHistory(kw)"
              >
                {{ kw }}
              </el-tag>
            </div>
          </div>

          <!-- 热门灵感 -->
          <div class="trending-section">
            <div class="section-header">
              <span class="section-label">
                <el-icon><TrendCharts /></el-icon> {{ t('inspiration.trending') }}
              </span>
            </div>
            <div class="tags-wrapper">
              <span
                v-for="kw in trendingKeywords"
                :key="kw"
                class="trending-tag"
                @click="handleQuickSearch(kw)"
              >
                # {{ kw }}
              </span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 外部搜索引导 -->
    <div v-if="showEmbed" class="external-search-guide" style="margin-top: 20px; padding: 40px 20px; background: white; border-radius: 12px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.05);">
      <el-result icon="info" title="已在新窗口打开小红书搜索">
        <template #sub-title>
          <div style="font-size: 15px; line-height: 1.6; color: #606266;">
            <p>由于小红书的安全策略限制（二维码不显示等问题），建议您在新窗口中浏览。</p>
            <p>请在弹出的新窗口中找到喜欢的笔记，<b>复制链接</b>并粘贴到下方进行解析。</p>
          </div>
        </template>
        <template #extra>
          <div style="max-width: 600px; margin: 30px auto 0; display: flex; gap: 12px;">
            <el-input
              v-model="noteUrl"
              size="large"
              :placeholder="t('inspiration.urlPlaceholder')"
              clearable
              @keyup.enter="handleParse"
            >
              <template #prefix>
                <el-icon><Link /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" size="large" :loading="parsing" @click="handleParse">
              {{ t('inspiration.parseButton') }}
            </el-button>
          </div>
          <div style="margin-top: 20px;">
             <el-button link type="primary" @click="openEmbedUrl">
               <el-icon style="margin-right: 4px"><TopRight /></el-icon>
               未弹出窗口？点击这里手动打开
             </el-button>
          </div>
        </template>
      </el-result>
    </div>

    <!-- 结果统计 -->
    <div v-if="results.length > 0" class="results-header">
      <h2 class="results-title">
        <el-icon><Collection /></el-icon>
        {{ t('inspiration.resultsTitle') }}
        <span class="results-count">({{ results.length }})</span>
      </h2>
    </div>

    <!-- 结果列表 -->
    <div v-if="results.length > 0" class="results-grid">
      <el-card
        v-for="(item, index) in results"
        :key="item.source_url"
        class="result-card"
        shadow="hover"
        @click="handleCardClick(item)"
      >
        <!-- 封面图 -->
        <div class="card-image">
          <el-image
            :src="item.cover_url"
            fit="cover"
            class="card-img"
            lazy
          >
            <template #error>
              <div class="image-error">
                <el-icon><PictureRounded /></el-icon>
              </div>
            </template>
            <template #placeholder>
              <div class="image-skeleton">
                <div class="skeleton-animation"></div>
              </div>
            </template>
          </el-image>
          
          <!-- 导入按钮 -->
          <div class="import-overlay">
            <el-button type="primary" circle class="action-btn" @click.stop="handleImport(item)">
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button type="success" circle class="action-btn" @click.stop="handleCopy(item)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 内容信息 -->
        <div class="card-content">
          <h3 class="card-title">{{ item.title }}</h3>
          <p class="card-description">{{ item.description }}</p>
          
          <!-- 多图预览 -->
          <div v-if="item.images && item.images.length > 1" class="image-gallery">
            <div 
              v-for="(img, idx) in item.images.slice(0, 5)" 
              :key="idx" 
              class="gallery-item"
              @click.stop
            >
              <el-image 
                :src="img" 
                :preview-src-list="item.images"
                :initial-index="idx"
                fit="cover" 
                class="gallery-img"
                hide-on-click-modal
                preview-teleported
              />
              <div v-if="idx === 4 && item.images.length > 5" class="more-count">
                +{{ item.images.length - 5 }}
              </div>
            </div>
          </div>
          
          <!-- 元信息 -->
          <div class="card-meta">
            <span v-if="item.author" class="meta-item">
              <el-icon class="meta-icon"><User /></el-icon>
              {{ item.author }}
            </span>
            <span v-if="item.likes" class="meta-item">
              <el-icon class="meta-icon"><Star /></el-icon>
              {{ formatNumber(item.likes) }}
            </span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && results.length === 0 && hasSearched && !showEmbed" class="empty-state">
      <el-empty description="" />
      <p class="empty-hint">{{ t('inspiration.noResultsHint') }}</p>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      :closable="false"
      show-icon
      class="error-alert"
    >
      <template #default>
        <div class="error-content">
          <p>{{ error }}</p>
        </div>
      </template>
    </el-alert>

    <!-- 加载状态 -->
    <div v-if="loading && results.length === 0" class="loading-state">
      <div class="skeleton-grid">
        <div v-for="i in 6" :key="i" class="skeleton-card">
          <div class="skeleton-image"></div>
          <div class="skeleton-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-meta"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 导入确认对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      :title="t('inspiration.importDialogTitle')"
      width="400px"
      align-center
      destroy-on-close
    >
      <div class="import-dialog-content">
        <p class="dialog-hint">{{ t('inspiration.importDialogContent') }}</p>
        
        <el-radio-group v-model="importType" class="import-options">
          <el-radio label="title" border class="import-option">
            <span class="option-title">{{ t('inspiration.importOptionTitle') }}</span>
            <span class="option-desc">{{ t('inspiration.importOptionTitleDesc') }}</span>
          </el-radio>
          
          <el-radio label="both" border class="import-option">
            <span class="option-title">{{ t('inspiration.importOptionBoth') }}</span>
            <span class="option-desc">{{ t('inspiration.importOptionBothDesc') }}</span>
          </el-radio>
          
          <el-radio label="desc" border class="import-option">
            <span class="option-title">{{ t('inspiration.importOptionDesc') }}</span>
            <span class="option-desc">{{ t('inspiration.importOptionDescDesc') }}</span>
          </el-radio>
        </el-radio-group>
        
        <div style="margin-top: 16px; padding: 0 4px;">
          <el-checkbox v-model="importImages" :label="t('inspiration.importImages')" />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" @click="confirmImport">
            {{ t('inspiration.importToTopic') }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 设置对话框 -->
    <el-dialog
      v-model="settingsVisible"
      :title="t('inspiration.cookieSettings')"
      width="500px"
      align-center
      destroy-on-close
    >
      <div class="settings-dialog-content">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          class="cookie-help-alert"
        >
          <template #default>
            <div class="cookie-help-text">
              {{ t('inspiration.cookieHelp') }}
            </div>
          </template>
        </el-alert>
        
        <el-form :model="cookieForm" label-position="top">
          <el-form-item label="Cookie">
            <el-input
              v-model="cookieForm.cookie"
              type="textarea"
              :rows="6"
              :placeholder="t('inspiration.cookiePlaceholder')"
              resize="none"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="settingsVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="savingCookie" @click="saveCookie">
            {{ t('common.save') }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { EditPen, Search, Link, Collection, PictureRounded, Download, User, RefreshRight, Star, Delete, CopyDocument, Close, TrendCharts, Setting, InfoFilled, TopRight, Clock } from '@element-plus/icons-vue'
import axios from 'axios'

import { useGeneratorStore } from '../stores/generator'

const router = useRouter()
const { t } = useI18n()
const generatorStore = useGeneratorStore()

// 响应式状态
const activeTab = ref('search')
const keyword = ref('')
const noteUrl = ref('')
const searching = ref(false)
const parsing = ref(false)
const loading = ref(false)
const error = ref('')
const hasSearched = ref(false)
const embedUrl = ref('')
const showEmbed = ref(false)



// 历史记录和热门推荐
const searchHistory = ref<string[]>([])
const trendingKeywords = ref([
  '冬日穿搭', '新年美甲', '旅行攻略', '家居改造', 
  '减脂食谱', '职场干货', '摄影技巧', '好物分享'
])

// 导入对话框状态
const importDialogVisible = ref(false)
const importType = ref('title') // title, both, desc
const importImages = ref(true)
const selectedItem = ref<any>(null)

// Cookie设置对话框
const settingsVisible = ref(false)
const cookieForm = ref({
  cookie: ''
})
const savingCookie = ref(false)

// 搜索结果
const results = ref<Array<{
  title: string
  cover_url: string
  description: string
  source_url: string
  author?: string
  likes?: number
}>>([])

// 初始化加载历史记录
onMounted(() => {
  const history = localStorage.getItem('inspiration_search_history')
  if (history) {
    try {
      searchHistory.value = JSON.parse(history)
    } catch (e) {
      console.error('Failed to parse search history', e)
    }
  }
})

// 保存历史记录
const saveHistory = (kw: string) => {
  if (!kw) return
  const index = searchHistory.value.indexOf(kw)
  if (index > -1) {
    searchHistory.value.splice(index, 1)
  }
  searchHistory.value.unshift(kw)
  // 最多保留10条
  if (searchHistory.value.length > 10) {
    searchHistory.value = searchHistory.value.slice(0, 10)
  }
  localStorage.setItem('inspiration_search_history', JSON.stringify(searchHistory.value))
}

// 删除历史记录
const deleteHistory = (kw: string) => {
  const index = searchHistory.value.indexOf(kw)
  if (index > -1) {
    searchHistory.value.splice(index, 1)
    localStorage.setItem('inspiration_search_history', JSON.stringify(searchHistory.value))
  }
}

// 清空历史记录
const clearHistory = () => {
  searchHistory.value = []
  localStorage.removeItem('inspiration_search_history')
}

// 点击热门或历史记录
const handleQuickSearch = (kw: string) => {
  keyword.value = kw
  handleSearch()
}

// Tab切换处理
const handleTabChange = (tabName: string) => {
  console.log('切换到:', tabName)
  // 清空之前的搜索结果
  results.value = []
  error.value = ''
  hasSearched.value = false
  showEmbed.value = false
}

const openEmbedUrl = () => {
  if (embedUrl.value) {
    window.open(embedUrl.value, '_blank')
  }
}

// 填充示例链接
const fillExampleUrl = () => {
  noteUrl.value = 'https://www.xiaohongshu.com/explore/695d333c000000000a02d266?xsec_token=CBjUoUnHqBU-sGN_NU_Fe4TIBvjbCn6pptTtw_-HpvOJs='
}

// 关键词搜索
const handleSearch = async () => {
  if (!keyword.value.trim()) {
    ElMessage.warning(t('inspiration.searchHint'))
    return
  }

  // 切换到嵌入模式
  showEmbed.value = true
  embedUrl.value = `https://www.xiaohongshu.com/search_result?keyword=${encodeURIComponent(keyword.value.trim())}&type=54`
  window.open(embedUrl.value, '_blank')
  hasSearched.value = true
  
  // 保存搜索历史
  saveHistory(keyword.value.trim())
}

/*
const handleSearchOld = async () => {
  if (!keyword.value.trim()) {
    ElMessage.warning(t('inspiration.searchHint'))
    return
  }

  searching.value = true
  loading.value = true
  error.value = ''

  try {
    const response = await axios.post('/api/inspiration/search', {
      keyword: keyword.value.trim()
    })

    if (response.data.success) {
      results.value = response.data.items
      hasSearched.value = true
      ElMessage.success(`${t('inspiration.totalResults')} ${response.data.items.length} ${t('inspiration.items')}`)
      saveHistory(keyword.value.trim())
    } else {
      ElMessage.error(response.data.message || t('inspiration.searchFailed'))
      error.value = response.data.message || t('inspiration.searchFailed')
    }
  } catch (err: any) {
    console.error('搜索失败:', err)
    ElMessage.error(t('inspiration.errorOccurred'))
    error.value = t('inspiration.searchFailed')
  } finally {
    searching.value = false
    loading.value = false
  }
}
*/

// 链接解析
const handleParse = async () => {
  if (!noteUrl.value.trim()) {
    ElMessage.warning(t('inspiration.parseHint'))
    return
  }

  parsing.value = true
  loading.value = true
  error.value = ''

  try {
    const response = await axios.post('/api/inspiration/parse', {
      url: noteUrl.value.trim()
    })

    if (response.data.success && response.data.item) {
      results.value = [response.data.item]
      hasSearched.value = true
      ElMessage.success(t('inspiration.parseSuccess'))
    } else {
      ElMessage.error(response.data.message || t('inspiration.parseFailed'))
      error.value = response.data.message || t('inspiration.parseFailed')
    }
  } catch (err: any) {
    console.error('解析失败:', err)
    ElMessage.error(t('inspiration.errorOccurred'))
    error.value = t('inspiration.parseFailed')
  } finally {
    parsing.value = false
    loading.value = false
  }
}

// 点击卡片跳转到首页并填充主题
const handleCardClick = (item: any) => {
  handleImport(item)
}

// 复制文案
const handleCopy = (item: any) => {
  const text = `${item.title}\n\n${item.description}`
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success(t('inspiration.copySuccess'))
  }).catch(() => {
    ElMessage.error(t('home.copyFailed'))
  })
}

// 导入到创作流程（打开对话框）
const handleImport = (item: any) => {
  selectedItem.value = item
  importType.value = 'title' // 重置为默认
  importDialogVisible.value = true
}

// 确认导入
const confirmImport = async () => {
  if (!selectedItem.value) return
  
  const item = selectedItem.value
  let topic = item.title
  
  if (importType.value === 'desc') {
    topic = item.description
  } else if (importType.value === 'both') {
    topic = `${item.title}\n\n${item.description}`
  }
  
  // 处理图片
  let files: File[] = []
  if (importImages.value && item.images && item.images.length > 0) {
    // 限制最多5张，避免请求过多
    const imageUrls = item.images.slice(0, 5)
    
    // 显示加载提示
    const loadingInstance = ElLoading.service({
      lock: true,
      text: '正在准备图片资源...',
      background: 'rgba(0, 0, 0, 0.7)',
    })

    try {
      // 并行下载图片
      const promises = imageUrls.map(async (url: string, index: number) => {
        try {
          // 使用fetch获取图片Blob
          const response = await fetch(url, { mode: 'cors' })
          if (!response.ok) throw new Error('Network response was not ok')
          const blob = await response.blob()
          // 创建File对象
          const filename = `ref_image_${index}_${Date.now()}.jpg`
          return new File([blob], filename, { type: blob.type })
        } catch (e) {
          console.warn('Failed to fetch image:', url, e)
          return null
        }
      })
      
      const results = await Promise.all(promises)
      files = results.filter((f): f is File => f !== null)
      
    } catch (e) {
      console.error('Error preparing images:', e)
    } finally {
      loadingInstance.close()
    }
  }
  
  importDialogVisible.value = false
  
  // 直接更新 Store 状态
  generatorStore.setTopic(topic)
  
  if (files.length > 0) {
    // 设置用户图片
    generatorStore.setUserImages(files)
    // 自动开启参考图功能
    generatorStore.setReferenceImageEnabled(true)
    // 生成预览URL并设置参考图
    const refImages = files.map((file: File) => ({
      file,
      url: URL.createObjectURL(file)
    }))
    generatorStore.setReferenceImages(refImages)
    
    ElMessage.success(`${t('inspiration.importSuccess')}: ${topic} (+${files.length}张参考图)`)
  } else {
    // 清空可能存在的旧图片
    generatorStore.setUserImages([])
    generatorStore.clearReferenceImages()
    generatorStore.setReferenceImageEnabled(false)
    ElMessage.success(`${t('inspiration.importSuccess')}: ${topic}`)
  }

  router.push('/')
}

// 打开设置
const openSettings = async () => {
  try {
    const response = await axios.get('/api/config/system')
    if (response.data?.config) {
      const systemConfig = response.data.config
      if (systemConfig.xiaohongshu?.cookie) {
        cookieForm.value.cookie = systemConfig.xiaohongshu.cookie
      }
    }
  } catch (e) {
    console.error('获取配置失败', e)
  }
  settingsVisible.value = true
}

// 保存Cookie
const saveCookie = async () => {
  savingCookie.value = true
  try {
    // 获取当前系统配置
    const configResponse = await axios.get('/api/config/system')
    const currentConfig = configResponse.data?.config || {}
    
    // 更新小红书Cookie
    const newConfig = {
      ...currentConfig,
      xiaohongshu: {
        ...currentConfig.xiaohongshu,
        cookie: cookieForm.value.cookie
      }
    }
    
    // 更新配置
    await axios.post('/api/config/system', newConfig)
    
    ElMessage.success(t('inspiration.cookieSaveSuccess'))
    settingsVisible.value = false
  } catch (e) {
    console.error('保存Cookie失败', e)
    ElMessage.error(t('inspiration.cookieSaveFailed'))
  } finally {
    savingCookie.value = false
  }
}

// 格式化数字（如：1.2k, 1.5万）
const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.inspiration-container {
  min-height: 100vh;
  background: var(--xhs-gradient-bg-1);
  padding-bottom: var(--xhs-space-3xl);
}

// Hero区域 / Hero Section
.hero-section {
  background: var(--xhs-gradient-primary);
  padding: var(--xhs-space-2xl) var(--xhs-space-lg);
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    animation: float 20s ease-in-out infinite;
  }

  @keyframes float {
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
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--xhs-space-sm);
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 16px;
  border-radius: var(--xhs-radius-2xl);
  backdrop-filter: blur(10px);
  margin-bottom: var(--xhs-space-lg);
  font-size: var(--xhs-text-sm);
  font-weight: var(--xhs-font-weight-medium);
  animation: fadeInUp 0.6s ease-out;
}

.hero-title {
  font-size: var(--xhs-text-3xl);
  font-weight: var(--xhs-font-weight-bold);
  margin-bottom: var(--xhs-space-sm);
  animation: fadeInUp 0.6s ease-out 0.2s;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.hero-subtitle {
  font-size: var(--xhs-text-lg);
  opacity: 0.95;
  max-width: 600px;
  margin: 0 auto;
  animation: fadeInUp 0.6s ease-out 0.4s;
}

// 搜索区域 / Search Section
.search-section {
  max-width: 1200px;
  margin: -32px auto 0;
  position: relative;
  z-index: 10;
}

.search-card {
  border: none;
  border-radius: var(--xhs-radius-2xl);
  box-shadow: var(--xhs-shadow-lg);
  overflow: hidden;
  transition: all var(--xhs-duration-base) var(--xhs-ease-default);
  position: relative;

  &:hover {
    box-shadow: var(--xhs-shadow-hover);
    transform: translateY(-4px);
  }
}

.card-header-actions {
  position: absolute;
  top: var(--xhs-space-md);
  right: var(--xhs-space-lg);
  z-index: 10;
}

.settings-btn {
  font-size: var(--xhs-text-sm);
  color: var(--xhs-text-secondary);
  
  &:hover {
    color: var(--xhs-primary);
  }
}

:deep(.search-tabs) {
  .el-tabs__header {
    margin: 0 auto var(--xhs-space-xl);
    max-width: 360px;
    background: var(--xhs-bg-secondary);
    border-radius: var(--xhs-radius-full);
    padding: 4px;
    border: none;
  }

  .el-tabs__nav-wrap {
    width: 100%;
    &::after {
      display: none;
    }
  }

  .el-tabs__nav-scroll {
    width: 100%;
    overflow: visible;
  }

  .el-tabs__nav {
    width: 100%;
    display: flex;
    border: none !important;
  }

  .el-tabs__item {
    flex: 1;
    text-align: center;
    height: 40px;
    line-height: 40px;
    padding: 0;
    border: none;
    border-radius: var(--xhs-radius-full);
    color: var(--xhs-text-secondary);
    font-size: var(--xhs-text-base);
    font-weight: var(--xhs-font-weight-medium);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &.is-active {
      background: white;
      color: var(--xhs-primary);
      font-weight: var(--xhs-font-weight-semibold);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    &:hover:not(.is-active) {
      color: var(--xhs-text-primary);
    }
  }

  .el-tabs__active-bar {
    display: none;
  }
}

.search-extras {
  padding: 0 var(--xhs-space-xl) var(--xhs-space-xl);
  border-top: 1px solid var(--xhs-bg-secondary);
}

.history-section,
.trending-section {
  margin-top: var(--xhs-space-lg);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--xhs-space-md);
}

.section-label {
  display: flex;
  align-items: center;
  gap: var(--xhs-space-xs);
  font-size: var(--xhs-text-sm);
  color: var(--xhs-text-secondary);
  font-weight: var(--xhs-font-weight-medium);
}

.clear-btn {
  padding: 0;
  height: auto;
  font-size: var(--xhs-text-xs);
  color: var(--xhs-text-tertiary);
  
  &:hover {
    color: var(--xhs-text-secondary);
  }
}

.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: var(--xhs-space-sm);
}

.history-tag {
  cursor: pointer;
  border: none;
  background: var(--xhs-bg-secondary);
  color: var(--xhs-text-secondary);
  transition: all 0.2s;
  
  &:hover {
    background: var(--xhs-bg-tertiary);
    color: var(--xhs-text-primary);
  }
}

.trending-tag {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255, 36, 66, 0.05);
  color: var(--xhs-primary);
  border-radius: var(--xhs-radius-full);
  font-size: var(--xhs-text-sm);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(255, 36, 66, 0.1);
    transform: translateY(-1px);
  }
}

.search-input-wrapper {
  padding: var(--xhs-space-xl);
  display: flex;
  gap: var(--xhs-space-md);
  align-items: center;
}

.search-button {
  min-width: 140px;
  background: var(--xhs-gradient-button);
  border: none;
  font-weight: var(--xhs-font-weight-semibold);
  font-size: var(--xhs-text-base);
  transition: all var(--xhs-duration-base) var(--xhs-ease-default);

  &:hover {
    background: var(--xhs-gradient-button-hover);
    transform: translateY(-2px);
    box-shadow: var(--xhs-shadow-hover);
  }

  &:active {
    transform: translateY(0);
  }
}

// 结果头部 / Results Header
.results-header {
  max-width: 1200px;
  margin: var(--xhs-space-xl) auto;
  padding: 0 var(--xhs-space-lg);
}

.results-title {
  display: flex;
  align-items: center;
  gap: var(--xhs-space-sm);
  font-size: var(--xhs-text-2xl);
  font-weight: var(--xhs-font-weight-semibold);
  color: var(--xhs-text-primary);
}

.results-count {
  font-size: var(--xhs-text-base);
  color: var(--xhs-text-tertiary);
  font-weight: var(--xhs-font-weight-regular);
}

// 结果网格 / Results Grid
.results-grid {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--xhs-space-lg);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--xhs-space-lg);

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    padding: 0 var(--xhs-space-md);
  }

  @media (min-width: 769px) and (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

// 结果卡片 / Result Cards
.result-card {
  cursor: pointer;
  border: none;
  border-radius: var(--xhs-radius-xl);
  overflow: hidden;
  transition: all var(--xhs-duration-base) var(--xhs-ease-default);
  background: white;

  &:hover {
    transform: translateY(-8px);
    box-shadow: var(--xhs-shadow-xl);

    .card-image {
      .import-overlay {
        opacity: 1;
      }

      .card-img {
        transform: scale(1.05);
      }
    }
  }
}

.card-image {
  position: relative;
  width: 100%;
  height: 280px;
  overflow: hidden;
  background: var(--xhs-bg-secondary);

  .import-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to bottom, rgba(255, 36, 66, 0.7) 0%, rgba(255, 36, 66, 0.9) 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--xhs-space-md);
    color: white;
    opacity: 0;
    transition: opacity var(--xhs-duration-base) var(--xhs-ease-default);
    backdrop-filter: blur(2px);

    .action-btn {
      width: 44px;
      height: 44px;
      font-size: 20px;
      border: none;
      
      &:hover {
        transform: scale(1.1);
      }
    }
  }

  .card-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform var(--xhs-duration-base) var(--xhs-ease-default);
  }

  .image-error,
  .image-skeleton {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--xhs-bg-tertiary);
    color: var(--xhs-text-tertiary);
  }

  .image-error {
    font-size: 48px;
  }

  .skeleton-animation {
    width: 40px;
    height: 40px;
    background: linear-gradient(90deg, var(--xhs-bg-tertiary) 25%, var(--xhs-bg-secondary) 50%, var(--xhs-bg-tertiary) 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: var(--xhs-radius-lg);
  }

  @keyframes skeleton-loading {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }
}

.card-content {
  padding: var(--xhs-space-lg);
}

.card-title {
  font-size: var(--xhs-text-lg);
  font-weight: var(--xhs-font-weight-semibold);
  color: var(--xhs-text-primary);
  margin: 0 0 var(--xhs-space-sm);
  line-height: var(--xhs-leading-tight);
  
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-description {
  font-size: var(--xhs-text-base);
  color: var(--xhs-text-secondary);
  line-height: var(--xhs-leading-normal);
  margin: 0 0 var(--xhs-space-md);
  
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.image-gallery {
  display: flex;
  gap: 6px;
  margin-bottom: var(--xhs-space-md);
  overflow: hidden;
}

.gallery-item {
  position: relative;
  flex: 1;
  aspect-ratio: 1;
  cursor: pointer;
  overflow: hidden;
  border-radius: var(--xhs-radius-md);
  
  &:hover {
    opacity: 0.9;
  }
}

.gallery-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.more-count {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--xhs-text-lg);
  font-weight: var(--xhs-font-weight-semibold);
  backdrop-filter: blur(2px);
}

.card-meta {
  display: flex;
  gap: var(--xhs-space-md);
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--xhs-space-xs);
  font-size: var(--xhs-text-sm);
  color: var(--xhs-text-tertiary);
}

.meta-icon {
  font-size: 14px;
}

// 空状态 / Empty State
.empty-state {
  width: 100%;
  max-width: 1200px;
  margin: var(--xhs-space-4xl) auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--xhs-space-2xl);
}

.empty-hint {
  font-size: var(--xhs-text-base);
  color: var(--xhs-text-secondary);
  margin: var(--xhs-space-xl) 0 var(--xhs-space-lg);
  line-height: var(--xhs-leading-relaxed);
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

// 错误提示 / Error Alert
.error-alert {
  max-width: 1200px;
  margin: var(--xhs-space-lg) auto;
  border-radius: var(--xhs-radius-xl);
}

.error-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--xhs-space-md);
  flex-wrap: wrap;
}

// 加载状态 / Loading State
.loading-state {
  max-width: 1200px;
  margin: var(--xhs-space-xl) auto;
  padding: 0 var(--xhs-space-lg);
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--xhs-space-lg);

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }

  @media (min-width: 769px) and (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.skeleton-card {
  background: white;
  border-radius: var(--xhs-radius-xl);
  overflow: hidden;
  padding: 0;
}

.skeleton-image {
  height: 280px;
  background: var(--xhs-bg-secondary);
}

.skeleton-content {
  padding: var(--xhs-space-lg);
}

.skeleton-title {
  height: 24px;
  background: var(--xhs-bg-tertiary);
  border-radius: var(--xhs-radius-sm);
  margin: 0 0 var(--xhs-space-sm);
}

.skeleton-text {
  height: 60px;
  background: var(--xhs-bg-tertiary);
  border-radius: var(--xhs-radius-sm);
  margin: 0 0 var(--xhs-space-md);
}

.skeleton-meta {
  height: 20px;
  width: 120px;
  background: var(--xhs-bg-tertiary);
  border-radius: var(--xhs-radius-sm);
}

// 动画 / Animations
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.import-dialog-content {
  padding: var(--xhs-space-sm) 0;
}

.dialog-hint {
  margin-bottom: var(--xhs-space-md);
  color: var(--xhs-text-secondary);
}

.import-options {
  display: flex;
  flex-direction: column;
  gap: var(--xhs-space-sm);
  width: 100%;
}

.import-option {
  margin-right: 0 !important;
  width: 100%;
  height: auto !important;
  padding: var(--xhs-space-md) !important;
  display: flex;
  
  :deep(.el-radio__label) {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    white-space: normal;
  }
}

.option-title {
  font-weight: var(--xhs-font-weight-semibold);
  color: var(--xhs-text-primary);
}

.option-desc {
  font-size: var(--xhs-text-xs);
  color: var(--xhs-text-tertiary);
}

.settings-dialog-content {
  padding: var(--xhs-space-sm) 0;
}

.cookie-help-alert {
  margin-bottom: var(--xhs-space-lg);
  background-color: #e6f7ff; /* 浅蓝色背景 */
  border: 1px solid #91d5ff; /* 边框 */
  
  :deep(.el-alert__title), 
  :deep(.el-alert__description) {
    color: #0050b3; /* 深蓝色文字 */
  }
  
  :deep(.el-alert__icon) {
    color: #1890ff; /* 图标颜色 */
  }
}

.cookie-help-text {
  line-height: 1.6;
  font-size: var(--xhs-text-sm);
  color: #003a8c; /* 正文深蓝色 */
  white-space: pre-line;
}
</style>
