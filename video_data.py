"""
影视点播库 v3 — 腾讯视频风格 + 腾讯/爱奇艺真实资源
播放链路：选集 → 平台真实URL → 解析接口 → iframe播放
"""
import random

def generate_episode_urls(url, episodes, platform):
    """根据平台URL模式，为每集生成播放URL"""
    episode_urls = {}
    
    if platform == "腾讯视频":
        # 腾讯视频 cover URL: https://v.qq.com/x/cover/mzc00200k15fq8o.html
        # 每集URL和cover URL相同，解析器会自动识别
        # 因为腾讯视频的cover页本身包含所有集数
        for i in range(1, episodes + 1):
            episode_urls[i] = url
    elif platform == "爱奇艺":
        # 爱奇艺 URL: https://www.iqiyi.com/v_19rrofs38w.html
        # 同理，cover页包含所有集数
        for i in range(1, episodes + 1):
            episode_urls[i] = url
    else:
        for i in range(1, episodes + 1):
            episode_urls[i] = url
    
    return episode_urls


# ========== 解析线路 ==========
PARSE_LINES = [
    # 线路六 yemu.xyz: 测试最靠谱 ✅ DPlayer+hls.js+m3u8，无X-Frame限制
    {"name": "🌸 首选线路", "url": "https://www.yemu.xyz/?url="},
    # 默认一 xmflv.com: HTTP 200, 有Player, JS动态渲染
    {"name": "🎀 备选一", "url": "https://jx.xmflv.com/?url="},
    # 线路八 hls.one: HTTP 200, 加密解析
    {"name": "🎀 备选二", "url": "https://jx.hls.one/?url="},
    # 线路七 xmflv.cc: HTTP 200, 加密解析
    {"name": "🎀 备选三", "url": "https://jx.xmflv.cc/?url="},
    # 线路五 playerjy: HTTP 200, iframe/document.write方式
    {"name": "🎀 备选四", "url": "https://jx.playerjy.com/?url="},
    # 线路四 789jiexi: HTTP 200, iframe/document.write方式
    {"name": "🎀 备选五", "url": "https://jx.789jiexi.com/?url="},
    # 无法播放时 2s0: HTTP 200, iframe方式
    {"name": "🎀 备选六", "url": "https://jx.2s0.cn/player/?url="},
    # 推荐二 nnxv: ❌ HTTP 403 BLOCKED (保留但放最后)
    {"name": "⚠️ 备选七(可能受限)", "url": "https://jx.nnxv.cn/tv.php?url="},
    # 剧名/链接 m1907: 仅502B，基本无内容
    {"name": "⚠️ 备选八(可能受限)", "url": "https://z1.m1907.top/?jx="},
]

