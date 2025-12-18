<template>
  <!-- 主题输入组合框组件 -->
  <div class="composer-container">
    <!-- 输入区域 -->
    <div class="composer-input-wrapper">
      <div class="search-icon-static">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <textarea
        ref="textareaRef"
        :value="modelValue"
        @input="handleInput"
        class="composer-textarea"
        placeholder="输入主题，例如：秋季显白美甲..."
        @keydown.enter.prevent="handleEnter"
        :disabled="loading"
        rows="1"
      ></textarea>
    </div>

    <!-- 模板和模型选择 -->
    <div class="template-model-selector">
      <div class="selector-item">
        <label class="selector-label">平台选择</label>
        <el-select 
          v-model="selectedPlatform" 
          placeholder="请选择平台"
          size="large"
          class="selector-input"
        >
          <el-option
            v-for="platform in platforms"
            :key="platform.value"
            :label="platform.label"
            :value="platform.value"
          />
        </el-select>
      </div>

      <div class="selector-item">
        <label class="selector-label">文本服务商</label>
        <el-select 
          v-model="generatorStore.textProviderId" 
          placeholder="请选择文本服务商"
          size="large"
          clearable
          class="selector-input"
        >
          <el-option 
            v-for="provider in generatorStore.textProviders.filter(p => p.enabled)" 
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
    </div>

    <!-- 已上传图片预览 -->
    <div v-if="uploadedImages.length > 0" class="uploaded-images-preview">
      <div
        v-for="(img, idx) in uploadedImages"
        :key="idx"
        class="uploaded-image-item"
      >
        <img :src="img.preview" :alt="`图片 ${idx + 1}`" />
        <button class="remove-image-btn" @click="removeImage(idx)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="upload-hint">
        这些图片将用于生成封面和内容参考
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="composer-toolbar">
      <div class="toolbar-left">
        <label class="tool-btn" :class="{ 'active': uploadedImages.length > 0 }" title="上传参考图">
          <input
            type="file"
            accept="image/*"
            multiple
            @change="handleImageUpload"
            :disabled="loading"
            style="display: none;"
          />
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
          <span v-if="uploadedImages.length > 0" class="badge-count">{{ uploadedImages.length }}</span>
        </label>
      </div>
      <div class="toolbar-right">
        <button
              class="btn btn-primary generate-btn"
              @click="$emit('generate', selectedPlatform)"
              :disabled="!modelValue.trim() || loading"
            >
              <span v-if="loading" class="spinner-sm"></span>
              <span v-else>生成大纲</span>
            </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted, onMounted } from 'vue'
import axios from 'axios'

/**
 * 主题输入组合框组件
 *
 * 功能：
 * - 主题文本输入（自动调整高度）
 * - 参考图片上传（最多5张）
 * - 平台选择（动态加载）
 * - 文本服务商选择
 * - 生成按钮
 */

// 定义上传的图片类型
interface UploadedImage {
  file: File
  preview: string
}

// 引入状态管理
import { useGeneratorStore } from '../../stores/generator'
const generatorStore = useGeneratorStore()

// 定义 Props
const props = defineProps<{
  modelValue: string
  loading: boolean
}>()

// 定义 Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'generate', platform: string): void
  (e: 'imagesChange', images: File[]): void
}>()

// 输入框引用
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// 已上传的图片
const uploadedImages = ref<UploadedImage[]>([])

// 平台选择
const selectedPlatform = ref('xiaohongshu')
const platforms = ref<Array<{value: string, label: string}>>([
  { value: 'xiaohongshu', label: '小红书' },
  { value: 'douyin', label: '抖音' },
  { value: 'wechat', label: '微信' },
  { value: 'toutiao', label: '头条' }
])

// 加载平台列表
const loadPlatforms = async () => {
  try {
    const response = await axios.get('/api/config/templates')
    let platformTemplates: any = {}
    
    // 检查响应格式，兼容不同的响应结构
    if (response.data?.templates?.platform_templates) {
      // 如果响应有 templates.platform_templates 结构
      platformTemplates = response.data.templates.platform_templates
    } else if (response.data?.platform_templates) {
      // 如果响应直接有 platform_templates 结构
      platformTemplates = response.data.platform_templates
    } else if (response.data?.templates) {
      // 旧格式兼容
      platformTemplates = response.data.templates
    }
    
    const platformList: Array<{value: string, label: string}> = []
    
    // 遍历模板键，添加到平台列表
    Object.entries(platformTemplates).forEach(([key, template]: [string, any]) => {
      // 检查是否已经存在
      if (!platformList.some(p => p.value === key)) {
        // 从模板配置中获取平台中文名称，如果没有则使用键作为标签
        platformList.push({ 
          value: key, 
          label: template?.name || key 
        })
      }
    })
    
    // 更新平台列表
    platforms.value = platformList
    
    // 如果当前选择的平台不在列表中，选择第一个平台
    if (!platformList.some(p => p.value === selectedPlatform.value)) {
      selectedPlatform.value = platformList[0]?.value || 'xiaohongshu'
    }
    
    console.log('平台列表加载成功:', platformList)
  } catch (error) {
    console.error('加载平台列表失败:', error)
    // 加载失败时，尝试使用所有平台模板键作为列表
    try {
      const response = await axios.get('/api/config/templates')
      let allPlatformKeys: string[] = []
      
      if (response.data?.templates?.platform_templates) {
        allPlatformKeys = Object.keys(response.data.templates.platform_templates)
      } else if (response.data?.platform_templates) {
        allPlatformKeys = Object.keys(response.data.platform_templates)
      } else if (response.data?.templates) {
        allPlatformKeys = Object.keys(response.data.templates)
      }
      
      // 使用平台键作为标签，确保至少能显示所有平台
      const fallbackPlatformList = allPlatformKeys.map(key => ({
        value: key,
        label: key
      }))
      
      platforms.value = fallbackPlatformList
      console.log('使用回退平台列表:', fallbackPlatformList)
    } catch (fallbackError) {
      console.error('回退平台列表加载也失败:', fallbackError)
    }
  }
}

