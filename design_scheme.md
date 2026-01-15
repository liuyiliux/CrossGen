# 图文内容生成实现文档

## 1. 需求分析

用户希望生成的大纲支持以下结构：
- **一个总标题**：整个图文内容的标题
- **一个总文案**：整个图文内容的主体文案（最好带#话题）
- **多个图片提示词**：每个图片对应一个提示词，用`<page>`标签分割

这种结构类似于小红书和抖音的图文关系，即一个标题和文案对应多张图片。

### 1.1 灵感获取功能需求

新增灵感获取功能，允许用户：
- 搜索小红书热门图文内容
- 获取创作灵感和参考
- 查看热门主题和内容结构
- 直接使用搜索结果作为创作参考

### 1.2 灵感页面功能
- 🔍 关键词搜索功能
- 📱 小红书链接解析功能
- 📊 搜索结果展示（图文列表）
- 💡 空状态和错误提示
- 🔄 重试机制
- 🎨 紫色主题设计风格

### 1.3 灵感卡片展示
- 🖼️ 缩略图预览
- 📝 标题和描述
- 👍 点赞数和互动数据
- 📱 平台标识
- 🔄 刷新按钮
- 🔗 链接按钮

### 1.4 国际化支持
- 🌐 中文和英文双语支持
- 📝 统一的重试文本配置
- 🎯 优化错误提示文本
- 📋 搜索失败提示文本

### 1.5 样式设计
- 🎨 紫色渐变背景（#673AB7）
- 📐 响应式布局
- 💎 图标使用（EditPen替代Lightbulb）
- 📱 移动端适配
- 🎨 空状态和错误状态的视觉优化

## 2. 实现状态

✅ **已完成实现**
- [x] 后端数据模型修改
- [x] 前端数据模型修改
- [x] 平台模板更新
- [x] 大纲生成服务的解析逻辑更新
- [x] 前端OutlineView更新
- [x] 同步逻辑更新
- [x] 所有平台模板更新
- [x] 灵感获取功能实现
- [x] 灵感页面UI设计
- [x] 国际化配置完善
- [x] 样式优化和主题设计
- [x] 错误处理和重试机制

## 2. 实现状态

✅ **已完成实现**

- [x] 后端数据模型修改
- [x] 前端数据模型修改
- [x] 平台模板更新
- [x] 大纲生成服务的解析逻辑更新
- [x] 前端OutlineView更新
- [x] 同步逻辑更新
- [x] 所有平台模板更新

## 3. 数据结构设计

### 3.1 后端数据模型

修改 `Outline` 模型，增加标题和文案字段，而 `Page` 模型只保留图片提示词相关字段：

```python
class Outline(BaseModel):
    """大纲数据模型"""
    raw: str
    title: Optional[str] = None        # 总标题
    copywriting: Optional[str] = None  # 总文案
    pages: List[Page] = []

class Page(BaseModel):
    """页面数据模型"""
    index: int
    type: str
    content: str
    image_prompt: Optional[str] = None  # 单张图片提示词
```

### 3.2 前端数据模型

```typescript
interface Page {
  index: number
  type: 'cover' | 'content' | 'summary'
  content: string
  image_prompt?: string  // 单张图片提示词
}

interface GeneratorState {
  // ... 其他字段
  outline: {
    raw: string
    title?: string          // 总标题
    copywriting?: string    // 总文案
    pages: Page[]
  }
  // ... 其他字段
}
```

## 4. 实现方案

### 4.1 平台模板更新

更新 `platform_templates.yaml` 中的所有平台模板，要求AI生成包含总标题、总文案和多个图片提示词的内容。

**反推平台模板示例**：

```yaml
fantui:
  name: 反推
  outline_template: '你是一个图片创作高手。用户会给你一个要求以及说明，你需要生成包含一个标题、一个文案和多个图片提示词的内容。
    # ... 模板内容
  image_template: '{full_outline}'
  video_template: '请生成一个适合小红书的短视频脚本，根据以下主题和大纲：
    # ... 模板内容
```

### 4.2 大纲生成服务的解析逻辑

