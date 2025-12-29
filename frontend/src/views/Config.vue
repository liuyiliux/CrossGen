<template>
  <div class="config-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <h1>{{ t('config.title') }}</h1>
          <p>{{ t('config.subtitle') }}</p>
        </div>
      </template>
      
      <!-- 配置标签页 -->
      <el-tabs v-model="activeTab" type="card" class="config-tabs">
        <!-- 通用设置 -->
        <el-tab-pane :label="t('config.generalSettings')" name="general">
          <div class="general-config">
            <el-card shadow="hover" class="general-config-card">
              <template #header>
                <h3 class="card-subtitle">{{ t('config.systemConfig') }}</h3>
              </template>
              
              <el-form ref="generalFormRef" :model="generalConfig" label-width="150px" class="general-form">
                <!-- Redis 开关 -->
                <el-form-item :label="t('config.enableRedis')">
                  <el-switch v-model="generalConfig.redis_enabled" />
                  <span class="help-text">{{ t('config.redisHelp') }}</span>
                </el-form-item>
                
                <!-- Redis 连接信息 -->
                <el-form-item :label="t('config.redisUrl')">
                  <el-input v-model="generalConfig.redis_url" :placeholder="t('config.redisUrlPlaceholder')" />
                </el-form-item>
                
                <!-- Redis 密码 -->
                <el-form-item :label="t('config.redisPassword')">
                  <el-input
                    v-model="generalConfig.redis_password"
                    type="password"
                    show-password
                    :placeholder="t('config.redisPasswordPlaceholder')"
                  />
                </el-form-item>
                
                <!-- Redis 测试按钮 -->
                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="testRedisConnection" 
                    :loading="testingRedis"
                  >
                    <el-icon><Connection /></el-icon>
                    {{ t('config.testRedisConnection') }}
                  </el-button>
                </el-form-item>
                
                <!-- MySQL 配置 -->
                <el-collapse v-model="mysqlCollapse" class="mysql-collapse">
                  <el-collapse-item :title="t('config.mysqlConfig')" name="mysql">
                    <el-form-item :label="t('config.enableMysql')">
                      <el-switch v-model="generalConfig.mysql_enabled" />
                      <span class="help-text">{{ t('config.mysqlHelp') }}</span>
                    </el-form-item>
                    
                    <el-form-item :label="t('config.mysqlHost')">
                      <el-input v-model="generalConfig.mysql_host" :placeholder="t('config.mysqlHostPlaceholder')" />
                    </el-form-item>
                    
                    <el-form-item :label="t('config.mysqlPort')">
                      <el-input-number
                        v-model="generalConfig.mysql_port"
                        :min="1"
                        :max="65535"
                        :step="1"
                        :placeholder="t('config.mysqlPortPlaceholder')"
                      />
                    </el-form-item>
                    
                    <el-form-item :label="t('config.mysqlDatabase')">
                      <el-input v-model="generalConfig.mysql_database" :placeholder="t('config.mysqlDatabasePlaceholder')" />
                    </el-form-item>
                    
                    <el-form-item :label="t('config.mysqlUsername')">
                      <el-input v-model="generalConfig.mysql_username" :placeholder="t('config.mysqlUsernamePlaceholder')" />
                    </el-form-item>
                    
                    <el-form-item :label="t('config.mysqlPassword')">
                      <el-input
                        v-model="generalConfig.mysql_password"
                        type="password"
                        show-password
                        :placeholder="t('config.mysqlPasswordPlaceholder')"
                      />
                    </el-form-item>

                    <!-- MySQL 测试按钮 -->
                    <el-form-item>
                      <el-button 
                        type="primary" 
                        @click="testMysqlConnection" 
                        :loading="testingMysql"
                      >
                        <el-icon><Connection /></el-icon>
                        {{ t('config.testMysqlConnection') }}
                      </el-button>
                    </el-form-item>
                  </el-collapse-item>
                </el-collapse>
                
                <!-- 操作按钮 -->
                <div class="form-actions">
                  <el-button type="primary" @click="saveGeneralConfig" :loading="savingGeneral" size="large">
                    <el-icon><Upload /></el-icon>
                    {{ t('common.save') }}
                  </el-button>
                  <el-button @click="resetGeneralConfig" :loading="savingGeneral">
                    <el-icon><RefreshRight /></el-icon>
                    {{ t('common.reset') }}
                  </el-button>
                </div>
              </el-form>
            </el-card>
          </div>
        </el-tab-pane>
        
        <!-- 平台模板配置 -->
        <el-tab-pane :label="t('config.platformTemplates')" name="templates">
          <div class="template-config">
            <!-- 平台选择 -->
            <el-form-item :label="t('config.selectPlatform')">
              <el-select
                v-model="selectedPlatform"
                :placeholder="t('config.platformPlaceholder')"
                size="large"
                @change="loadPlatformTemplate"
              >
                <el-option
                  v-for="platform in platforms"
                  :key="platform.value"
                  :label="platform.label"
                  :value="platform.value"
                />
              </el-select>
            </el-form-item>
            
            <!-- 模板配置表单 -->
            <el-card v-if="currentTemplate" shadow="hover" class="template-card">
              <template #header>
                <div class="template-card-header">
                  <h3 class="card-subtitle">{{ t('config.templateConfig') }}</h3>
                  <div class="template-actions">
                    <el-button size="small" @click="copyTemplate">
                      <el-icon><CopyDocument /></el-icon>
                      {{ t('config.copyTemplate') }}
                    </el-button>
                    <el-button size="small" type="danger" @click="deleteTemplate">
                      <el-icon><Delete /></el-icon>
                      {{ t('config.deleteTemplate') }}
                    </el-button>
                  </div>
                </div>
              </template>
              
              <el-form ref="templateFormRef" :model="currentTemplate" label-width="120px" class="template-form">
                <!-- 大纲模板 -->
                <el-form-item :label="t('config.outlineTemplate')">
                  <el-input
                    v-model="currentTemplate.outline_template"
                    type="textarea"
                    :rows="15"
                    :placeholder="t('config.outlineTemplatePlaceholder')"
                  />
                </el-form-item>
                
                <!-- 图片模板 -->
                <el-form-item :label="t('config.imageTemplate')">
                  <el-input
                    v-model="currentTemplate.image_template"
                    type="textarea"
                    :rows="15"
                    :placeholder="t('config.imageTemplatePlaceholder')"
                  />
                </el-form-item>
                
                <!-- 视频模板 -->
                <el-form-item :label="t('config.videoTemplate')">
                  <el-input
                    v-model="currentTemplate.video_template"
                    type="textarea"
                    :rows="15"
                    :placeholder="t('config.videoTemplatePlaceholder')"
                  />
                </el-form-item>
                
                
                
                <!-- 操作按钮 -->
                <div class="form-actions">
                  <el-button type="primary" @click="saveTemplate" :loading="saving" size="large">
                    <el-icon><Upload /></el-icon>
                    {{ t('common.save') }}
                  </el-button>
                  <el-button @click="resetTemplate" :loading="saving">
                    <el-icon><RefreshRight /></el-icon>
                    {{ t('common.reset') }}
                  </el-button>
                </div>
              </el-form>
            </el-card>
            
            <!-- 未选择平台提示 -->
            <el-empty
              v-else
              :description="t('config.noPlatformSelected')"
              :image-size="200"
            />
          </div>
        </el-tab-pane>
        
        <!-- AI提供商配置 -->
        <el-tab-pane :label="t('config.aiProviders')" name="providers">
          <div class="ai-config-container">
            
            <!-- 文本生成配置 -->
            <el-card shadow="hover" class="ai-config-card" style="margin-top: 20px;">
              <template #header>
                <div class="ai-config-header">
                  <h3>{{ t('config.textGeneration') }}</h3>
                  <p>{{ t('config.textGenerationDesc') }}</p>
                  <el-button type="primary" size="small" @click="openProviderDialog('text')">
                    <el-icon><Plus /></el-icon>
                    {{ t('common.add') }}
                  </el-button>
                </div>
              </template>
              
              <div class="provider-list">
                <div 
                  v-for="(provider, index) in textProviders" 
                  :key="index" 
                  class="provider-item"
                >
                  <div class="provider-header">
                    <div class="provider-info">
                      <el-tag :type="getProviderTypeColor(provider.type)">{{ provider.type }}</el-tag>
                      <span class="provider-name">{{ provider.name }}</span>
                    </div>
                    <div class="provider-actions">
              <el-button 
                size="small" 
                @click="testProviderConnection('text', provider)"
                :loading="testingProviders[`text_${provider.name}`]"
                :disabled="testingProviders[`text_${provider.name}`]"
              >
                <el-icon><Connection /></el-icon>
                {{ t('common.test') }}
              </el-button>
              <el-button size="small" @click="openProviderDialog('text', provider)">
                <el-icon><Edit /></el-icon>
                {{ t('common.edit') }}
              </el-button>
              <el-button size="small" @click="copyProvider('text', provider)">
                <el-icon><CopyDocument /></el-icon>
                {{ t('common.copy') }}
              </el-button>
              <el-button size="small" type="danger" @click="deleteProvider('text', provider.name)">
                <el-icon><Delete /></el-icon>
                {{ t('common.delete') }}
              </el-button>
            </div>
                  </div>
                  <div class="provider-config-item">
                    <span class="config-label">模型：</span>
                    <span class="config-value">{{ provider.model }}</span>
                  </div>
                  <div class="provider-config-item">
                    <span class="config-label">状态：</span>
                    <el-tag :type="getProviderStatusColor(provider.status)">
                      {{ getProviderStatusText(provider.status) }}
                    </el-tag>
                  </div>
                  <div class="provider-config-item">
                    <span class="config-label">启用：</span>
                    <el-switch v-model="provider.enabled" @change="toggleProviderEnabled('text', provider)" />
                  </div>
                </div>
                
                <el-empty v-if="textProviders.length === 0" :description="t('config.noTextProviders')" />
              </div>
            </el-card>
            
            <!-- 图片生成配置 -->
            <el-card shadow="hover" class="ai-config-card" style="margin-top: 20px;">
              <template #header>
                <div class="ai-config-header">
                  <h3>{{ t('config.imageGeneration') }}</h3>
                  <p>{{ t('config.imageGenerationDesc') }}</p>
                  <el-button type="primary" size="small" @click="openProviderDialog('image')">
                    <el-icon><Plus /></el-icon>
                    {{ t('common.add') }}
                  </el-button>
                </div>
              </template>
              
              <div class="provider-list">
                <div 
                  v-for="(provider, index) in imageProviders" 
                  :key="index" 
                  class="provider-item"
                >
                  <div class="provider-header">
                    <div class="provider-info">
                      <el-tag :type="getProviderTypeColor(provider.type)">{{ provider.type }}</el-tag>
                      <span class="provider-name">{{ provider.name }}</span>
                    </div>
                    <div class="provider-actions">
              <el-button 
                size="small" 
                @click="testProviderConnection('image', provider)"
                :loading="testingProviders[`image_${provider.name}`]"
                :disabled="testingProviders[`image_${provider.name}`]"
              >
                <el-icon><Connection /></el-icon>
                {{ t('common.test') }}
              </el-button>
              <el-button size="small" @click="openProviderDialog('image', provider)">
                <el-icon><Edit /></el-icon>
                {{ t('common.edit') }}
              </el-button>
              <el-button size="small" @click="copyProvider('image', provider)">
                <el-icon><CopyDocument /></el-icon>
                {{ t('common.copy') }}
              </el-button>
              <el-button size="small" type="danger" @click="deleteProvider('image', provider.name)">
                <el-icon><Delete /></el-icon>
                {{ t('common.delete') }}
              </el-button>
            </div>
                  </div>
                  <div class="provider-config-item">
                    <span class="config-label">模型：</span>
                    <span class="config-value">{{ provider.model }}</span>
                  </div>
                  <div class="provider-config-item">
                    <span class="config-label">状态：</span>
                    <el-tag :type="provider.status === 'connected' ? 'success' : 'warning'">
                      {{ provider.status === 'connected' ? t('common.connected') : t('common.disconnected') }}
                    </el-tag>
                  </div>
                  <div class="provider-config-item">
                    <span class="config-label">启用：</span>
                    <el-switch v-model="provider.enabled" @change="toggleProviderEnabled('image', provider)" />
                  </div>
                </div>
                
                <el-empty v-if="imageProviders.length === 0" :description="t('config.noImageProviders')" />
              </div>
            </el-card>
          </div>
        </el-tab-pane>
        
        <!-- 提供商编辑弹窗 -->
        <el-dialog
          v-model="providerDialogVisible"
          :title="isEditing ? t('config.editProvider') : t('config.addProvider')"
          width="600px"
        >
          <el-form ref="providerFormRef" :model="currentProvider" label-width="120px" class="provider-form">
            <el-form-item :label="t('config.type')" required>
              <el-select v-model="currentProvider.type" :placeholder="t('config.typePlaceholder')">
                <el-option label="OpenAI API" value="openai" />
                <el-option label="Google-Gemini" value="gemini" />
                <el-option label="SiliconFlow" value="siliconflow" />
                <el-option label="Generic Config" value="generic" />
              </el-select>
            </el-form-item>
            
            <el-form-item :label="t('config.providerName')" required>
              <el-input
                v-model="currentProvider.name"
                :placeholder="t('config.providerNamePlaceholder')"
              />
              <span class="help-text">{{ t('config.providerNameHelp') }}</span>
            </el-form-item>
            
            <el-form-item :label="t('config.apiKey')" required>
              <el-input
                v-model="currentProvider.api_key"
                type="password"
                show-password
                :placeholder="t('config.apiKeyPlaceholder')"
              />
            </el-form-item>
            
            <el-form-item :label="t('config.baseUrl')" required>
              <el-input
                v-model="currentProvider.base_url"
                :placeholder="t('config.baseUrlPlaceholder')"
              />
            </el-form-item>
            
            <el-form-item :label="t('config.model')" required>
              <el-input
                v-model="currentProvider.model"
                :placeholder="t('config.modelPlaceholder')"
              />
            </el-form-item>
            
            <el-form-item :label="t('config.apiEndpoint')" v-if="currentProvider.type === 'openai'">
              <el-input
                v-model="currentProvider.api_endpoint"
                :placeholder="t('config.apiEndpointPlaceholder')"
              />
              <span class="help-text">{{ t('config.apiEndpointHelp') }}</span>
            </el-form-item>
            
            <!-- 通用配置相关字段 -->
            <el-form-item :label="t('config.requestTemplate')" v-if="currentProvider.type === 'generic'">
              <el-input
                v-model="currentProvider.request_config.template"
                type="textarea"
                :rows="10"
                :placeholder="t('config.requestTemplatePlaceholder')"
              />
              <span class="help-text">{{ t('config.requestTemplateHelp') }}</span>
            </el-form-item>
            

            
            <el-form-item :label="t('config.maxOutputTokens')">
              <el-input-number
                v-model="currentProvider.max_output_tokens"
                :min="100"
                :max="100000"
                :step="100"
                :placeholder="t('config.maxOutputTokensPlaceholder')"
              />
              <span class="help-text">{{ t('config.maxOutputTokensHelp') }}</span>
            </el-form-item>
            
            <el-form-item :label="t('config.timeout')">
              <el-input-number
                v-model="currentProvider.timeout"
                :min="5"
                :max="300"
                :step="5"
                :placeholder="t('config.timeoutPlaceholder')"
              />
              <span class="help-text">{{ t('config.timeoutHelp') }}</span>
            </el-form-item>
            
            <el-form-item :label="t('config.enabled')">
              <el-switch v-model="currentProvider.enabled" />
              <span class="help-text">{{ t('config.enabledHelp') }}</span>
            </el-form-item>
            
            <!-- 图片提供商特有配置 -->
            <template v-if="providerType === 'image'">
              <!-- 参考图配置 -->
              <el-form-item :label="t('config.supportReferenceImage')">
                <el-switch v-model="currentProvider.support_reference_image" />
                <span class="help-text">{{ t('config.supportReferenceImageHelp') }}</span>
              </el-form-item>
              
              <el-form-item :label="t('config.referenceImageField')">
                <el-input
                  v-model="currentProvider.reference_image_field"
                  :placeholder="t('config.referenceImageFieldPlaceholder')"
                />
                <span class="help-text">{{ t('config.referenceImageFieldHelp') }}</span>
              </el-form-item>
              
              <el-form-item :label="t('config.supportMultipleReferenceImages')">
                <el-switch v-model="currentProvider.support_multiple_reference_images" />
                <span class="help-text">{{ t('config.supportMultipleReferenceImagesHelp') }}</span>
              </el-form-item>
              
              <!-- 支持的尺寸 - 所有类型提供商都显示 -->
              <el-form-item :label="t('config.supportedSizes')">
                <el-input
                  v-model="currentProvider.supported_sizes"
                  type="textarea"
                  :placeholder="t('config.supportedSizesPlaceholder')"
                  :rows="3"
                />
                <span class="help-text">{{ t('config.supportedSizesHelp') }}</span>
              </el-form-item>
              
              <!-- SiliconFlow特有配置 -->
              <template v-if="currentProvider.type === 'siliconflow'">
                <el-form-item :label="t('config.imageJsonPath')" required>
                  <el-input
                    v-model="currentProvider.image_jsonpath"
                    :placeholder="t('config.imageJsonPathPlaceholder')"
                  />
                  <span class="help-text">{{ t('config.imageJsonPathHelp') }}</span>
                </el-form-item>
                
                <el-form-item :label="t('config.returnFormat')" required>
                  <el-select v-model="currentProvider.return_format" :placeholder="t('config.returnFormatPlaceholder')">
                    <el-option label="URL链接" value="url" />
                    <el-option label="Base64编码" value="base64" />
                  </el-select>
                  <span class="help-text">{{ t('config.returnFormatHelp') }}</span>
                </el-form-item>
                
                <el-form-item :label="t('config.imageParameters')">
                  <el-input
                    v-model="currentProvider.image_parameters"
                    type="textarea"
                    :placeholder="t('config.imageParametersPlaceholder')"
                    :rows="4"
                  />
                  <span class="help-text">{{ t('config.imageParametersHelp') }}</span>
                </el-form-item>
              </template>
              
              <!-- OpenAI特有配置 -->
              <template v-if="currentProvider.type === 'openai'">
                <el-form-item :label="t('config.imageQuality')">
                  <el-select v-model="currentProvider.image_quality" :placeholder="t('config.imageQualityPlaceholder')">
                    <el-option label="标准质量" value="standard" />
                    <el-option label="高清质量" value="hd" />
                  </el-select>
                  <span class="help-text">{{ t('config.imageQualityHelp') }}</span>
                </el-form-item>
                
                <!-- 响应配置 -->
                <el-divider :content="t('config.responseConfig')" content-position="left" />
                
                <el-form-item :label="t('config.responseImagesPath')">
                  <el-input
                    v-model="currentProvider.response_config.images_path"
                    :placeholder="t('config.responseImagesPathPlaceholder')"
                  />
                  <span class="help-text">{{ t('config.responseImagesPathHelp') }}</span>
                </el-form-item>
                
                <el-form-item :label="t('config.responseUsagePath')">
                  <el-input
                    v-model="currentProvider.response_config.usage_path"
                    :placeholder="t('config.responseUsagePathPlaceholder')"
                  />
                  <span class="help-text">{{ t('config.responseUsagePathHelp') }}</span>
                </el-form-item>
                
                <el-form-item :label="t('config.responseErrorPath')">
                  <el-input
                    v-model="currentProvider.response_config.error_path"
                    :placeholder="t('config.responseErrorPathPlaceholder')"
                  />
                  <span class="help-text">{{ t('config.responseErrorPathHelp') }}</span>
                </el-form-item>
                
                <el-form-item :label="t('config.responseFormat')">
                  <el-select v-model="currentProvider.response_config.response_format" :placeholder="t('config.responseFormatPlaceholder')">
                    <el-option label="URL链接" value="url" />
                    <el-option label="Base64编码" value="base64" />
                  </el-select>
                  <span class="help-text">{{ t('config.responseFormatHelp') }}</span>
                </el-form-item>
              </template>
              
              <!-- Gemini特有配置 -->
              <template v-if="currentProvider.type === 'gemini'">
                <!-- 响应配置 -->
                <el-divider :content="t('config.responseConfig')" content-position="left" />
                
                <el-form-item :label="t('config.responseImagesPath')">
                  <el-input
                    v-model="currentProvider.response_config.images_path"
                    :placeholder="t('config.responseImagesPathPlaceholder')"
                  />
                  <span class="help-text">{{ t('config.responseImagesPathHelp') }}</span>
                </el-form-item>
                
                <el-form-item :label="t('config.responseUsagePath')">
                  <el-input
                    v-model="currentProvider.response_config.usage_path"
                    :placeholder="t('config.responseUsagePathPlaceholder')"
                  />
                  <span class="help-text">{{ t('config.responseUsagePathHelp') }}</span>
                </el-form-item>
                
                <el-form-item :label="t('config.responseErrorPath')">
                  <el-input
                    v-model="currentProvider.response_config.error_path"
                    :placeholder="t('config.responseErrorPathPlaceholder')"
                  />
                  <span class="help-text">{{ t('config.responseErrorPathHelp') }}</span>
                </el-form-item>
                
                <el-form-item :label="t('config.responseFormat')">
                  <el-select v-model="currentProvider.response_config.response_format" :placeholder="t('config.responseFormatPlaceholder')">
                    <el-option label="URL链接" value="url" />
                    <el-option label="Base64编码" value="base64" />
                  </el-select>
                  <span class="help-text">{{ t('config.responseFormatHelp') }}</span>
                </el-form-item>
              </template>
            </template>
          </el-form>
          
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="providerDialogVisible = false">{{ t('common.cancel') }}</el-button>
              <el-button type="primary" @click="testProviderConnection(providerType, currentProvider, true)" :loading="testingConnection">{{ t('config.testConnection') }}</el-button>
              <el-button type="primary" @click="saveProviderConfig" :loading="savingProvider">{{ t('common.save') }}</el-button>
            </span>
          </template>
        </el-dialog>
        
        <!-- 复制模板弹窗 -->
        <el-dialog
          v-model="copyTemplateVisible"
          :title="t('config.copyTemplate')"
          width="500px"
        >
          <el-form ref="copyTemplateFormRef" :model="copyTemplateForm" :rules="copyTemplateRules" label-width="120px" class="copy-template-form">
            <el-form-item :label="t('config.platformId')" prop="platformId" required>
              <el-input
                v-model="copyTemplateForm.platformId"
                :placeholder="t('config.platformIdPlaceholder')"
              />
            </el-form-item>
            
            <el-form-item :label="t('config.platformName')" prop="platformName" required>
              <el-input
                v-model="copyTemplateForm.platformName"
                :placeholder="t('config.platformNamePlaceholder')"
              />
            </el-form-item>
          </el-form>
          
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="copyTemplateVisible = false">{{ t('common.cancel') }}</el-button>
              <el-button type="primary" @click="handleCopyTemplate" :loading="copyingTemplate">{{ t('common.confirm') }}</el-button>
            </span>
          </template>
        </el-dialog>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

