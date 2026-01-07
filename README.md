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
- **MySQL** - 关系型数据库（可选）
- **Pydantic** - 数据验证和序列化

### 前端技术栈
- **Vue 3** - 现代化前端框架
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Element Plus** - UI组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Vue I18n** - 国际化支持
- **Sass** - CSS预处理器

### AI集成
- **OpenAI** - GPT文本生成
- **Google Gemini** - Gemini文本和图像生成
- **SiliconFlow** - 多种模型支持
- **Generic API** - 通用AI API集成
- **Stable Diffusion** - 图像生成

### 工具链
- **Docker** - 容器化部署
- **uv** - Python包管理
- **npm/pnpm** - Node.js包管理
- **Prettier** - 代码格式化
- **ESLint** - 代码质量检查
- **MyPy** - Python类型检查

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Redis 6.0+ (可选)
- MySQL 8.0+ (可选)
- Git

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

# 编辑配置文件
# 1. 编辑系统配置
nano config/system_config.yaml
# 2. 编辑AI提供商配置
nano config/text_providers.yaml
nano config/image_providers.yaml
# 3. 编辑平台模板配置
nano config/platform_templates.yaml
```

3. **后端设置**
```bash
cd backend

# 确保安装 uv
pip install uv

# 同步依赖 (会自动创建虚拟环境)
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入API密钥和数据库配置
nano .env

# 启动后端
uv run python -m src.app
```

4. **前端设置**
```bash
cd frontend
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

5. **访问应用**
- 前端: http://localhost:3001 (默认端口，可在vite.config.ts中修改)
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 配置管理: http://localhost:3001/config

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
│   └── .env.example        # 环境变量模板
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # Vue组件
│   │   ├── locales/        # 国际化翻译
│   │   ├── views/          # 页面视图
│   │   ├── stores/         # 状态管理
│   │   ├── services/       # API服务
│   │   ├── styles/         # 样式文件
│   │   └── utils/          # 工具函数
│   ├── package.json        # Node.js依赖
│   └── vite.config.ts      # Vite配置
├── config/                 # 配置文件
│   ├── system_config.yaml                  # 系统配置
│   ├── system_config.yaml.example          # 系统配置示例
│   ├── platform_templates.yaml             # 平台模板配置
│   ├── platform_templates.yaml.example     # 平台模板配置示例
│   ├── text_providers.yaml                 # 文本AI提供商配置
│   ├── text_providers.yaml.example         # 文本AI提供商配置示例
│   ├── image_providers.yaml                # 图像AI提供商配置
│   └── image_providers.yaml.example        # 图像AI提供商配置示例
├── .gitignore              # Git忽略文件
├── design_scheme.md        # 设计方案
├── package.json            # 根目录package.json
└── README.md               # 项目说明文档
```

## ⚙️ 配置说明

### 系统配置

系统配置文件位于 `config/system_config.yaml`，用于配置数据库连接、Redis缓存、日志级别等系统级参数。

```yaml
# config/system_config.yaml
# 系统配置示例
logger:
  level: "INFO"  # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
  file_path: "logs/yiliu.log"  # 日志文件路径
  rotation: "10 MB"  # 日志文件轮转大小
  retention: 7  # 日志保留天数

# 数据库配置（可选，默认为None）
database:
  url: "mysql://username:password@localhost:3306/yiliu_db"  # MySQL数据库URL
  pool_size: 10  # 连接池大小
  max_overflow: 20  # 最大溢出连接数
  echo: false  # 是否打印SQL语句

# Redis配置
aio_redis:
  url: "redis://localhost:6379/0"  # Redis连接URL，/0表示使用0号数据库
  encoding: "utf-8"  # 编码
  decode_responses: true  # 是否自动解码响应
  db: 0  # Redis数据库编号

# API配置
api:
  prefix: "/api"  # API前缀
  timeout: 300  # API超时时间（秒）

