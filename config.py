import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for the small redbook project

# Jiqizhixin website configuration
JIQIZHIXIN_RSS_URL = os.getenv("JIQIZHIXIN_RSS_URL", "https://www.jiqizhixin.com/rss.xml")

# Popular articles configuration
TOP_ARTICLES_COUNT = int(os.getenv("TOP_ARTICLES_COUNT", "5"))

# Schedule configuration
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")

# AI model configuration
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "kimi-k2")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# Output directory
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")