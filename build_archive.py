# -*- coding: utf-8 -*-
"""
往期索引页生成器 —— 扫描 amazon_charts_YYYYMMDD.html，
按导出日自动推算「近30天」数据窗口（导出日前29天 ~ 导出日，含首尾共30天）。
每期摘要在 META 里补；新增期次时只需加一条 META 记录后重跑本脚本。
"""
import glob
from datetime import datetime, timedelta

# 每期摘要（可选；不填则显示 —）
META = {
    '20261009': ('27,285 台', '$28.0M', '+0.9%', '双周持平内部换庄：英国+27%领涨、美国-8.5%三期累跌25%；MOVA登顶；Greenworks回切C30Z；甜区回摆500-800'),
    '20260924': ('27,033 台', '$28.0M', '-5.5%', '美国独自出清(-18%)、欧洲四国反弹；甜区由500-800上移800-1000；视觉路线获品牌溢价'),
    '20260911': ('28,596 台', '$31.2M', '-3.3%', '价格重心下移；Greenworks C30Z→C20Z；WORX重夺第1'),
    '20260904': ('29,672 台', '$33.6M', '-3.6%', 'Greenworks C30Z空降美国冠军；欧洲全面承压'),
    '20260821': ('—', '—', '—', '夏季旺季大盘'),
    '20260710': ('—', '—', '—', ''),
    '20260703': ('—', '—', '—', ''),
    '20260626': ('—', '—', '—', ''),
}


def window_label(key: str) -> str:
    end = datetime.strptime(key, '%Y%m%d')
    start = end - timedelta(days=29)  # 含首尾共30天
    return f"{start.month}.{start.day}–{end.month}.{end.day}"


# ---- 第二部分：割草机大盘看板（非亚马逊期次的常驻看板）----
DASHBOARDS = [
    {
        'href': 'market_seasonality.html',
        'icon': '',
        'title': '亚马逊看板 | 欧洲/美国',
        'window': '📅 卖家精灵市场分析 · 2025-01 至 2026-09 月度 · 中英双语',
        'stats': [('📦 欧洲 418,961 台', 'up', '+37.0%'), ('📦 美国 89,527 台', 'up', '+64.8%')],
        'note': '欧洲＝DE/FR/IT/UK 合并（UK £ 按 ECB 汇率换算 € 对比），美国独立成区；含销量/均价的季节性、月度同比与分国详情。',
    },
    {
        'href': 'gfk_germany_dashboard.html',
        'icon': '🇩🇪',
        'title': 'GfK 德国看板',
        'window': '📅 GfK 德国市场月度面板',
        'stats': [],
        'note': 'GfK 德国割草机市场大盘看板（金额份额 / Mio EUR 等口径见页内注释）。',
    },
]

db_cards = []
for d in DASHBOARDS:
    stats = ''.join(
        f'<span>{txt}</span>' + (f'<span class="{cls}">{g}</span>' if g else '')
        for txt, cls, g in d['stats']
    )
    stats_row = f'<div class="card-stats">{stats}</div>' if stats else ''
    db_cards.append(f"""
    <a class="card" href="{d['href']}">
      <div class="card-date">{(d['icon'] + ' ') if d['icon'] else ''}{d['title']}</div>
      <div class="card-window">{d['window']}</div>
      {stats_row}
      <div class="card-note">{d['note']}</div>
    </a>""")

files = sorted(glob.glob("amazon_charts_2*.html"), reverse=True)
cards = []
for i, f in enumerate(files):
    key = f.replace('amazon_charts_', '').replace('.html', '')
    dt = f"{key[:4]}-{key[4:6]}-{key[6:]}"
    win = window_label(key)
    sales, rev, g, note = META.get(key, ('—', '—', '—', ''))
    latest = ' <span class="new-badge">最新</span>' if i == 0 else ''
    gcls = 'down' if g.startswith('-') else ('up' if g.startswith('+') else 'neutral')
    cards.append(f"""
    <a class="card" href="{f}">
      <div class="card-date">{dt}{latest}</div>
      <div class="card-window">📅 近30天数据窗口：{win}</div>
      <div class="card-stats">
        <span>📦 {sales}</span>
        <span>💰 {rev}</span>
        <span class="{gcls}">{g}</span>
      </div>
      <div class="card-note">{note}</div>
    </a>""")

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>往期索引 · 割草机亚马逊数据看板</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
       background:#f5f7fa; color:#1d1d1f; padding:24px 32px; }}
