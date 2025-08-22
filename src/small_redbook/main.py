import os
import sys
import argparse

def main():
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='小红书文案生成器')
    parser.add_argument('--once', action='store_true', help='立即执行一次任务')
    parser.add_argument('--mcp', action='store_true', help='启用MCP模式')
    
    args = parser.parse_args()
    
    if args.once:
        # 立即执行一次任务
        from agents.main_agent import MainAgent
        agent = MainAgent()
        agent.run_once()
    elif args.mcp:
        # 启动MCP服务器模式
        try:
            from mcp import ClientSession
            from mcp.client.stdio import stdio_client
            from mcp.types import StdioServerParameters
            import asyncio
            
            # 启动MCP服务器
            print("启动MCP服务器模式...")
            os.system("python -m small_redbook.mcp.tools")
        except ImportError:
            print("MCP模块未安装，请先安装langchain-mcp和mcp包")
    else:
        # 创建输出目录
        from config import OUTPUT_DIR
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        # 启动定时任务
        from scheduler import run_scheduler
        run_scheduler()

if __name__ == "__main__":
    main()