<template>
  <div class="batch-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <h1>{{ t('batch.title') }}</h1>
          <p>{{ t('batch.subtitle') }}</p>
        </div>
      </template>

      <el-form ref="batchFormRef" :model="batchForm" label-width="120px" class="batch-form">
        <!-- 主题输入 -->
        <el-form-item :label="t('batch.topicLabel')" required>
          <el-input
            v-model="batchForm.topics"
            type="textarea"
            :rows="6"
            :placeholder="t('batch.topicPlaceholder')"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <!-- 参考图上传 -->
        <el-form-item :label="t('batch.referenceImages')">
          <div class="reference-images">
            <el-upload
              v-model:file-list="referenceImages"
              action="#"
              :auto-upload="false"
              :on-change="handleImageChange"
              :on-remove="handleImageRemove"
              list-type="picture-card"
              accept="image/*"
              :limit="5"
              :on-exceed="handleExceed"
            >
              <el-icon><Plus /></el-icon>
              <template #tip>
                <div class="el-upload__tip">
                  {{ t('batch.formatTip') }}
                </div>
              </template>
            </el-upload>

            <!-- 已上传图片预览 -->
            <div class="image-preview-list" v-if="previewImages.length > 0">
              <div class="preview-title">{{ t('batch.selectedImages', { count: previewImages.length }) }}</div>
              <div class="image-preview-container">
                <div 
                  v-for="(image, index) in previewImages" 
                  :key="index" 
                  class="preview-item"
                >
                  <el-image
                    :src="image.url"
                    fit="cover"
                    :preview-src-list="previewImages.map(img => img.url)"
                  />
                  <div class="preview-remove" @click="removePreviewImage(index)">
                    <el-icon><Close /></el-icon>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <!-- 文本服务商选择 -->
        <el-form-item :label="t('composer.textProvider')">
          <el-select 
            v-model="batchForm.textProviderId" 
            :placeholder="t('composer.selectTextProvider')"
            size="large"
            clearable
            style="width: 100%;"
          >
            <el-option 
              v-for="provider in generatorStore.textProviders.filter(p => p.enabled)" 
              :key="provider.name" 
              :label="`${provider.name} (${provider.model})`" 
              :value="provider.name" 
            >
              <div class="option-content">
                <div class="option-name">{{ provider.name }}</div>
                <div class="option-desc">{{ provider.type }} - {{ provider.model }}</div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 平台选择 -->
        <el-form-item :label="t('batch.targetPlatforms')" required>
          <el-checkbox-group v-model="batchForm.platforms">
            <el-checkbox
              v-for="platform in platforms"
              :key="platform.value"
              :label="platform.value"
            >
              {{ platform.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="generateBatch" :loading="generating" size="large">
            <el-icon v-if="!generating"><Plus /></el-icon>
            <el-icon v-else><Loading /></el-icon>
            {{ t('batch.startBatchGenerate') }}
          </el-button>
          <el-button @click="resetForm" :loading="generating">{{ t('common.reset') }}</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 状态展示 -->
      <el-card v-if="jobInfo" shadow="hover" class="status-card">
        <template #header>
          <div class="status-header">
            <h3>{{ t('batch.generationStatus') }}</h3>
            <el-tag :type="getStatusType(jobInfo.status)">{{ jobInfo.status }}</el-tag>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('batch.jobId')">{{ jobInfo.job_id }}</el-descriptions-item>
          <el-descriptions-item :label="t('batch.createdAt')">{{ formatTime(jobInfo.created_at) }}</el-descriptions-item>
          <el-descriptions-item :label="t('batch.completionProgress')">
            <el-progress 
              :percentage="calculateProgress(jobInfo)" 
              :status="getStatusProgress(jobInfo.status)"
            />
          </el-descriptions-item>
          <el-descriptions-item :label="t('batch.processingResults')">
            <span v-if="jobInfo.completed > 0">{{ jobInfo.completed }} {{ t('batch.successCount') }}</span>
            <span v-if="jobInfo.failed > 0" class="failed-count">{{ jobInfo.failed }} {{ t('batch.failedCount') }}</span>
            <span v-if="jobInfo.completed === 0 && jobInfo.failed === 0">{{ t('batch.processing') }}</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="status-actions">
          <el-button 
            type="primary" 
            size="small" 
            @click="checkStatus" 
            :loading="checkingStatus"
          >
            <el-icon><Refresh /></el-icon>
            {{ t('batch.refreshStatus') }}
          </el-button>
          <el-button 
            v-if="jobInfo.status === 'processing'" 
            type="danger" 
            size="small" 
            @click="cancelJob"
          >
            <el-icon><Close /></el-icon>
            {{ t('batch.cancelJob') }}
          </el-button>
        </div>
      </el-card>
      
      <!-- 结果展示 -->
      <el-card v-if="results.length > 0" shadow="hover" class="results-card">
        <template #header>
          <div class="results-header">
            <h3>{{ t('batch.generationResults') }}</h3>
            <el-button type="success" size="small" @click="downloadResults">
              <el-icon><Download /></el-icon>
              {{ t('batch.downloadResults') }}
            </el-button>
          </div>
        </template>
        
        <el-collapse v-model="activeNames" accordion>
          <el-collapse-item 
            v-for="(result, index) in results" 
            :key="index" 
            :title="`${getPlatformLabel(result.platform)} - ${result.title}`"
          >
            <div class="result-content">
              <h4>{{ result.title }}</h4>
              <div class="content">{{ result.content }}</div>
              <div v-if="result.images.length > 0" class="images">
                <h5>{{ t('batch.generatedImages') }}：</h5>
                <div class="image-list">
                  <el-image 
                    v-for="(image, imgIndex) in result.images" 
                    :key="imgIndex" 
                    :src="image" 
                    :preview-src-list="result.images"
                    fit="cover"
                    class="result-image"
                  />
                </div>
              </div>
              <div class="metadata">
                <el-tag size="small" class="platform-tag">{{ getPlatformLabel(result.platform) }}</el-tag>
                <span class="time">{{ formatTime(result.created_at) }}</span>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

// 国际化
const { t } = useI18n()
import { Plus, Loading, Refresh, Close, Download } from '@element-plus/icons-vue'
import axios from 'axios'
import dayjs from 'dayjs'

// 导入平台工具函数
import { getPlatformOptions, loadPlatformConfig } from '../utils/platformUtils'

// 引入状态管理
import { useGeneratorStore } from '../stores/generator'

// 表单引用
const batchFormRef = ref()

// 引入状态管理
const generatorStore = useGeneratorStore()

// 批量生成表单
const batchForm = reactive({
  topics: '',
  platforms: [] as string[],
  textProviderId: generatorStore.textProviderId
})

// 参考图相关
const referenceImages = ref<any[]>([])
const previewImages = ref<any[]>([])

// 平台选项
const platforms = ref<Array<{value: string, label: string}>>([])

// 生成状态
const generating = ref(false)
const checkingStatus = ref(false)
const jobInfo = ref<any>(null)
const results = ref<any[]>([])
const activeNames = ref(['0'])

// 获取平台标签
const getPlatformLabel = (platform: string) => {
  const found = platforms.value.find(p => p.value === platform)
  return found ? found.label : platform
}

// 组件挂载时加载平台配置和文本服务商数据
onMounted(async () => {
  // 加载平台配置
  await loadPlatformConfig()
  platforms.value = getPlatformOptions()
  
  // 如果没有加载到平台配置，显示警告并使用默认平台
  if (platforms.value.length === 0) {
    console.warn('未加载到平台配置，使用默认平台')
    // 添加默认平台选项
    platforms.value = [
      { label: '小红书', value: 'xiaohongshu' },
      { label: '抖音', value: 'douyin' },
      { label: '微信', value: 'wechat' },
      { label: '头条', value: 'toutiao' }
    ]
  }
  
  // 加载文本服务商数据
  try {
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
  } catch (error: any) {
    console.error('加载文本服务商数据失败:', error)
  }
})

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取进度条状态
const getStatusProgress = (status: string) => {
  return status === 'completed' ? 'success' : status === 'failed' ? 'exception' : ''
}

// 格式化时间
const formatTime = (time: string | Date) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 计算进度百分比
const calculateProgress = (info: any) => {
  if (!info || !info.total) return 0
  const total = info.total
  const completed = info.completed || 0
  const failed = info.failed || 0
  return Math.round(((completed + failed) / total) * 100)
}

// 重置表单
const resetForm = () => {
  batchFormRef.value?.resetFields()
  jobInfo.value = null
  results.value = []
  activeNames.value = ['0']
}

// 开始批量生成
const generateBatch = async () => {
  // 表单验证
  if (!batchForm.topics.trim()) {
    ElMessage.error(t('batch.pleaseEnterTopics'))
    return
  }
  
  if (batchForm.platforms.length === 0) {
    ElMessage.error(t('batch.pleaseSelectPlatforms'))
    return
  }
  
  // 解析主题列表
  const topics = batchForm.topics
    .split('\n')
    .map(topic => topic.trim())
    .filter(topic => topic)
    
  if (topics.length === 0) {
    ElMessage.error(t('batch.pleaseEnterValidTopics'))
    return
  }
  
  generating.value = true
  
  try {
    // 准备参考图数据
    const formData = new FormData()
    formData.append('topics', JSON.stringify(topics))
    formData.append('platforms', JSON.stringify(batchForm.platforms))
    
    // 添加文本服务商参数
    if (batchForm.textProviderId) {
      formData.append('text_provider', batchForm.textProviderId)
    }
    
    // 添加参考图
    previewImages.value.forEach((img, index) => {
      formData.append(`reference_images[${index}]`, img.file, img.file.name)
    })
    
    // 调用后端API
    const response = await axios.post('/api/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    jobInfo.value = response.data
    ElMessage.success('批量生成任务已启动')
    
    // 自动检查状态
    checkStatus()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '批量生成启动失败')
    console.error('批量生成失败:', error)
  } finally {
    generating.value = false
  }
}

// 检查生成状态
const checkStatus = async () => {
  if (!jobInfo.value?.job_id) return
  
  checkingStatus.value = true
  
  try {
    const response = await axios.get(`/api/batch/${jobInfo.value.job_id}/status`)
    jobInfo.value = response.data
    
    // 如果任务完成，获取结果
    if (response.data.status === 'completed') {
      await getResults()
    }
    
    // 如果任务正在处理，继续检查
    if (response.data.status === 'processing') {
      setTimeout(checkStatus, 3000)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取状态失败')
    console.error('获取状态失败:', error)
  } finally {
    checkingStatus.value = false
  }
}

// 获取生成结果
const getResults = async () => {
  if (!jobInfo.value?.job_id) return
  
  try {
    const response = await axios.get(`/api/batch/${jobInfo.value.job_id}/results`)
    if (response.data?.results) {
      results.value = response.data.results
      ElMessage.success('获取生成结果成功')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取结果失败')
    console.error('获取结果失败:', error)
  }
}

// 取消任务
const cancelJob = async () => {
  if (!jobInfo.value?.job_id) return
// 取消任务
  try {
    await ElMessageBox.confirm(t('batch.confirmCancelJob'), t('batch.cancelJob'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning'
    })
    
    await axios.delete(`/api/batch/${jobInfo.value.job_id}`)
    await checkStatus()
    ElMessage.success('任务已取消')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '取消任务失败')
      console.error('取消任务失败:', error)
    }
  }
}

// 图片上传相关函数
const handleImageChange = (file: any, fileList: any[]) => {
  // 检查文件大小
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  
  // 检查文件类型
  if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.raw.type)) {
    ElMessage.error('只支持 JPG、PNG 格式图片')
    return false
  }
  
  // 生成预览URL
  const reader = new FileReader()
  reader.readAsDataURL(file.raw)
  reader.onload = (e) => {
    previewImages.value.push({
      url: e.target?.result as string,
      file: file.raw
    })
  }
  
  return true
}

