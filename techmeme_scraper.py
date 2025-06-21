import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

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
    fg.updated(datetime.utcnow())

    # 定位Most Popular区域
    most_popular = soup.find("h2", string=lambda s: s and "Most Popular" in s)
    if not most_popular:
        print("未找到Most Popular区域")
        return

    # 获取5条新闻
    news_items = []
    for sib in most_popular.find_next_siblings():
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
        if item.name == "li":
            a = item.find("a")
        else:
            a = item
        if not a or not a.has_attr("href"):
            continue
        link = a["href"]
        if link.startswith("/"):
            link = "https://www.theverge.com" + link
        title = a.get_text(strip=True)
        # 尝试获取摘要
        desc = ""
        # 尝试获取作者和时间
        author = "The Verge"
        published = datetime.utcnow().isoformat() + "Z"
        # 进入新闻详情页抓取摘要、作者、发布时间
        try:
            detail = requests.get(link, headers=headers, timeout=10)
            detail.raise_for_status()
            detail_soup = BeautifulSoup(detail.text, "html.parser")
            # 摘要
            desc_tag = detail_soup.find("meta", attrs={"name": "description"})
            if desc_tag and desc_tag.has_attr("content"):
                desc = desc_tag["content"]
            # 作者
            author_tag = detail_soup.find("meta", attrs={"name": "author"})
            if author_tag and author_tag.has_attr("content"):
                author = author_tag["content"]
            # 发布时间
            pub_tag = detail_soup.find("meta", attrs={"property": "article:published_time"})
            if pub_tag and pub_tag.has_attr("content"):
                published = pub_tag["content"]
        except Exception as e:
            pass

        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link, rel="alternate")
        fe.author({"name": author})
        fe.published(published)
        fe.updated(published)
        fe.summary(desc, type="html")
        fe.content(desc, type="html")

    fg.atom_file("rss.xml", pretty=True)
    print("已生成rss.xml（Atom格式）")

if __name__ == "__main__":
    generate_verge_popular_atom()
