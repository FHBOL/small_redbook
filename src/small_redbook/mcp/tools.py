"""
MCP工具定义文件
定义与小红书文案生成相关的MCP工具
"""
from mcp.types import Tool
from mcp.server import FastMCP
from mcp.server.stdio import stdio_server
from typing import List, Dict, Any
import asyncio
from datetime import datetime
import json

# 创建MCP服务器实例
app = FastMCP("small-redbook-mcp-server")

# 定义MCP工具
@app.tool()
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.tool()
def format_article_info(title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
    """格式化文章信息"""
    return {
        "title": title,
        "content": content[:2000],  # 限制内容长度
        "tags": tags or []
    }

@app.tool()
def save_xiaohongshu_copy(title: str, content: str, original_title: str, tags: List[str] = None) -> str:
    """保存小红书文案"""
    # 这里可以实现保存到文件的逻辑
    result = {
        "title": title,
        "content": content,
        "tags": tags or [],
        "original_title": original_title,
        "saved_at": datetime.now().isoformat()
    }
    return json.dumps(result, ensure_ascii=False)

# 主函数，用于启动MCP服务器
async def main():
    """启动MCP服务器"""
    await app.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())