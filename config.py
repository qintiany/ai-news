# AI News Aggregator - 新闻源配置
# 每1小时抓取一次，去重排序取最新10条

RSS_FEEDS = [
    # === 官方一手信源 ===
    {"name": "OpenAI", "url": "https://openai.com/news/rss.xml", "category": "官方"},
    {"name": "Google AI", "url": "https://blog.google/technology/ai/rss/", "category": "官方"},
    {"name": "Hugging Face", "url": "https://huggingface.co/blog/feed.xml", "category": "官方"},
    {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/feed/", "category": "官方"},
    {"name": "Anthropic", "url": "https://www.anthropic.com/feed.xml", "category": "官方"},
    {"name": "Meta AI", "url": "https://ai.meta.com/feed/", "category": "官方"},
    
    # === 科技媒体 ===
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "媒体"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "category": "媒体"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "category": "媒体"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "category": "媒体"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "媒体"},
    {"name": "Wired AI", "url": "https://www.wired.com/feed/tag/ai/latest/rss", "category": "媒体"},
    
    # === AI 社区/研究 ===
    {"name": "arXiv AI", "url": "https://rss.arxiv.org/rss/cs.AI", "category": "研究"},
    {"name": "MarkTechPost", "url": "https://www.marktechpost.com/feed/", "category": "研究"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "category": "社区"},
    {"name": "Reddit ML", "url": "https://old.reddit.com/r/MachineLearning/.rss", "category": "社区"},
    
    # === AI 简报 ===
    {"name": "Last Week in AI", "url": "https://lastweekin.ai/feed", "category": "简报"},
    {"name": "THE DECODER", "url": "https://the-decoder.com/feed/", "category": "简报"},
]

# YouTube 频道 (通过 RSS)
YOUTUBE_CHANNELS = [
    {"name": "Matt Wolfe", "channel_id": "UCeQxLxuEzMqQ-E4k-d6FVvQ", "category": "YouTube"},
    {"name": "AI Explained", "channel_id": "UCn2vAPnIImYPuYZTQa3qZGA", "category": "YouTube"},
    {"name": "Two Minute Papers", "channel_id": "UCbfYPyITQ-7l4upoX8nvctg", "category": "YouTube"},
    {"name": "Matthew Berman", "channel_id": "UCQoHEEAPIxvXhTQ3cNrMnwA", "category": "YouTube"},
    {"name": "AI Andy", "channel_id": "UC0qryCLcETcMJWRz7FXC3FQ", "category": "YouTube"},
    {"name": "David Shapiro", "channel_id": "UCx9QVEAkL3SXMjzQLDz7GZg", "category": "YouTube"},
    {"name": "The AI Advantage", "channel_id": "UCLXlW4I7P0gFw0rUNwz05mw", "category": "YouTube"},
]

# 每页显示数量
NEWS_PER_PAGE = 10

# 数据保留天数
RETENTION_DAYS = 7

# 抓取间隔(分钟)
FETCH_INTERVAL_MINUTES = 60
