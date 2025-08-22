import time
import schedule
from config import SCHEDULE_TIME
import os
from datetime import datetime

# 尝试导入MCP相关模块
try:
    from .mcp import mcp_server_manager
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

def job():
    """
    定时任务执行函数
    """
    # 导入并运行主agent
    from agents.main_agent import MainAgent
    agent = MainAgent()
    agent.process_articles()
    
    # 如果MCP可用，停止所有服务器
    if MCP_AVAILABLE:
        mcp_server_manager.stop_all_servers()

def run_scheduler():
    """
    启动定时任务调度器
    """
    # 如果MCP可用，自动启动配置的服务器
    if MCP_AVAILABLE:
        mcp_server_manager.auto_start_configured_servers()
    
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
    # 如果MCP可用，自动启动配置的服务器
    if MCP_AVAILABLE:
        mcp_server_manager.auto_start_configured_servers()
    
    job()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 立即执行一次
        run_once()
    else:
        # 启动定时任务
        run_scheduler()