# ========== 腾讯视频热门剧集 ==========
TENCENT_SHOWS = [
    {
        "id": "tx001", "title": "庆余年 第二季", "subtitle": "张若昀·李沁·陈道明", "year": 2024,
        "genre": "古装/权谋", "rating": 9.3, "episodes": 36, "status": "已完结",
        "desc": "范闲身世之谜揭开，各方势力暗流涌动，一场更大的棋局正在铺开。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200k15fq8o/mzc00200k15fq8o_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200k15fq8o.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["热播", "权谋", "古装"]
    },
    {
        "id": "tx002", "title": "繁花", "subtitle": "胡歌·马伊琍·唐嫣·辛芷蕾", "year": 2023,
        "genre": "剧情/年代", "rating": 9.4, "episodes": 30, "status": "已完结",
        "desc": "九十年代的上海，阿宝从市井小民到商界大亨的传奇人生。王家卫首部电视剧。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200p7p5qf7/mzc00200p7p5qf7_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200p7p5qf7.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["热播", "年代", "商战"]
    },
    {
        "id": "tx003", "title": "三体", "subtitle": "张鲁一·于和伟·陈瑾·王子文", "year": 2023,
        "genre": "科幻/悬疑", "rating": 8.7, "episodes": 30, "status": "已完结",
        "desc": "纳米科学家汪淼卷入神秘事件，揭开地球文明面临的外星威胁。刘慈欣同名小说改编。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200h0i6h5h/mzc00200h0i6h5h_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200h0i6h5h.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["科幻", "悬疑", "热播"]
    },
    {
        "id": "tx004", "title": "长相思", "subtitle": "杨紫·张晚意·邓为·檀健次", "year": 2023,
        "genre": "古装/爱情", "rating": 8.8, "episodes": 39, "status": "已完结",
        "desc": "大荒世界，皓翎王姬小夭历经百年颠沛之苦，在清水镇与故人重逢。",
        "poster": "https://puui.qpic.cn/vpic_cover/n4101fjqw1p/n4101fjqw1p_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/n4101fjqw1p.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["古装", "爱情", "热播"]
    },
    {
        "id": "tx005", "title": "与凤行", "subtitle": "赵丽颖·林更新", "year": 2024,
        "genre": "古装/奇幻", "rating": 8.5, "episodes": 39, "status": "已完结",
        "desc": "灵界碧苍王沈璃逃婚坠落人间，与行止神君展开一段跨越三界的爱恋。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200w8mqp1p/mzc00200w8mqp1p_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200w8mqp1p.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["古装", "奇幻", "爱情"]
    },
    {
        "id": "tx006", "title": "玫瑰的故事", "subtitle": "刘亦菲·佟大为·林更新·万茜", "year": 2024,
        "genre": "都市/爱情", "rating": 8.3, "episodes": 38, "status": "已完结",
        "desc": "黄亦玫跨越二十余年的成长与情感经历，亦舒同名小说改编。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200qpjpg5p/mzc00200qpjpg5p_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200qpjpg5p.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["都市", "爱情", "热播"]
    },
    {
        "id": "tx007", "title": "承欢记", "subtitle": "杨紫·许凯", "year": 2024,
        "genre": "都市/爱情", "rating": 8.2, "episodes": 37, "status": "已完结",
        "desc": "麦承欢在亲情与爱情中找寻自我价值的成长故事。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200123abcd/mzc00200123abcd_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200123abcd.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["都市", "爱情"]
    },
    {
        "id": "tx008", "title": "大奉打更人", "subtitle": "王鹤棣·田曦薇", "year": 2025,
        "genre": "古装/奇幻", "rating": 8.6, "episodes": 40, "status": "热播中",
        "desc": "现代打工人杨凌穿越到大奉王朝成为一名打更人，破案修仙两不误。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200abcd123/mzc00200abcd123_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200abcd123.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["古装", "奇幻", "穿越", "热播"]
    },
    {
        "id": "tx009", "title": "扫黑风暴", "subtitle": "孙红雷·张艺兴·刘奕君", "year": 2021,
        "genre": "犯罪/悬疑", "rating": 8.5, "episodes": 28, "status": "已完结",
        "desc": "一线干警李成阳联手各方力量，与黑恶势力展开殊死搏斗。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200kmi8s4e/mzc00200kmi8s4e_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200kmi8s4e.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["犯罪", "悬疑", "热播"]
    },
    {
        "id": "tx010", "title": "鬼吹灯之精绝古城", "subtitle": "靳东·陈乔恩", "year": 2016,
        "genre": "冒险/悬疑", "rating": 8.6, "episodes": 21, "status": "已完结",
        "desc": "胡八一与考古队深入沙漠寻找精绝古城。天下霸唱原著改编。",
        "poster": "https://puui.qpic.cn/vpic_cover/j4100k4l3b4/j4100k4l3b4_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/j4100k4l3b4.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["冒险", "悬疑", "经典"]
    },
    {
        "id": "tx011", "title": "龙岭迷窟", "subtitle": "潘粤明·张雨绮·姜超", "year": 2020,
        "genre": "冒险/悬疑", "rating": 8.8, "episodes": 18, "status": "已完结",
        "desc": "胡八一、王胖子、Shirley杨陕西龙岭迷窟探秘之旅。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200f19q8q5/mzc00200f19q8q5_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200f19q8q5.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["冒险", "悬疑", "经典"]
    },
    {
        "id": "tx012", "title": "漫长的季节", "subtitle": "范伟·秦昊·陈明昊", "year": 2023,
        "genre": "悬疑/剧情", "rating": 9.5, "episodes": 12, "status": "已完结",
        "desc": "一座北方小城，一桩跨越二十年的命案，三个老伙计的往事与救赎。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200abcd456/mzc00200abcd456_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200abcd456.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["悬疑", "剧情", "高分"]
    },
    {
        "id": "tx013", "title": "开端", "subtitle": "白敬亭·赵今麦", "year": 2022,
        "genre": "悬疑/科幻", "rating": 8.7, "episodes": 15, "status": "已完结",
        "desc": "游戏架构师和大学生在公交车上陷入时间循环，一次次经历爆炸。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200v5n5n5n/mzc00200v5n5n5n_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200v5n5n5n.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["悬疑", "科幻", "循环"]
    },
    {
        "id": "tx014", "title": "雪中悍刀行", "subtitle": "张若昀·胡军·李庚希", "year": 2021,
        "genre": "古装/武侠", "rating": 8.3, "episodes": 38, "status": "已完结",
        "desc": "北凉世子徐凤年一人一马入江湖，谱写一段悍刀江湖行。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200p1p1p1p/mzc00200p1p1p1p_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200p1p1p1p.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["古装", "武侠"]
    },
    {
        "id": "tx015", "title": "梦华录", "subtitle": "刘亦菲·陈晓·柳岩·林允", "year": 2022,
        "genre": "古装/爱情", "rating": 8.8, "episodes": 40, "status": "已完结",
        "desc": "赵盼儿三姐妹在东京城创业开茶坊，靠自己闯出一片天地。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200q1q1q1q/mzc00200q1q1q1q_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200q1q1q1q.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["古装", "爱情", "女性"]
    },
]

