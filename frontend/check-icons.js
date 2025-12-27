// 检查Element Plus Icons中可用的图标
import * as ElementIcons from '@element-plus/icons-vue'

console.log('Available Element Plus Icons:')
console.log(Object.keys(ElementIcons))

// 查找与语言相关的图标
const languageRelatedIcons = Object.keys(ElementIcons).filter(iconName => 
  iconName.toLowerCase().includes('language') ||
  iconName.toLowerCase().includes('translation') ||
  iconName.toLowerCase().includes('globe') ||
  iconName.toLowerCase().includes('world') ||
  iconName.toLowerCase().includes('locale') ||
  iconName.toLowerCase().includes('i18n')
)

console.log('\nLanguage-related icons:')
console.log(languageRelatedIcons)

// 查找一些可能适合的替代图标
const alternativeIcons = Object.keys(ElementIcons).filter(iconName => 
  iconName.toLowerCase().includes('setting') ||
  iconName.toLowerCase().includes('tool') ||
  iconName.toLowerCase().includes('menu') ||
  iconName.toLowerCase().includes('more')
)

console.log('\nAlternative icons that might work:')
console.log(alternativeIcons.slice(0, 10)) // 只显示前10个