// 组件挂载时加载平台列表
onMounted(() => {
  loadPlatforms()
})

/**
 * 处理输入变化
 */
function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
  adjustHeight()
}

/**
 * 处理回车键
 */
function handleEnter(e: KeyboardEvent) {
  if (e.shiftKey) return // 允许 Shift+Enter 换行
  emit('generate', selectedPlatform.value)
}

/**
 * 自动调整输入框高度
 */
function adjustHeight() {
  const el = textareaRef.value
  if (!el) return

  el.style.height = 'auto'
  const newHeight = Math.max(64, Math.min(el.scrollHeight, 200))
  el.style.height = newHeight + 'px'
}

/**
 * 处理图片上传
 */
function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (!target.files) return

  const files = Array.from(target.files)
  files.forEach((file) => {
    // 限制最多 5 张图片
    if (uploadedImages.value.length >= 5) {
      return
    }
    // 检查文件大小
    if (file.size > 5 * 1024 * 1024) {
      // 可以添加错误提示
      return
    }
    // 检查文件类型
    if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
      // 可以添加错误提示
      return
    }
    // 创建预览 URL
    const preview = URL.createObjectURL(file)
    uploadedImages.value.push({ file, preview })
  })

  // 通知父组件
  emitImagesChange()

  // 清空 input，允许重复选择同一文件
  target.value = ''
}

/**
 * 移除图片
 */
function removeImage(index: number) {
  const img = uploadedImages.value[index]
  // 释放预览 URL
  URL.revokeObjectURL(img.preview)
  uploadedImages.value.splice(index, 1)

  // 通知父组件
  emitImagesChange()
}

/**
 * 通知父组件图片变化
 */
function emitImagesChange() {
  const files = uploadedImages.value.map(img => img.file)
  emit('imagesChange', files)
}

/**
 * 清理所有预览 URL
 */
function clearPreviews() {
  uploadedImages.value.forEach(img => URL.revokeObjectURL(img.preview))
  uploadedImages.value = []
}

// 组件卸载时清理
onUnmounted(() => {
  clearPreviews()
})

// 暴露方法给父组件
defineExpose({
  clearPreviews
})
</script>

<style scoped>
/* 组合框容器 */
.composer-container {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.06);
  max-width: 800px;
  margin: 0 auto;
}

/* 输入区域 */
.composer-input-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

/* 模板和模型选择器 */
.template-model-selector {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.selector-item {
  flex: 1;
  min-width: 300px;
}

.selector-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary, #1a1a1a);
  margin-bottom: 8px;
}

.selector-input {
  width: 100%;
}

.option-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary, #1a1a1a);
}

.option-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary, #666);
  line-height: 1.4;
}

.search-icon-static {
  flex-shrink: 0;
  padding-top: 8px;
  color: #999;
}

.composer-textarea {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  line-height: 1.6;
  resize: none;
  min-height: 44px;
  max-height: 200px;
  padding: 8px 0;
  font-family: inherit;
  color: var(--el-text-color-primary, #1a1a1a);
}

.composer-textarea::placeholder {
  color: #999;
}

.composer-textarea:disabled {
  background: transparent;
  color: #999;
}

/* 已上传图片预览 */
.uploaded-images-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
  align-items: center;
}

.uploaded-image-item {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.uploaded-image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
}

.uploaded-image-item:hover .remove-image-btn {
  opacity: 1;
}

.remove-image-btn:hover {
  background: var(--el-color-danger, #ff2442);
}

.upload-hint {
  flex: 1;
  font-size: 12px;
  color: var(--el-text-color-secondary, #666);
  text-align: right;
}

/* 工具栏 */
.composer-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.tool-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #f5f5f5;
  border: none;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: #eee;
  color: var(--el-color-primary, #ff2442);
}

.tool-btn.active {
  background: rgba(255, 36, 66, 0.1);
  color: var(--el-color-primary, #ff2442);
}

.badge-count {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  background: var(--el-color-primary, #ff2442);
  color: white;
  border-radius: 9px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

/* 生成按钮 */
.generate-btn {
  padding: 10px 24px;
  font-size: 15px;
  border-radius: 100px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--el-color-primary, #ff2442);
  border: none;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background: var(--el-color-primary-dark-2, #e0213e);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.3);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载动画 */
.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
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