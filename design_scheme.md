# 图文内容生成实现文档

## 1. 需求分析

用户希望生成的大纲支持以下结构：
- **一个总标题**：整个图文内容的标题
- **一个总文案**：整个图文内容的主体文案（最好带#话题）
- **多个图片提示词**：每个图片对应一个提示词，用`<page>`标签分割

这种结构类似于小红书和抖音的图文关系，即一个标题和文案对应多张图片。

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

### 9.2 高级使用

- **批量生成**：输入多个主题，批量生成大纲和图片
- **自定义模板**：修改平台模板，调整生成规则
- **调整参数**：调整AI模型参数，优化生成效果

## 10. 注意事项

### 10.1 模板格式要求

- 模板中的输出格式必须严格按照要求，使用【标题】、【文案】和【图片提示词】开头
- 图片提示词之间必须用`<page>`标签分隔
- 避免在内容中使用 | 竖线符号

### 10.2 AI生成内容处理

- 处理AI生成内容格式不规范的情况
- 确保解析逻辑健壮，能够处理各种边缘情况
- 添加适当的错误处理和日志记录

### 10.3 性能优化

- 考虑性能问题，特别是当图片数量较多时
- 优化前端渲染，避免频繁更新DOM
- 优化后端处理，提高生成速度

## 11. 维护建议

### 11.1 定期更新模板

- 定期检查平台规则变化，更新模板内容
- 根据用户反馈调整模板，优化生成效果

### 11.2 监控和日志

- 添加适当的监控和日志，跟踪生成过程中的问题
- 定期分析日志，优化生成算法和参数

### 11.3 持续改进

- 收集用户反馈，持续改进功能和体验
- 探索新的AI模型和技术，提高生成质量
- 支持更多平台和内容类型

## 12. 技术栈

- **后端**：Python、FastAPI、Pydantic
- **前端**：Vue 3、TypeScript、Pinia
- **AI服务**：大语言模型API
- **配置管理**：YAML

## 13. 总结

图文内容生成功能已成功实现，支持总标题+总文案+多张图片的内容结构。所有平台的模板都已更新，能够生成符合要求的大纲内容。

该实现方案具有良好的扩展性和兼容性，能够适应不同平台的需求变化，为用户提供高质量的图文内容生成服务。