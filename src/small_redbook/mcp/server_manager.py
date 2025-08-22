"""
MCP服务器管理器
用于管理本地和第三方MCP服务器
"""
import json
import os
import subprocess
import asyncio
import configparser
from typing import Dict, Any, Optional, List

class MCPServerManager:
    """MCP服务器管理器"""
    
    def __init__(self, config_file: str = "mcp-config.json", auto_config_file: str = None):
        self.config_file = config_file
        self.auto_config_file = auto_config_file or os.path.join(os.path.dirname(__file__), "auto_config.ini")
        self.servers: Dict[str, subprocess.Popen] = {}
        self.config: Dict[str, Any] = {}
        self.auto_config: configparser.ConfigParser = configparser.ConfigParser()
        self.load_config()
        self.load_auto_config()
    
    def load_config(self):
        """加载MCP服务器配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            print(f"加载了 {len(self.config.get('mcpServers', {}))} 个MCP服务器配置")
        else:
            print(f"配置文件 {self.config_file} 不存在")
            self.config = {"mcpServers": {}}
    
    def load_auto_config(self):
        """加载自动集成配置"""
        if os.path.exists(self.auto_config_file):
            self.auto_config.read(self.auto_config_file)
            print(f"加载了自动集成配置: {self.auto_config_file}")
        else:
            print(f"自动集成配置文件 {self.auto_config_file} 不存在")
    
    def is_auto_integration_enabled(self) -> bool:
        """检查是否启用了MCP自动集成功能"""
        if 'general' in self.auto_config:
            return self.auto_config.getboolean('general', 'enable_mcp_auto_integration', fallback=False)
        return False
    
    def get_auto_start_servers(self) -> List[str]:
        """获取需要自动启动的服务器列表"""
        servers = []
        if 'mcp_servers' in self.auto_config:
            for server_name, enabled in self.auto_config['mcp_servers'].items():
                if enabled.lower() == 'true':
                    servers.append(server_name)
        return servers
    
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
    
    def auto_start_configured_servers(self):
        """自动启动配置的服务器"""
        if not self.is_auto_integration_enabled():
            print("MCP自动集成功能未启用")
            return
        
        auto_start = self.auto_config.getboolean('general', 'auto_start_servers', fallback=True)
        if not auto_start:
            print("自动启动服务器功能未启用")
            return
        
        servers_to_start = self.get_auto_start_servers()
        if not servers_to_start:
            print("未配置需要自动启动的服务器")
            # 如果没有明确配置，启动所有服务器
            servers_to_start = list(self.config.get("mcpServers", {}).keys())
        
        print(f"自动启动MCP服务器: {servers_to_start}")
        for server_name in servers_to_start:
            self.start_server(server_name)

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