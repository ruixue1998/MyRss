import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# 1. 获取 The Verge 首页
home_url = "https://www.theverge.com/"
resp = requests.get(home_url)
soup = BeautifulSoup(resp.text, "html.parser")

# 2. 提取 Top Stories 和 Most Popular 标题
top_titles = set()

# Top Stories
for h2 in soup.find_all('h2'):
    if 'Top Stories' in h2.get_text():
        section = h2.find_parent('section')
        if section:
            for a in section.find_all('a'):
                title = a.get_text(strip=True)
                if title:
                    top_titles.add(title)

# Most Popular
for h2 in soup.find_all('h2'):
    if 'Most Popular' in h2.get_text():
        section = h2.find_parent('section')
        if section:
            for a in section.find_all('a'):
                title = a.get_text(strip=True)
                if title:
                    top_titles.add(title)

# 3. 获取 RSS
rss_url = "https://www.theverge.com/rss/index.xml"
rss_resp = requests.get(rss_url)
rss_root = ET.fromstring(rss_resp.content)
channel = rss_root.find('channel')
items = channel.findall('item')

# 4. 只保留匹配的 <item>
for item in items:
    title = item.find('title').text.strip()
    if title not in top_titles:
        channel.remove(item)

# 5. 保存新 RSS，结构不变
ET.ElementTree(rss_root).write('filtered_rss.xml', encoding='utf-8', xml_declaration=True)
