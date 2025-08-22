"""
MCP客户端文件
在Langchain agent中集成MCP工具
"""
from langchain.tools import tool
from typing import List, Dict, Any
import json
from datetime import datetime
import os
import configparser
from urllib.parse import urljoin

# 尝试导入MCP相关模块
try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.client.sse import sse_client
    MCP_AVAILABLE = True
    print("MCP模块导入成功")
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"MCP模块导入失败: {e}")

class MCPClient:
    """MCP客户端包装类"""
    
    def __init__(self):
        self.mcp_available = MCP_AVAILABLE
        self.third_party_services = {}
        
        if self.mcp_available:
            # 定义本地MCP服务器参数
            self.server_params = StdioServerParameters(
                command="python",
                args=["-m", "small_redbook.mcp.tools"]
            )
            
            # 加载第三方MCP服务配置
            self.load_third_party_config()
    
    def load_third_party_config(self):
        """加载第三方MCP服务配置"""
        config_path = os.path.join(os.path.dirname(__file__), "third_party_config.ini")
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            
            for section in config.sections():
                if config.getboolean(section, "enabled", fallback=False):
                    self.third_party_services[section] = {
                        "url": config.get(section, "url"),
                        "auth_token": config.get(section, "auth_token", fallback=None)
                    }
            print(f"加载了 {len(self.third_party_services)} 个第三方MCP服务")
    
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
    
    async def call_third_party_tool(self, service_name: str, tool_name: str, params: Dict[str, Any]) -> Any:
        """调用第三方MCP服务的工具"""
        if not self.mcp_available or service_name not in self.third_party_services:
            return None
            
        service_config = self.third_party_services[service_name]
        service_url = service_config["url"]
        auth_token = service_config["auth_token"]
        
        try:
            # 根据URL类型选择合适的客户端
            if service_url.startswith("http://") or service_url.startswith("https://"):
                # 检查是否是SSE端点
                if "/sse" in service_url or service_url.endswith(".sse"):
                    async with sse_client(service_url) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            result = await session.call_tool(tool_name, params)
                            return result.content if result.content else None
                else:
                    # 对于HTTP客户端，我们需要使用不同的方法
                    # 这里简化处理，实际项目中可能需要更复杂的实现
                    print(f"HTTP客户端调用暂未实现: {service_url}")
                    return None
            else:
                print(f"不支持的服务URL类型: {service_url}")
                return None
        except Exception as e:
            print(f"调用第三方MCP服务失败: {e}")
            return None

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

# 第三方MCP工具装饰器
def third_party_tool(service_name: str, tool_name: str):
    """创建第三方MCP工具的装饰器"""
    async def tool_func(**kwargs) -> Any:
        """调用第三方MCP工具"""
        return await mcp_client.call_third_party_tool(service_name, tool_name, kwargs)
    
    # 为函数添加文档字符串
    tool_func.__doc__ = f"调用第三方MCP服务 {service_name} 的 {tool_name} 工具"
    
    return tool(tool_func)