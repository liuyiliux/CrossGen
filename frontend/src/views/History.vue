<template>
  <div class="history-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <h1>{{ t('history.title') }}</h1>
<p>{{ t('history.subtitle') }}</p>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="search-filter">
        <el-form :model="searchForm" inline class="search-form">
          <el-form-item :label="t('history.search')">
            <el-input
              v-model="searchForm.keyword"
              :placeholder="t('history.keywordPlaceholder')"
              clearable
              size="large"
              @keyup.enter="searchHistory"
            >
              <template #append>
                <el-icon @click="searchHistory"><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item :label="t('history.selectPlatform')">
            <el-select
              v-model="searchForm.platform"
              :placeholder="t('history.selectPlatform')" 
              clearable
              size="large"
              style="width: 180px;"
            >
              <el-option :label="t('history.all')" value="" />
              <el-option
                v-for="option in platformOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('history.dateRange')">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              :range-separator="t('history.to')"
              :start-placeholder="t('history.startDate')"
              :end-placeholder="t('history.endDate')"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              size="large"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="searchHistory" size="large">
              <el-icon><Search /></el-icon>
              {{ t('history.search') }}
            </el-button>
            <el-button @click="resetSearch" size="large">
              <el-icon><RefreshRight /></el-icon>
              {{ t('common.reset') }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-dropdown @command="handleBatchAction">
            <el-button type="warning" size="large">
              <el-icon><MoreFilled /></el-icon>
              {{ t('history.batchOperation') }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="delete">
                <el-icon><Delete /></el-icon>
                {{ t('history.batchDelete') }}
              </el-dropdown-item>
              <el-dropdown-item command="export">
                <el-icon><Download /></el-icon>
                {{ t('history.batchExport') }}
              </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 历史记录列表 -->
      <div class="history-list">
        <!-- 有数据时显示表格和分页 -->
        <template v-if="filteredHistory.length > 0">
          <el-table
            ref="historyTableRef"
            :data="filteredHistory"
            border
            style="width: 100%"
            class="history-table"
            @selection-change="handleSelectionChange"
          >
            <!-- 多选框 -->
            <el-table-column type="selection" width="55" />
            
            <!-- 序号 -->
            <el-table-column type="index" :label="t('common.index')" width="80" />
            
            <!-- 主题 -->
            <el-table-column prop="topic" :label="t('history.topic')" min-width="200" show-overflow-tooltip>
              <template #default="scope">
                <div class="topic-cell">
                  <span class="topic-text">{{ scope.row.topic }}</span>
                  <el-tag :type="getPlatformType(scope.row.platform)" size="small" class="platform-tag">
                    {{ getPlatformLabel(scope.row.platform) }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            
            <!-- 生成时间 -->
            <el-table-column prop="created_at" :label="t('history.createdAt')" width="200" show-overflow-tooltip>
              <template #default="scope">
                {{ formatTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            
            <!-- 状态 -->
            <el-table-column prop="status" :label="t('history.status')" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)" effect="light">
                  {{ getStatusLabel(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <!-- 操作 -->
            <el-table-column :label="t('common.action')" width="360" fixed="right">
              <template #default="scope">
                <div class="action-buttons-group">
                  <el-button type="primary" size="small" @click="viewHistory(scope.row)">
                    <el-icon><View /></el-icon>
                    {{ t('common.view') }}
                  </el-button>
                  <el-button type="warning" size="small" @click="copyAndEdit(scope.row)" :disabled="!scope.row.outline">
                    <el-icon><CopyDocument /></el-icon>
                    {{ t('common.copy') }}
                  </el-button>
                  <el-button type="success" size="small" @click="editHistory(scope.row)" :disabled="!scope.row.outline">
                    <el-icon><EditPen /></el-icon>
                    {{ t('common.edit') }}
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteHistory(scope.row.id)">
                    <el-icon><Delete /></el-icon>
                    {{ t('common.delete') }}
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredHistory.length"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </template>
        
        <!-- 空状态 -->
        <el-empty
          v-else
          :description="t('history.noHistory')"
          :image-size="200"
        />
      </div>
    </el-card>
    
    <!-- 历史详情对话框 -->
    <el-dialog
      v-model="historyDialogVisible"
      :title="`${t('history.detail')} - ${selectedHistory?.topic || ''}`"
      width="80%"
      class="history-dialog"
    >
      <div v-if="selectedHistory" class="history-detail">
        <!-- 基本信息 -->
        <el-descriptions :column="3" border class="detail-info">
            <el-descriptions-item :label="t('history.topic')">{{ selectedHistory.topic }}</el-descriptions-item>
            <el-descriptions-item :label="t('history.platform')">
              <el-tag :type="getPlatformType(selectedHistory.platform)">
                {{ getPlatformLabel(selectedHistory.platform) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="t('history.createdAt')">{{ formatTime(selectedHistory.created_at) }}</el-descriptions-item>
            <el-descriptions-item :label="t('history.generationTime')">{{ selectedHistory.generation_time?.toFixed(2) }}秒</el-descriptions-item>
            <el-descriptions-item :label="t('history.status')">
              <el-tag :type="getStatusType(selectedHistory.status)">
                {{ getStatusLabel(selectedHistory.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="t('history.textModel')">{{ selectedHistory.text_model || t('history.defaultModel') }}</el-descriptions-item>
            <el-descriptions-item :label="t('history.imageModel')">{{ selectedHistory.image_model || t('history.defaultModel') }}</el-descriptions-item>
            <el-descriptions-item :label="t('history.resultCount')">{{ selectedHistory.images?.length || 0 }}</el-descriptions-item>
          </el-descriptions>
        
        <!-- 生成结果 -->
            <div class="detail-results">
              <h3 class="results-title">{{ t('history.generationResults') }}</h3>
              
              <el-tabs v-model="activeResultTab" type="card" class="result-tabs">
                <!-- 大纲视图选项卡 -->
                <el-tab-pane :label="t('history.outlineView')" name="outline">
                  <div class="outline-view" v-if="selectedHistory.outline">
                    <h4 class="outline-title">{{ t('history.generatedOutline') }}</h4>
                    <div class="outline-pages">
                      <div 
                        v-for="page in selectedHistory.outline.pages" 
                        :key="page.index" 
                        class="outline-page"
                        :class="`page-type-${page.type}`"
                      >
                        <div class="page-header">
                          <el-tag :type="getPageType(page.type)" size="small" class="page-type-tag">
                            {{ getPageTypeName(page.type) }}
                          </el-tag>
                          <span class="page-index">第{{ page.index + 1 }}页</span>
                        </div>
                        <div class="page-content">
                          {{ page.content }}
                        </div>
                      </div>
                    </div>
                    
                    <!-- 原始大纲文本 -->
                    <div class="outline-raw">
                      <h5>{{ t('history.rawOutlineText') }}</h5>
                      <el-input
                        type="textarea"
                        :value="selectedHistory.outline.raw"
                        readonly
                        :rows="10"
                        class="raw-textarea"
                      />
                    </div>
                  </div>
                  <el-empty v-else description="暂无大纲数据" :image-size="150" />
                </el-tab-pane>
                
                <!-- 图片视图选项卡 -->
                <el-tab-pane :label="t('history.generatedImages')" name="images">
                  <div class="images-view" v-if="selectedHistory.images && selectedHistory.images.length > 0">
                    <div class="image-grid">
                      <div 
                        v-for="(image, imgIndex) in selectedHistory.images" 
                        :key="imgIndex" 
                        class="image-item"
                      >
                        <!-- 大纲页面信息 -->
                        <template v-if="selectedHistory.outline && selectedHistory.outline.pages[imgIndex]">
                          <div class="image-outline-info">
                            <div class="page-type" :class="selectedHistory.outline.pages[imgIndex].type">
                              {{ selectedHistory.outline.pages[imgIndex].type === 'cover' ? t('history.cover') : 
                                 selectedHistory.outline.pages[imgIndex].type === 'summary' ? t('history.summary') : t('history.contentPage') }}
                            </div>
                            <div class="image-page-content-preview">
                              {{ selectedHistory.outline.pages[imgIndex].content }}
                            </div>
                          </div>
                        </template>
                        
                        <!-- 图片 -->
                        <el-image
                          :src="store.processImageUrl(image.url) || ''"
                          :preview-src-list="selectedHistory.images.filter((img: any) => img.url).map((img: any) => store.processImageUrl(img.url))"
                          fit="cover"
                          class="result-image"
                          lazy
                        >
                          <!-- 加载占位符 -->
                <template #loading>
                  <div class="image-placeholder">
                    <el-icon><PictureRounded /></el-icon>
                    <span>{{ t('common.loading') }}</span>
                  </div>
                </template>
                <!-- 错误占位符 -->
                <template #error>
                  <div class="image-placeholder error">
                    <el-icon><PictureRounded /></el-icon>
                    <span>{{ t('common.loadFailed') }}</span>
                  </div>
                </template>
                        </el-image>
                        
                        <!-- 图片状态 -->
                        <div class="image-status">
                          <el-tag :type="image.status === 'done' ? 'success' : image.status === 'error' ? 'danger' : 'warning'" size="small">
                              {{ image.status === 'done' ? t('common.success') : image.status === 'error' ? t('common.failed') : image.status || t('common.unknown') }}
                            </el-tag>
                        </div>
                      </div>
                    </div>
                  </div>
                  <el-empty v-else description="暂无生成图片" :image-size="150" />
                </el-tab-pane>
                
                <!-- 各平台结果选项卡 -->
                <el-tab-pane
                  v-for="(result, index) in selectedHistory.results || []"
                  :key="index"
                  :label="getPlatformLabel(result.platform)"
                  :name="(index + 2).toString()"
                >
                  <div class="result-detail">
                    <h4 class="result-title">{{ result.title }}</h4>
                    <div class="result-content">{{ result.content }}</div>
                    
                    <!-- 生成图片 -->
                    <div v-if="result.images && result.images.length > 0" class="result-images">
                      <h5>{{ t('history.generatedImages') }}：</h5>
                      <div class="image-grid">
                        <el-image
                          v-for="(image, imgIndex) in result.images"
                          :key="imgIndex"
                          :src="store.processImageUrl(image)"
                          :preview-src-list="result.images.map((img: any) => store.processImageUrl(img))"
                          fit="cover"
                          class="result-image"
                          lazy
                        >
                          <!-- 加载占位符 -->
                              <template #loading>
                                <div class="image-placeholder">
                                  <el-icon><PictureRounded /></el-icon>
                                  <span>{{ t('common.loading') }}</span>
                                </div>
                              </template>
                              <!-- 错误占位符 -->
                              <template #error>
                                <div class="image-placeholder error">
                                  <el-icon><PictureRounded /></el-icon>
                                  <span>{{ t('common.loadFailed') }}</span>
                                </div>
                              </template>
                        </el-image>
                      </div>
                    </div>
                    
                    <!-- 元数据 -->
                    <div class="result-metadata">
                      <el-tag size="small" effect="plain" v-for="(value, key) in result.metadata" :key="key">
                        {{ key }}: {{ value }}
                      </el-tag>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { useGeneratorStore } from '../stores/generator'

// 国际化
const { t } = useI18n()
import {
  Search,
  RefreshRight,
  MoreFilled,
  ArrowDown,
  Delete,
  Download,
  View,
  CopyDocument,
  EditPen
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import axios from 'axios'

// 创建store实例
const store = useGeneratorStore()

// 搜索和筛选
const searchForm = reactive({
  keyword: '',
  platform: '',
  dateRange: [] as string[]
})

// 表格引用
const historyTableRef = ref()

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 选择的历史记录
const selectedHistory = ref<any>(null)
const historyDialogVisible = ref(false)
const activeResultTab = ref('outline')

// 批量选择
const selectedRows = ref<any[]>([])

// 历史记录数据
const historyList = ref<any[]>([])

// 加载状态
const loading = ref(false)

// 筛选后的历史记录
const filteredHistory = computed(() => {
  return historyList.value
})

// 加载历史记录
const loadHistory = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    
    // 添加搜索参数
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    if (searchForm.platform) {
      params.platform = searchForm.platform
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }
    
    const response = await axios.get('/api/history', { params })
    historyList.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error: any) {
    ElMessage.error('加载历史记录失败: ' + (error.response?.data?.detail || error.message))
    historyList.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 页面加载时加载历史记录
onMounted(() => {
  loadHistory()
})

// 导入共享平台映射工具
import { getPlatformLabel, getPlatformType, getPlatformOptions, loadPlatformConfig } from '../utils/platformUtils'

// 平台选项
const platformOptions = ref(getPlatformOptions())

// 加载平台配置
onMounted(async () => {
  await loadPlatformConfig()
  // 更新平台选项
  platformOptions.value = getPlatformOptions()
  // 重新加载历史记录，确保平台名称正确显示
  loadHistory()
})

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    success: 'success',
    failed: 'danger',
    processing: 'warning',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const labelMap: Record<string, any> = {
    success: t('common.success'),
    failed: t('common.failed'),
    processing: t('common.processing'),
    cancelled: t('common.cancelled'),
    image_generating: t('history.imageGenerating'),
    image_success: t('history.imageSuccess'),
    image_failed: t('history.imageFailed'),
    outline_generating: t('history.outlineGenerating'),
    outline_success: t('history.outlineSuccess'),
    outline_failed: t('history.outlineFailed')
  }
  return labelMap[status] || status
}

// 获取页面类型对应的标签类型
const getPageType = (type: string) => {
  const typeMap: Record<string, any> = {
    cover: 'primary',
    content: 'success',
    summary: 'warning'
  }
  return typeMap[type] || 'info'
}

// 获取页面类型名称
const getPageTypeName = (type: string) => {
  const nameMap: Record<string, any> = {
    cover: t('history.cover'),
    content: t('history.content'),
    summary: t('history.summary')
  }
  return nameMap[type] || type
}

// 格式化时间
const formatTime = (time: string | Date) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 搜索历史
const searchHistory = () => {
  pagination.currentPage = 1
  loadHistory()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.platform = ''
  searchForm.dateRange = []
  pagination.currentPage = 1
  loadHistory()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadHistory()
}

const handleCurrentChange = (current: number) => {
  pagination.currentPage = current
  loadHistory()
}

// 批量操作
const handleBatchAction = (command: string) => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning(t('history.pleaseSelectHistory'))
    return
  }
  
  switch (command) {
    case 'delete':
      batchDelete()
      break
    case 'export':
      batchExport()
      break
  }
}

// 批量删除
const batchDelete = async () => {
  ElMessageBox.confirm(
    t('history.confirmBatchDelete', { count: selectedRows.value.length }),
    t('history.batchDelete'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning'
    }
  )
  .then(async () => {
    const ids = selectedRows.value.map(row => row.id)
    
    try {
      const response = await axios.delete('/api/history', {
        data: ids
      })
      
      if (response.data.success_count > 0) {
        ElMessage.success(`成功删除 ${response.data.success_count} 条历史记录`)
        // 重新加载历史记录
        loadHistory()
        selectedRows.value = []
      } else {
        ElMessage.warning('删除失败')
      }
    } catch (error: any) {
      ElMessage.error('批量删除失败: ' + (error.response?.data?.detail || error.message))
    }
  })
  .catch(() => {
    // 取消删除
  })
}

// 批量导出
const batchExport = () => {
  const dataStr = JSON.stringify(selectedRows.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${t('history.historyExport')}-${dayjs().format('YYYYMMDD-HHmmss')}.json`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('批量导出成功')
}

// 查看历史详情
const viewHistory = async (history: any) => {
  try {
    const response = await axios.get(`/api/history/${history.id}`)
    selectedHistory.value = response.data
    activeResultTab.value = 'outline'
    historyDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error('获取历史记录详情失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 删除历史记录
const deleteHistory = async (id: string) => {
  ElMessageBox.confirm(t('history.confirmDelete'), t('common.confirmDelete'), {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    type: 'warning'
  })
  .then(async () => {
    try {
      await axios.delete(`/api/history/${id}`)
      ElMessage.success('删除成功')
      // 重新加载历史记录
      loadHistory()
    } catch (error: any) {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  })
  .catch(() => {
    // 取消删除
  })
}

// 处理选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
}

// 复制历史记录并跳转到大纲页
const copyAndEdit = (history: any) => {
  if (!history.outline) {
    ElMessage.warning(t('history.noOutlineToCopy'))
    return
  }
  
  // 保存历史记录到本地存储
  localStorage.setItem('copiedHistory', JSON.stringify(history))
  
  // 跳转到大纲页
  window.location.href = '/outline'
}

// 编辑历史记录
const editHistory = (history: any) => {
  if (!history.outline) {
    ElMessage.warning(t('history.noOutlineToCopy'))
    return
  }
  // 保存历史记录ID和内容到本地存储
  localStorage.setItem('editHistoryId', history.id)
  localStorage.setItem('copiedHistory', JSON.stringify(history))
  // 跳转到大纲页
  window.location.href = '/outline'
}

</script>

<style scoped lang="scss">
.history-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
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

.search-filter {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 16px;
  
  @media (max-width: 1024px) {
    flex-direction: column;
    align-items: stretch;
  }
}

.search-form {
  flex: 1;
  
  .el-form-item {
    margin-right: 16px;
    margin-bottom: 12px;
  }
}

.action-buttons {
  display: flex;
  gap: 8px;
  
  @media (max-width: 1024px) {
    justify-content: flex-start;
  }
}

.history-list {
  margin-top: 16px;
}

.history-table {
    .el-table__header-wrapper {
      background-color: var(--el-bg-color-page);
    }
    
    .el-table__body-wrapper {
      max-height: 600px;
      overflow-y: auto;
    }
    
    /* 隐藏表格自带的空状态文本 */
    .el-table__empty-text {
      display: none;
    }
  
  .topic-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .topic-text {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .platform-tag {
      flex-shrink: 0;
    }
  }
  
  // 按钮组样式 - 小红书风格
  .action-buttons-group {
    display: flex;
    flex-wrap: nowrap;
    gap: 6px;
    align-items: stretch;
    width: 100%;
    
    .el-button {
      flex: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 4px 10px;
      font-size: 12px;
      border-radius: 6px;
      font-weight: 600;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      white-space: nowrap;
      
      .el-icon {
        margin-right: 4px;
        font-size: 14px;
        flex-shrink: 0;
      }
      
      .el-button__content {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
      }
      
      &:hover {
        transform: translateY(-1px) !important;
      }
      
      &:active {
        transform: translateY(0) !important;
      }
    }
  }
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.history-dialog {
  max-height: 90vh;
  overflow-y: auto;
}

.history-detail {
  padding: 8px 0;
}

.detail-info {
  margin-bottom: 24px;
}

.detail-results {
  margin-top: 24px;
}

.results-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.result-tabs {
  margin-top: 8px;
}

.result-detail {
  padding: 16px 0;
  
  .result-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: 0 0 16px 0;
    line-height: 1.4;
  }
  
  .result-content {
    font-size: 16px;
    line-height: 1.8;
    color: var(--el-text-color-regular);
    margin-bottom: 20px;
    white-space: pre-wrap;
  }
  
  .result-images {
      margin-bottom: 20px;
      
      h5 {
        margin: 0 0 12px 0;
        font-size: 16px;
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
      
      .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 20px;
        
        .result-image {
          width: 100%;
          height: 220px;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
          object-fit: cover;
          
          &:hover {
            transform: scale(1.03);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
          }
        }
      }
    }
  
  .result-metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--el-border-color-light);
    
    .el-tag {
      margin: 0;
    }
  }
}

/* 大纲视图样式 */
.outline-view {
  padding: 8px 0;
}

.outline-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 16px 0;
}

.outline-pages {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.outline-page {
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-light);
  transition: all 0.3s ease;
  background: #fafafa;
}

.outline-page:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: var(--el-color-primary-light-3);
}

.page-type-cover {
  background: rgba(255, 36, 66, 0.05);
}

.page-type-content {
  background: rgba(103, 194, 58, 0.05);
}

.page-type-summary {
  background: rgba(230, 162, 60, 0.05);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.page-type-tag {
  flex-shrink: 0;
}

.page-index {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.page-content {
  font-size: 16px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
}

.outline-raw {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color-light);
}

.outline-raw h5 {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 12px 0;
}

.raw-textarea {
  font-family: monospace;
  font-size: 13px;
  line-height: 1.4;
  background: #f5f5f5;
  border-color: var(--el-border-color-light);
}

.raw-textarea::placeholder {
  color: #999;
}

/* 图片视图样式 */
.image-item {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.image-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.image-outline-info {
  padding: 12px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: #fafafa;
}

.image-outline-info .page-type {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  margin-bottom: 8px;
}

.image-outline-info .page-type.cover {
  background: #FFE8E8;
  color: #FF4D4F;
}

.image-outline-info .page-type.content {
  background: #E6F7FF;
  color: #1890FF;
}

.image-outline-info .page-type.summary {
  background: #F6FFED;
  color: #52C41A;
}

.image-page-content-preview {
  font-size: 12px;
  color: var(--el-text-color-primary);
  line-height: 1.4;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  word-break: break-word;
}

.image-status {
  padding: 8px 12px;
  border-top: 1px solid var(--el-border-color-light);
  background: #fafafa;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}</style>