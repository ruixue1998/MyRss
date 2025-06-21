import requests
from bs4 import BeautifulSoup, Tag
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

def get_entry_id(detail_soup, link):
    # 优先用 canonical，其次 og:url，最后 fallback 用原始链接
    id_tag = detail_soup.find("link", rel="canonical")
    if id_tag and id_tag.has_attr("href"):
        return id_tag["href"]
    og_url = detail_soup.find("meta", attrs={"property": "og:url"})
    if og_url and og_url.has_attr("content"):
        return og_url["content"]
    return link

def get_categories(detail_soup):
    categories = []
    section_tag = detail_soup.find("meta", attrs={"property": "article:section"})
    if section_tag and section_tag.has_attr("content"):
        categories.append(section_tag["content"])
    tag_tags = detail_soup.find_all("meta", attrs={"property": "article:tag"})
    for tag in tag_tags:
        if tag.has_attr("content"):
            categories.append(tag["content"])
    return categories

def get_content_html(detail_soup):
    # 优先取正文article，保留图片
    article = detail_soup.find("article")
    if article:
        # 保证图片src为绝对路径
        for img in article.find_all("img"):
            if img.has_attr("src") and img["src"].startswith("/"):
                img["src"] = "https://www.theverge.com" + img["src"]
        return str(article)
    # 兜底：用 og:description
    og_desc = detail_soup.find("meta", attrs={"property": "og:description"})
    if og_desc and og_desc.has_attr("content"):
        return og_desc["content"]
    return ""

def generate_verge_popular_atom():
    url = "https://www.theverge.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    fg = FeedGenerator()
    fg.id("https://www.theverge.com/rss/index.xml")
    fg.title("The Verge Most Popular")
    fg.subtitle("The Verge 首页 Most Popular 前5新闻")
    fg.link(href="https://www.theverge.com", rel="alternate")
    fg.link(href="https://www.theverge.com/rss/index.xml", rel="self")
    fg.language("en")
    fg.icon("https://platform.theverge.com/wp-content/uploads/sites/2/2025/01/verge-rss-large_80b47e.png?w=150&h=150&crop=1")
    fg.updated(datetime.now(timezone.utc))

    # 定位Most Popular区域
    most_popular = soup.find("h2", string=lambda s: 'Most Popular' in s if isinstance(s, str) else False)
    if not most_popular:
        print("未找到Most Popular区域")
        return

    # 获取5条新闻
    news_items = []
    for sib in most_popular.find_next_siblings():
        if isinstance(sib, Tag):
            if sib.name in ["ol", "ul"]:
                news_items = sib.find_all("li", limit=5)
                break
            elif sib.name == "div":
                news_items = sib.find_all("a", limit=5)
                break

    if not news_items:
        print("未找到Most Popular新闻条目")
        return

    for item in news_items:
        # 兼容li结构和a结构
        if isinstance(item, Tag) and item.name == "li":
            a = item.find("a")
        elif isinstance(item, Tag):
            a = item
        else:
            continue
        if not (