const handleImageRemove = (file: any, fileList: any[]) => {
  // 从预览列表中移除
  const index = previewImages.value.findIndex(img => img.file === file.raw)
  if (index > -1) {
    previewImages.value.splice(index, 1)
  }
}

const handleExceed = () => {
  ElMessage.error(t('batch.maxImagesError'))
}

const removePreviewImage = (index: number) => {
  previewImages.value.splice(index, 1)
  // 同步更新上传组件的文件列表
  referenceImages.value.splice(index, 1)
}

// 下载结果
const downloadResults = () => {
  if (results.value.length === 0) {
    ElMessage.warning(t('batch.noResultsToDownload'))
    return
  }
  
  // 简单的JSON下载
  const dataStr = JSON.stringify(results.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${t('batch.batchResults')}-${dayjs().format('YYYYMMDD-HHmmss')}.json`
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped lang="scss">
.batch-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 参考图上传样式 */
.reference-images {
  margin-top: 16px;
}

.image-preview-list {
  margin-top: 16px;
}

.preview-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
}

.image-preview-container {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.preview-item {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-item .el-image {
  width: 100%;
  height: 100%;
}

.preview-remove {
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--el-color-danger);
  transition: all 0.3s;
}

.preview-remove:hover {
  background-color: var(--el-color-danger);
  color: white;
}

.preview-remove .el-icon {
  font-size: 14px;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  
  p {
    margin: 0;
    color: var(--el-text-color-secondary);
  }
}

.batch-form {
  margin-bottom: 24px;
}

/* 选项内容样式 */
.option-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.option-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.status-card {
  margin-bottom: 24px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
}

.status-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: flex-end;
}

.failed-count {
  color: var(--el-color-danger);
  margin-left: 8px;
}

.results-card {
  margin-bottom: 24px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
}

.result-content {
  padding: 16px 0;
  
  h4 {
    margin: 0 0 12px 0;
    font-size: 16px;
    font-weight: 600;
  }
  
  .content {
    margin-bottom: 16px;
    line-height: 1.6;
    color: var(--el-text-color-regular);
  }
  
  .images {
    margin-bottom: 16px;
    
    h5 {
      margin: 0 0 8px 0;
      font-size: 14px;
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
    
    .image-list {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      
      .result-image {
        width: 200px;
        height: 200px;
        border-radius: 8px;
        cursor: pointer;
      }
    }
  }
  
  .metadata {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--el-border-color-light);
    
    .platform-tag {
      margin-right: 8px;
    }
    
    .time {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
}
</style>