# 图片配置
image:
  save_path: "images"  # 图片保存路径
  max_size: 10485760  # 图片最大大小（10MB）
  quality: 90  # 图片质量（0-100）
  allowed_formats: ["jpg", "jpeg", "png"]  # 允许的图片格式
```

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
    api_key: "${OPENAI_API_KEY}"  # API密钥，支持环境变量
    model: "gpt-4"  # 模型名称
    max_tokens: 2000  # 最大生成 token 数
    temperature: 0.7  # 温度参数，控制生成内容的随机性
    top_p: 0.95  # 核采样参数
    frequency_penalty: 0.0  # 频率惩罚
    presence_penalty: 0.0  # 存在惩罚

# config/image_providers.yaml
providers:
  stable_diffusion:
    api_key: "${STABLE_DIFFUSION_API_KEY}"
    base_url: "https://api.stability.ai/v1/generation"
    model: "stable-diffusion-xl-1024-v1-0"
    width: 1024  # 图片宽度
    height: 1024  # 图片高度
    steps: 50  # 生成步数
    cfg_scale: 7.0  # 配置比例
    samples: 1  # 生成数量
```

## 📖 使用指南

### 基础使用

1. **启动应用**
   - 后端：`uv run python -m src.app`
   - 前端：`npm run dev`
   - 访问：http://localhost:3001

2. **创作流程**
   - **输入创作主题**：在首页输入框中输入创作主题（如："冬日少女写真"）
   - **选择目标平台**：从下拉菜单中选择目标发布平台（如：反推、小红书、抖音等）
   - **生成大纲**：点击"生成"按钮，等待AI生成内容大纲
   - **编辑优化**：
     - 修改总标题
     - 完善总文案，支持#话题标签
     - 调整图片提示词，优化画面效果
     - 添加或删除图片，调整内容结构
   - **生成图片**：点击"生成图片"按钮，等待AI生成高质量图片
   - **查看结果**：在历史记录页面查看所有生成的内容
   - **下载导出**：支持单个或批量下载生成的图文内容

### 内容结构

逸流生成的内容采用以下结构化格式：

- **总标题**：整个图文内容的核心标题，吸引用户注意力
- **总文案**：图文内容的主体文字，支持#话题标签和换行
- **图片提示词**：每个图片对应一个详细的AI生成提示词，用`<page>`标签分割
- **生成图片**：AI根据提示词生成的高质量图片，自动保存到本地

### 批量生成

1. 点击"批量生成"按钮
2. 批量输入多个创作主题（每行一个）
3. 选择目标平台和生成参数
4. 点击"开始批量生成"启动任务
5. 实时查看生成进度和状态
6. 批量下载所有生成结果

### 历史记录管理

1. 点击导航栏"历史记录"进入历史页面
2. 查看所有已生成的图文内容
3. 支持按时间、平台、状态进行筛选
4. 点击单个记录查看详细内容
5. 支持重新生成、编辑、删除操作
6. 支持批量导出和删除

### 配置管理

1. 点击导航栏"配置"进入配置管理页面
2. **平台模板配置**：
   - 修改现有平台模板
   - 调整模板参数和生成规则
   - 添加新的平台模板
3. **AI提供商配置**：
   - 配置API密钥和访问参数
   - 支持OpenAI、Google Gemini、SiliconFlow等
   - 调整模型参数和生成设置
4. **系统配置**：
   - 调整日志级别和存储路径
   - 配置数据库和Redis连接
   - 设置API超时和其他系统参数
5. 保存配置后自动生效

### 图片管理

1. 在生成结果页面查看图片
2. 支持图片预览和放大查看
3. 支持图片替换和重新生成
4. 支持图片下载和删除
5. 自动保存到本地指定目录

### 日志管理

1. 系统自动记录操作日志和错误信息
2. 日志文件位于`logs/yiliu.log`
3. 支持日志轮转和自动清理
4. 便于问题排查和系统监控

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

### 本地开发部署

