# MCP模块初始化文件

# 导出主要的MCP客户端
from .client import mcp_client, third_party_tool

# 导出MCP服务器管理器
from .server_manager import mcp_server_manager

# 导出MCP工具注册器
from .tool_registrar import initialize_tool_registrar

# 注意：第三方工具需要在配置文件中启用相应的服务才能使用
# 从third_party_tools导入工具（如果已定义）
try:
    from .third_party_tools import *
except ImportError:
    pass

__all__ = [
    "mcp_client",
    "third_party_tool",
    "mcp_server_manager",
    "initialize_tool_registrar"
]