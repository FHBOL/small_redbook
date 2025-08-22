import time
import schedule
from config import SCHEDULE_TIME
from data_fetcher import fetch_articles_from_rss, get_popular_articles
from copy_generator import generate_xiaohongshu_copy
import os
from datetime import datetime
import re

def job():
    """
    定时任务执行函数
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[{current_time}] 开始执行任务...")
    
    # 创建输出目录
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 1. 获取文章列表
    articles = fetch_articles_from_rss()
    if not articles:
        print("未获取到文章列表")
        return
    
    print(f"获取到 {len(articles)} 篇文章")
    
    # 2. 筛选热门文章
    popular_articles = get_popular_articles(articles)
    if not popular_articles:
        print("未筛选到热门文章")
        return
    
    print(f"筛选出 {len(popular_articles)} 篇热门文章")
    
    # 3. 生成小红书文案
    for i, article in enumerate(popular_articles):
        print(f"正在生成第 {i+1} 篇文章的小红书文案: {article.get('title', '')}")
        xiaohongshu_copy = generate_xiaohongshu_copy(article)
        if xiaohongshu_copy:
            print(f"生成小红书文案成功: {xiaohongshu_copy.get('title', '')}")
            # 保存到文件，文件名包含时间戳
            # 清理标题中的特殊字符
            clean_title = re.sub(r'[^\w\s-]', '', article.get('title', 'unknown')[:10])
            clean_title = re.sub(r'[-\s]+', '_', clean_title).strip('_')
            
            filename = f"output/{timestamp}_{i+1}_{clean_title}.txt"
            
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

def run_scheduler():
    """
    启动定时任务调度器
    """
    # 设置定时任务
    schedule.every().day.at(SCHEDULE_TIME).do(job)
    
    print(f"定时任务已启动，每天 {SCHEDULE_TIME} 执行")
    
    # 持续运行调度器
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

def run_once():
    """
    立即执行一次任务
    """
    print("立即执行一次任务...")
    job()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 立即执行一次
        run_once()
    else:
        # 启动定时任务
        run_scheduler()