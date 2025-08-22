import os
import sys

def main():
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # 解析命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 立即执行一次任务
        from agents.main_agent import MainAgent
        agent = MainAgent()
        agent.run_once()
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