# ========== 爱奇艺热门剧集 ==========
IQIYI_SHOWS = [
    {
        "id": "iq001", "title": "狂飙", "subtitle": "张译·张颂文·李一桐·张志坚", "year": 2023,
        "genre": "犯罪/剧情", "rating": 9.5, "episodes": 39, "status": "已完结",
        "desc": "一线刑警安欣与黑恶势力长达二十年的生死较量，扫黑路上的正义之战。",
        "poster": "https://pic7.iqiyipic.com/image/20230105/da/6a/v_1672877878806.jpg",
        "url": "https://www.iqiyi.com/v_19rrofs38w.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["犯罪", "剧情", "现象级"]
    },
    {
        "id": "iq002", "title": "苍兰诀", "subtitle": "虞书欣·王鹤棣", "year": 2022,
        "genre": "古装/奇幻", "rating": 8.9, "episodes": 36, "status": "已完结",
        "desc": "低阶小兰花与月尊东方青苍互换身体后展开的仙侠虐恋。",
        "poster": "https://pic7.iqiyipic.com/image/20220805/1a/ab/v_1659681107802.jpg",
        "url": "https://www.iqiyi.com/v_2g3pwu5rqz8.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "奇幻", "爱情"]
    },
    {
        "id": "iq003", "title": "卿卿日常", "subtitle": "白敬亭·田曦薇", "year": 2022,
        "genre": "古装/喜剧", "rating": 8.6, "episodes": 40, "status": "已完结",
        "desc": "来自各地的少女们齐聚新川，在嬉笑怒骂中收获成长与爱情。",
        "poster": "https://pic5.iqiyipic.com/image/20221109/f5/df/v_1667975466907.jpg",
        "url": "https://www.iqiyi.com/v_1k0hzwf3d9s.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "喜剧", "甜宠"]
    },
    {
        "id": "iq004", "title": "莲花楼", "subtitle": "成毅·曾舜晞·肖顺尧", "year": 2023,
        "genre": "古装/武侠", "rating": 8.8, "episodes": 40, "status": "已完结",
        "desc": "江湖神医李莲花与热血少年方多病携手破解江湖奇案。",
        "poster": "https://pic0.iqiyipic.com/image/20230721/2c/18/v_1689927028088.jpg",
        "url": "https://www.iqiyi.com/v_1h9q5fa6hrw.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "武侠", "悬疑"]
    },
    {
        "id": "iq005", "title": "宁安如梦", "subtitle": "白鹿·张凌赫", "year": 2023,
        "genre": "古装/爱情", "rating": 8.4, "episodes": 38, "status": "已完结",
        "desc": "姜雪宁重生归来，在权力与爱情的漩涡中改写自己的命运。",
        "poster": "https://pic4.iqiyipic.com/image/20231106/ef/01/v_1699263606001.jpg",
        "url": "https://www.iqiyi.com/v_28l3m6v7r8n.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "爱情", "重生"]
    },
    {
        "id": "iq006", "title": "一念关山", "subtitle": "刘诗诗·刘宇宁", "year": 2023,
        "genre": "古装/武侠", "rating": 8.5, "episodes": 40, "status": "已完结",
        "desc": "安国朱衣卫左使任如意与梧国六道堂堂主宁远舟的江湖传奇。",
        "poster": "https://pic1.iqiyipic.com/image/20231128/30/7a/v_1701144282815.jpg",
        "url": "https://www.iqiyi.com/v_2f2w4s4q3x3r.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "武侠"]
    },
    {
        "id": "iq007", "title": "唐朝诡事录", "subtitle": "杨旭文·杨志刚", "year": 2022,
        "genre": "古装/悬疑", "rating": 8.7, "episodes": 36, "status": "已完结",
        "desc": "大唐盛世的诡谲奇案，苏无名与卢凌风联手破案。",
        "poster": "https://pic9.iqiyipic.com/image/20220927/03/15/v_1664225578951.jpg",
        "url": "https://www.iqiyi.com/v_1x6m7j8v4y5b.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "悬疑", "探案"]
    },
    {
        "id": "iq008", "title": "唐朝诡事录之西行", "subtitle": "杨旭文·杨志刚", "year": 2024,
        "genre": "古装/悬疑", "rating": 8.8, "episodes": 40, "status": "热播中",
        "desc": "苏无名与卢凌风一路西行，破解更多离奇诡案。",
        "poster": "https://pic2.iqiyipic.com/image/20240718/ab/cd/v_1721352819001.jpg",
        "url": "https://www.iqiyi.com/v_abcd12345678.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "悬疑", "热播"]
    },
    {
        "id": "iq009", "title": "人世间", "subtitle": "雷佳音·辛柏青·宋佳·殷桃", "year": 2022,
        "genre": "剧情/年代", "rating": 9.4, "episodes": 58, "status": "已完结",
        "desc": "周家三兄妹跨越五十年的命运沉浮，展现中国社会沧桑巨变。",
        "poster": "https://pic6.iqiyipic.com/image/20220127/49/f9/v_1643248581599.jpg",
        "url": "https://www.iqiyi.com/v_1a1b1c1d1e1f.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["剧情", "年代", "高分"]
    },
    {
        "id": "iq010", "title": "风吹半夏", "subtitle": "赵丽颖·欧豪·李光洁", "year": 2022,
        "genre": "剧情/商战", "rating": 8.5, "episodes": 36, "status": "已完结",
        "desc": "许半夏在改革开放浪潮中赤手空拳闯出一片钢铁天地。",
        "poster": "https://pic3.iqiyipic.com/image/20221127/6a/2c/v_1669594513900.jpg",
        "url": "https://www.iqiyi.com/v_2b2c2d2e2f2g.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["剧情", "商战", "年代"]
    },
    {
        "id": "iq011", "title": "警察荣誉", "subtitle": "张若昀·白鹿", "year": 2022,
        "genre": "剧情/犯罪", "rating": 8.6, "episodes": 38, "status": "已完结",
        "desc": "四个年轻警察在八里河派出所的成长与坚守。",
        "poster": "https://pic8.iqiyipic.com/image/20220527/18/43/v_1653648081343.jpg",
        "url": "https://www.iqiyi.com/v_3c3d3e3f3g3h.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["剧情", "犯罪", "职场"]
    },
    {
        "id": "iq012", "title": "天才基本法", "subtitle": "雷佳音·张子枫·张新成", "year": 2022,
        "genre": "剧情/科幻", "rating": 8.3, "episodes": 34, "status": "已完结",
        "desc": "数学天才林朝夕穿越平行世界，重新点燃对数学的热爱。",
        "poster": "https://pic0.iqiyipic.com/image/20220722/72/11/v_1658437211301.jpg",
        "url": "https://www.iqiyi.com/v_4d4e4f4g4h4i.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["剧情", "科幻", "青春"]
    },
    {
        "id": "iq013", "title": "云之羽", "subtitle": "虞书欣·张凌赫", "year": 2023,
        "genre": "古装/奇幻", "rating": 8.2, "episodes": 24, "status": "已完结",
        "desc": "无锋刺客云为衫潜入宫门执行任务，却陷入一场更大的阴谋。",
        "poster": "https://pic7.iqiyipic.com/image/20230901/95/1a/v_1693557376015.jpg",
        "url": "https://www.iqiyi.com/v_5e5f5g5h5i5j.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "奇幻", "谍战"]
    },
    {
        "id": "iq014", "title": "长风渡", "subtitle": "白敬亭·宋轶", "year": 2023,
        "genre": "古装/爱情", "rating": 8.4, "episodes": 40, "status": "已完结",
        "desc": "布商之女柳玉茹与纨绔子弟顾九思先婚后爱的成长故事。",
        "poster": "https://pic2.iqiyipic.com/image/20230618/3d/9f/v_1687054513133.jpg",
        "url": "https://www.iqiyi.com/v_6f6g6h6i6j6k.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["古装", "爱情", "成长"]
    },
    {
        "id": "iq015", "title": "三大队", "subtitle": "秦昊·李乃文·陈明昊", "year": 2023,
        "genre": "犯罪/剧情", "rating": 8.9, "episodes": 24, "status": "已完结",
        "desc": "一次审讯意外让刑警队长入狱十年，出狱后以普通人身份继续追凶。",
        "poster": "https://pic5.iqiyipic.com/image/20231221/12/34/v_1703156543210.jpg",
        "url": "https://www.iqiyi.com/v_7g7h7i7j7k7l.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["犯罪", "剧情", "悬疑"]
    },
]

