"""
MCP客户端文件
在Langchain agent中集成MCP工具
"""
from langchain.tools import tool
from typing import List, Dict, Any
import json
from datetime import datetime
import os

# 尝试导入MCP相关模块
try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
    MCP_AVAILABLE = True
    print("MCP模块导入成功")
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"MCP模块导入失败: {e}")

class MCPClient:
    """MCP客户端包装类"""
    
    def __init__(self):
        self.mcp_available = MCP_AVAILABLE
        if self.mcp_available:
            # 定义MCP服务器参数
            self.server_params = StdioServerParameters(
                command="python",
                args=["-m", "small_redbook.mcp.tools"]
            )
    
    async def get_current_time(self) -> str:
        """获取当前时间"""
        if self.mcp_available:
            try:
                async with stdio_client(self.server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        # 调用MCP工具
                        result = await session.call_tool("get_current_time", {})
                        return result.content if result.content else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"MCP调用失败: {e}")
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    async def format_article_info(self, title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
        """格式化文章信息"""
        if self.mcp_available:
            try:
                async with stdio_client(self.server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        # 调用MCP工具
                        params = {
                            "title": title,
                            "content": content,
                            "tags": tags or []
                        }
                        result = await session.call_tool("format_article_info", params)
                        if result.content:
                            return json.loads(result.content)
            except Exception as e:
                print(f"MCP调用失败: {e}")
        
        # 默认实现
        return {
            "title": title,
            "content": content[:2000],
            "tags": tags or []
        }
    
    async def save_xiaohongshu_copy(self, title: str, content: str, original_title: str, tags: List[str] = None) -> str:
        """保存小红书文案"""
        if self.mcp_available:
            try:
                async with stdio_client(self.server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        # 调用MCP工具
                        params = {
                            "title": title,
                            "content": content,
                            "original_title": original_title,
                            "tags": tags or []
                        }
                        result = await session.call_tool("save_xiaohongshu_copy", params)
                        if result.content:
                            return result.content
            except Exception as e:
                print(f"MCP调用失败: {e}")
        
        # 默认实现
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_title = "".join(c for c in original_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title[:20] if len(clean_title) > 20 else clean_title
        filename = f"output/{timestamp}_{clean_title}.txt"
        
        # 确保output目录存在
        os.makedirs("output", exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write("小红书文案:\n")
            f.write(f"标题: {title}\n")
            f.write(f"内容: {content}\n")
            f.write(f"标签: {', '.join(tags or [])}\n")
        
        return f"文案已保存到 {filename}"

# 创建全局MCP客户端实例
mcp_client = MCPClient()

# 定义Langchain工具
@tool
async def get_current_time_tool() -> str:
    """获取当前时间的工具"""
    return await mcp_client.get_current_time()

@tool
async def format_article_info_tool(title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
    """格式化文章信息的工具"""
    return await mcp_client.format_article_info(title, content, tags)

@tool
async def save_xiaohongshu_copy_tool(title: str, content: str, original_title: str, tags: List[str] = None) -> str:
    """保存小红书文案的工具"""
    return await mcp_client.save_xiaohongshu_copy(title, content, original_title, tags)