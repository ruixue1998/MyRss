import requests
from lxml import etree, html

def get_top_stories_links():
    url = "https://www.theverge.com/"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    doc = html.fromstring(resp.content)
    # 选取Top Stories区域的5个新闻链接
    # 2024年6月的结构，Top Stories在data-cy="top-stories"的div下
    top_stories = doc.xpath('//div[@data-cy="top-stories"]//a[@data-analytics-link="article"]/@href')
    # 只取前5个，并补全为完整链接
    links = []
    for href in top_stories:
        if href.startswith("http"):
            links.append(href)
        else:
            links.append("https://www.theverge.com" + href)
        if len(links) == 5:
            break
    return links

def filter_rss_by_links(rss_url, output_file, links):
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

    # 只保留链接在links里的entry
    entries = root.findall('atom:entry', namespaces=ns)
    count = 0
    for entry in entries:
        link_elem = entry.find('atom:link', namespaces=ns)
        if link_elem is not None:
            href = link_elem.get('href')
            if href in links:
                new_feed.append(entry)
                count += 1

    # 写入新文件
    tree = etree.ElementTree(new_feed)
    tree.write(output_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
    print(f"已生成 {output_file}，共包含{count}条Top Stories新闻。")

if __name__ == "__main__":
    top_links = get_top_stories_links()
    filter_rss_by_links(
        rss_url="https://www.theverge.com/rss/index.xml",
        output_file="rss.xml",
        links=top_links
    )