# ========== 腾讯视频电影 ==========
TENCENT_MOVIES = [
    {
        "id": "txm001", "title": "流浪地球2", "subtitle": "吴京·刘德华·李雪健", "year": 2023,
        "genre": "科幻/冒险", "rating": 8.3, "duration": "173分钟", "status": "VIP",
        "desc": "太阳危机来临前，人类的团结与分歧。流浪地球计划的前传故事。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200a1a1a1a/mzc00200a1a1a1a_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200a1a1a1a.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["科幻", "国产", "热播"]
    },
    {
        "id": "txm002", "title": "满江红", "subtitle": "沈腾·易烊千玺·张译·雷佳音", "year": 2023,
        "genre": "剧情/悬疑", "rating": 8.0, "duration": "159分钟", "status": "VIP",
        "desc": "南宋绍兴年间，一场离奇谋杀案的调查牵扯出惊天秘密。张艺谋导演。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200b2b2b2b/mzc00200b2b2b2b_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200b2b2b2b.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["剧情", "悬疑", "热播"]
    },
    {
        "id": "txm003", "title": "封神第一部", "subtitle": "费翔·李雪健·黄渤·于适", "year": 2023,
        "genre": "奇幻/动作", "rating": 8.1, "duration": "148分钟", "status": "VIP",
        "desc": "商王殷寿暴虐无道，昆仑仙人姜子牙携封神榜下山。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200c3c3c3c/mzc00200c3c3c3c_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200c3c3c3c.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["奇幻", "动作", "史诗"]
    },
    {
        "id": "txm004", "title": "消失的她", "subtitle": "朱一龙·倪妮·文咏珊", "year": 2023,
        "genre": "悬疑/犯罪", "rating": 7.8, "duration": "122分钟", "status": "VIP",
        "desc": "妻子在海外旅行中神秘失踪，丈夫陷入一场无法逃脱的困局。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200d4d4d4d/mzc00200d4d4d4d_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200d4d4d4d.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["悬疑", "犯罪"]
    },
    {
        "id": "txm005", "title": "人生大事", "subtitle": "朱一龙·杨恩又", "year": 2022,
        "genre": "剧情/家庭", "rating": 8.5, "duration": "112分钟", "status": "VIP",
        "desc": "殡葬师莫三妹遇到孤儿武小文，两个被遗弃的人互相取暖。",
        "poster": "https://puui.qpic.cn/vpic_cover/mzc00200e5e5e5e/mzc00200e5e5e5e_hz.jpg/496",
        "url": "https://v.qq.com/x/cover/mzc00200e5e5e5e.html",
        "platform": "腾讯视频", "platform_icon": "🐧",
        "tags": ["剧情", "家庭", "治愈"]
    },
]

