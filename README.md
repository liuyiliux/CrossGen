# 逸流（Yiliu）- 多平台图文生成器

> 🚀 基于AI的一站式多平台图文内容生成工具

## 项目简介

逸流是一款智能化的多平台图文生成器，帮助内容创作者通过"一句话"快速生成符合小红书、抖音、微信公众号、头条号等平台特色的专业图文内容。

### ✨ 核心特性

- 🎯 **一键生成**: 一句话输入，自动生成多平台图文内容
- 🔄 **多平台适配**: 支持小红书、抖音、公众号、头条号等主流平台
- 🧠 **AI驱动**: 集成GPT、Claude等LLM和Stable Diffusion图像生成
- ⚡ **批量处理**: 支持批量主题并行生成
- 🎨 **模板化**: 灵活的平台模板配置，快速响应平台规则变化
- 📱 **响应式**: 现代化Web界面，支持多设备访问

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
git clone https://github.com/your-org/yiliu.git
cd yiliu
```

2. **后端设置**
```bash
cd backend
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install uv
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
```yaml
# config/platform_templates.yaml
platform_templates:
  xiaohongshu:
    title_style:
      max_length: 20
      punctuation: "emoji_allowed"
    image_requirements:
      ratio: "3:4"
      count: 3-5
    output_format: "markdown"
```

### AI提供商配置
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
1. 输入创作主题（如："秋季显白美甲"）
2. 选择目标发布平台
3. 点击生成按钮
4. 查看生成的图文内容
5. 下载或导出结果

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
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

当前进度: 🚧 第一阶段开发中 (12%)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 项目主页: https://github.com/your-org/yiliu
- 问题反馈: https://github.com/your-org/yiliu/issues
- 邮箱: team@yiliu.com

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [OpenAI](https://openai.com/)

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**