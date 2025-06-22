import requests
from bs4 import BeautifulSoup
from lxml import etree

# 1. 获取首页 Top Stories 和 Most Popular 的所有标题
home_url = "https://www.theverge.com/"
resp = requests.get(home_url)
soup = BeautifulSoup(resp.text, "html.parser")

def extract_titles(section_title):
    titles = set()
    # 查找对应区块
    section = soup.find("h2", string=section_title)
    if section:
        # 取父节点下所有标题
        for tag in section.find_parent().find_all(["h3", "h2", "a"]):
            text = tag.get_text(strip=True)
            if text:
                titles.add(text)
    return titles

top_titles = extract_titles("Top Stories")
popular_titles = extract_titles("Most Popular")
all_titles = top_titles | popular_titles

# 2. 解析 RSS/Atom
rss_url = "https://www.theverge.com/rss/index.xml"
rss_resp = requests.get(rss_url)
rss_tree = etree.fromstring(rss_resp.content)

namespace = {'atom': 'http://www.w3.org/2005/Atom'}
entries = rss_tree.findall('atom:entry', namespace)
for entry in entries:
    title_elem = entry.find('atom:title', namespace)
    if title_elem is not None:
        title = title_elem.text.strip()
        if title not in all_titles:
            rss_tree.remove(entry)

# 3. 保存为 rss.xml
etree.ElementTree(rss_tree).write("rss.xml", encoding="utf-8", xml_declaration=True)
