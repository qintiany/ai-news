"""
AI News Hub + 实时影视中心
新闻聚合 + 猫眼资源实时API + 快速解析播放
"""
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import threading

from database import init_db, get_latest_news, get_stats, get_categories, get_sources
from fetcher import fetch_all
from config import FETCH_INTERVAL_MINUTES
from api_client import (
    search_videos, get_category_list, get_home_data, get_trending,
    get_parse_lines, get_all_categories, test_parse_speed, build_play_urls
)

app = Flask(__name__)
init_db()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_all, 'interval', minutes=FETCH_INTERVAL_MINUTES, id='fetch_news', next_run_time=None)
    scheduler.start()
    print("⏰ 定时抓取已启动")

threading.Timer(10, start_scheduler).start()


# ==================== 首页 ====================
@app.route("/")
def index():
    page = int(request.args.get('page', 1))
    per_page = 20
    category = request.args.get('category', '全部')
    source = request.args.get('source', '全部')
    offset = (page - 1) * per_page
    news_list, total = get_latest_news(limit=per_page, offset=offset, category=category, source=source)
    stats = get_stats()
    cats = get_categories()
    srcs = get_sources()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_pages = (total + per_page - 1) // per_page

    # 首页数据（带容错）
    try:
        home_data = get_home_data()
    except:
        home_data = {}
    try:
        trending = get_trending()
    except:
        trending = []
    cats_video = get_all_categories()

    return render_template("index.html",
        active_tab="news",
        news=news_list, stats=stats, now=now,
        categories=cats, sources=srcs,
        page=page, total_pages=total_pages, total=total,
        current_category=category, current_source=source,
        per_page=per_page,
        parse_lines=get_parse_lines(),
        video_categories=cats_video,
        home_data=home_data,
        trending=trending,
    )


# ==================== 影视页 ====================
@app.route("/video")
def video_page():
    from database import get_categories, get_sources
    try:
        home_data = get_home_data()
    except:
        home_data = {}
    try:
        trending = get_trending()
    except:
        trending = []
    return render_template("index.html",
        active_tab="video",
        news=[], stats={}, now="", categories=get_categories(), sources=get_sources(),
        page=1, total_pages=1, total=0, per_page=20,
        current_category="全部", current_source="全部",
        parse_lines=get_parse_lines(),
        video_categories=get_all_categories(),
        home_data=home_data,
        trending=trending,
    )


# ==================== 新闻 API ====================
@app.route("/api/news")
def api_news():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    category = request.args.get('category', None)
    source = request.args.get('source', None)
    offset = (page - 1) * per_page
    news_list, total = get_latest_news(limit=per_page, offset=offset, category=category, source=source)
    return jsonify({"count": len(news_list), "total": total, "page": page, "news": news_list})

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


# ==================== 实时影视 API ====================
@app.route("/api/video/search")
def api_video_search():
    q = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    if not q or len(q) < 1:
        return jsonify({"count": 0, "videos": [], "total": 0})
    videos, total = search_videos(q, page=page)
    return jsonify({"count": len(videos), "videos": videos, "total": total, "page": page})

@app.route("/api/video/category")
def api_video_category():
    cat = request.args.get('cat', '国产剧')
    page = int(request.args.get('page', 1))
    videos, total = get_category_list(cat, page=page)
    return jsonify({"count": len(videos), "videos": videos, "total": total, "cat": cat, "page": page})

@app.route("/api/video/trending")
def api_video_trending():
    videos = get_trending()
    return jsonify({"count": len(videos), "videos": videos})

@app.route("/api/video/categories")
def api_video_categories():
    return jsonify(get_all_categories())

@app.route("/api/video/home")
def api_video_home():
    return jsonify(get_home_data())

@app.route("/api/video/parse_lines")
def api_parse_lines():
    return jsonify(get_parse_lines())

@app.route("/api/video/parse_test")
def api_parse_test():
    """测试解析线路速度"""
    return jsonify(test_parse_speed())


@app.route("/api/video/play_urls")
def api_video_play_urls():
    """根据视频名获取各平台播放URL，支持集数"""
    name = request.args.get('name', '')
    ep = request.args.get('ep', None)
    unit = request.args.get('unit', '集')
    if not name:
        return jsonify({"error": "need name"}), 400
    
    episode_num = int(ep) if ep else None
    urls = build_play_urls(name, episode_num, unit)
    return jsonify({"name": name, "episode": episode_num, "urls": urls})


@app.route("/api/video/episodes")
def api_video_episodes():
    """获取指定视频的剧集列表"""
    name = request.args.get('name', '')
    note = request.args.get('note', '')
    if not name:
        return jsonify({"error": "need name"}), 400
    
    from episode_provider import parse_episode_info, generate_episodes
    ep_info = parse_episode_info(note, name)
    episodes = generate_episodes(ep_info, name)
    
    return jsonify({
        "name": name,
        "total": ep_info.get("total"),
        "current": ep_info.get("current"),
        "is_movie": ep_info.get("is_movie"),
        "unit": ep_info.get("unit", "集"),
        "episodes": episodes,
    })


@app.route("/api/video/parse")
def api_video_parse():
    """解析播放指定URL"""
    url = request.args.get('url', '')
    line = int(request.args.get('line', 0))
    if not url:
        return jsonify({"error": "need url"}), 400
    lines = get_parse_lines()
    if line >= len(lines):
        line = 0
    parse_url = lines[line]["url"] + url
    return jsonify({"parse_url": parse_url, "line_name": lines[line]["name"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