更新 `generation_service.py` 中的解析逻辑，支持从AI生成的内容中提取总标题、总文案和多个图片提示词：

```python
# 解析AI生成的内容，提取总标题、总文案和多个图片提示词
def parse_generated_content(generated_text):
    # 初始化结果
    title = ""
    copywriting = ""
    image_prompts = []
    
    # 查找总标题
    title_match = re.search(r'【标题】：(.*?)\n(?=【文案】：|$)', generated_text, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
    
    # 查找总文案
    copywriting_match = re.search(r'【文案】：(.*?)\n(?=【图片提示词】：|$)', generated_text, re.DOTALL)
    if copywriting_match:
        copywriting = copywriting_match.group(1).strip()
    
    # 提取所有图片提示词部分（从第一个【图片提示词】：开始）
    image_prompts_section = generated_text
    image_start_match = re.search(r'【图片提示词】：', generated_text)
    if image_start_match:
        image_prompts_section = generated_text[image_start_match.start():]
    
    # 按<page>标签分割图片提示词
    page_sections = image_prompts_section.split('<page>')
    
    for section in page_sections:
        section = section.strip()
        if not section:
            continue
        
        # 提取当前页面的图片提示词
        image_prompt_match = re.search(r'【图片提示词】：(.*?)(?=\n<page>|$)', section, re.DOTALL)
        if image_prompt_match:
            image_prompt = image_prompt_match.group(1).strip()
            if image_prompt:
                image_prompts.append(image_prompt)
    
    return title, copywriting, image_prompts
```

### 4.3 前端Generator Store更新

更新 `generator.ts` 中的状态管理，添加标题和文案字段：

### 4.4 灵感获取功能实现

#### 4.4.1 灵感页面组件
- `InspirationView.vue`：灵感搜索页面
- 搜索功能：关键词搜索和小红书链接解析
- 结果展示：图文卡片列表
- 空状态和错误提示
- 重试机制

#### 4.4.2 灵感卡片组件
- `InspirationCard.vue`：灵感卡片展示组件
- 图片展示：缩略图预览
- 信息展示：标题、描述、点赞数
- 交互功能：链接跳转、刷新

#### 4.4.3 状态管理
- `inspirationStore.ts`：灵感获取状态管理
- 搜索状态：loading、error、results
- 搜索参数：关键词、页码
- 结果缓存：避免重复请求

#### 4.4.4 API服务
- `inspiration_service.ts`：灵感获取API服务
- 搜索API：关键词搜索
- 解析API：小红书链接解析
- 错误处理：网络错误、解析错误

#### 4.4.5 样式设计
- 紫色主题：`--xhs-accent-purple` 颜色变量
- 卡片样式：阴影、渐变背景
- 响应式布局：移动端适配
- 空状态：友好的提示文本

### 4.4 灵感页面UI设计

#### 4.4.1 搜索区域
```html
<!-- 搜索框 -->
<div class="search-container">
  <el-input
    v-model="searchKeyword"
    placeholder="输入关键词搜索小红书相关图文内容"
    size="large"
    clearable
    @keyup.enter="handleSearch"
  />
  <el-button type="primary" @click="handleSearch">搜索</el-button>
</div>

<!-- 链接解析区域 -->
<div class="parse-container">
  <el-input
    v-model="parseUrl"
    placeholder="粘贴小红书笔记链接"
    size="large"
    clearable
  />
  <el-button type="primary" @click="handleParse">解析链接</el-button>
</div>
```

#### 4.4.2 结果展示区域
```html
<!-- 搜索结果列表 -->
<div class="results-container">
  <el-row :gutter="20">
    <el-col :span="6" v-for="item in results" :key="item.id">
      <div class="inspiration-card">
        <img :src="item.image" alt="" class="card-image" />
        <div class="card-info">
          <h3 class="card-title">{{ item.title }}</h3>
          <p class="card-desc">{{ item.description }}</p>
          <div class="card-meta">
            <span class="likes">{{ formatNumber(item.likes) }} 点赞</span>
            <span class="platform">{{ item.platform }}</span>
          </div>
          <div class="card-actions">
            <el-button type="primary" size="small" @click="handleView(item)">查看</el-button>
            <el-button size="small" @click="handleRefresh(item)">刷新</el-button>
          </div>
        </div>
      </div>
    </el-col>
  </el-row>
</div>
```