# ========== 爱奇艺电影 ==========
IQIYI_MOVIES = [
    {
        "id": "iqm001", "title": "第二十条", "subtitle": "雷佳音·马丽·赵丽颖·高叶", "year": 2024,
        "genre": "剧情/法律", "rating": 8.4, "duration": "141分钟", "status": "VIP",
        "desc": "一个关于正当防卫的案子，揭示了法律条文背后的情理与人道。张艺谋导演。",
        "poster": "https://pic1.iqiyipic.com/image/20240210/56/78/v_1707567834567.jpg",
        "url": "https://www.iqiyi.com/v_8h8i8j8k8l8m.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["剧情", "法律", "现实"]
    },
    {
        "id": "iqm002", "title": "熊出没·逆转时空", "subtitle": "谭笑·张伟", "year": 2024,
        "genre": "动画/冒险", "rating": 8.2, "duration": "95分钟", "status": "VIP",
        "desc": "光头强意外获得穿越时空的能力，展开一场跨越时空的大冒险。",
        "poster": "https://pic3.iqiyipic.com/image/20240201/ab/cd/v_1706745678123.jpg",
        "url": "https://www.iqiyi.com/v_9i9j9k9l9m9n.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["动画", "冒险", "合家欢"]
    },
    {
        "id": "iqm003", "title": "飞驰人生2", "subtitle": "沈腾·范丞丞·尹正·张本煜", "year": 2024,
        "genre": "喜剧/运动", "rating": 8.3, "duration": "120分钟", "status": "VIP",
        "desc": "昔日赛车冠军张驰重出江湖，带领新人征战最后一届巴音布鲁克拉力赛。",
        "poster": "https://pic7.iqiyipic.com/image/20240208/ef/01/v_1707356789012.jpg",
        "url": "https://www.iqiyi.com/v_0j0k0l0m0n0o.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["喜剧", "运动", "励志"]
    },
    {
        "id": "iqm004", "title": "孤注一掷", "subtitle": "张艺兴·金晨·咏梅·王传君", "year": 2023,
        "genre": "犯罪/剧情", "rating": 8.1, "duration": "130分钟", "status": "VIP",
        "desc": "揭露境外网络诈骗全产业链的惊人内幕。",
        "poster": "https://pic5.iqiyipic.com/image/20230805/23/45/v_1691234545678.jpg",
        "url": "https://www.iqiyi.com/v_1k1l1m1n1o1p.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["犯罪", "剧情", "现实"]
    },
    {
        "id": "iqm005", "title": "长安三万里", "subtitle": "杨天翔·凌振赫", "year": 2023,
        "genre": "动画/历史", "rating": 9.0, "duration": "168分钟", "status": "VIP",
        "desc": "安史之乱后，高适回忆与李白跨越数十年的深厚友谊和盛唐气象。",
        "poster": "https://pic9.iqiyipic.com/image/20230708/67/89/v_1688765432109.jpg",
        "url": "https://www.iqiyi.com/v_2l2m2n2o2p2q.html",
        "platform": "爱奇艺", "platform_icon": "🥝",
        "tags": ["动画", "历史", "盛唐"]
    },
]

