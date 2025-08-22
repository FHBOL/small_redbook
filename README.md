# 小红书文案生成器 (Langchain版本)

这个项目可以自动从机器之心官网获取热门文章，并使用AI模型生成小红书风格的文案。项目已重构为使用Langchain框架的智能agent架构，并支持使用uv管理Python环境。

## 功能特点

1. 从机器之心RSS源自动获取最新文章
2. 根据标题关键词和内容质量筛选热门文章
3. 调用AI模型生成小红书风格文案
4. 支持定时执行和立即执行两种模式
5. 生成的文案包含标题、正文和标签
6. 支持MCP (Model Context Protocol) 集成，提供标准化的工具接口

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

## MCP集成

本项目集成了MCP (Model Context Protocol)，提供标准化的工具接口，便于与其他AI系统集成。

### MCP工具

1. `get_current_time`: 获取当前时间
2. `format_article_info`: 格式化文章信息用于小红书文案生成
3. `save_xiaohongshu_copy`: 保存生成的小红书文案到文件

### 启动MCP服务器模式

```bash
source .venv/bin/activate  # 激活虚拟环境
python -m small_redbook.main --mcp
```

### 第三方MCP服务集成

项目支持通过标准MCP配置文件集成第三方MCP服务：

1. 编辑 `mcp-config.json` 文件定义服务器配置
2. 使用 `mcp_server_manager` 启动和管理服务器

示例配置：
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp-server"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/filesystem-server"]
    }
  }
}
```

启动服务器：
```python
from src.small_redbook.mcp import mcp_server_manager

# 启动Playwright MCP服务器
mcp_server_manager.start_server("playwright")

# 查看服务器状态
status = mcp_server_manager.get_server_status("playwright")
print(f"Playwright服务器状态: {status}")
```

### MCP自动集成功能

项目支持自动集成配置的MCP服务：

1. 在 `mcp-config.json` 中定义MCP服务器
2. 在 `src/small_redbook/mcp/auto_config.ini` 中配置自动集成选项
3. 启动任务时自动启动配置的MCP服务器

示例自动配置：
```ini
[general]
# 是否启用MCP自动集成功能
enable_mcp_auto_integration = true

# 是否自动启动配置的MCP服务器
auto_start_servers = true

[mcp_servers]
# 配置需要自动启动的MCP服务器
playwright = true
filesystem = false
```

当启用自动集成功能后，系统会在任务启动时自动启动配置的MCP服务器，并在任务完成时自动停止它们。

### 第三方服务配置（传统方式）

项目也支持通过INI文件配置第三方服务：

1. 编辑 `src/small_redbook/mcp/third_party_config.ini` 文件
2. 启用需要的第三方服务并配置URL和认证信息
3. 在agent中注册相应的工具

## 配置

在 `.env` 文件中设置以下参数：

1. `DASHSCOPE_API_KEY`: 心流平台的API密钥
2. `AI_MODEL_NAME`: 使用的AI模型名称
3. `SCHEDULE_TIME`: 定时执行的时间（格式：HH:MM）
4. 其他配置参数...

## 使用方法

### 立即执行一次

```bash
source .venv/bin/activate  # 激活虚拟环境
python -m small_redbook.main --once
```

### 定时执行

```bash
source .venv/bin/activate  # 激活虚拟环境
python -m small_redbook.main
```

默认会在每天设定的时间执行任务。

## 项目架构

项目采用Langchain框架构建，包含以下主要组件：

1. **ArticleAgent**: 负责文章获取和处理
2. **CopyAgent**: 负责文案生成
3. **MainAgent**: 协调整个流程
4. **MCP Tools**: 提供标准化的工具接口

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
- 集成MCP (Model Context Protocol) 提供标准化工具接口