#### 4.4.3 空状态和错误提示
```html
<!-- 空状态 -->
<div v-if="isEmptyState" class="empty-state">
  <el-icon class="empty-icon"><Document /></el-icon>
  <h3>{{ t('inspiration.noResultsTitle') }}</h3>
  <p>{{ t('inspiration.noResultsHint') }}</p>
  <el-button type="primary" @click="handleRetry">{{ t('common.retry') }}</el-button>
</div>

<!-- 错误提示 -->
<div v-if="hasError" class="error-alert">
  <el-icon class="error-icon"><Error /></el-icon>
  <div class="error-content">
    <p>{{ t('inspiration.searchFailed') }}</p>
    <el-button type="danger" @click="handleRetry">{{ t('common.retry') }}</el-button>
  </div>
</div>
```

### 4.5 样式设计

#### 4.5.1 灵感卡片样式
```scss
.inspiration-card {
  border-radius: var(--xhs-radius-lg);
  overflow: hidden;
  box-shadow: var(--xhs-shadow-sm);
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
  }
  
  .card-image {
    width: 100%;
    height: 180px;
    object-fit: cover;
  }
  
  .card-info {
    padding: var(--xhs-space-lg);
    background: var(--xhs-bg-secondary);
    
    .card-title {
      font-size: var(--xhs-text-lg);
      font-weight: 600;
      margin-bottom: var(--xhs-space-sm);
      color: var(--xhs-text-primary);
    }
    
    .card-desc {
      font-size: var(--xhs-text-sm);
      color: var(--xhs-text-secondary);
      margin-bottom: var(--xhs-space-md);
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .card-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--xhs-space-md);
      
      .likes {
        font-size: var(--xhs-text-sm);
        color: var(--xhs-text-secondary);
      }
      
      .platform {
        font-size: var(--xhs-text-xs);
        background: var(--xhs-accent-purple);
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
      }
    }
    
    .card-actions {
      display: flex;
      gap: var(--xhs-space-sm);
    }
  }
}
```

#### 4.5.2 空状态样式
```scss
.empty-state {
  max-width: 800px;
  margin: var(--xhs-space-4xl) auto;
  text-align: center;
  padding: var(--xhs-space-2xl);
  
  .empty-icon {
    font-size: 4rem;
    color: var(--xhs-text-secondary);
    margin-bottom: var(--xhs-space-lg);
  }
  
  h3 {
    font-size: var(--xhs-text-xl);
    color: var(--xhs-text-primary);
    margin-bottom: var(--xhs-space-md);
  }
  
  p {
    font-size: var(--xhs-text-base);
    color: var(--xhs-text-secondary);
    max-width: 500px;
    margin: 0 auto var(--xhs-space-xl);
    line-height: var(--xhs-leading-relaxed);
  }
}
```

#### 4.5.3 错误提示样式
```scss
.error-alert {
  max-width: 800px;
  margin: var(--xhs-space-3xl) auto;
  border-radius: var(--xhs-radius-xl);
  background: var(--xhs-bg-danger);
  color: white;
  padding: var(--xhs-space-xl);
  text-align: center;
  
  .error-icon {
    font-size: 3rem;
    margin-bottom: var(--xhs-space-lg);
  }
  
  .error-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--xhs-space-md);
    
    p {
      font-size: var(--xhs-text-base);
      margin: 0;
    }
  }
}
```

### 4.6 国际化配置

#### 4.6.1 中文配置
```typescript
inspiration: {
  title: '灵感获取',
  subtitle: '搜索小红书热门图文，获取创作灵感',
  search: '搜索',
  parse: '解析链接',
  searchPlaceholder: '输入关键词搜索小红书相关图文内容',
  parsePlaceholder: '粘贴小红书笔记链接',
  noResultsTitle: '暂无搜索结果',
  noResultsHint: '试试其他关键词或直接输入笔记链接',
  searchFailed: '搜索失败，请重试',
  loading: '加载中...',
  refresh: '刷新'
}
```