// 国际化
const { t } = useI18n()
import { Upload, RefreshRight, Refresh, Plus, Edit, Delete, Connection, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'

// 标签页状态
const activeTab = ref('templates')
const activeCollapse = ref(['title_style'])
const mysqlCollapse = ref(['mysql'])

// 加载状态
const saving = ref(false)
const loading = ref(false)

// 平台选择
const selectedPlatform = ref('xiaohongshu')
const platforms = ref<Array<{value: string, label: string}>>([
  { value: 'xiaohongshu', label: '小红书' },
  { value: 'douyin', label: '抖音' },
  { value: 'wechat', label: '微信' },
  { value: 'toutiao', label: '头条' }
])

// 模板配置
const templateFormRef = ref()
const currentTemplate = ref<any>(null)
const originalTemplate = ref<any>(null)

// 复制模板配置
const copyTemplateVisible = ref(false)
const copyTemplateFormRef = ref()
const copyingTemplate = ref(false)
const copyTemplateForm = reactive({
  platformId: '',
  platformName: ''
})

// 复制模板表单规则
const copyTemplateRules = {
  platformId: [
    { required: true, message: '请输入平台英文ID', trigger: 'blur' },
    { validator: (rule: any, value: any, callback: any) => {
      if (value === selectedPlatform.value) {
        callback(new Error('新平台英文ID不能与当前平台相同'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  platformName: [
    { required: true, message: '请输入平台中文名称', trigger: 'blur' }
  ]
}

// 加载所有平台列表
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
    
    platforms.value = platformList
  } catch (error) {
    console.error('加载平台列表失败:', error)
    // 加载失败时使用默认平台列表
  }
}

// 提供商配置
const textProviders = ref<any[]>([])
const imageProviders = ref<any[]>([])

// 提供商弹窗状态
const providerDialogVisible = ref(false)
const providerType = ref<'text' | 'image'>('text')
const isEditing = ref(false)
const originalProviderName = ref('') // 保存原始服务商名称，用于编辑时的URL参数
const currentProvider = ref<any>({
  name: '',
  type: 'openai',
  api_key: '',
  base_url: '',
  model: '',
  status: 'disconnected',
  enabled: true,
  timeout: 30,
  request_config: {
    template: ''
  },
  response_config: {
    images_path: '',
    usage_path: '',
    error_path: '',
    format_mapping: {
      url: 'url',
      base64: 'b64_json'
    }
  }
})
const providerFormRef = ref()
const testingConnection = ref(false)
const savingProvider = ref(false)

// 测试状态管理
const testingProviders = ref<Record<string, boolean>>({}) // 记录正在测试的服务商

// 通用设置
const generalFormRef = ref()
const generalConfig = ref<any>({
  redis_enabled: false,
  redis_url: 'redis://localhost:6379/0',
  redis_password: '',
  mysql_enabled: false,
  mysql_host: 'localhost',
  mysql_port: 3306,
  mysql_database: '',
  mysql_username: '',
  mysql_password: ''
})
const originalGeneralConfig = ref<any>(null)
const savingGeneral = ref(false)
// 测试连接状态
const testingRedis = ref(false)
const testingMysql = ref(false)



// 获取平台标签
const getPlatformLabel = (platform: string, platformConfig?: any) => {
  // 从平台配置中获取中文名称，如果没有则使用平台ID作为默认值
  return platformConfig?.name || platform
}



// 初始化
onMounted(() => {
  loadPlatforms()
  loadPlatformTemplate()
  loadProviders()
  loadGeneralConfig()
})

// 加载平台模板
const loadPlatformTemplate = async () => {
  if (!selectedPlatform.value) return
  
  loading.value = true
  try {
    const response = await axios.get(`/api/config/template/${selectedPlatform.value}`)
    if (response.data?.template) {
      // 深拷贝模板数据
      const template = JSON.parse(JSON.stringify(response.data.template))
      
      // 确保模板字段存在
      if (!template.outline_template) {
        template.outline_template = ''
      }
      if (!template.image_template) {
        template.image_template = ''
      }
      if (!template.video_template) {
        template.video_template = ''
      }
      
      currentTemplate.value = template
      originalTemplate.value = JSON.parse(JSON.stringify(template))
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载模板失败')
    console.error('加载模板失败:', error)
  } finally {
    loading.value = false
  }
}



// 保存模板配置
const saveTemplate = async () => {
  if (!selectedPlatform.value || !currentTemplate.value) return
  
  saving.value = true
  try {
    await axios.post(`/api/config/template/${selectedPlatform.value}`, currentTemplate.value)
    originalTemplate.value = JSON.parse(JSON.stringify(currentTemplate.value))
    ElMessage.success('配置保存成功')
    
    // 重新加载平台列表，确保新增的平台被正确加载
    await loadPlatforms()
    // 重新加载当前平台模板，确保数据最新
    await loadPlatformTemplate()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存配置失败')
    console.error('保存配置失败:', error)
  } finally {
    saving.value = false
  }
}

// 重置模板
const resetTemplate = () => {
  if (originalTemplate.value) {
    currentTemplate.value = JSON.parse(JSON.stringify(originalTemplate.value))
    ElMessage.info('配置已重置')
  }
}

// 删除模板
const deleteTemplate = () => {
  if (!selectedPlatform.value) {
    ElMessage.warning('请先选择一个平台')
    return
  }
  
  // 弹出确认对话框
  ElMessageBox.confirm(
    `确定要删除 ${getPlatformLabel(selectedPlatform.value, currentTemplate.value)} 平台的模板吗？删除后不可恢复。`,
    '删除模板',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true
    }
  )
  .then(async () => {
    try {
      // 调用删除API
      await axios.delete(`/api/config/template/${selectedPlatform.value}`)
      
      ElMessage.success('模板删除成功')
      
      // 重新加载平台列表
      await loadPlatforms()
      
      // 重置当前模板和选择的平台
      selectedPlatform.value = platforms.value[0]?.value || ''
      currentTemplate.value = null
      originalTemplate.value = null
      
      // 如果还有平台，加载第一个平台的模板
      if (selectedPlatform.value) {
        await loadPlatformTemplate()
      }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '删除模板失败')
      console.error('删除模板失败:', error)
    }
  })
  .catch(() => {
    // 取消删除
  })
}

// 打开复制模板弹窗
const copyTemplate = () => {
  // 初始化表单数据
  copyTemplateForm.platformId = selectedPlatform.value
  copyTemplateForm.platformName = getPlatformLabel(selectedPlatform.value, currentTemplate.value)
  // 打开弹窗
  copyTemplateVisible.value = true
}

// 处理复制模板
const handleCopyTemplate = async () => {
  // 验证表单
  if (!copyTemplateFormRef.value) return
  
  try {
    await copyTemplateFormRef.value.validate()
    
    copyingTemplate.value = true
    
    // 复制当前模板数据
    const templateCopy = JSON.parse(JSON.stringify(currentTemplate.value))
    
    // 添加平台中文名称到模板配置
    templateCopy.name = copyTemplateForm.platformName
    
    // 保存到新平台
    await axios.post(`/api/config/template/${copyTemplateForm.platformId}`, templateCopy)
    
    // 关闭弹窗
    copyTemplateVisible.value = false
    
    // 重新加载平台列表
    await loadPlatforms()
    
    ElMessage.success(`模板已成功复制到${copyTemplateForm.platformName}（${copyTemplateForm.platformId}）平台`)
  } catch (error: any) {
    if (error.name === 'ValidateError') {
      // 表单验证失败，已经显示错误提示
      return
    }
    
    ElMessage.error(error.response?.data?.detail || '复制模板失败')
    console.error('复制模板失败:', error)
  } finally {
    copyingTemplate.value = false
  }
}

// 加载提供商配置
const loadProviders = async () => {
  loading.value = true
  try {
    // 加载文本提供商
    const textResponse = await axios.get('/api/config/providers/text')
    if (textResponse.data?.providers?.providers) {
      textProviders.value = Object.entries(textResponse.data.providers.providers).map(([name, provider]: [string, any]) => ({
        name,
        type: provider.type || 'openai',
        model: provider.model,
        status: 'disconnected', // 默认为未连接，需要测试
        enabled: provider.enabled !== undefined ? provider.enabled : true, // 默认启用
        timeout: provider.timeout !== undefined ? provider.timeout : 30, // 默认30秒
        request_config: provider.request_config || { template: '' },
        response_config: provider.response_config || { images_path: '', usage_path: '', error_path: '' },
        ...provider
      }))
    }
    
    // 加载图像提供商
    const imageResponse = await axios.get('/api/config/providers/image')
    if (imageResponse.data?.providers?.providers) {
      imageProviders.value = Object.entries(imageResponse.data.providers.providers).map(([name, provider]: [string, any]) => {
        // 深拷贝提供商数据
        const providerCopy = {
          name,
          type: provider.type || 'openai',
          model: provider.model,
          status: 'disconnected', // 默认为未连接，需要测试
          enabled: provider.enabled !== undefined ? provider.enabled : true, // 默认启用
          timeout: provider.timeout !== undefined ? provider.timeout : 30, // 默认30秒
          request_config: provider.request_config || { template: '' },
          response_config: provider.response_config || { images_path: '', usage_path: '', error_path: '' },
          ...provider
        }
        
        // 如果supported_sizes是数组，转换为JSON字符串显示
        if (Array.isArray(providerCopy.supported_sizes)) {
          providerCopy.supported_sizes = JSON.stringify(providerCopy.supported_sizes, null, 2)
        } else if (providerCopy.supported_sizes === undefined || providerCopy.supported_sizes === null) {
          // 如果不存在，设置为默认尺寸数组的JSON字符串
          providerCopy.supported_sizes = JSON.stringify(["1024x1024", "1056x1584", "1584x1056"], null, 2)
        }
        
        return providerCopy
      })
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载提供商配置失败')
    console.error('加载提供商配置失败:', error)
  } finally {
    loading.value = false
  }
}

// 打开提供商对话框
const openProviderDialog = (type: 'text' | 'image', provider?: any) => {
  providerType.value = type
  isEditing.value = !!provider
  originalProviderName.value = ''
  
  if (provider) {
      // 深拷贝提供商数据
      const providerCopy = JSON.parse(JSON.stringify(provider))
      
      // 如果supported_sizes是数组，转换为JSON字符串显示
      if (providerCopy.supported_sizes && Array.isArray(providerCopy.supported_sizes)) {
        providerCopy.supported_sizes = JSON.stringify(providerCopy.supported_sizes, null, 2)
      }
      
      currentProvider.value = providerCopy
      originalProviderName.value = provider.name // 保存原始服务商名称
    } else {
      // 重置表单
      currentProvider.value = {
        name: '',
        type: 'openai',
        api_key: '',
        base_url: '',
        model: '',
        api_endpoint: '',
        max_output_tokens: 8000,
        status: 'disconnected',
        enabled: true,
        timeout: 30,
        supported_sizes: JSON.stringify(["1024x1024", "1056x1584", "1584x1056"], null, 2), // 默认尺寸
        request_config: {
          template: ''
        },
        response_config: {
          images_path: '',
          usage_path: '',
          error_path: '',
          format_mapping: {
            url: 'url',
            base64: 'b64_json'
          }
        }
      }
    }
  
  providerDialogVisible.value = true
}

// 统一的测试连接函数
const testProviderConnection = async (
  type: any,
  provider: any,
  isEditingMode: boolean = false
) => {
  // 解包ref对象
  const resolvedType = typeof type === 'object' && type.value !== undefined ? type.value : type
  const resolvedProvider = typeof provider === 'object' && provider.value !== undefined ? provider.value : provider
  
  // 检查provider是否有效
  if (!resolvedProvider || !resolvedProvider.name) {
    ElMessage.error('提供商配置无效，缺少名称字段')
    return
  }
  
  const providerKey = `${resolvedType}_${resolvedProvider.name}`
  
  // 显示加载状态
  if (isEditingMode) {
    testingConnection.value = true
  } else {
    // 更新列表中提供商的状态为测试中
    const providersList = resolvedType === 'text' ? textProviders.value : imageProviders.value
    const providerIndex = providersList.findIndex(p => p.name === resolvedProvider.name)
    if (providerIndex !== -1) {
      providersList[providerIndex].status = 'testing'
      testingProviders.value[providerKey] = true
    }
  }
  
  try {
    // 调用后端API测试连接
    // 在编辑模式下，我们发送提供商配置进行测试，而不是依赖已保存的配置
    const response = await axios.post(
      isEditingMode 
        ? `/api/config/provider/test/${resolvedType}` 
        : `/api/config/provider/test/${resolvedType}/${resolvedProvider.name}`,
      isEditingMode ? resolvedProvider : undefined
    )
    
    if (response.data?.success) {
      // 测试成功处理
      const successMsg = isEditingMode 
        ? '连接测试成功'
        : `服务商 ${resolvedProvider.name} 连接测试成功`
      ElMessage.success({
        message: successMsg,
        duration: 3000
      })
      
      if (isEditingMode) {
        currentProvider.value.status = 'connected'
      } else {
        const providersList = resolvedType === 'text' ? textProviders.value : imageProviders.value
        const providerIndex = providersList.findIndex(p => p.name === resolvedProvider.name)
        if (providerIndex !== -1) {
          providersList[providerIndex].status = 'connected'
        }
      }
    } else {
      // 测试失败处理
      const errorMsg = isEditingMode 
        ? '连接测试失败'
        : `服务商 ${resolvedProvider.name} 连接测试失败`
      ElMessage.error({
        message: errorMsg,
        duration: 4000
      })
      
      if (isEditingMode) {
        currentProvider.value.status = 'disconnected'
      } else {
        const providersList = resolvedType === 'text' ? textProviders.value : imageProviders.value
        const providerIndex = providersList.findIndex(p => p.name === resolvedProvider.name)
        if (providerIndex !== -1) {
          providersList[providerIndex].status = 'disconnected'
        }
      }
    }
  } catch (error: any) {
    // 异常处理
    const errorDetail = error.response?.data?.detail || '未知错误'
    const errorMsg = isEditingMode 
      ? `连接测试失败: ${errorDetail}`
      : `服务商 ${resolvedProvider.name} 连接测试失败: ${errorDetail}`
    ElMessage.error({
      message: errorMsg,
      duration: 4000
    })
    
    if (isEditingMode) {
      currentProvider.value.status = 'disconnected'
    } else {
      const providersList = resolvedType === 'text' ? textProviders.value : imageProviders.value
      const providerIndex = providersList.findIndex(p => p.name === resolvedProvider.name)
      if (providerIndex !== -1) {
        providersList[providerIndex].status = 'disconnected'
      }
    }
  } finally {
    if (isEditingMode) {
      testingConnection.value = false
    } else {
      delete testingProviders.value[providerKey]
    }
  }
}

// 保存提供商配置
const saveProviderConfig = async () => {
  // 表单验证
  if (!currentProvider.value.name || !currentProvider.value.api_key || !currentProvider.value.base_url || !currentProvider.value.model) {
    ElMessage.error(t('config.fillCompleteProviderConfig'))
    return
  }
  
  savingProvider.value = true
  try {
    // 编辑模式下使用原始名称作为URL参数，新增模式下使用新名称
    const providerUrlName = isEditing.value ? originalProviderName.value : currentProvider.value.name
    
    // 深拷贝当前配置，避免修改原始数据
    const providerConfig = JSON.parse(JSON.stringify(currentProvider.value))
    
    // 处理supported_sizes字段，确保它是JSON数组
    if (providerConfig.supported_sizes) {
      try {
        // 如果是字符串，解析为JSON数组
        if (typeof providerConfig.supported_sizes === 'string') {
          providerConfig.supported_sizes = JSON.parse(providerConfig.supported_sizes)
        }
      } catch (e) {
        ElMessage.error(t('config.supportedSizesFormatError'))
        savingProvider.value = false
        return
      }
    }
    
    const response = await axios.post(`/api/config/provider/${providerType.value}/${providerUrlName}`, {
      ...providerConfig
      // 名称需要保存到配置中，以便支持重命名
    })
    
    ElMessage.success('提供商配置保存成功')
    providerDialogVisible.value = false
    loadProviders() // 重新加载配置
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存提供商配置失败')
    console.error('保存提供商配置失败:', error)
  } finally {
    savingProvider.value = false
  }
}

// 切换提供商启用状态
const toggleProviderEnabled = async (type: 'text' | 'image', provider: any) => {
  try {
    // 调用后端API更新启用状态
    await axios.post(`/api/config/provider/${type}/${provider.name}`, {
      ...provider
    })
    ElMessage.success(`提供商 ${provider.name} ${provider.enabled ? '已启用' : '已禁用'}`)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新启用状态失败')
    console.error('更新启用状态失败:', error)
    // 恢复原来的状态
    provider.enabled = !provider.enabled
  }
}

// 删除提供商
const deleteProvider = async (type: 'text' | 'image', name: string) => {
  try {
    await ElMessageBox.confirm(`确定要删除提供商 ${name} 吗？`, '删除提供商', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/api/config/provider/${type}/${name}`)
    ElMessage.success('提供商删除成功')
    loadProviders() // 重新加载配置
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除提供商失败')
      console.error('删除提供商失败:', error)
    }
  }
}

// 复制提供商
const copyProvider = (type: 'text' | 'image', provider: any) => {
  // 深拷贝提供商数据
  const providerCopy = JSON.parse(JSON.stringify(provider))
  
  // 自动为名称添加"-复制"后缀
  let newName = `${provider.name}-复制`
  
  // 检查是否已存在相同名称，存在则添加数字后缀
  const providersList = type === 'text' ? textProviders.value : imageProviders.value
  let copyCount = 1
  while (providersList.some(p => p.name === newName)) {
    copyCount++
    newName = `${provider.name}-复制${copyCount}`
  }
  
  providerCopy.name = newName
  providerCopy.status = 'disconnected' // 重置状态
  
  // 打开编辑对话框，填充复制的数据
  openProviderDialog(type, providerCopy)
}

// 获取提供商类型颜色
const getProviderTypeColor = (type: string) => {
  const colorMap: Record<string, any> = {
    openai: 'primary',
    gemini: 'success',
    siliconflow: 'warning',
    generic: 'info'
  }
  return colorMap[type] || 'info'
}

// 获取提供商状态颜色
const getProviderStatusColor = (status: string) => {
  const colorMap: Record<string, any> = {
    connected: 'success',
    disconnected: 'warning',
    testing: 'info'
  }
  return colorMap[status] || 'warning'
}

// 获取提供商状态文本
const getProviderStatusText = (status: string) => {
  const textMap: Record<string, any> = {
    connected: t('common.connected'),
    disconnected: t('common.disconnected'),
    testing: t('common.testing')
  }
  return textMap[status] || t('common.unknownStatus')
}

// 加载通用配置
const loadGeneralConfig = async () => {
  loading.value = true
  try {
    // 调用后端的通用配置API获取实际配置
    const response = await axios.get('/api/config/general')
    if (response.data?.config) {
      generalConfig.value = response.data.config
      originalGeneralConfig.value = JSON.parse(JSON.stringify(generalConfig.value))
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载通用配置失败')
    console.error('加载通用配置失败:', error)
  } finally {
    loading.value = false
  }
}

// 保存通用配置
const saveGeneralConfig = async () => {
  savingGeneral.value = true
  try {
    // 调用后端的保存通用配置API
    const response = await axios.post('/api/config/general', generalConfig.value)
    if (response.data?.message) {
      originalGeneralConfig.value = JSON.parse(JSON.stringify(generalConfig.value))
      ElMessage.success(response.data.message)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存通用配置失败')
    console.error('保存通用配置失败:', error)
  } finally {
    savingGeneral.value = false
  }
}

// 重置通用配置
const resetGeneralConfig = () => {
  if (originalGeneralConfig.value) {
    generalConfig.value = JSON.parse(JSON.stringify(originalGeneralConfig.value))
    ElMessage.info('通用配置已重置')
  }
}

// 测试Redis连接
const testRedisConnection = async () => {
  testingRedis.value = true
  try {
    const response = await axios.post('/api/config/test/redis', generalConfig.value)
    if (response.data?.success) {
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data.message || 'Redis连接测试失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || 'Redis连接测试失败')
    console.error('测试Redis连接失败:', error)
  } finally {
    testingRedis.value = false
  }
}

// 测试MySQL连接
const testMysqlConnection = async () => {
  testingMysql.value = true
  try {
    const response = await axios.post('/api/config/test/mysql', generalConfig.value)
    if (response.data?.success) {
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data.message || 'MySQL连接测试失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || 'MySQL连接测试失败')
    console.error('测试MySQL连接失败:', error)
  } finally {
    testingMysql.value = false
  }
}



</script>

<style scoped lang="scss">
.config-container {
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

.config-tabs {
  margin-top: 16px;
}

.card-subtitle {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.template-config {
  padding: 16px 0;
}

.format-mapping-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.format-mapping-config {
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  margin-bottom: 8px;
}

.template-card {
  margin-top: 16px;
  border-radius: 8px;
}

.template-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-actions {
  display: flex;
  gap: 8px;
}

.template-form {
  max-width: 800px;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-start;
}

.provider-tabs {
  margin-top: 16px;
}

.provider-config {
  padding: 16px 0;
}

.reload-btn {
  margin-bottom: 16px;
}

.provider-table {
  margin-top: 8px;
  
  .el-table__header-wrapper {
    background-color: var(--el-bg-color-page);
  }
  
  .el-table__body-wrapper {
    max-height: 500px;
    overflow-y: auto;
  }
}

/* AI配置样式 */
.ai-config-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-config-card {
  border-radius: 8px;
  overflow: hidden;
}

.ai-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.ai-config-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.ai-config-header p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.provider-item {
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.provider-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.provider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.provider-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.provider-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.provider-actions {
  display: flex;
  gap: 8px;
}

.provider-config-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.config-label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.config-value {
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.help-text {
  margin-left: 12px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}




</style>
