import json
import os
from openai import OpenAI
from config import DASHSCOPE_API_KEY, AI_MODEL_NAME

def generate_xiaohongshu_copy(article_info):
    """
    调用AI模型生成小红书风格的文案
    :param article_info: 文章信息
    :return: 生成的文案
    """
    try:
        # 初始化OpenAI客户端
        client = OpenAI(
            base_url="https://apis.iflow.cn/v1",
            api_key=DASHSCOPE_API_KEY,
        )
        
        # 使用配置文件中的模型名称
        print(f"正在调用文本模型: {AI_MODEL_NAME}")
        
        # 构造提示词
        prompt = f"""
        请根据以下文章信息，生成一篇小红书风格的文案，包含标题、正文内容和标签。

        文章标题: {article_info['title']}
        文章内容: {article_info['content'][:2000]}  # 限制内容长度
        
        要求:
        1. 标题要有吸引力，使用小红书常用的emoji，单独一行返回
        2. 正文内容要通俗易懂，面向普通读者，使用小红书风格的语言，单独一行返回
        3. 标签要以#开头，用空格分隔，单独一行返回
        4. 严格按照以下格式返回，不要包含其他解释文字:
        [标题开始]
        你的标题内容
        [标题结束]
        [正文开始]
        你的正文内容
        [正文结束]
        [标签开始]
        #标签1 #标签2 #标签3 #标签4 #标签5 #标签6 #标签7 #标签8
        [标签结束]
        """
        
        # 调用模型
        response = client.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个小红书文案专家，擅长将科技类文章转换为小红书风格的文案。严格按照指定格式返回内容，不要包含其他解释文字。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        print("API调用完成")
        
        # 检查响应是否有效
        if not response:
            print("API返回空响应")
            return None
            
        # 检查是否有错误
        if hasattr(response, 'error_code') and response.error_code:
            print(f"API返回错误: {response.message}")
            return None
            
        # 获取响应内容
        result = None
        if hasattr(response, 'choices') and response.choices:
            if response.choices[0] and hasattr(response.choices[0], 'message'):
                if hasattr(response.choices[0].message, 'content'):
                    result = response.choices[0].message.content
        
        # 如果上面的方法失败，尝试其他方式获取响应内容
        if not result:
            # 尝试直接获取响应内容
            if hasattr(response, 'content'):
                result = response.content
            # 尝试转换为字符串
            elif hasattr(response, '__str__'):
                result = str(response)
        
        print(f"生成的文案内容: {result}")
        
        # 确保返回有效数据
        if not result:
            print("模型返回空结果")
            return None
            
        # 检查是否是错误信息
        if "error" in result.lower() or "ErrorMsg" in result:
            print("模型返回错误信息")
            return None
            
        # 解析自定义格式的内容
        try:
            # 提取标题
            title_start = result.find("[标题开始]")
            title_end = result.find("[标题结束]")
            if title_start != -1 and title_end != -1:
                title = result[title_start+6:title_end].strip()
            else:
                print("无法找到标题")
                return None
                
            # 提取正文
            content_start = result.find("[正文开始]")
            content_end = result.find("[正文结束]")
            if content_start != -1 and content_end != -1:
                content = result[content_start+6:content_end].strip()
            else:
                print("无法找到正文")
                return None
                
            # 提取标签
            tags_start = result.find("[标签开始]")
            tags_end = result.find("[标签结束]")
            if tags_start != -1 and tags_end != -1:
                tags_str = result[tags_start+6:tags_end].strip()
                # 按空格分割标签
                tags = [tag.strip() for tag in tags_str.split() if tag.strip().startswith('#')]
            else:
                print("无法找到标签")
                return None
                
            # 构造返回数据
            copy_data = {
                'title': title,
                'content': content,
                'tags': tags
            }
            
            print("内容解析成功")
            return copy_data
            
        except Exception as e:
            print(f"内容解析错误: {e}")
            return None
        
    except Exception as e:
        print(f"生成小红书文案失败: {e}")
        import traceback
        traceback.print_exc()
        return None