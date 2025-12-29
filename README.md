# 逸流（Yiliu）- 多平台图文生成器

> 🚀 基于AI的一站式多平台图文内容生成工具

## 项目简介

逸流是一款智能化的多平台图文生成器，帮助内容创作者通过"一句话"快速生成符合小红书、抖音、微信公众号、头条号、反推等平台特色的专业图文内容。

### ✨ 核心特性

- 🎯 **一键生成**: 一句话输入，自动生成多平台图文内容
- 🔄 **多平台适配**: 支持小红书、抖音、公众号、头条号、反推等主流平台
- 🧠 **AI驱动**: 集成GPT、Claude等LLM和Stable Diffusion图像生成
- ⚡ **批量处理**: 支持批量主题并行生成
- 🎨 **模板化**: 灵活的平台模板配置，快速响应平台规则变化
- 📱 **响应式**: 现代化Web界面，支持多设备访问
- 📋 **结构化内容**: 支持总标题+总文案+多张图片的内容结构
- 💾 **优化的图片存储**: 生成的图片自动保存到本地文件夹，避免base64字符串过长问题
- 📊 **完善的日志系统**: 详细的日志记录，便于问题排查和系统监控
- 🔧 **灵活的图片管理**: 支持图片的创建、更新、删除和替换操作

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.11+** - 主要开发语言
- **FastAPI** - 现代化Web框架
- **uv** - 快速包管理器
- **Redis** - 缓存和任务队列
- **Pydantic** - 数据验证和序列化

### 前端技术栈
- **Vue 3** - 现代化前端框架
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Element Plus** - UI组件库
- **Pinia** - 状态管理

### AI集成
- **OpenAI** - GPT文本生成
- **Anthropic** - Claude文本生成
- **Stable Diffusion** - 图像生成

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Redis 6.0+
- Git

### 安装步骤

1. **克隆项目**
```bash
git clone https://cnb.cool/yiliu/yiliu.git
cd yiliu
```

2. **后端设置**
```bash
cd backend

# 确保安装 uv
pip install uv

# 同步依赖 (会自动创建虚拟环境)
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入API密钥

# 启动后端
uv run python -m src.app
```

3. **前端设置**
```bash
cd frontend
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

4. **访问应用**
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📁 项目结构

```
yiliu/
├── backend/                 # 后端代码
│   ├── src/
│   │   ├── api/            # API路由
│   │   ├── services/       # 业务服务
│   │   ├── providers/      # AI提供商
│   │   ├── models/         # 数据模型
│   │   └── utils/          # 工具函数
│   ├── pyproject.toml      # Python依赖配置
│   └── .env.example       # 环境变量模板
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── stores/        # 状态管理
│   │   ├── services/      # API服务
│   │   └── utils/         # 工具函数
│   ├── package.json       # Node.js依赖
│   └── vite.config.ts     # Vite配置
├── config/                # 配置文件
│   ├── platform_templates.yaml
│   ├── text_providers.yaml
│   └── image_providers.yaml
├── docs/                  # 项目文档
├── scripts/               # 部署脚本
└── deploy/               # 部署配置
```

## ⚙️ 配置说明

### 平台模板配置

平台模板配置文件位于 `config/platform_templates.yaml`，用于定义不同平台的内容生成规则。每个平台模板包含以下主要部分：

```yaml
# config/platform_templates.yaml
platform_templates:
  fantui:  # 反推平台
    name: 反推
    outline_template: '你是一个图片创作高手。用户会给你一个要求以及说明，你需要生成包含一个标题、一个文案和多个图片提示词的内容。
      # ... 模板内容
    image_template: '{full_outline}'
    video_template: '请生成一个适合小红书的短视频脚本，根据以下主题和大纲：
      # ... 模板内容
```

**模板字段说明**：
- `name`: 平台中文名称
- `outline_template`: 大纲生成模板，用于生成包含标题、文案和图片提示词的完整内容
- `image_template`: 图片生成模板，用于生成单张图片
- `video_template`: 视频生成模板，用于生成视频脚本

### AI提供商配置

AI提供商配置文件位于 `config/text_providers.yaml` 和 `config/image_providers.yaml`，用于配置AI服务的API密钥和参数。

```yaml
# config/text_providers.yaml
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    max_tokens: 2000
```

## 📖 使用指南

### 基础使用

1. **输入创作主题**（如："冬日少女写真"）
2. **选择目标发布平台**（如：反推、小红书、抖音等）
3. **点击生成按钮**，等待AI生成大纲
4. **编辑大纲内容**（可选）
   - 修改总标题
   - 修改总文案
   - 调整图片提示词
   - 添加或删除图片
5. **生成图片**，等待AI生成图片
6. **查看生成的图文内容**
7. **下载或导出结果**

### 内容结构

逸流生成的内容采用以下结构化格式：

- **总标题**：整个图文内容的标题
- **总文案**：整个图文内容的主体文案，支持#话题标签
- **图片提示词**：每个图片对应一个提示词，用`<page>`标签分割

### 批量生成

1. 批量输入多个主题
2. 选择目标平台
3. 启动批量生成任务
4. 实时查看生成进度
5. 批量下载所有结果

### 配置管理

1. 访问配置页面
2. 修改平台模板参数
3. 配置AI提供商密钥
4. 调整生成参数
5. 保存并应用配置

## 🔧 开发指南

### 本地开发

1. 安装开发依赖
2. 启动开发服务器
3. 进行代码修改
4. 运行测试验证
5. 提交代码变更

### 代码规范

- 后端: PEP8 + Black + isort + MyPy
- 前端: ESLint + Prettier + TypeScript
- 提交: Conventional Commits

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
pnpm test
```

## 📦 部署

### Docker部署

```bash
# 构建镜像
docker build -t yiliu:latest .

# 运行容器
docker-compose up -d
```

### 生产部署

1. 配置环境变量
2. 构建生产版本
3. 部署到云服务器
4. 配置反向代理
5. 设置监控告警

## 📊 项目状态

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

当前进度: ✅ 正式版已发布，支持多平台图文生成

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 项目主页: https://cnb.cool/yiliu/yiliu
- 问题反馈: https://cnb.cool/yiliu/yiliu/issues
- 邮箱: 44165547@qq.com
- 微信:liuyiliux 说明来意

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [OpenAI](https://openai.com/)

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**