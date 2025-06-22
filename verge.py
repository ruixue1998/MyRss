import requests
from bs4 import BeautifulSoup
from lxml import etree

# 1. 获取 The Verge 首页，提取 Top Stories 和 Most Popular 标题
home_url = "https://www.theverge.com/"
resp = requests.get(home_url)
soup = BeautifulSoup(resp.text, "html.parser")

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

# 2. 获取 Atom Feed
rss_url = "https://www.theverge.com/rss/index.xml"
rss_resp = requests.get(rss_url)
rss_content = rss_resp.content

# 3. 用lxml解析，保留所有内容
parser = etree.XMLParser(remove_blank_text=True)
root = etree.fromstring(rss_content, parser=parser)

# 4. 处理命名空间
ns = {'atom': 'http://www.w3.org/2005/Atom'}

# 5. 过滤entry，只保留标题匹配的
for entry in root.findall('atom:entry', namespaces=ns):
    title_elem = entry.find('atom:title', namespaces=ns)
    if title_elem is not None:
        title = title_elem.text.strip()
        if title not in top_titles:
            root.remove(entry)

# 6. 保存新 Atom Feed，保留格式和CDATA
et = etree.ElementTree(root)
et.write('filtered_atom.xml', encoding='utf-8', xml_declaration=True, pretty_print=True)