.container {{ max-width:900px; margin:0 auto; }}
.top-nav {{ display:flex; align-items:center; justify-content:space-between;
           margin-bottom:28px; padding:12px 20px; background:#fff;
           border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,0.05); }}
.top-nav .nav-brand {{ font-size:15px; font-weight:700; }}
.top-nav .nav-links a {{ font-size:13px; color:#0071e3; text-decoration:none; margin-left:18px; font-weight:600; }}
h1 {{ font-size:24px; font-weight:700; margin:8px 0 4px; }}
h2.sec-title {{ font-size:19px; font-weight:700; margin:40px 0 4px; }}
.subtitle {{ font-size:13px; color:#86868b; margin-bottom:24px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.card {{ display:block; background:#fff; border-radius:14px; padding:20px 24px;
        box-shadow:0 1px 3px rgba(0,0,0,0.05); text-decoration:none; color:#1d1d1f;
        transition:transform .12s ease, box-shadow .12s ease; }}
.card:hover {{ transform:translateY(-2px); box-shadow:0 6px 16px rgba(0,0,0,0.08); }}
.card-date {{ font-size:17px; font-weight:700; }}
.card-window {{ font-size:12px; color:#86868b; margin-top:3px; }}
.card-stats {{ display:flex; gap:14px; margin:12px 0 8px; font-size:13px; font-weight:600;
              font-variant-numeric:tabular-nums; }}
.card-stats .up {{ color:#34c759; }} .card-stats .down {{ color:#ff3b30; }} .card-stats .neutral {{ color:#86868b; }}
.card-note {{ font-size:12.5px; color:#48484a; line-height:1.5; }}
.new-badge {{ display:inline-block; background:#0071e3; color:#fff; font-size:10px; font-weight:700;
             padding:2px 7px; border-radius:5px; vertical-align:middle; margin-left:6px; }}
.footer {{ font-size:12px; color:#aeaeb2; margin-top:28px; line-height:1.7; }}
</style>
</head>
<body>
<div class="container">
  <div class="top-nav">
    <div class="nav-brand">🗺️ 割草机亚马逊数据看板</div>
    <div class="nav-links">
      <a href="amazon_charts_latest.html">最新一期</a>
      <a href="price_trend.html">📈 价格趋势</a>
      <a href="index.html">首页</a>
    </div>
  </div>
  <h1>📚 往期索引</h1>
  <h2 class="sec-title">一、亚马逊 BSR 看板（往期）</h2>
  <div class="subtitle">亚马逊 6 国（DE/US/FR/IT/ES/GB）智能割草机 BSR 数据看板 · 每期为导出日的近 30 天累计销量 · 点击卡片查看当期完整图表</div>
  <div class="grid">
    {''.join(cards)}
  </div>

  <h2 class="sec-title">二、割草机大盘看板</h2>
  <div class="subtitle">非亚马逊期次的常驻大盘看板 · 点击卡片进入</div>
  <div class="grid">
    {''.join(db_cards)}
  </div>

  <div class="footer">
    数据口径：每期为导出日近 30 天累计销量（窗口 = 导出日前 29 天至导出日，共 30 天）；两期相隔 7 天时，差值等价于「新 1 周 vs 旧 1 周」的周对比。<br>
    2026-09-11 期起口径收紧为「智能/机器人割草机」（已剔除手推式及独立配件），上期数据同口径重述。
  </div>
</div>
</body>
</html>"""

with open("archive.html", "w", encoding="utf-8") as f:
    f.write(html)
print("archive.html rebuilt:", [(f, window_label(f.replace('amazon_charts_','').replace('.html',''))) for f in files])
