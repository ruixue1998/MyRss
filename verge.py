import requests
from bs4 import BeautifulSoup
from lxml import etree
import os

def get_top_titles():
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
    return top_titles

def is_match(entry_title, titles):
    # 宽松匹配，防止因细微差别误删
    for t in titles:
        if entry_title.strip().lower() in t.strip().lower() or t.strip().lower() in entry_title.strip().lower():
            return True
    return False

def main():
    # 1. 获取 Top Stories 和 Most Popular 标题
    top_titles = get_top_titles()
    print("【调试】Top Stories/Most Popular 标题：", top_titles)

    # 2. 获取 Atom Feed
    rss_url = "https://www.theverge.com/rss/index.xml"
    rss_resp = requests.get(rss_url)
    rss_content = rss_resp.content

    # 3. 用lxml解析
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(rss_content, parser=parser)

    # 4. 处理命名空间
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    entries = root.findall('atom:entry', namespaces=ns)
    print("【调试】原始 entry 数量：", len(entries))

    # 打印所有 entry 的标题，人工比对
    all_entry_titles = []
    for entry in entries:
        title_elem = entry.find('atom:title', namespaces=ns)
        if title_elem is not None:
            entry_title = title_elem.text.strip()
            all_entry_titles.append(entry_title)
    print("【调试】Feed中所有 entry 的标题：", all_entry_titles)

    # 5. 只删除不需要的entry，绝不动其它内容
    removed_count = 0
    for entry in list(entries):
        title_elem = entry.find('atom:title', namespaces=ns)
        if title_elem is not None:
            entry_title = title_elem.text.strip()
            if not is_match(entry_title, top_titles):
                root.remove(entry)
                removed_count += 1

    print("【调试】删除的 entry 数量：", removed_count)
    print("【调试】保留后的 entry 数量：", len(root.findall('atom:entry', namespaces=ns)))

    # 6. 保存，覆盖rss.xml，保留所有内容和格式
    et = etree.ElementTree(root)
    et.write('rss.xml', encoding='utf-8', xml_declaration=True, pretty_print=True)
    print("rss.xml 已更新！")
    print("文件修改时间：", os.path.getmtime('rss.xml'))

    # 可选：输出部分内容做人工检查
    with open('rss.xml', 'r', encoding='utf-8') as f:
        print("rss.xml 前500字符：\n", f.read(500))

if __name__ == "__main__":
    main()
