from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, List
import os
import re
import json
from datetime import datetime
from config import DASHSCOPE_API_KEY, AI_MODEL_NAME, OUTPUT_DIR, TOP_ARTICLES_COUNT
from agents.article_agent import ArticleAgent, fetch_articles_from_rss, get_popular_articles
from agents.copy_agent import CopyAgent

class MainAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatOpenAI(
            base_url="https://apis.iflow.cn/v1",
            api_key=DASHSCOPE_API_KEY,
            model=AI_MODEL_NAME,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Initialize sub-agents
        self.article_agent = ArticleAgent()
        self.copy_agent = CopyAgent()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
    
    def process_articles(self) -> None:
        """
        处理文章并生成小红书文案
        """
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"[{current_time}] 开始执行任务...")
        
        # 1. 获取文章列表
        print("正在获取文章列表...")
        articles = fetch_articles_from_rss.invoke({})
        if not articles:
            print("未获取到文章列表")
            return
        
        print(f"获取到 {len(articles)} 篇文章")
        
        # 2. 筛选热门文章
        print("正在筛选热门文章...")
        popular_articles = get_popular_articles.invoke({"articles": articles, "count": TOP_ARTICLES_COUNT})
        if not popular_articles:
            print("未筛选到热门文章")
            return
        
        print(f"筛选出 {len(popular_articles)} 篇热门文章")
        
        # 3. 生成小红书文案
        for i, article in enumerate(popular_articles):
            print(f"正在生成第 {i+1} 篇文章的小红书文案: {article.get('title', '')}")
            xiaohongshu_copy = self.copy_agent.generate_xiaohongshu_copy(article)
            if xiaohongshu_copy:
                print(f"生成小红书文案成功: {xiaohongshu_copy.get('title', '')}")
                # 保存到文件，文件名包含时间戳
                # 清理标题中的特殊字符
                clean_title = re.sub(r'[^\w\s-]', '', article.get('title', 'unknown')[:10])
                clean_title = re.sub(r'[-\s]+', '_', clean_title).strip('_')
                
                filename = f"{OUTPUT_DIR}/{timestamp}_{i+1}_{clean_title}.txt"
                
                with open(filename, "w", encoding="utf-8") as f:
                    # 写入时间信息
                    f.write(f"生成时间: {current_time}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # 写入原始文章信息
                    f.write("原始文章信息:\n")
                    f.write(f"标题: {article.get('title', '')}\n")
                    f.write(f"链接: {article.get('link', '')}\n")
                    f.write(f"发布时间: {article.get('published', '')}\n")
                    f.write(f"摘要: {article.get('summary', '')}\n")
                    # 写入完整正文内容
                    f.write(f"正文内容: {article.get('content', '')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # 写入生成的小红书文案
                    f.write("生成的小红书文案:\n")
                    f.write(f"标题: {xiaohongshu_copy.get('title', '')}\n")
                    f.write(f"内容: {xiaohongshu_copy.get('content', '')}\n")
                    f.write(f"标签: {', '.join(xiaohongshu_copy.get('tags', []))}\n")
            else:
                print(f"生成小红书文案失败: {article.get('title', '')}")
        
        print(f"[{current_time}] 任务执行完成")
    
    def run_once(self) -> None:
        """
        立即执行一次任务
        """
        print("立即执行一次任务...")
        self.process_articles()