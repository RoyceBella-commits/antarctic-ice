#!/usr/bin/env python3
"""Build the Antarctic Ice static site.

Each page lives in src/pages/<path>.html and starts with a front-matter comment:

    <!--
    title: 页面标题
    description: 一句话描述
    nav: models            # models | colding | harness | research | enterprise | pricing (optional)
    -->
    <section>...</section>
    <!--head--><style>...</style><!--/head-->   # optional: moved into <head> (page-only CSS)
    <!--scripts-->        # optional: everything after this goes after site.js
    <script>...</script>

Inside a page, write {{root}} before any site-internal path (e.g. {{root}}pricing.html);
the build replaces it with the right relative prefix. Run:  python3 tools/build.py
"""
import html
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pages"
# 404.html is served from any depth on GitHub Pages, so it uses the absolute site path.
BASE_PATH = os.environ.get("BASE_PATH", "/antarctic-ice/")

NAV = [
    ("models", "models.html", "模型"),
    ("colding", "colding.html", "Colding Plan"),
    ("harness", "harness.html", "Harness"),
    ("research", "research.html", "研究"),
    ("enterprise", "enterprise.html", "企业"),
    ("pricing", "pricing.html", "定价"),
]

FOOTER = [
    ("产品", [("models/cold-floe.html", "Cold Floe"), ("models/cold-sleet.html", "Cold Sleet"),
             ("models/cold-hail-ku.html", "Cold Hail-ku"), ("colding.html", "Colding Plan"), ("harness.html", "Harness")]),
    ("公司", [("about.html", "关于我们"), ("careers.html", "招聘：诚聘驯犬工程师"), ("news.html", "新闻"),
             ("partners.html", "冰川合作伙伴"), ("safety.html", "负责任冷缩政策")]),
    ("资源", [("docs.html", "文档"), ("harness-sizes.html", "马具尺码表"),
             ("status.html", "状态：全部系统正常结冰", "x-status"), ("community.html", "社区")]),
    ("法律", [("privacy.html", "隐私政策"), ("terms.html", "使用条款"), ("disclaimer.html", "冷责声明")]),
]

LOGO_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
            '<path d="M12 2v20M3.34 7l17.32 10M3.34 17L20.66 7" />'
            '<path d="M9.5 3.5L12 6l2.5-2.5M9.5 20.5L12 18l2.5 2.5M3.6 10.4L6.8 9.5 5.9 6.3M18.1 17.7l-.9-3.2 3.2-.9M3.6 13.6l3.2.9-.9 3.2M18.1 6.3l-.9 3.2 3.2.9" /></svg>')

TEMPLATE = """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <meta name="description" content="{description}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta name="theme-color" content="#0E1A24" />
    <link rel="icon" href="@ROOT@assets/favicon.svg" type="image/svg+xml" />
    <link rel="stylesheet" href="@ROOT@assets/css/site.css" />
    <script>document.documentElement.classList.add("x-js");</script>
{head}
  </head>
  <body>
    <div class="x-site" id="top">
      <a class="x-skip" href="#main">跳到正文</a>
      <a class="x-announce" href="@ROOT@models/cold-floe.html"><b>Cold Floe 4.5</b>&nbsp;现已发布 — <span>迄今最冷静的模型 →</span></a>

      <header class="x-nav" id="x-nav">
        <div class="x-wrap x-nav__in">
          <a class="x-logo" href="@ROOT@index.html" aria-label="Antarctic 首页">
            {logo}
            Antarctic
          </a>
          <ul class="x-nav__links" id="x-links">
{nav}
          </ul>
          <a class="x-btn x-btn--dark x-nav__cta" href="@ROOT@start.html">开始冷却</a>
          <button class="x-menu" id="x-menu" type="button" aria-label="打开菜单" aria-expanded="false" aria-controls="x-links">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M3 7h16M3 15h16" /></svg>
          </button>
        </div>
      </header>

      <main id="main">
{content}
      </main>

      <footer class="x-foot">
        <div class="x-wrap">
          <div class="x-foot__grid">
            <div class="x-foot__brand">
              <a class="x-logo" href="@ROOT@index.html" aria-label="Antarctic 首页">
                {logo}
                Antarctic
              </a>
              <p>冷静、可控、不会过热的智能。</p>
            </div>
{footer}
          </div>
          <div class="x-foot__bottom">
            <p>© 2026 Antarctic Ice, Inc. 保留所有冰块。</p>
            <p class="x-disc">本网站为虚构品牌恶搞创作，不代表任何真实公司或产品。</p>
          </div>
        </div>
      </footer>
    </div>
    <script src="@ROOT@assets/js/site.js"></script>
{scripts}
  </body>
</html>
"""


