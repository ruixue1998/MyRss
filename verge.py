import requests
from lxml import html, etree

def get_top_stories_titles():
    url = "https://www.theverge.com/"
    print(f"正在请求 The Verge 首页: {url}")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"请求首页失败: {e}")
        return []
    doc = html.fromstring(resp.content)
    # 选取Top Stories区域的5个新闻标题
    print("正在解析首页 Top Stories 区域...")
    top_stories = doc.xpath('//div[@data-cy="top-stories"]//a[@data-analytics-link="article"]')
    print(f"共找到 {len(top_stories)} 个 Top Stories 链接节点")
    titles = []
    for a in top_stories:
        title = a.text_content().strip()
        print(f"抓取到标题: {title}")
        if title:
            titles.append(title)
        if len(titles) == 5:
            break
    print("【Top Stories 标题列表】")
    for idx, t in enumerate(titles, 1):
        print(f"{idx}. {t}")
    print("-" * 40)
    return titles

def filter_rss_by_titles(rss_url, output_file, titles):
    print(f"正在请求 RSS 源: {rss_url}")
    try:
        resp = requests.get(rss_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"请求RSS失败: {e}")
        return
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
    print(f"RSS 共找到 {len(entries)} 条 entry")
    count = 0
    for entry in entries:
        title_elem = entry.find('atom:title', namespaces=ns)
        if title_elem is not None:
            entry_title = title_elem.text.strip()
            print(f"RSS entry标题: {entry_title}")
            matched = False
            for top_title in titles:
                print(f"  与Top Stories标题对比: {top_title}")
                # 忽略大小写，模糊匹配
                if top_title.lower() in entry_title.lower() or entry_title.lower() in top_title.lower():
                    matched = True
                    print("    => 匹配成功！")
                    break
            if matched:
                new_feed.append(entry)
                count += 1
            else:
                print("    => 未匹配")
    print("-" * 40)
    print(f"最终匹配到 {count} 条Top Stories新闻。")

    # 写入新文件
    tree = etree.ElementTree(new_feed)
    tree.write(output_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
    print(f"已生成 {output_file}，共包含{count}条Top Stories新闻。")

if __name__ == "__main__":
    top_titles = get_top_stories_titles()
    if not top_titles:
        print("未获取到任何 Top Stories 标题，程序终止。")
    else:
        filter_rss_by_titles(
            rss_url="https://www.theverge.com/rss/index.xml",
            output_file="rss.xml",
            titles=top_titles
        )
