from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from typing import List, Dict
import feedparser
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
import time
from config import JIQIZHIXIN_RSS_URL, DASHSCOPE_API_KEY, AI_MODEL_NAME

@tool
def fetch_articles_from_rss() -> List[Dict]:
    """
    从机器之心RSS获取最新文章列表
    :return: 文章列表
    """
    try:
        # 解析RSS
        feed = feedparser.parse(JIQIZHIXIN_RSS_URL)
        
        articles = []
        for entry in feed.entries:
            article = {
                'title': entry.title,
                'link': entry.link,
                'summary': getattr(entry, 'summary', ''),
                'published': getattr(entry, 'published', ''),
                'author': getattr(entry, 'author', '机器之心')
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        print(f"获取RSS文章列表失败: {e}")
        return []

@tool
def fetch_article_content_with_playwright(url: str) -> Dict:
    """
    使用Playwright获取文章详细内容
    :param url: 文章链接
    :return: 文章详细内容
    """
    try:
        print(f"使用Playwright获取文章内容: {url}")
        
        with sync_playwright() as p:
            # 启动浏览器（无头模式）
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 设置视口大小
            page.set_viewport_size({"width": 1280, "height": 800})
            
            # 设置用户代理
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
            })
            
            # 访问页面
            response = page.goto(url, wait_until='networkidle')
            
            if response and response.status == 200:
                # 等待页面加载完成
                page.wait_for_timeout(5000)
                
                # 获取页面标题
                title = page.title()
                print(f"页面标题: {title}")
                
                # 尝试多种选择器来提取文章内容
                content = ""
                
                # 更精确的文章内容选择器
                content_selectors = [
                    'article .content',
                    '.article-content .content',
                    '.article-content',
                    '.content-wrapper',
                    '.article-body',
                    '.post-content',
                    '.entry-content',
                    '[class*="article"] [class*="content"]'
                ]
                
                for selector in content_selectors:
                    try:
                        content_elements = page.query_selector_all(selector)
                        if content_elements:
                            # 合并所有匹配元素的文本
                            full_content = ""
                            for element in content_elements:
                                element_text = element.inner_text().strip()
                                # 过滤掉太短的内容和可能的噪声内容
                                if element_text and len(element_text) > 100 and "登录" not in element_text and "会员" not in element_text:
                                    # 过滤掉包含列表项的内容（可能是推荐文章）
                                    if "今天" not in element_text and "08月" not in element_text:
                                        full_content += element_text + "\n\n"
                            
                            if len(full_content) > len(content):
                                content = full_content
                                print(f"通过选择器 {selector} 提取到内容，长度: {len(content)}")
                                if len(content) > 500:  # 如果内容足够长，认为找到了正文
                                    break
                    except Exception as e:
                        print(f"使用选择器 {selector} 提取内容时出错: {e}")
                        continue
                
                # 如果没找到特定内容区域，尝试查找包含文章主要内容的div
                if not content or len(content) < 500:
                    try:
                        # 查找所有div元素
                        div_elements = page.query_selector_all('div')
                        for div in div_elements:
                            div_text = div.inner_text().strip()
                            # 查找包含较长文本且不包含噪声词汇的div
                            if len(div_text) > 1000 and "登录" not in div_text and "会员" not in div_text:
                                # 检查是否包含文章相关内容
                                if any(keyword in div_text for keyword in ["AI", "人工智能", "模型", "芯片", "数据"]):
                                    # 过滤掉包含推荐列表的内容
                                    if "今天" not in div_text[:500] and "08月" not in div_text[:500]:
                                        content = div_text
                                        print(f"从div提取到内容，长度: {len(content)}")
                                        break
                    except Exception as e:
                        print(f"从div提取内容时出错: {e}")
                
                # 提取文章标签
                tags = []
                try:
                    # 查找标签相关的元素
                    tag_elements = page.query_selector_all('.tag, .tags, [class*="tag"], a[href*="tag"]')
                    for tag_element in tag_elements:
                        tag_text = tag_element.inner_text().strip()
                        if tag_text and len(tag_text) > 1 and len(tag_text) < 30 and "#" not in tag_text:
                            tags.append(tag_text)
                    
                    # 如果没找到标签，尝试从页面文本中提取
                    if not tags:
                        page_text = page.inner_text()
                        # 简单的标签提取（假设标签在文章末尾）
                        lines = page_text.split('\n')
                        for line in lines[-20:]:  # 检查最后20行
                            if line.strip().startswith('#') and len(line.strip()) < 30:
                                tags.append(line.strip())
                    
                    # 去重
                    tags = list(set(tags))[:10]  # 最多保留10个标签
                    print(f"提取到标签: {tags}")
                except Exception as e:
                    print(f"提取标签时出错: {e}")
                
                # 关闭浏览器
                browser.close()
                
                print(f"最终提取到的内容长度: {len(content)}")
                
                # 如果内容太短，认为获取失败
                if len(content) < 300:
                    print("内容太短，认为获取失败")
                    return {'content': '', 'tags': []}
                
                return {
                    'content': content[:8000] if content else '',  # 限制内容长度为8000字符
                    'tags': tags
                }
            else:
                print(f"访问页面失败，状态码: {response.status if response else 'None'}")
                browser.close()
    except Exception as e:
        print(f"使用Playwright获取文章内容失败 {url}: {e}")
    
    return {}

