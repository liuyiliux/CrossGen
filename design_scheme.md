# 图文内容生成方案设计

## 1. 需求分析

用户希望生成的大纲支持以下结构：
- **一个总标题**：整个图文内容的标题
- **一个总文案**：整个图文内容的主体文案（最好带#话题）
- **多个图片提示词**：每个图片对应一个提示词，用<page>标签分割

这种结构类似于小红书和抖音的图文关系，即一个标题和文案对应多张图片。

## 2. 数据结构设计

### 2.1 后端数据模型

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

### 2.2 前端数据模型

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

## 3. 实现方案

### 3.1 修改反推模板

更新 `platform_templates.yaml` 中的反推模板，要求AI生成包含总标题、总文案和多个图片提示词的内容：

```yaml
outline_template: '你是一个图片创作高手。用户会给你一个要求以及说明，你需要生成包含一个标题、一个文案和多个图片提示词的内容。

用户的要求以及说明：
{topic}

要求：
1. 内容控制在 3-5 张图片
2. 所有图片的主体和关键物品相同，只有细微变化
3. 每张图片的背景可以不同
4. 文案中最好包含相关的#话题标签

输出格式（严格遵守）：
- 首先是总标题，使用【标题】：开头
- 接下来是总文案，使用【文案】：开头
- 然后是多个图片提示词，每张图片使用【图片提示词】：开头，用<page>标签分割不同图片
- 内容要具体、详细，方便后续生成图片
- 避免在内容中使用 | 竖线符号

示例输出：
【标题】：夏日海滩度假
【文案】：夏日海滩，享受阳光与海浪的拥抱，让心情随着海风飞扬。#夏日度假 #海滩拍照 #夏日穿搭
【图片提示词】：一张高质量、写实风格的女性照片，主角是一位年轻女性，身穿蓝色比基尼，站在海滩上，阳光明媚，海浪轻柔，背景是蓝色的天空和白色的云朵。

<page>

【图片提示词】：一张高质量、写实风格的女性照片，主角是同一位年轻女性，身穿蓝色比基尼，坐在沙滩椅上，手持一杯鸡尾酒，背景是蓝色的大海和白色的沙滩。

<page>

【图片提示词】：一张高质量、写实风格的女性照片，主角是同一位年轻女性，身穿蓝色比基尼，在海水中嬉戏，溅起水花，背景是蓝色的大海和远处的帆船。
'
```

### 3.2 修改大纲生成服务的解析逻辑

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

# 在生成大纲时使用
title, copywriting, image_prompts = parse_generated_content(generated_text)

# 创建大纲对象
outline = Outline(
    raw=generated_text,
    title=title,
    copywriting=copywriting,
    pages=[
        Page(
            index=i,
            type="content",
            content=prompt,
            image_prompt=prompt
        ) for i, prompt in enumerate(image_prompts)
    ]
)
```

### 3.3 修改前端Generator Store

更新 `generator.ts` 中的状态管理，添加标题和文案字段：

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

### 3.4 修改前端OutlineView

更新 `OutlineView.vue`，添加总标题和总文案的编辑区域：

```html
<!-- 总标题输入 -->
<div class="section-title">标题</div>
<textarea
  v-model="outline.title"
  class="textarea-paper"
  placeholder="在此输入标题..."
  @input="store.updateOutlineTitle(outline.title)"
/>
<div class="word-count">{{ (outline.title || '').length }} 字</div>

<!-- 总文案输入 -->
<div class="section-title">文案</div>
<textarea
  v-model="outline.copywriting"
  class="textarea-paper"
  placeholder="在此输入文案..."
  @input="store.updateOutlineCopywriting(outline.copywriting)"
/>
<div class="word-count">{{ (outline.copywriting || '').length }} 字</div>

<!-- 图片提示词列表 -->
<div class="section-title">图片提示词</div>
<div v-for="page in outline.pages" :key="page.index" class="page-item">
  <div class="page-header">
    <span class="page-index">第 {{ page.index + 1 }} 张</span>
  </div>
  <textarea
    v-model="page.content"
    class="textarea-paper"
    placeholder="在此输入图片提示词..."
    @input="store.updatePage(page.index, page.content)"
  />
  <div class="word-count">{{ (page.content || '').length }} 字</div>
</div>
```

## 4. 实现步骤

1. **修改后端Outline模型**：在`history.py`中添加title和copywriting字段
2. **更新前端Generator Store**：在`generator.ts`中添加title和copywriting字段
3. **修改反推模板**：在`platform_templates.yaml`中更新反推模板，支持新的数据结构
4. **更新大纲生成服务的解析逻辑**：在`generation_service.py`中添加解析总标题、总文案和多个图片提示词的逻辑
5. **修改前端OutlineView**：在`OutlineView.vue`中添加总标题、总文案的编辑区域
6. **更新syncRawFromPages方法**：在`generator.ts`中更新raw文本生成逻辑
7. **测试修改后的功能**：确保大纲生成和编辑正常工作

## 5. 预期效果

- 用户可以生成包含一个标题、一个文案和多个图片提示词的大纲
- 大纲编辑界面支持分别编辑总标题、总文案和每个图片提示词
- 生成的内容结构类似于小红书和抖音的图文关系
- 支持后续图片生成时使用正确的标题、文案和图片提示词

## 6. 注意事项

- 确保向后兼容，支持旧版数据结构
- 处理AI生成内容格式不规范的情况
- 优化用户界面，确保编辑体验良好
- 考虑性能问题，特别是当图片数量较多时

## 7. 技术栈

- 后端：Python、FastAPI、Pydantic
- 前端：Vue 3、TypeScript、Pinia
- AI服务：大语言模型API