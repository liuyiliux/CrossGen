// i18n 配置文件
import { createI18n } from 'vue-i18n'
import zhCnLocale from './zh-CN'
import enLocale from './en'

// Element Plus 语言包
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'

// 本地存储的语言键名
const LANG_KEY = 'app-language'

// 获取本地存储的语言，默认为中文
const getLocale = () => {
  return localStorage.getItem(LANG_KEY) || 'zh-CN'
}

// 设置本地存储的语言
const setLocale = (lang: string) => {
  localStorage.setItem(LANG_KEY, lang)
}

// 语言包合并，包含 Element Plus 的语言包
const messages = {
  'zh-CN': {
    ...zhCnLocale,
    el: zhCn.el
  },
  'en': {
    ...enLocale,
    el: en.el
  }
}

// 创建 i18n 实例
const i18n = createI18n({
  legacy: false, // 使用 Composition API，必须设置为 false
  locale: getLocale(), // 设置初始语言
  fallbackLocale: 'zh-CN', // 回退语言
  messages // 语言包
})

export {
  i18n,
  getLocale,
  setLocale
}
