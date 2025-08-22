import time
import schedule
from config import SCHEDULE_TIME
import os
from datetime import datetime

def job():
    """
    定时任务执行函数
    """
    # 导入并运行主agent
    from agents.main_agent import MainAgent
    agent = MainAgent()
    agent.process_articles()

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