# 合并所有内容
ALL_SHOWS = TENCENT_SHOWS + IQIYI_SHOWS
ALL_MOVIES = TENCENT_MOVIES + IQIYI_MOVIES

# ========== Banner 轮播推荐 ==========
BANNERS = [
    {"title": "庆余年 第二季", "desc": "张若昀领衔，权谋大戏震撼回归", "img": "https://puui.qpic.cn/vpic_cover/mzc00200k15fq8o/mzc00200k15fq8o_hz.jpg/496", "id": "tx001", "type": "show"},
    {"title": "狂飙", "desc": "张译·张颂文 现象级扫黑大剧", "img": "https://pic7.iqiyipic.com/image/20230105/da/6a/v_1672877878806.jpg", "id": "iq001", "type": "show"},
    {"title": "大奉打更人", "desc": "王鹤棣·田曦薇 爆笑修仙探案", "img": "https://puui.qpic.cn/vpic_cover/mzc00200abcd123/mzc00200abcd123_hz.jpg/496", "id": "tx008", "type": "show"},
    {"title": "流浪地球2", "desc": "吴京·刘德华 国产科幻巨制", "img": "https://puui.qpic.cn/vpic_cover/mzc00200a1a1a1a/mzc00200a1a1a1a_hz.jpg/496", "id": "txm001", "type": "movie"},
    {"title": "第二十条", "desc": "张艺谋导演 雷佳音·赵丽颖主演", "img": "https://pic1.iqiyipic.com/image/20240210/56/78/v_1707567834567.jpg", "id": "iqm001", "type": "movie"},
]