def parse_page(text):
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.split("  #")[0].strip()
    body = text[m.end():]
    head = ""
    hm = re.search(r"<!--head-->(.*?)<!--/head-->", body, re.S)
    if hm:
        head = hm.group(1).strip()
        body = body[:hm.start()] + body[hm.end():]
    scripts = ""
    if "<!--scripts-->" in body:
        body, scripts = body.split("<!--scripts-->", 1)
    return meta, body.strip("\n").rstrip(), scripts.strip(), head


def render(rel, meta, body, scripts, page_head=""):
    depth = rel.count("/")
    root = BASE_PATH if rel == "404.html" else "../" * depth
    active = meta.get("nav", "")
    nav = "\n".join(
        '            <li><a href="{{root}}%s"%s>%s</a></li>' % (href, ' aria-current="page"' if key == active else "", label)
        for key, href, label in NAV)
    cols = []
    for head, links in FOOTER:
        items = []
        for link in links:
            cls = ' class="%s"' % link[2] if len(link) > 2 else ""
            items.append('<li><a href="@ROOT@%s"%s>%s</a></li>' % (link[0], cls, link[1]))
        cols.append('            <div><h4>%s</h4><ul>%s</ul></div>' % (head, "".join(items)))
    title = meta.get("title", "")
    full_title = "Antarctic 南极冰 官网" if rel == "index.html" else "%s · Antarctic 南极冰" % title
    out = TEMPLATE.format(
        title=html.escape(full_title, quote=False),
        description=html.escape(meta.get("description", ""), quote=True),
        logo=LOGO_SVG,
        nav=nav,
        footer="\n".join(cols),
        content=body,
        scripts=("    " + scripts) if scripts else "",
        head=("    " + page_head) if page_head else "",
    )
    return out.replace("@ROOT@", root).replace("{{root}}", root)


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])


def check_links(outputs):
    parsed = {}
    for rel, text in outputs.items():
        p = LinkCollector()
        p.feed(text)
        parsed[rel] = p
    problems = []
    for rel, p in parsed.items():
        if rel == "404.html":
            continue
        base = Path(rel).parent
        for link in p.links:
            if re.match(r"^(https?:|mailto:|tel:|data:|javascript:)", link):
                continue
            path, _, frag = link.partition("#")
            path = path.split("?")[0]
            if not path:
                target = rel
            else:
                target = os.path.normpath(str(base / path)).replace("\\", "/")
            if target.endswith("/"):
                target += "index.html"
            if target in parsed:
                if frag and frag not in parsed[target].ids and frag not in ("top", "main"):
                    problems.append("%s: missing anchor %s" % (rel, link))
            elif not (ROOT / target).exists():
                problems.append("%s: broken link %s" % (rel, link))
    return problems


def main():
    outputs = {}
    for src in sorted(SRC.rglob("*.html")):
        rel = src.relative_to(SRC).as_posix()
        try:
            meta, body, scripts, head = parse_page(src.read_text(encoding="utf-8"))
        except ValueError as e:
            print("skip %s: %s" % (rel, e))
            continue
        outputs[rel] = render(rel, meta, body, scripts, head)
    for rel, text in outputs.items():
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    print("built %d pages" % len(outputs))
    problems = check_links(outputs)
    for pr in problems:
        print("  !", pr)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
