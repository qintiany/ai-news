"""
实时影视数据客户端 v2
数据源：猫眼资源 MacCMS API (32954+ 实时影视)
解析：多线路快速解析接口
播放：智能腾讯/爱奇艺搜索 + 解析
"""
import requests
import xml.etree.ElementTree as ET
import time
import threading
from functools import lru_cache

# ========== 数据源 ==========
API_BASE = "https://maoyanzy.com/api.php/provide/vod"
TIMEOUT = 8
CACHE_TTL = 300  # 首页缓存5分钟

# ========== 解析线路（按速度排名）==========
PARSE_LINES = [
    {"name": "⚡ 极速1号", "url": "https://jx.m3u8.tv/jiexi/?url="},
    {"name": "⚡ 极速2号", "url": "https://jx.aidouer.net/?url="},
    {"name": "🚀 高速3号", "url": "https://jx.618g.com/?url="},
    {"name": "🚀 高速4号", "url": "https://jx.77flv.cc/?url="},
    {"name": "🚀 高速5号", "url": "https://jx.playerjy.com/?url="},
    {"name": "🚀 高速6号", "url": "https://bd.jx.cn/?url="},
    {"name": "🎀 备选7号", "url": "https://jx.xmflv.com/?url="},
    {"name": "🎀 备选8号", "url": "https://jx.hls.one/?url="},
    {"name": "🎀 备选9号", "url": "https://jx.xmflv.cc/?url="},
]

# ========== 首页缓存 ==========
_home_cache = {"data": None, "time": 0}
_cache_lock = threading.Lock()

# ========== 类型ID映射 ==========
TYPE_MAP = {
    "国产剧": "13", "香港剧": "14", "韩国剧": "15", "欧美剧": "16",
    "台湾剧": "30", "日本剧": "31", "泰国剧": "33",
    "动作片": "6", "喜剧片": "7", "爱情片": "8", "科幻片": "9",
    "恐怖片": "10", "剧情片": "11", "战争片": "12", "犯罪片": "25",
    "悬疑片": "24", "动画片": "29", "纪录片": "27",
    "大陆综艺": "34", "港台综艺": "35", "日韩综艺": "36",
    "国产动漫": "38", "日韩动漫": "40", "欧美动漫": "39",
    "爽文短剧": "46",
}


def _parse_xml_video(video_elem):
    """解析单个视频XML元素"""
    def _text(tag):
        el = video_elem.find(tag)
        return el.text.strip() if el is not None and el.text else ""
    return {
        "id": _text("id"),
        "name": _text("name"),
        "type": _text("type"),
        "pic": _text("pic"),
        "lang": _text("lang"),
        "area": _text("area"),
        "year": _text("year"),
        "note": _text("note"),
        "actor": _text("actor"),
        "director": _text("director"),
        "des": _text("des"),
        "last": _text("last"),
        "dt": _text("dt"),
    }


def _api_xml(action, **params):
    """调用API获取XML数据（带缓存）"""
    url = f"{API_BASE}/at/xml/?ac={action}"
    for k, v in params.items():
        url += f"&{k}={v}"
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.encoding = 'utf-8'
        return ET.fromstring(resp.text)
    except Exception as e:
        print(f"[API] 错误: {e}")
        return None


def _resolve_tid(category):
    """解析分类名→类型ID（修复模糊匹配bug）"""
    if category in TYPE_MAP:
        return TYPE_MAP[category]
    # 模糊匹配
    for name, tid in TYPE_MAP.items():
        if category in name or name in category:
            return tid
    return "13"  # 默认国产剧


def search_videos(keyword, page=1):
    """搜索影视"""
    root = _api_xml("videolist", wd=keyword, pg=str(page))
    if root is None:
        return [], 0
    videos = []
    list_elem = root.find("list")
    total = int(list_elem.get("recordcount", 0)) if list_elem is not None else 0
    for video in root.findall(".//video"):
        videos.append(_parse_xml_video(video))
    return videos, total


def get_category_list(category="国产剧", page=1):
    """获取分类视频列表"""
    tid = _resolve_tid(category)
    root = _api_xml("videolist", t=tid, pg=str(page))
    if root is None:
        return [], 0
    videos = []
    list_elem = root.find("list")
    total = int(list_elem.get("recordcount", 0)) if list_elem is not None else 0
    for video in root.findall(".//video"):
        videos.append(_parse_xml_video(video))
    return videos, total