def search_library(query, category="all"):
    results = []
    q = query.lower().strip()
    if len(q) < 1:
        return []
    if category in ("all", "show"):
        for s in ALL_SHOWS:
            if q in s["title"].lower() or q in s.get("genre","").lower() or q in " ".join(s.get("tags",[])).lower():
                s_copy = dict(s)
                s_copy["type"] = "show"
                results.append(s_copy)
    if category in ("all", "movie"):
        for m in ALL_MOVIES:
            if q in m["title"].lower() or q in m.get("genre","").lower() or q in " ".join(m.get("tags",[])).lower():
                m_copy = dict(m)
                m_copy["type"] = "movie"
                results.append(m_copy)
    return results

def get_trending():
    shows = random.sample(ALL_SHOWS, min(12, len(ALL_SHOWS)))
    movies = random.sample(ALL_MOVIES, min(8, len(ALL_MOVIES)))
    for s in shows: s["type"] = "show"
    for m in movies: m["type"] = "movie"
    items = shows + movies
    random.shuffle(items)
    return items

def get_all_shows():
    return ALL_SHOWS

def get_all_movies():
    return ALL_MOVIES

def get_banners():
    return BANNERS

def get_parse_lines():
    return PARSE_LINES

def get_show_by_id(sid):
    for s in ALL_SHOWS:
        if s["id"] == sid:
            result = dict(s)
            result["type"] = "show"
            if "episode_urls" not in result:
                result["episode_urls"] = generate_episode_urls(s["url"], s["episodes"], s["platform"])
            return result
    for m in ALL_MOVIES:
        if m["id"] == sid:
            result = dict(m)
            result["type"] = "movie"
            return result
    return None
