import requests
from lxml import etree

def extract_top_entries_from_verge_rss(rss_url, output_file, num_entries=6):
    # 获取官方RSS
    resp = requests.get(rss_url)
    resp.raise_for_status()
    xml = resp.content

    # 解析XML
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml, parser=parser)

    # 命名空间
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

    # 只保留前num_entries条entry
    entries = root.findall('atom:entry', namespaces=ns)
    for entry in entries[:num_entries]:
        new_feed.append(entry)

    # 写入新文件
    tree = etree.ElementTree(new_feed)
    tree.write(output_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
    print(f"已生成 {output_file}，共包含{num_entries}条新闻。")

if __name__ == "__main__":
    extract_top_entries_from_verge_rss(
        rss_url="https://www.theverge.com/rss/index.xml",
        output_file="rss.xml",
        num_entries=6
    )