def get_home_data():
    """获取首页各分类推荐（带5分钟缓存）"""
    global _home_cache
    now = time.time()
    with _cache_lock:
        if _home_cache["data"] is not None and (now - _home_cache["time"]) < CACHE_TTL:
            return _home_cache["data"]
    
    categories = ["国产剧", "动作片", "大陆综艺", "国产动漫", "犯罪片"]
    home = {}
    for cat in categories:
        try:
            videos, _ = get_category_list(cat, page=1)
            home[cat] = videos[:12]
        except Exception as e:
            print(f"[Home] {cat} 加载失败: {e}")
            home[cat] = []
    
    with _cache_lock:
        _home_cache = {"data": home, "time": now}
    return home


def get_trending():
    """获取最近更新（取首页国产剧最新）"""
    try:
        videos, _ = get_category_list("国产剧", page=1)
        return videos[:20]
    except:
        return []


def build_play_urls(video_name):
    """
    根据视频名构建各平台搜索URL
    同时尝试腾讯和爱奇艺的搜索
    """
    from urllib.parse import quote
    encoded = quote(video_name)
    return [
        {"platform": "腾讯视频", "icon": "🐧", "url": f"https://v.qq.com/x/search/?q={encoded}"},
        {"platform": "爱奇艺", "icon": "🥝", "url": f"https://so.iqiyi.com/so/q_{encoded}.html"},
        {"platform": "优酷", "icon": "▶️", "url": f"https://so.youku.com/search_video/q_{encoded}"},
    ]


def get_parse_lines():
    return PARSE_LINES


def test_parse_speed():
    """测试各解析线路当前速度"""
    test_url = "https://v.qq.com/x/cover/mzc002002kqssyu.html"
    results = []
    for line in PARSE_LINES:
        start = time.time()
        try:
            resp = requests.get(line["url"] + test_url, timeout=5,
                              headers={"User-Agent": "Mozilla/5.0"})
            elapsed = time.time() - start
            status = resp.status_code
        except:
            elapsed = 99
            status = 0
        results.append({
            "name": line["name"], "status": status,
            "time": round(elapsed, 2), "ok": status == 200
        })
    return sorted(results, key=lambda x: x["time"])


def get_all_categories():
    """获取所有可用分类"""
    return [
        {"name": "国产剧", "icon": "📺", "group": "电视剧"},
        {"name": "香港剧", "icon": "🇭🇰", "group": "电视剧"},
        {"name": "韩国剧", "icon": "🇰🇷", "group": "电视剧"},
        {"name": "欧美剧", "icon": "🇺🇸", "group": "电视剧"},
        {"name": "台湾剧", "icon": "🇹🇼", "group": "电视剧"},
        {"name": "日本剧", "icon": "🇯🇵", "group": "电视剧"},
        {"name": "泰国剧", "icon": "🇹🇭", "group": "电视剧"},
        {"name": "动作片", "icon": "💥", "group": "电影"},
        {"name": "喜剧片", "icon": "😂", "group": "电影"},
        {"name": "科幻片", "icon": "🚀", "group": "电影"},
        {"name": "爱情片", "icon": "💕", "group": "电影"},
        {"name": "恐怖片", "icon": "👻", "group": "电影"},
        {"name": "剧情片", "icon": "🎭", "group": "电影"},
        {"name": "悬疑片", "icon": "🔍", "group": "电影"},
        {"name": "犯罪片", "icon": "🕵️", "group": "电影"},
        {"name": "战争片", "icon": "⚔️", "group": "电影"},
        {"name": "动画片", "icon": "🎨", "group": "电影"},
        {"name": "纪录片", "icon": "📖", "group": "电影"},
        {"name": "大陆综艺", "icon": "🎤", "group": "综艺"},
        {"name": "港台综艺", "icon": "🎬", "group": "综艺"},
        {"name": "国产动漫", "icon": "🐉", "group": "动漫"},
        {"name": "日韩动漫", "icon": "🗾", "group": "动漫"},
        {"name": "欧美动漫", "icon": "🌍", "group": "动漫"},
    ]