@tool
def fetch_article_content(url: str) -> Dict:
    """
    通过网页抓取获取文章详细内容（优先使用requests，失败后使用Playwright）
    :param url: 文章链接
    :return: 文章详细内容
    """
    try:
        # 首先尝试使用requests获取内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        
        print(f"正在获取文章内容: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容长度: {len(response.text)}")
        
        if response.status_code == 200:
            # 检查是否是登录页面
            if "登录" in response.text and "会员" in response.text:
                print("检测到登录页面，尝试使用Playwright获取内容")
                return fetch_article_content_with_playwright(url)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试多种选择器来提取文章内容
            content = ""
            
            # 尝试查找文章正文的常见选择器
            content_selectors = [
                'article .content',
                '.article-content .content',
                '.article-content',
                '.content-wrapper',
                '.article-body',
                '.post-content',
                '.entry-content',
                '[class*="article"] [class*="content"]'
            ]
            
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    print(f"找到 {len(content_elements)} 个匹配元素，选择器: {selector}")
                    # 合并所有匹配元素的文本
                    full_content = ""
                    for element in content_elements:
                        # 移除script和style标签
                        for script in element(["script", "style", "nav", "header", "footer", "aside"]):
                            script.decompose()
                        element_text = element.get_text().strip()
                        # 过滤掉太短的内容和可能的噪声内容
                        if element_text and len(element_text) > 100 and "登录" not in element_text and "会员" not in element_text:
                            # 过滤掉包含列表项的内容（可能是推荐文章）
                            if "今天" not in element_text and "08月" not in element_text:
                                full_content += element_text + "\n\n"
                    
                    if len(full_content) > len(content):
                        content = full_content
                        print(f"提取到的内容长度: {len(content)}")
                        if len(content) > 500:  # 如果内容足够长，认为找到了正文
                            print("内容足够长，认为找到了正文")
                            break
            
            # 如果没找到特定内容区域，则尝试其他方法
            if not content or len(content) < 300:
                print("未找到特定内容区域，尝试其他方法")
                # 尝试查找包含文章内容的特定div
                article_divs = soup.find_all('div')
                for div in article_divs:
                    # 移除script和style标签
                    for script in div(["script", "style", "nav", "header", "footer", "aside"]):
                        script.decompose()
                    div_content = div.get_text().strip()
                    # 查找包含较长文本且不包含登录相关词汇的div
                    if len(div_content) > 1000 and "登录" not in div_content and "会员" not in div_content:
                        # 检查是否包含文章相关内容
                        if any(keyword in div_content for keyword in ["AI", "人工智能", "模型", "芯片", "数据"]):
                            # 过滤掉包含推荐列表的内容
                            if "今天" not in div_content[:500] and "08月" not in div_content[:500]:
                                content = div_content
                                print(f"从div提取到的内容长度: {len(content)}")
                                break
            
            # 提取文章标签或分类
            tags = []
            tag_elements = soup.find_all('a', class_=re.compile(r'tag|category', re.I)) or \
                          soup.find_all('a', attrs={'rel': 'tag'}) or \
                          soup.find_all(class_=re.compile(r'tag|category', re.I))
            for tag in tag_elements:
                tag_text = tag.get_text().strip()
                if tag_text and len(tag_text) > 1 and len(tag_text) < 30 and "#" not in tag_text:
                    tags.append(tag_text)
            
            # 去重
            tags = list(set(tags))[:10]  # 最多保留10个标签
            
            print(f"最终提取到的内容长度: {len(content)}")
            print(f"提取到的标签: {tags}")
            
            # 如果内容太短，认为获取失败，尝试使用Playwright
            if len(content) < 300:
                print("内容太短，尝试使用Playwright获取内容")
                return fetch_article_content_with_playwright(url)
            
            return {
                'content': content[:8000] if content else '',  # 限制内容长度为8000字符
                'tags': tags
            }
    except Exception as e:
        print(f"使用requests获取文章内容失败 {url}: {e}")
        # 如果requests失败，尝试使用Playwright
        print("尝试使用Playwright获取内容")
        return fetch_article_content_with_playwright(url)
    
    return {}

