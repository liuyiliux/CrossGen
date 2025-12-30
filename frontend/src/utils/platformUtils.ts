/**
 * 平台名称映射工具
 * 用于将平台英文名称映射为中文显示名称
 */

import axios from 'axios'

// 平台名称映射表，动态从后端获取
let platformLabels: Record<string, string> = {}
// 平台类型映射表，动态从后端获取
let platformTypes: Record<string, string> = {}
// 加载状态
let isLoaded = false

/**
 * 从后端加载平台配置
 */
export const loadPlatformConfig = async (): Promise<void> => {
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
    
    // 构建平台名称映射表
    const newPlatformLabels: Record<string, string> = {}
    const newPlatformTypes: Record<string, string> = {}
    
    // 遍历模板键，构建映射表
    Object.entries(platformTemplates).forEach(([key, template]: [string, any]) => {
      // 从模板配置中获取平台中文名称，如果没有则使用键作为标签
      newPlatformLabels[key] = template?.name || key
      // 设置默认平台类型
      newPlatformTypes[key] = template?.type || 'info'
    })
    
    // 更新映射表
    platformLabels = newPlatformLabels
    platformTypes = newPlatformTypes
    isLoaded = true
    
    console.log('平台配置加载成功:', platformLabels)
  } catch (error) {
    console.error('加载平台配置失败:', error)
    // 加载失败时，使用默认映射表
    platformLabels = {
      xiaohongshu: '小红书',
      douyin: '抖音',
      wechat: '微信',
      toutiao: '头条',
      ceshi: '测试平台'
    }
    platformTypes = {
      xiaohongshu: 'primary',
      douyin: 'success',
      wechat: 'warning',
      toutiao: 'info',
      ceshi: 'primary'
    }
  }
}

/**
 * 获取平台中文显示名称
 * @param platform 平台英文名称
 * @returns 平台中文显示名称
 */
export const getPlatformLabel = (platform: string | null | undefined): string => {
  if (!platform) return '未知平台'
  return platformLabels[platform] || platform
}

/**
 * 获取平台对应的标签类型
 * @param platform 平台英文名称
 * @returns Element Plus 标签类型
 */
export const getPlatformType = (platform: string | null | undefined): string => {
  if (!platform) return 'info'
  return platformTypes[platform] || 'info'
}

/**
 * 获取所有平台选项，用于动态生成平台选择下拉框的选项
 * @returns 平台选项数组
 */
export const getPlatformOptions = (): { label: string; value: string }[] => {
  return Object.entries(platformLabels).map(([value, label]) => ({
    label,
    value
  }))
}

/**
 * 获取平台配置加载状态
 * @returns 是否已加载
 */
export const isPlatformConfigLoaded = (): boolean => {
  return isLoaded
}

/**
 * 手动更新平台映射表（用于开发调试）
 * @param newLabels 新的平台名称映射表
 */
export const updatePlatformLabels = (newLabels: Record<string, string>): void => {
  platformLabels = { ...platformLabels, ...newLabels }
}

/**
 * 手动更新平台类型映射表（用于开发调试）
 * @param newTypes 新的平台类型映射表
 */
export const updatePlatformTypes = (newTypes: Record<string, string>): void => {
  platformTypes = { ...platformTypes, ...newTypes }
}