#!/usr/bin/env python3
"""把确认过的首页设计整理为无外部依赖的静态站点。"""
from pathlib import Path
import base64
import hashlib
import re

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
ASSETS = DIST / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
fragment = (ROOT / "src/home.html").read_text()


def asset(name, data, suffix):
    if isinstance(data, str):
        data = data.encode()
    filename = f"{name}-{hashlib.sha256(data).hexdigest()[:12]}.{suffix}"
    (ASSETS / filename).write_bytes(data)
    return f"/assets/{filename}"


def image(match):
    return asset("hero", base64.b64decode(match[2]), "jpg" if match[1] == "jpeg" else match[1])


fragment = re.sub(r"data:image/(jpeg|png);base64,([A-Za-z0-9+/=]+)", image, fragment)
hero = re.search(r'src="(/assets/hero-[^"]+)"', fragment)[1]
css = re.search(r"<style>([\s\S]*?)</style>", fragment)[1]
script = re.search(r"<script>([\s\S]*?)</script>", fragment)[1]
fragment = re.sub(r"<style>[\s\S]*?</style>|<script>[\s\S]*?</script>", "", fragment)
fragment = fragment.replace('style="color:var(--jx-accent)"', 'class="jx-brand-dot"')
css += """
:root { color-scheme:light dark; }
html,body { margin:0; background:light-dark(#f5f5f7,#080809); }
#jiyax-quiet .jx-viewport { height:100dvh; height:100svh; }
#jiyax-quiet .jx-brand-dot { color:var(--jx-accent); }
#jiyax-quiet button, #jiyax-quiet a { cursor:pointer; }
@media(max-width:600px) {
  #jiyax-quiet .jx-languages { margin-right:0; }
}
"""
css += (ROOT / "src/site.css").read_text()

script = script.replace("      const state = { version:2, lang:'zh',", """      let savedLanguage = null;
      try { savedLanguage = localStorage.getItem('jiyax.language.preference'); } catch (_) {}
      const requestedLanguage = new URLSearchParams(location.search).get('lang');
      const preferredLanguage = chooseJiyaxLanguage(navigator.languages?.[0] || navigator.language || '', savedLanguage, requestedLanguage);
      const state = { version:2, lang:preferredLanguage,""")
script = script.replace("      let stateRevision = 0;\n", "")
start = script.index("      const save = () => {")
end = script.index("      const syncSlides", start)
script = script[:start] + """      const save = () => {
        const url = new URL(location.href);
        url.searchParams.set('lang', state.lang);
        history.replaceState(null, '', url.pathname + url.search + url.hash);
      };
""" + script[end:]
start = script.index("      const restore = saved => {")
script = script[:start] + "      renderLanguage();\n    })();\n"
script = script.replace("viewport:'JIYAX 可滚动网站预览'", "viewport:'JIYAX — 无际涯'")
script = script.replace("viewport:'JIYAX scrollable website preview'", "viewport:'JIYAX — Think further. Go beyond.'")
script = script.replace("detailPreview:'内容结构预览 · 子站域名为规划'", "detailPreview:'栏目筹备中 · 即将上线'")
script = script.replace("detailPreview:'Content preview · proposed subdomain'", "detailPreview:'Coming soon · a preview of this section'")
script = script.replace("        viewport.lang=state.lang;", """        viewport.lang=state.lang;
        document.documentElement.lang=state.lang==='en'?'en':'zh-CN';
        document.title=state.lang==='en'?'JIYAX — AI, VPS & Crypto':'无际涯 JIYAX | AI 订阅、VPS 推荐与加密';
        const description=state.lang==='en'
          ?'Explore AI subscriptions, VPS recommendations and crypto with JIYAX. Think further. Go beyond.'
          :'无际涯 JIYAX：探索 ChatGPT、Claude AI 订阅，VPS 推荐与自托管，以及加密货币、U 卡和数字游民生活。';
        document.querySelector('meta[name="description"]').content=description;
        document.querySelector('meta[property="og:title"]').content=document.title;
        document.querySelector('meta[property="og:description"]').content=description;
        document.querySelector('meta[property="og:locale"]').content=state.lang==='en'?'en_US':'zh_CN';
        const canonical='https://jiyax.com/?lang='+state.lang;
        document.querySelector('link[rel="canonical"]').href=canonical;
        document.querySelector('meta[property="og:url"]').content=canonical;""")
assert "window.openai" not in script and "Tweak" not in script
script = (ROOT / "src/language.js").read_text() + "\n" + script

stylesheet = asset("site", css, "css")
javascript = asset("site", script, "js")
head = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>无际涯 JIYAX | AI 订阅、VPS 推荐与加密</title>
  <meta name="description" content="无际涯 JIYAX：探索 ChatGPT、Claude AI 订阅，VPS 推荐与自托管，以及加密货币、U 卡和数字游民生活。">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="theme-color" content="#f5f5f7">
  <link rel="canonical" href="https://jiyax.com/?lang=zh">
  <link rel="alternate" hreflang="zh-CN" href="https://jiyax.com/?lang=zh">
  <link rel="alternate" hreflang="en" href="https://jiyax.com/?lang=en">
  <link rel="alternate" hreflang="x-default" href="https://jiyax.com/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="JIYAX · 无际涯">
  <meta property="og:title" content="无际涯 JIYAX | AI 订阅、VPS 推荐与加密">
  <meta property="og:description" content="探索 AI、VPS 与更自由的数字生活。Think further. Go beyond.">
  <meta property="og:url" content="https://jiyax.com/">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:image" content="https://jiyax.com{hero}">
  <meta property="og:image:alt" content="JIYAX silver infinity sculpture">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="JIYAX · 无际涯">
  <meta name="twitter:description" content="AI subscriptions, VPS recommendations and crypto. Think further. Go beyond.">
  <meta name="twitter:image" content="https://jiyax.com{hero}">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="{hero}" as="image" fetchpriority="high">
  <link rel="stylesheet" href="{stylesheet}">
  <script src="{javascript}" defer></script>
</head>
<body>
"""
(DIST / "index.html").write_text(head + fragment + "\n</body>\n</html>\n")
(DIST / "favicon.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="#1d1d1f"/><text x="32" y="46" text-anchor="middle" font-family="Arial,sans-serif" font-weight="700" font-size="43" fill="#fff">J</text></svg>\n''')
(DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://jiyax.com/sitemap.xml\n")
(DIST / "sitemap.xml").write_text('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://jiyax.com/?lang=zh</loc>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="https://jiyax.com/?lang=zh"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://jiyax.com/?lang=en"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://jiyax.com/"/>
  </url>
  <url>
    <loc>https://jiyax.com/?lang=en</loc>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="https://jiyax.com/?lang=zh"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://jiyax.com/?lang=en"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://jiyax.com/"/>
  </url>
</urlset>
''')
print(f"Built {DIST}; HTML {len((head + fragment).encode()):,} bytes")
print(f"Assets: {stylesheet}, {javascript}, {hero}")