#### 4.6.2 英文配置
```typescript
inspiration: {
  title: 'Inspiration',
  subtitle: 'Search trending content for creative ideas',
  search: 'Search',
  parse: 'Parse Link',
  searchPlaceholder: 'Enter keywords to search Xiaohongshu related content',
  parsePlaceholder: 'Paste Xiaohongshu note link',
  noResultsTitle: 'No results found',
  noResultsHint: 'Try different keywords or directly enter a note link',
  searchFailed: 'Search failed, please retry',
  loading: 'Loading...',
  refresh: 'Refresh'
}
```

### 4.7 重试机制实现

#### 4.7.1 错误处理
- 网络错误：显示友好的错误提示
- 解析错误：显示具体错误信息
- 超时错误：自动重试机制

#### 4.7.2 重试逻辑
```typescript
async function handleRetry() {
  if (searchState.loading) return;
  
  searchState.loading = true;
  searchState.error = null;
  
  try {
    await searchResults();
  } catch (error) {
    ElMessage.error(error.message || '重试失败，请检查网络连接');
  } finally {
    searchState.loading = false;
  }
}
```

### 4.8 首页灵感入口

#### 4.8.1 快速操作卡片
```html
<el-card shadow="hover" @click="$router.push('/inspiration')" class="action-card">
  <div class="action-card-content">
    <div class="action-icon inspiration-icon">
      <el-icon><EditPen /></el-icon>
    </div>
    <h4>{{ t('home.inspirationGet') }}</h4>
    <p>{{ t('home.inspirationDesc') }}</p>
    <el-button type="primary" size="small">{{ t('home.goTo') }}</el-button>
  </div>
</el-card>
```

#### 4.8.2 导航栏入口
```html
<el-menu-item index="/inspiration">
  <el-icon><EditPen /></el-icon>
  <span>{{ t('common.inspiration') }}</span>
</el-menu-item>
```

### 4.9 样式主题

#### 4.9.1 紫色变量定义
```scss
:root {
  --xhs-accent-purple: #9C27B0; /* 小红书紫色 */
  --xhs-purple-light: rgba(156, 39, 176, 0.1); /* 浅紫色背景 */
  --xhs-purple-hover: #8E24AA; /* 悬停状态紫色 */
}
```

#### 4.9.2 灵感图标样式
```scss
.inspiration-icon {
  background: linear-gradient(135deg, rgba(103, 58, 183, 0.12) 0%, rgba(156, 39, 176, 0.12) 100%);
  color: var(--xhs-accent-purple);
  
  .el-icon {
    font-size: 2rem;
  }
}
```

## 5. 实现方案

### 5.1 灵感获取API设计

#### 5.1.1 搜索API
- 端点：`/api/inspiration/search`
- 方法：GET
- 参数：
  - `keyword`: 搜索关键词
  - `page`: 页码
  - `limit`: 每页数量

#### 5.1.2 解析API
- 端点：`/api/inspiration/parse`
- 方法：POST
- 参数：
  - `url`: 小红书笔记链接

### 5.2 前端实现

#### 5.2.1 灵感页面组件结构
```
InspirationView/
├── InspirationView.vue          # 主页面
├── components/
│   ├── InspirationCard.vue      # 灵感卡片组件
│   └── SearchBar.vue           # 搜索栏组件
└── styles/
    └── inspiration.scss        # 灵感页面样式
```

#### 5.2.2 状态管理
```typescript
// inspirationStore.ts
interface InspirationState {
  keyword: string;
  url: string;
  results: InspirationItem[];
  loading: boolean;
  error: string | null;
  page: number;
  hasMore: boolean;
}

// API服务
class InspirationService {
  async search(keyword: string, page: number): Promise<InspirationItem[]>;
  async parseUrl(url: string): Promise<InspirationItem>;
  async refresh(item: InspirationItem): Promise<InspirationItem>;
}
```

### 5.3 后端实现

#### 5.3.1 API路由
- `inspiration.py`: 灵感获取API
- `xiaohongshu_service.py`: 小红书服务