1. **安装依赖**
   - 后端：`uv sync`
   - 前端：`npm install`

2. **配置文件**
   - 复制配置文件模板：`cp config/system_config.yaml.example config/system_config.yaml`
   - 编辑配置文件，填入数据库、Redis和AI提供商信息

3. **启动服务**
   - 后端：`uv run python -m src.app`
   - 前端：`npm run dev`

### 生产部署

#### 1. 准备工作

- 安装Python 3.11+、Node.js 18+、Redis 6.0+、MySQL 8.0+（可选）
- 配置服务器防火墙，开放必要端口（默认8000、3001）
- 配置域名和SSL证书（推荐）

#### 2. 前端构建

```bash
cd frontend
npm install
npm run build
# 构建产物将生成在 dist 目录
```

#### 3. 后端部署

```bash
cd backend
uv sync --frozen
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件
# 启动后端服务
uv run python -m src.app
```

#### 4. 反向代理配置

推荐使用Nginx作为反向代理服务器，配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态资源
    location / {
        root /path/to/yiliu/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
    }
}
```

#### 5. 进程管理

推荐使用Supervisor或systemd管理服务进程：

**systemd配置示例（后端）：**

```ini
[Unit]
Description=Yiliu Backend Service
After=network.target redis.service mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/yiliu/backend
ExecStart=/path/to/uv run python -m src.app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Docker部署（待完善）

项目支持Docker容器化部署，相关配置文件正在完善中。

## 📊 项目状态

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

当前进度: ✅ 正式版已发布，支持多平台图文生成

## 📝 最近更新

- 添加了系统配置文件 `system_config.yaml`，支持 MySQL 和 Redis 配置
- 实现了历史记录功能，支持查看和管理之前生成的内容
- 添加了批量生成功能，支持一次性生成多个主题
- 优化了图片生成和存储逻辑
- 实现了多种 AI 提供商的支持，包括 OpenAI、Google Gemini 和 SiliconFlow
- 添加了国际化支持，支持中文和英文
- 实现了平台模板配置，支持快速适配不同平台
- 添加了响应式设计，支持多设备访问
- 实现了配置管理页面，支持在线修改平台模板和 AI 提供商配置

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🌟 GitHub 地址

- **GitHub 主页**: [https://github.com/liuyiliux/CrossGen](https://github.com/liuyiliux/CrossGen)
- **GitHub Issues**: [https://github.com/liuyiliux/CrossGen/issues](https://github.com/liuyiliux/CrossGen/issues)

## 📞 联系我们

- 项目主页: https://cnb.cool/yiliu/yiliu | https://github.com/liuyiliux/CrossGen
- 问题反馈: https://cnb.cool/yiliu/yiliu/issues | https://github.com/liuyiliux/CrossGen/issues
- 邮箱: 44165547@qq.com
- 微信:liuyiliux 说明来意

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库
- [OpenAI](https://openai.com/) - AI模型提供商
- [Google Gemini](https://gemini.google.com/) - Google AI模型
- [SiliconFlow](https://siliconflow.cn/) - AI模型平台 (邀请码: https://cloud.siliconflow.cn/i/fTKOkjDc)
- [Stable Diffusion](https://stability.ai/stable-diffusion) - 图像生成模型
- [uv](https://github.com/astral-sh/uv) - 快速Python包管理器
- [Pydantic](https://docs.pydantic.dev/) - 数据验证和序列化
- [Redis](https://redis.io/) - 内存数据库
- [MySQL](https://www.mysql.com/) - 关系型数据库
- [Vue Router](https://router.vuejs.org/) - Vue路由管理器
- [Pinia](https://pinia.vuejs.org/) - Vue状态管理
- [Vue I18n](https://vue-i18n.intlify.dev/) - Vue国际化支持
- [Sass](https://sass-lang.com/) - CSS预处理器
- [Vite](https://vitejs.dev/) - 前端构建工具

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**