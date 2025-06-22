import requests
from lxml import html, etree

def get_top_stories_titles():
    url = "https://www.theverge.com/"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    doc = html.fromstring(resp.content)
    # 选取Top Stories区域的5个新闻标题
    top_stories = doc.xpath('//div[@data-cy="top-stories"]//a[@data-analytics-link="article"]')
    titles = []
    for a in top_stories:
        title = a.text_content().strip()
        if title:
            titles.append(title)
        if len(titles) == 5:
            break
    return titles

def filter_rss_by_titles(rss_url, output_file, titles):
    resp = requests.get(rss_url, timeout=10)
    resp.raise_for_status()
    xml = resp.content

    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml, parser=parser)

    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'thr': 'http://purl.org/syndication/thread/1.0'
    }

    # 构建新feed
    new_feed = etree.Element(root.tag, nsmap=root.nsmap)
    # 复制feed下除entry外的所有节点
    for child in root:
        if child.tag.endswith('entry'):
            continue
        new_feed.append(child)

    # 只保留标题在titles里的entry
    entries = root.findall('atom:entry', namespaces=ns)
    count = 0
    for entry in entries:
        title_elem = entry.find('atom:title', namespaces=ns)
        if title_elem is not None:
            entry_title = title_elem.text.strip()
            for top_title in titles:
                if entry_title == top_title:
                    new_feed.append(entry)
                    count += 1
                    break

    # 写入新文件
    tree = etree.ElementTree(new_feed)
    tree.write(output_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
    print(f"已生成 {output_file}，共包含{count}条Top Stories新闻。")

if __name__ == "__main__":
    top_titles = get_top_stories_titles()
    print("Top Stories 标题：")
    for t in top_titles:
        print(t)
    filter_rss_by_titles(
        rss_url="https://www.theverge.com/rss/index.xml",
        output_file="rss.xml",
        titles=top_titles
    )
