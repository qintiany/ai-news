import sqlite3
import os
from datetime import datetime, timedelta
from config import RETENTION_DAYS

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "news.db"))


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            summary TEXT DEFAULT '',
            source TEXT NOT NULL,
            category TEXT DEFAULT '其他',
            published_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hot_score REAL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_news_url ON news(url)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_news_hot ON news(hot_score DESC)
    """)
    conn.commit()
    conn.close()


def insert_news(title, url, summary, source, category, published_at):
    """插入新闻（去重）"""
    conn = get_db()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO news (title, url, summary, source, category, published_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, url, summary, source, category, published_at))
        conn.commit()
        return True
    except Exception as e:
        print(f"插入失败: {e}")
        return False
    finally:
        conn.close()


def get_latest_news(limit=10, offset=0, category=None, source=None):
    """获取最新新闻（按发布时间+热度排序），支持分页和分类筛选"""
    conn = get_db()
    conditions = ["published_at > datetime('now', '-7 days')"]
    params = []
    
    if category and category != '全部':
        conditions.append("category = ?")
        params.append(category)
    
    if source and source != '全部':
        conditions.append("source = ?")
        params.append(source)
    
    where_clause = " AND ".join(conditions)
    
    rows = conn.execute(f"""
        SELECT id, title, url, summary, source, category, published_at, hot_score
        FROM news
        WHERE {where_clause}
        ORDER BY hot_score DESC, published_at DESC
        LIMIT ? OFFSET ?
    """, params + [limit, offset]).fetchall()
    
    # 获取总数
    total = conn.execute(f"""
        SELECT COUNT(*) FROM news WHERE {where_clause}
    """, params).fetchone()[0]
    
    conn.close()
    return [dict(row) for row in rows], total


def get_categories():
    """获取所有分类及数量"""
    conn = get_db()
    rows = conn.execute("""
        SELECT category, COUNT(*) as cnt 
        FROM news 
        WHERE published_at > datetime('now', '-7 days')
        GROUP BY category 
        ORDER BY cnt DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_sources():
    """获取所有来源及数量"""
    conn = get_db()
    rows = conn.execute("""
        SELECT source, COUNT(*) as cnt 
        FROM news 
        WHERE published_at > datetime('now', '-7 days')
        GROUP BY source 
        ORDER BY cnt DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_news_by_source(source):
    """按来源获取新闻"""
    conn = get_db()
    rows = conn.execute("""
        SELECT id, title, url, summary, source, category, published_at
        FROM news
        WHERE source = ?
        ORDER BY published_at DESC
        LIMIT 20
    """, (source,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_hot_scores():
    """更新热度分数：发布时间越近 + 来源权重越高"""
    conn = get_db()
    conn.execute("""
        UPDATE news SET hot_score = (
            CASE
                WHEN category = '官方' THEN 3
                WHEN category = '媒体' THEN 2
                WHEN category = 'YouTube' THEN 1.5
                ELSE 1
            END
        ) * (
            1.0 / (1 + (julianday('now') - julianday(published_at)) * 10)
        ) * 100
    """)
    conn.commit()
    conn.close()


def cleanup_old_news():
    """清理过期新闻"""
    conn = get_db()
    cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    conn.execute("DELETE FROM news WHERE published_at < ?", (cutoff.isoformat(),))
    conn.commit()
    conn.close()


def get_stats():
    """获取统计信息"""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]
    sources = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM news GROUP BY source ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    today = conn.execute(
        "SELECT COUNT(*) FROM news WHERE date(published_at) = date('now')"
    ).fetchone()[0]
    conn.close()
    return {
        "total": total,
        "today": today,
        "sources": [dict(row) for row in sources],
    }
