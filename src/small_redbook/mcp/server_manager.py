"""
MCP服务器管理器
用于管理本地和第三方MCP服务器
"""
import json
import os
import subprocess
import asyncio
from typing import Dict, Any, Optional

class MCPServerManager:
    """MCP服务器管理器"""
    
    def __init__(self, config_file: str = "mcp-config.json"):
        self.config_file = config_file
        self.servers: Dict[str, subprocess.Popen] = {}
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """加载MCP服务器配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            print(f"加载了 {len(self.config.get('mcpServers', {}))} 个MCP服务器配置")
        else:
            print(f"配置文件 {self.config_file} 不存在")
            self.config = {"mcpServers": {}}
    
    def start_server(self, server_name: str) -> bool:
        """启动指定的MCP服务器"""
        if server_name not in self.config.get("mcpServers", {}):
            print(f"服务器 {server_name} 未在配置中定义")
            return False
        
        server_config = self.config["mcpServers"][server_name]
        command = server_config["command"]
        args = server_config.get("args", [])
        env = server_config.get("env", {})
        
        try:
            # 合并环境变量
            env_vars = os.environ.copy()
            env_vars.update(env)
            
            # 启动服务器进程
            process = subprocess.Popen(
                [command] + args,
                env=env_vars,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.servers[server_name] = process
            print(f"已启动MCP服务器: {server_name}")
            return True
        except Exception as e:
            print(f"启动MCP服务器 {server_name} 失败: {e}")
            return False
    
    def stop_server(self, server_name: str):
        """停止指定的MCP服务器"""
        if server_name in self.servers:
            process = self.servers[server_name]
            process.terminate()
            process.wait()
            del self.servers[server_name]
            print(f"已停止MCP服务器: {server_name}")
    
    def stop_all_servers(self):
        """停止所有MCP服务器"""
        for server_name in list(self.servers.keys()):
            self.stop_server(server_name)
    
    def list_servers(self) -> Dict[str, Any]:
        """列出所有配置的服务器"""
        return self.config.get("mcpServers", {})
    
    def get_server_status(self, server_name: str) -> str:
        """获取服务器状态"""
        if server_name not in self.config.get("mcpServers", {}):
            return "未配置"
        
        if server_name in self.servers:
            process = self.servers[server_name]
            if process.poll() is None:
                return "运行中"
            else:
                return "已停止"
        else:
            return "未启动"

# 创建全局MCP服务器管理器实例
mcp_server_manager = MCPServerManager()

# 示例用法：
"""
# 启动Playwright MCP服务器
mcp_server_manager.start_server("playwright")

# 启动文件系统MCP服务器
mcp_server_manager.start_server("filesystem")

# 查看所有服务器状态
for name in mcp_server_manager.list_servers():
    status = mcp_server_manager.get_server_status(name)
    print(f"{name}: {status}")
"""