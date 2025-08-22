# 小红书文案生成器

这个项目可以自动从机器之心官网获取热门文章，并使用心流AI模型生成小红书风格的文案。

## 功能特点

1. 从机器之心RSS源自动获取最新文章
2. 根据标题关键词和内容质量筛选热门文章
3. 调用心流AI模型生成小红书风格文案
4. 支持定时执行和立即执行两种模式
5. 生成的文案包含标题、正文和标签

## 安装依赖

```bash
pip install -r requirements.txt
```

如果需要使用Playwright功能，还需要安装浏览器驱动：

```bash
playwright install chromium
```

## 配置

在 `config.py` 文件中设置以下参数：

1. `DASHSCOPE_API_KEY`: 心流平台的API密钥
2. `AI_MODEL_NAME`: 使用的AI模型名称（当前使用glm-4.5）
3. `SCHEDULE_TIME`: 定时执行的时间（格式：HH:MM）

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

## 输出格式

生成的文案会保存在 `output` 目录下，文件名格式为：
`{日期}_{序号}_{文章标题}.txt`

每个文件包含：
1. 生成时间
2. 原始文章信息
3. 生成的小红书文案（标题、正文、标签）

## 技术实现

- 使用feedparser解析RSS源
- 使用requests和BeautifulSoup进行网页抓取
- 使用Playwright处理需要登录的页面
- 使用OpenAI兼容的客户端调用心流平台API
- 使用schedule实现定时任务

## 版本历史

### v1.0 (2025-08-22)
- 基础功能实现
- RSS文章获取和筛选
- AI文案生成
- 定时任务支持
- 使用自定义标记格式避免JSON解析错误
- 移除不必要的截图功能以提高效率