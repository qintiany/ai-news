"""
AI News Hub + 视频中心 - 主应用
新闻聚合 + 视频解析 + 影视点播
"""
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import threading

from database import init_db, get_latest_news, get_stats, get_categories, get_sources
from fetcher import fetch_all
from config import FETCH_INTERVAL_MINUTES
from video_data import search_library, get_trending, get_all_shows, get_all_movies, get_banners, get_parse_lines, get_show_by_id

app = Flask(__name__)

init_db()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        fetch_all, 'interval', minutes=FETCH_INTERVAL_MINUTES,
        id='fetch_news', next_run_time=None
    )
    scheduler.start()
    print("⏰ 定时抓取已启动")

threading.Timer(10, start_scheduler).start()


# ==================== 新闻页面 ====================

@app.route("/")
def index():
    """首页 - AI 新闻"""
    page = int(request.args.get('page', 1))
    per_page = 12
    category = request.args.get('category', '全部')
    source = request.args.get('source', '全部')

    offset = (page - 1) * per_page
    news_list, total = get_latest_news(limit=per_page, offset=offset, category=category, source=source)
    stats = get_stats()
    categories = get_categories()
    sources = get_sources()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_pages = (total + per_page - 1) // per_page

    return render_template("index.html",
        active_tab="news",
        news=news_list, stats=stats, now=now,
        categories=categories, sources=sources,
        page=page, total_pages=total_pages, total=total,
        current_category=category, current_source=source,
        per_page=per_page,
        parse_lines=get_parse_lines(), banners=get_banners(),
        trending=[],
        tencent_shows=[s for s in get_all_shows() if s.get("platform") == "腾讯视频"],
        iqiyi_shows=[s for s in get_all_shows() if s.get("platform") == "爱奇艺"],
        all_movies=get_all_movies()
    )


# ==================== 视频页面 ====================

@app.route("/video")
def video_page():
    trending = get_trending()
    shows = get_all_shows()
    movies = get_all_movies()
    banners = get_banners()
    parse_lines = get_parse_lines()
    from database import get_categories, get_sources
    return render_template("index.html",
        active_tab="video",
        news=[], stats={"total": 0, "today": 0, "sources": []}, now="",
        categories=get_categories(), sources=get_sources(),
        page=1, total_pages=1, total=0, per_page=12,
        current_category="全部", current_source="全部",
        parse_lines=parse_lines, banners=banners,
        trending=trending,
        tencent_shows=[s for s in shows if s.get("platform") == "腾讯视频"],
        iqiyi_shows=[s for s in shows if s.get("platform") == "爱奇艺"],
        all_movies=movies
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
    return jsonify({"count": len(news_list), "total": total, "page": page, "per_page": per_page, "news": news_list})

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

@app.route("/api/categories")
def api_categories():
    return jsonify(get_categories())

@app.route("/api/sources")
def api_sources():
    return jsonify(get_sources())


# ==================== 视频 API ====================

@app.route("/api/video/search")
def api_video_search():
    q = request.args.get('q', '')
    cat = request.args.get('type', 'all')
    results = search_library(q, cat)
    return jsonify({"count": len(results), "results": results})

@app.route("/api/video/trending")
def api_video_trending():
    return jsonify(get_trending())

@app.route("/api/video/movies")
def api_video_movies():
    return jsonify(get_all_movies())

@app.route("/api/video/shows")
def api_video_shows():
    return jsonify(get_all_shows())

@app.route("/api/video/parse_lines")
def api_parse_lines():
    return jsonify(get_parse_lines())

@app.route("/api/video/detail/<sid>")
def api_video_detail(sid):
    show = get_show_by_id(sid)
    if show:
        return jsonify(show)
    return jsonify({"error": "not found"}), 404


# ==================== 影视详情 API (给 JS 调用) ====================

@app.route("/api/show/<sid>")
def api_show_detail(sid):
    show = get_show_by_id(sid)
    if show:
        return jsonify(show)
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
