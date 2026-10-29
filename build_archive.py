# -*- coding: utf-8 -*-
"""
往期索引页生成器 —— 扫描 amazon_charts_YYYYMMDD.html，
按导出日自动推算「近30天」数据窗口（导出日前29天 ~ 导出日，含首尾共30天）。
每期摘要在 META 里补；新增期次时只需加一条 META 记录后重跑本脚本。

页面支持中文/English 切换：框架文字与第二部分卡片双语；
第一部分（亚马逊往期）的中文编辑摘要不译（点进去的当期看板亦为中文）。
"""
import glob
from datetime import datetime, timedelta

# 每期摘要（可选；不填则显示 —）。note 为中文编辑摘要，不翻译。
META = {
    '20261009': ('27,285', '$28.0M', '+0.9%', '双周持平内部换庄：英国+27%领涨、美国-8.5%三期累跌25%；MOVA登顶；Greenworks回切C30Z；甜区回摆500-800'),
    '20260924': ('27,033', '$28.0M', '-5.5%', '美国独自出清(-18%)、欧洲四国反弹；甜区由500-800上移800-1000；视觉路线获品牌溢价'),
    '20260911': ('28,596', '$31.2M', '-3.3%', '价格重心下移；Greenworks C30Z→C20Z；WORX重夺第1'),
    '20260904': ('29,672', '$33.6M', '-3.6%', 'Greenworks C30Z空降美国冠军；欧洲全面承压'),
    '20260821': ('—', '—', '—', '夏季旺季大盘'),
    '20260710': ('—', '—', '—', ''),
    '20260703': ('—', '—', '—', ''),
    '20260626': ('—', '—', '—', ''),
}

# ---- 第二部分：割草机大盘看板（非亚马逊期次的常驻看板，整卡中英双语）----
DASHBOARDS = [
    {
        'href': 'market_seasonality.html',
        'title': ('亚马逊看板 | 欧洲/美国', 'Amazon Dashboard | Europe / US'),
        'window': ('卖家精灵市场分析 · 2025-01 至 2026-09 月度 · 中英双语',
                   'Sellersprite Market Analysis · monthly 2025-01 to 2026-09 · ZH/EN'),
        'stats': [('📦 欧洲 418,961 台', '📦 Europe 418,961 units', 'up', '+37.0%'),
                  ('📦 美国 89,527 台', '📦 US 89,527 units', 'up', '+64.8%')],
        'note': ('欧洲＝DE/FR/IT/UK 合并（UK £ 按 ECB 汇率换算 € 对比），美国独立成区；含销量/均价的季节性、月度同比与分国详情。',
                 'Europe = DE/FR/IT/UK combined (UK £ converted to € at the ECB rate for comparison); the US is reported separately. Covers volume/avg-price seasonality, monthly YoY and per-market detail.'),
    },
    {
        'href': 'gfk_germany_dashboard.html',
        'title': ('🇩🇪 GfK 德国看板', '🇩🇪 GfK Germany Dashboard'),
        'window': None,
        'stats': [],
        'note': None,
    },
]


def dual(zh, en, tag='span'):
    """生成带中英双语文本的元素，JS 按当前语言切换 textContent。"""
    return f'<{tag} data-zh="{zh}" data-en="{en}">{zh}</{tag}>'


def window_label(key: str) -> str:
    end = datetime.strptime(key, '%Y%m%d')
    start = end - timedelta(days=29)  # 含首尾共30天
    return f"{start.month}.{start.day}–{end.month}.{end.day}"


files = sorted(glob.glob("amazon_charts_2*.html"), reverse=True)
cards = []
for i, f in enumerate(files):
    key = f.replace('amazon_charts_', '').replace('.html', '')
    dt = f"{key[:4]}-{key[4:6]}-{key[6:]}"
    win = window_label(key)
    sales, rev, g, note = META.get(key, ('—', '—', '—', ''))
    latest = (' <span class="new-badge" data-zh="最新" data-en="NEW">最新</span>'
              if i == 0 else '')
    gcls = 'down' if g.startswith('-') else ('up' if g.startswith('+') else 'neutral')
    sales_cell = (f'📦 {sales} <span data-zh="台" data-en="units">台</span>'
                  if sales != '—' else '📦 —')
    cards.append(f"""
    <a class="card" href="{f}">
      <div class="card-date">{dt}{latest}</div>
      <div class="card-window">📅 {dual('近30天数据窗口：', 'Trailing-30-day window: ')}{win}</div>
      <div class="card-stats">
        <span>{sales_cell}</span>
        <span>💰 {rev}</span>
        <span class="{gcls}">{g}</span>
      </div>
      <div class="card-note">{note}</div>
    </a>""")

db_cards = []
for d in DASHBOARDS:
    stats = ''.join(
        f'<span>{dual(zh_t, en_t)}</span><span class="{cls}">{g}</span>'
        for zh_t, en_t, cls, g in d['stats']
    )
    stats_row = f'<div class="card-stats">{stats}</div>' if stats else ''
    window_row = (f'<div class="card-window">{dual(d["window"][0], d["window"][1])}</div>'
                  if d['window'] else '')
    note_row = (f'<div class="card-note">{dual(d["note"][0], d["note"][1])}</div>'
                if d['note'] else '')
    db_cards.append(f"""
    <a class="card" href="{d['href']}">
      <div class="card-date">{dual(d['title'][0], d['title'][1])}</div>
      {window_row}{stats_row}{note_row}
    </a>""")

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title id="pageTitle" data-zh="往期索引 · 割草机亚马逊数据看板" data-en="Archive · Lawn Mower Amazon Dashboard">往期索引 · 割草机亚马逊数据看板</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
       background:#f5f7fa; color:#1d1d1f; padding:24px 32px; }}
