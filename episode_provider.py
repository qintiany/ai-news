"""
剧集提供器 v1
从MacCMS note字段提取集数 + 构造精准搜索URL
支持：电视剧/综艺/动漫的集数选择
"""
import re


def parse_episode_info(note_str, name=""):
    """
    从note字段解析集数信息
    "全46集" → total=46, current=46, is_movie=False
    "更新至第11集" → total=None, current=11, is_movie=False  
    "正片" → total=1, current=1, is_movie=True
    "全12期" → total=12, current=12, is_movie=False
    """
    note = note_str.strip() if note_str else ""
    
    # 电影/正片
    if note in ("正片", "HD", "HD高清", "TC", "TS", "DVD"):
        return {"total": 1, "current": 1, "is_movie": True, "unit": ""}
    
    # 匹配 "全XX集" 或 "全XX期" 或 "全XX话"
    m = re.match(r'全\s*(\d+)\s*(集|期|话|回)', note)
    if m:
        num = int(m.group(1))
        return {"total": num, "current": num, "is_movie": False, "unit": m.group(2)}
    
    # 匹配 "更新至第XX集" 或 "更新至XX集"
    m = re.match(r'更新至(?:第)?\s*(\d+)\s*(集|期|话)', note)
    if m:
        num = int(m.group(1))
        return {"total": None, "current": num, "is_movie": False, "unit": m.group(2)}
    
    # 匹配 "第XX集" (单集)
    m = re.match(r'第\s*(\d+)\s*(集|期|话)', note)
    if m:
        num = int(m.group(1))
        return {"total": num, "current": num, "is_movie": False, "unit": m.group(2)}
    
    # 匹配纯数字 "46"
    m = re.match(r'^(\d+)$', note)
    if m:
        num = int(m.group(1))
        return {"total": num, "current": num, "is_movie": False, "unit": "集"}
    
    # 无法解析 → 假设可播
    return {"total": 1, "current": 1, "is_movie": True, "unit": ""}


def generate_episodes(ep_info, name=""):
    """生成剧集列表，用于前端选集网格"""
    episodes = []
    total = ep_info.get("total") or ep_info.get("current") or 1
    unit = ep_info.get("unit", "集")
    
    for i in range(1, total + 1):
        episodes.append({
            "num": i,
            "label": f"第{i}{unit}",
            "search_query": f"{name} 第{i}{unit}",
        })
    
    return episodes


def get_episode_range_for_display(ep_info):
    """
    返回前端展示用的集数范围
    如果 total > 40，分段返回前40集的起始页码
    """
    total = ep_info.get("total") or ep_info.get("current") or 0
    if total <= 60:
        return list(range(1, total + 1))
    
    # 超长剧集 → 分段显示
    ranges = []
    for start in range(1, total + 1, 40):
        end = min(start + 39, total)
        ranges.append({"start": start, "end": end, "label": f"{start}-{end}"})
    return ranges


# ========== 播放URL构建 ==========

from urllib.parse import quote


def build_episode_play_urls(video_name, episode_num, unit="集"):
    """
    为指定剧集构建多平台搜索URL
    返回腾讯/爱奇艺/优酷的精准搜索链接
    """
    query = f"{video_name} 第{episode_num}{unit}"
    encoded = quote(query)
    
    return [
        {
            "platform": "腾讯视频", "icon": "🐧",
            "url": f"https://v.qq.com/x/search/?q={encoded}",
            "search_query": query,
        },
        {
            "platform": "爱奇艺", "icon": "🥝",
            "url": f"https://so.iqiyi.com/so/q_{encoded}.html",
            "search_query": query,
        },
        {
            "platform": "优酷", "icon": "▶️",
            "url": f"https://so.youku.com/search_video/q_{encoded}",
            "search_query": query,
        },
    ]


def build_movie_play_urls(video_name):
    """为电影构建播放URL"""
    encoded = quote(video_name)
    return [
        {
            "platform": "腾讯视频", "icon": "🐧",
            "url": f"https://v.qq.com/x/search/?q={encoded}",
        },
        {
            "platform": "爱奇艺", "icon": "🥝",
            "url": f"https://so.iqiyi.com/so/q_{encoded}.html",
        },
        {
            "platform": "优酷", "icon": "▶️",
            "url": f"https://so.youku.com/search_video/q_{encoded}",
        },
    ]
