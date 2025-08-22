"""
第三方MCP工具示例
演示如何使用第三方MCP服务
"""
from langchain.tools import tool
from .client import third_party_tool

# 注意：这些工具需要在third_party_config.ini中配置相应的服务才能使用
# 示例工具定义（需要在配置文件中启用相应的服务）

# 示例：天气查询工具（假设有一个第三方天气服务）
# weather_tool = third_party_tool("weather_service", "get_weather")

# 示例：数据库查询工具（假设有一个第三方数据库服务）
# database_query_tool = third_party_tool("database_service", "query")

# 示例：文件存储工具（假设有一个第三方存储服务）
# storage_upload_tool = third_party_tool("storage_service", "upload_file")

# 使用说明：
# 1. 在third_party_config.ini中启用相应的服务
# 2. 在agent中注册这些工具
# 3. 在需要时调用这些工具

# 示例用法（在agent中）：
"""
# 在agent的工具列表中添加第三方工具
# 首先检查工具是否已定义
if 'weather_tool' in globals():
    self.tools.append(weather_tool)

# 在处理逻辑中使用
if 'weather_tool' in globals():
    weather = await weather_tool.ainvoke({"city": "北京"})
"""