#### 5.3.2 服务逻辑
```python
class InspirationService:
    async def search_xiaohongshu(self, keyword: str, page: int) -> List[InspirationItem]:
        # 实现小红书搜索逻辑
        pass
    
    async def parse_xiaohongshu_url(self, url: str) -> InspirationItem:
        # 实现小红书链接解析逻辑
        pass
    
    async def refresh_item(self, item_id: str) -> InspirationItem:
        # 实现内容刷新逻辑
        pass
```

## 6. 所有平台模板更新

已更新以下平台的模板：
- ✅ **ceshi**（测试平台）
- ✅ **douyin**（抖音）
- ✅ **fantui**（反推）
- ✅ **toutiao**（头条）
- ✅ **wechat**（微信公众号）
- ✅ **xiaohongshu**（小红书）
- ✅ **inspiration**（灵感获取）

每个平台的模板都已更新为支持总标题+总文案+多张图片的内容结构。

```typescript
// 定义生成器状态
interface GeneratorState {
  // ... 其他字段
  
  // 大纲数据
  outline: {
    raw: string
    title?: string          // 总标题
    copywriting?: string    // 总文案
    pages: Page[]
  }
  
  // ... 其他字段
}

// 在actions中添加更新标题和文案的方法
/**
 * 更新大纲标题
 */
updateOutlineTitle(title: string) {
  this.outline.title = title
  this.syncRawFromPages()
},

/**
 * 更新大纲文案
 */
updateOutlineCopywriting(copywriting: string) {
  this.outline.copywriting = copywriting
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
}
```

### 4.4 前端OutlineView更新

更新 `OutlineView.vue`，添加总标题和总文案的编辑区域：

```html
<!-- 总标题输入 -->
<div class="topic-edit">
  <label style="display: block; font-size: 14px; color: #333; margin-bottom: 8px; font-weight: 500;">总标题</label>
  <el-input
    v-model="store.outline.title"
    placeholder="请输入总标题"
    size="large"
    clearable
    style="width: 100%;"
    @input="store.updateOutlineTitle(store.outline.title || '')"
  />
  <span style="font-size: 12px; color: #666; margin-top: 4px; display: block;">图文内容的总标题，用于展示在所有图片之上</span>
</div>

<!-- 总文案输入，占据两列 -->
<div class="topic-edit" style="grid-column: 1 / -1;">
  <label style="display: block; font-size: 14px; color: #333; margin-bottom: 8px; font-weight: 500;">总文案</label>
  <el-input
    v-model="store.outline.copywriting"
    placeholder="请输入总文案，最好包含相关#话题标签"
    size="large"
    clearable
    type="textarea"
    :rows="3"
    style="width: 100%; resize: vertical; min-height: 100px;"
    @input="store.updateOutlineCopywriting(store.outline.copywriting || '')"
  />
  <span style="font-size: 12px; color: #666; margin-top: 4px; display: block;">图文内容的总文案，将与所有图片关联，建议添加相关#话题标签</span>
</div>
```

## 5. 实现步骤

### 5.1 后端实现

1. **修改数据模型**：在 `history.py` 中修改 `Outline` 模型，添加 `title` 和 `copywriting` 字段
2. **更新大纲生成服务**：在 `generation_service.py` 中添加解析总标题、总文案和多个图片提示词的逻辑
3. **测试后端API**：验证API返回的数据结构符合预期

### 5.2 前端实现

1. **修改数据模型**：在 `generator.ts` 中修改 `GeneratorState` 接口，添加 `title` 和 `copywriting` 字段
2. **更新状态管理**：在 `generator.ts` 中添加更新标题和文案的方法
3. **更新同步逻辑**：在 `generator.ts` 中更新 `syncRawFromPages` 方法，支持从标题、文案和图片提示词生成 raw 文本
4. **更新前端界面**：在 `OutlineView.vue` 中添加总标题和总文案的编辑区域
5. **测试前端功能**：验证大纲生成、编辑和同步功能正常

### 5.3 平台模板更新

1. **更新反推平台模板**：在 `platform_templates.yaml` 中更新反推平台的 `outline_template`
2. **更新其他平台模板**：依次更新小红书、抖音、公众号、头条号等平台的 `outline_template`
3. **测试模板效果**：验证各平台生成的大纲符合预期格式