.container {{ max-width:900px; margin:0 auto; }}
.top-nav {{ display:flex; align-items:center; justify-content:space-between;
           margin-bottom:28px; padding:12px 20px; background:#fff;
           border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,0.05); }}
.top-nav .nav-brand {{ font-size:15px; font-weight:700; }}
.top-nav .nav-links a {{ font-size:13px; color:#0071e3; text-decoration:none; margin-left:18px; font-weight:600; }}
.langswitch {{ display:inline-flex; border:1px solid #d2d2d7; border-radius:999px; overflow:hidden; margin-left:18px; }}
.langswitch button {{ border:0; background:#fff; color:#0071e3; font:inherit; font-size:12px; font-weight:700;
                      padding:5px 13px; cursor:pointer; }}
.langswitch button.on {{ background:#0071e3; color:#fff; }}
h1 {{ font-size:24px; font-weight:700; margin:8px 0 4px; }}
h2.sec-title {{ font-size:19px; font-weight:700; margin:40px 0 4px; }}
.subtitle {{ font-size:13px; color:#86868b; margin-bottom:24px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.card {{ display:block; background:#fff; border-radius:14px; padding:20px 24px;
        box-shadow:0 1px 3px rgba(0,0,0,0.05); text-decoration:none; color:#1d1d1f;
        transition:transform .12s ease, box-shadow:.12s ease; }}
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
    <div class="nav-brand">{dual('🗺️ 割草机亚马逊数据看板', '🗺️ Lawn Mower Amazon Dashboard')}</div>
    <div class="nav-links">
      <a href="amazon_charts_latest.html">{dual('最新一期', 'Latest')}</a>
      <a href="price_trend.html">📈 {dual('价格趋势', 'Price Trend')}</a>
      <a href="index.html">{dual('首页', 'Home')}</a>
      <span class="langswitch">
        <button class="on" data-l="zh" type="button">中文</button>
        <button data-l="en" type="button">EN</button>
      </span>
    </div>
  </div>
  <h1>📚 {dual('往期索引', 'Archive')}</h1>
  <h2 class="sec-title">{dual('一、亚马逊 BSR 看板（往期）', '1. Amazon BSR dashboards (past issues)')}</h2>
  <div class="subtitle">{dual('亚马逊 6 国（DE/US/FR/IT/ES/GB）智能割草机 BSR 数据看板 · 每期为导出日的近 30 天累计销量 · 点击卡片查看当期完整图表',
                              'Amazon BSR dashboards for robotic lawn mowers across 6 markets (DE/US/FR/IT/ES/GB) · each issue shows trailing-30-day cumulative units on the export day · click a card for the full charts')}</div>
  <div class="grid">
    {''.join(cards)}
  </div>

  <h2 class="sec-title">{dual('二、割草机大盘看板', '2. Market dashboards')}</h2>
  <div class="subtitle">{dual('非亚马逊期次的常驻大盘看板 · 点击卡片进入',
                              'Standing market dashboards (not Amazon issues) · click a card to open')}</div>
  <div class="grid">
    {''.join(db_cards)}
  </div>

  <div class="footer">
    {dual('数据口径：每期为导出日近 30 天累计销量（窗口 = 导出日前 29 天至导出日，共 30 天）；两期相隔 7 天时，差值等价于「新 1 周 vs 旧 1 周」的周对比。',
          'Methodology: each issue shows trailing-30-day cumulative units as of the export day (window = export day minus 29 days through export day, 30 days inclusive); when two issues are 7 days apart, the difference equals a new-week vs prior-week comparison.')}<br>
    {dual('2026-09-11 期起口径收紧为「智能/机器人割草机」（已剔除手推式及独立配件），上期数据同口径重述。',
          'From the 2026-09-11 issue onward, scope is tightened to smart/robotic lawn mowers (push mowers and standalone accessories excluded); prior issues are restated on the same basis.')}
  </div>
</div>
<script>
(function(){{
  const titleEl=document.getElementById('pageTitle');
  function setLang(l){{
    document.documentElement.lang=l==='zh'?'zh-CN':'en';
    document.title=titleEl.dataset[l];
    document.querySelectorAll('[data-zh]').forEach(el=>{{ el.textContent=el.dataset[l]; }});
    document.querySelectorAll('.langswitch button').forEach(b=>b.classList.toggle('on',b.dataset.l===l));
  }}
  document.querySelectorAll('.langswitch button').forEach(b=>b.addEventListener('click',()=>setLang(b.dataset.l)));
}})();
</script>
</body>
</html>"""

with open("archive.html", "w", encoding="utf-8") as f:
    f.write(html)
print("archive.html rebuilt:", [(f, window_label(f.replace('amazon_charts_', '').replace('.html', ''))) for f in files])
