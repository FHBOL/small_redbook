# 小红书文案生成器 (Langchain版本)

这个项目可以自动从机器之心官网获取热门文章，并使用AI模型生成小红书风格的文案。项目已重构为使用Langchain框架的智能agent架构，并支持使用uv管理Python环境。

## 功能特点

1. 从机器之心RSS源自动获取最新文章
2. 根据标题关键词和内容质量筛选热门文章
3. 调用AI模型生成小红书风格文案
4. 支持定时执行和立即执行两种模式
5. 生成的文案包含标题、正文和标签

## 环境管理

本项目使用uv管理Python环境。uv是一个极快的Python包和项目管理器。

### 安装uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用pip安装
pip install uv
```

### 创建虚拟环境并安装依赖

```bash
# 使用uv创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装项目依赖
uv pip install -e .
```

### 安装Playwright浏览器驱动

```bash
playwright install chromium
```

## 配置

在 `.env` 文件中设置以下参数：

1. `DASHSCOPE_API_KEY`: 心流平台的API密钥
2. `AI_MODEL_NAME`: 使用的AI模型名称
3. `SCHEDULE_TIME`: 定时执行的时间（格式：HH:MM）
4. 其他配置参数...

## 使用方法

### 立即执行一次

```bash
python main.py --once
```

### 定时执行

```bash
python main.py
```

默认会在每天设定的时间执行任务。

## 项目架构

项目采用Langchain框架构建，包含以下主要组件：

1. **ArticleAgent**: 负责文章获取和处理
2. **CopyAgent**: 负责文案生成
3. **MainAgent**: 协调整个流程

## 输出格式

生成的文案会保存在 `output` 目录下，文件名格式为：
`{日期}_{序号}_{文章标题}.txt`

每个文件包含：
1. 生成时间
2. 原始文章信息
3. 生成的小红书文案（标题、正文、标签）

## 技术实现

- 使用Langchain构建智能agent
- 使用feedparser解析RSS源
- 使用requests和BeautifulSoup进行网页抓取
- 使用Playwright处理需要登录的页面
- 使用OpenAI兼容的客户端调用AI平台API
- 使用schedule实现定时任务
- 使用uv管理Python环境