@tool
def get_popular_articles(articles: List[Dict], count: int = 5) -> List[Dict]:
    """
    根据文章标题热度和内容质量筛选热门文章
    由于RSS不提供浏览量和评论数，我们通过标题关键词和内容长度来估算热度
    :param articles: 文章列表
    :param count: 热门文章数量
    :return: 热门文章列表
    """
    # 热门关键词列表
    hot_keywords = ['AI', '人工智能', '大模型', '深度学习', '机器学习', 'NLP', 'CV', 'GPT', 'BERT', '算法', '神经网络', '芯片', '数据集', '发布', '突破']
    
    def calculate_hot_score(article):
        score = 0
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        # 标题包含热门关键词加分
        for keyword in hot_keywords:
            if keyword in title:
                score += 15
            if keyword in summary:
                score += 8
        
        # 标题长度适中加分（标题过短或过长可能不够吸引人）
        if 10 <= len(title) <= 50:
            score += 5
            
        # 包含"最新"、"发布"等词汇加分
        if any(word in title for word in ['最新', '发布', '重磅', '突破', '升级', '开源']):
            score += 10
            
        # 内容长度加分
        summary_length = len(summary)
        if summary_length > 200:
            score += 10
        elif summary_length > 100:
            score += 5
            
        return score
    
    # 按热度评分排序
    sorted_articles = sorted(articles, key=calculate_hot_score, reverse=True)
    
    print(f"按热度排序后的前10篇文章:")
    for i, article in enumerate(sorted_articles[:10]):
        print(f"{i+1}. {article.get('title', '')}")
        print(f"   摘要长度: {len(article.get('summary', ''))}")
    
    # 获取前N篇文章的详细内容
    popular_articles = []
    for article in sorted_articles[:count * 2]:  # 多获取一些文章，因为有些可能获取不到内容
        print(f"\n正在处理文章: {article.get('title', '')}")
        # 获取文章详细内容
        content_info = fetch_article_content(article['link'])
        article.update(content_info)
        
        # 只有成功获取到内容的文章才加入热门列表
        if 'content' in article and article['content'] and len(article['content']) > 300:
            print(f"成功获取到内容，长度: {len(article['content'])}")
            popular_articles.append(article)
        else:
            print("未获取到有效内容")
        
        # 如果已经获取到足够的文章，就停止
        if len(popular_articles) >= count:
            break
        
        # 添加延时，避免请求过于频繁
        time.sleep(1)
    
    # 如果获取到的文章数量不够，就返回所有获取到的文章
    print(f"\n最终筛选出 {len(popular_articles)} 篇热门文章")
    return popular_articles[:count]

class ArticleAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatOpenAI(
            base_url="https://apis.iflow.cn/v1",
            api_key=DASHSCOPE_API_KEY,
            model=AI_MODEL_NAME,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Define tools
        self.tools = [
            fetch_articles_from_rss,
            fetch_article_content,
            fetch_article_content_with_playwright,
            get_popular_articles
        ]
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant that helps fetch and process articles from Jiqizhixin website. "
                      "You can fetch articles from RSS, get article content, and identify popular articles. "
                      "Use the appropriate tools to complete the user's request."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Create the agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def run(self, input_text: str) -> str:
        """Run the agent with the given input."""
        result = self.agent_executor.invoke({"input": input_text})
        return result["output"]