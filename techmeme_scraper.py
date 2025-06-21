import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def generate_verge_popular_rss():
    url = "https://www.theverge.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # 初始化RSS
    fg = FeedGenerator()
    fg.title("The Verge Most Popular")
    fg.link(href=url, rel="alternate")
    fg.description("The Verge 首页 Most Popular 前5新闻")
    fg.language("en")

    # 定位Most Popular区域
    most_popular = soup.find("h2", string=lambda s: s and "Most Popular" in s)
    if not most_popular:
        print("未找到Most Popular区域")
        return

    # 获取5条新闻
    news_items = []
    # Most Popular标题的下一个ul或div
    for sib in most_popular.find_next_siblings():
        # 兼容不同结构
        if sib.name == "ol" or sib.name == "ul":
            news_items = sib.find_all("li", limit=5)
            break
        elif sib.name == "div":
            # 可能是div包裹的
            news_items = sib.find_all("a", limit=5)
            break
    if not news_items:
        # 兜底方案：直接找所有包含新闻标题的a标签
        news_items = soup.select("section:has(h2:contains('Most Popular')) a")[:5]

    for item in news_items:
        # 兼容li结构和a结构
        if item.name == "li":
            a = item.find("a")
        else:
            a = item
        if not a or not a.has_attr("href"):
            continue
        link = a["href"]
        # 绝对路径
        if link.startswith("/"):
            link = "https://www.theverge.com" + link
        # 标题
        title = a.get_text(strip=True)
        # 描述（可选，首页一般没有摘要）
        desc = ""
        fe = fg.add_entry()
        fe.title(title)
        fe.link(href=link)
        fe.description(desc)
        fe.id(link)

    fg.rss_file("rss.xml", pretty=True)
    print("已生成rss.xml")

if __name__ == "__main__":
    generate_verge_popular_rss()