## 6. 所有平台模板更新

已更新以下平台的模板：

- ✅ **ceshi**（测试平台）
- ✅ **douyin**（抖音）
- ✅ **fantui**（反推）
- ✅ **toutiao**（头条）
- ✅ **wechat**（微信公众号）
- ✅ **xiaohongshu**（小红书）

每个平台的模板都已更新为支持总标题+总文案+多张图片的内容结构。

## 7. 实现结果

### 7.1 生成的大纲格式

生成的大纲格式示例：

```
【标题】：冬日少女写真
【文案】：冬日暖阳下的少女，享受美好时光 #冬日写真 #少女感 #冬日穿搭
【图片提示词】：年龄：20-25岁
脸型：瓜子脸
妆容：日系/韩系精致妆，粉色眼影，豆沙唇
发型：黑色长发，自然散落
服装：白色毛衣，浅色牛仔裤
姿势：站在雪地里，手持热饮，微笑看向镜头
背景：冬日雪景，阳光明媚
风格：清新、自然、温暖

<page>

【图片提示词】：年龄：20-25岁
脸型：瓜子脸
妆容：日系/韩系精致妆，粉色眼影，豆沙唇
发型：黑色长发，自然散落
服装：白色毛衣，浅色牛仔裤
姿势：坐在咖啡馆窗边，托腮看向窗外
背景：温暖的咖啡馆，窗外雪景
风格：温馨、文艺

<page>

【图片提示词】：年龄：20-25岁
脸型：瓜子脸
妆容：日系/韩系精致妆，粉色眼影，豆沙唇
发型：黑色长发，自然散落
服装：白色毛衣，浅色牛仔裤
姿势：站在圣诞树旁，手持礼物，开心微笑
背景：装饰精美的圣诞树，温暖的灯光
风格：节日、温馨、快乐
```

### 7.2 前端界面

前端界面支持：
- 总标题的编辑
- 总文案的编辑
- 图片提示词的编辑
- 图片的添加和删除
- 图片的拖拽排序
- 实时预览生成的图片

## 8. 验证和测试

### 8.1 功能验证

- ✅ 大纲生成功能正常
- ✅ 标题和文案编辑功能正常
- ✅ 图片提示词编辑功能正常
- ✅ 图片生成功能正常
- ✅ 所有平台模板生成的大纲格式正确

### 8.2 兼容性验证

- ✅ 向后兼容旧版数据结构
- ✅ 支持不同浏览器
- ✅ 支持不同设备

## 9. 使用示例

### 9.1 基础使用流程

#### 9.1.1 图文生成流程
1. **输入主题**："冬日少女写真"
2. **选择平台**："反推"
3. **生成大纲**：点击"生成大纲"按钮
4. **编辑大纲**：
   - 修改总标题为"冬日暖阳下的少女"
   - 修改总文案，添加#话题标签
   - 调整图片提示词
5. **生成图片**：点击"开始生成图片"按钮
6. **查看结果**：在结果页查看生成的图片
7. **下载或导出**：下载生成的图片或导出完整内容

#### 9.1.2 灵感获取流程
1. **首页入口**：点击首页"灵感获取"卡片
2. **搜索灵感**：输入关键词如"冬日少女写真"
3. **查看结果**：浏览搜索结果中的热门图文
4. **获取灵感**：点击查看详情或直接使用作为参考
5. **生成内容**：基于灵感生成新的图文内容

### 9.2 高级使用

- **批量生成**：输入多个主题，批量生成大纲和图片
- **自定义模板**：修改平台模板，调整生成规则
- **调整参数**：调整AI模型参数，优化生成效果
- **灵感融合**：结合搜索结果和AI生成，创造独特内容
- **多平台同步**：同一内容生成多平台适配版本

### 9.3 灵感功能使用

#### 9.3.1 搜索功能
- 关键词搜索：输入相关主题关键词
- 链接解析：粘贴小红书笔记链接获取详细内容
- 结果筛选：按平台、时间、热度筛选
- 内容预览：查看缩略图和简要信息

