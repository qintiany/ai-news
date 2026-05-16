"""
AI新闻抓取器 - 多源RSS聚合 + YouTube RSS
"""
import feedparser
import time
import re
import requests
from datetime import datetime, timedelta, timezone
from config import RSS_FEEDS, YOUTUBE_CHANNELS
from database import init_db, insert_news, update_hot_scores, cleanup_old_news

# YouTube RSS URL模板
YOUTUBE_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id={}"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def clean_html(raw_html):
    """去除HTML标签，提取纯文本"""
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext.strip()


def truncate(text, length=200):
    """截断文本"""
    if not text:
        return ""
    text = clean_html(text)
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "..."


def parse_date(entry):
    """解析RSS中的日期"""
    for key in ["published_parsed", "updated_parsed"]:
        if hasattr(entry, key) and getattr(entry, key):
            t = getattr(entry, key)
            return datetime(*t[:6], tzinfo=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def extract_image(entry):
    """从RSS条目中提取封面图"""
    # 尝试 media:content / media:thumbnail
    if "media_content" in entry and entry.media_content:
        for mc in entry.media_content:
            if "url" in mc:
                return mc["url"]
    if "media_thumbnail" in entry and entry.media_thumbnail:
        for mt in entry.media_thumbnail:
            if "url" in mt:
                return mt["url"]
    # 尝试 enclosures
    if "enclosures" in entry and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href", "")
    # 尝试 links 中的 image
    if "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image/"):
                return link.get("href", "")
    # 尝试从 summary 中提取 img 标签
    summary = entry.get("summary", entry.get("description", ""))
    if summary:
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', summary, re.I)
        if img_match:
            return img_match[1]
    return ""


def fetch_rss_feed(feed_info):
    """抓取单个RSS源"""
    results = []
    try:
        resp = requests.get(feed_info["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        
        if feed.bozo and not feed.entries:
            print(f"  ⚠️ {feed_info['name']}: 解析失败 - {feed.bozo_exception}")
            return results
        
        for entry in feed.entries[:8]:  # 每个源取最新8条(增加数量)
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            published = parse_date(entry)
            image = extract_image(entry)
            
            if title and link:
                results.append({
                    "title": title,
                    "url": link,
                    "summary": truncate(summary),
                    "source": feed_info["name"],
                    "category": feed_info["category"],
                    "published_at": published,
                    "image": image,
                })
        
        print(f"  ✅ {feed_info['name']}: {len(results)}条")
    except requests.Timeout:
        print(f"  ⏱️ {feed_info['name']}: 超时")
    except Exception as e:
        print(f"  ❌ {feed_info['name']}: {e}")
    
    return results


def fetch_youtube(channel_info):
    """抓取YouTube频道最新视频"""
    results = []
    try:
        url = YOUTUBE_RSS.format(channel_info["channel_id"])
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        
        for entry in feed.entries[:5]:  # 每个频道取最新5条(增加数量)
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            published = parse_date(entry)
            image = extract_image(entry)
            
            if title and link:
                results.append({
                    "title": f"🎬 {title}",
                    "url": link,
                    "summary": truncate(summary),
                    "source": channel_info["name"],
                    "category": "YouTube",
                    "published_at": published,
                    "image": image,
                })
        
        print(f"  ✅ {channel_info['name']}: {len(results)}条")
    except Exception as e:
        print(f"  ❌ {channel_info['name']}: {e}")
    
    return results


def fetch_all():
    """抓取全部源并入库"""
    print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] 开始抓取AI新闻...")
    all_news = []
    
    # 抓取RSS源
    for feed in RSS_FEEDS:
        news = fetch_rss_feed(feed)
        all_news.extend(news)
        time.sleep(0.3)  # 礼貌间隔
    
    # 抓取YouTube
    for channel in YOUTUBE_CHANNELS:
        news = fetch_youtube(channel)
        all_news.extend(news)
        time.sleep(0.3)
    
    # 入库（URL去重）
    saved = 0
    for item in all_news:
        if insert_news(
            title=item["title"],
            url=item["url"],
            summary=item["summary"],
            source=item["source"],
            category=item["category"],
            published_at=item["published_at"],
            image=item.get("image", ""),
        ):
            saved += 1
    
    # 更新热度 & 清理
    update_hot_scores()
    cleanup_old_news()
    
    print(f"📊 本次抓取: {len(all_news)}条, 新增: {saved}条\n")
    return len(all_news), saved


if __name__ == "__main__":
    init_db()
    fetch_all()
