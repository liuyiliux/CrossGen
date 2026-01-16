# 逸流（Yiliu）- 多平台图文生成器

> 🚀 基于 AI 的一站式多平台图文内容生成工具

## 🔗 项目地址

- **GitHub**: [https://github.com/liuyiliux/CrossGen](https://github.com/liuyiliux/CrossGen)
- **CNB**: [https://cnb.cool/yiliu/yiliu](https://cnb.cool/yiliu/yiliu)

## 项目简介

逸流是一款智能化的多平台图文生成器，帮助内容创作者通过"一句话"快速生成符合小红书、抖音、微信公众号、头条号、反推等平台特色的专业图文内容。最新版本集成了强大的**灵感获取**功能，支持从小红书链接解析并导入标题、文案及**参考图片**，让创作更高效。

### ✨ 核心特性

- 🎯 **一键生成**: 一句话输入，自动生成多平台图文内容
- 💡 **灵感获取**: 
  - 支持搜索小红书热门内容
  - **链接解析**: 深度解析笔记链接
  - **参考图导入**: 支持将原笔记图片直接导入作为 AI 绘图参考，精准还原风格
- 🔄 **多平台适配**: 支持小红书、抖音、公众号、头条号、反推等主流平台
- 🧠 **AI 驱动**: 集成 GPT、Claude 等 LLM 和 Stable Diffusion 图像生成
- ⚡ **批量处理**: 支持批量主题并行生成
- 🎨 **模板化**: 灵活的平台模板配置，快速响应平台规则变化
- 📱 **响应式**: 现代化 Web 界面，支持多设备访问
- 📋 **结构化内容**: 支持总标题+总文案+多张图片的内容结构
- 💾 **本地存储**: 生成的图片自动保存到本地文件夹
- 🔧 **灵活管理**: 支持图片的创建、更新、删除和替换操作

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.11+**
- **FastAPI**: 现代化 Web 框架
- **uv**: 极速包管理器
- **Redis**: 缓存和任务队列

### 前端技术栈
- **Vue 3** + **TypeScript**
- **Vite**: 快速构建工具
- **Element Plus**: UI 组件库
- **Pinia**: 状态管理

## 📂 项目结构

```text
yiliu/
├── backend/                # 后端代码 (FastAPI)
│   ├── src/
│   │   ├── api/           # API 路由定义
│   │   ├── models/        # 数据模型 (Pydantic)
│   │   ├── providers/     # AI 模型提供商实现
│   │   ├── services/      # 核心业务逻辑
│   │   ├── utils/         # 工具函数 (配置、日志等)
│   │   └── app.py         # 应用入口
│   └── scripts/           # 辅助脚本
├── frontend/               # 前端代码 (Vue 3)
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── views/         # 页面视图
│   │   ├── router/        # 路由配置
│   │   ├── styles/        # 样式文件 (SCSS)
│   │   └── utils/         # 前端工具函数
│   └── index.html         # 入口 HTML
├── config/                 # 配置文件模板
│   ├── system_config.yaml      # 系统配置
│   ├── platform_templates.yaml # 平台模板
│   ├── text_providers.yaml     # LLM 提供商配置
│   └── image_providers.yaml    # 绘图模型配置
└── docs/                   # 项目文档
```

## 🚀 快速开始

详细操作请参阅 [用户操作手册](docs/User_Manual.md)。

### 环境要求
- Python 3.11+
- Node.js 18+
- Redis 6.0+ (可选)

### 安装步骤

1. **克隆项目**
```bash
git clone https://cnb.cool/yiliu/yiliu.git
cd yiliu
```

2. **配置文件设置**
```bash
# 复制配置文件模板
cp config/system_config.example.yaml config/system_config.yaml
cp config/text_providers.yaml.example config/text_providers.yaml
cp config/image_providers.yaml.example config/image_providers.yaml
cp config/platform_templates.yaml.example config/platform_templates.yaml

# 请根据实际情况编辑上述 yaml 配置文件填入 API Key
```

3. **后端启动**
```bash
cd backend
pip install uv
uv sync
# 配置环境变量
cp .env.example .env
# 启动
uv run python -m src.app
```

4. **前端启动**
```bash
cd frontend
npm install
npm run dev
```

5. **访问应用**
- 前端: http://localhost:3001
- 后端 API: http://localhost:8000/docs

## 📝 最近更新

- **[修复] 参考图导入**: 修复了从灵感页面导入时，参考图片无法正确传递到创作页面的问题。
- **[新增] 灵感获取**: 支持搜索和解析小红书内容。
- **[优化] 搜索体验**: 优化了灵感搜索失败页的空状态和错误提示样式。
- **[优化] 配置管理**: 支持在线修改平台模板和 AI 提供商配置。

## 🤝 贡献指南

欢迎提交 Pull Request 来改进本项目！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系我们

- 问题反馈: [GitHub Issues](https://github.com/liuyiliux/CrossGen/issues)
- 邮箱: 44165547@qq.com