#### 9.3.2 灵感卡片操作
- 查看详情：点击卡片查看完整内容
- 刷新数据：更新过时的灵感内容
- 复制链接：获取原笔记链接
- 收藏保存：保存喜欢的灵感

## 10. 注意事项

### 10.1 模板格式要求

- 模板中的输出格式必须严格按照要求，使用【标题】、【文案】和【图片提示词】开头
- 图片提示词之间必须用`<page>`标签分隔
- 避免在内容中使用 | 竖线符号

### 10.2 AI生成内容处理

- 处理AI生成内容格式不规范的情况
- 确保解析逻辑健壮，能够处理各种边缘情况
- 添加适当的错误处理和日志记录

### 10.3 灵感功能注意事项

- 搜索频率限制：避免频繁搜索导致IP被封
- 内容合规性：确保使用的内容符合平台规则
- 隐私保护：注意用户数据的隐私和安全
- 版权意识：尊重原创内容，避免侵权

### 10.4 性能优化

- 考虑性能问题，特别是当图片数量较多时
- 优化前端渲染，避免频繁更新DOM
- 优化后端处理，提高生成速度
- 实现搜索结果缓存，减少重复请求

## 11. 维护建议

### 11.1 定期更新模板

- 定期检查平台规则变化，更新模板内容
- 根据用户反馈调整模板，优化生成效果
- 添加新的平台支持，扩展适用范围

### 11.2 监控和日志

- 添加适当的监控和日志，跟踪生成过程中的问题
- 定期分析日志，优化生成算法和参数
- 监控灵感搜索API的使用情况和性能

### 11.3 持续改进

- 收集用户反馈，持续改进功能和体验
- 探索新的AI模型和技术，提高生成质量
- 支持更多平台和内容类型
- 扩展灵感获取的来源和方式

### 11.4 未来计划

#### 11.4.1 灵感功能扩展
- 🔍 高级搜索：支持多条件筛选和排序
- 📱 移动端优化：更好的移动设备体验
- 🎨 个性化推荐：基于用户偏好的灵感推荐
- 📊 数据分析：提供搜索趋势和热点分析

#### 11.4.2 AI集成优化
- 🤖 多模型支持：集成更多AI模型和提供商
- 🔄 实时生成：优化生成速度和响应时间
- 📈 质量提升：改进生成内容的质量和相关性
- 🎨 样式控制：提供更多生成参数和样式选项

#### 11.4.3 平台扩展
- 📱 新平台支持：添加更多社交平台模板
- 🌐 多语言支持：扩展到更多语言和文化
- 📱 跨平台同步：支持多平台内容同步发布
- 📊 数据统计：提供详细的内容分析统计

#### 11.4.4 用户体验
- 📱 响应式设计：优化移动端体验
- ⚡ 性能优化：提高页面加载速度
- 🎨 主题定制：支持自定义界面主题
- 📱 离线功能：支持离线内容预览和编辑

#### 11.4.5 安全和隐私
- 🔒 数据加密：加强用户数据保护
- 📝 合规性：确保符合相关法律法规
- 🛡️ 安全防护：防止滥用和恶意使用
- 📱 隐私控制：提供更细粒度的隐私设置

## 12. 技术栈

- **后端**：Python、FastAPI、Pydantic
- **前端**：Vue 3、TypeScript、Pinia
- **AI服务**：大语言模型API、图像生成API
- **配置管理**：YAML
- **搜索服务**：小红书API集成
- **状态管理**：Pinia、Vue I18n

## 13. 总结

图文内容生成功能已成功实现，支持总标题+总文案+多张图片的内容结构。所有平台的模板都已更新，能够生成符合要求的大纲内容。

灵感获取功能已成功实现，为用户提供：
- 🔍 搜索小红书热门图文获取创作灵感
- 📱 链接解析和内容提取
- 🎨 紫色主题的视觉设计
- 💬 完善的中英文国际化支持
- 🔁 错误处理和重试机制

该实现方案具有良好的扩展性和兼容性，能够适应不同平台的需求变化，为用户提供高质量的图文内容生成服务。未来将继续扩展灵感功能，提升AI生成质量，支持更多平台和优化用户体验。