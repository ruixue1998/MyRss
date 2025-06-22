import feedparser
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

# 你要抓取的RSS源
RSS_URL = "https://www.theverge.com/rss/index.xml"

# 你要筛选的标题列表（去重后的Top Stories和Most Popular）
TARGET_TITLES = [
    "The Nintendo Switch 2 is an awesome upgrade for parents like me",
    "Meta announces Oakley smart glasses",
    "28 Years Later is a bleak fever dream with rage pumping through its veins",
    "Inside the courthouse reshaping the future of the internet",
    "What happens when AI comes for our fonts?",
    "You sound like ChatGPT",
    "The Verge’s guide to Amazon Prime Day 2025",
    "Apple’s tiny M4 Mac Mini has dropped to its lowest price yet",
    "Samsung’s entry-level Galaxy Watch 7 has returned to its best price to date"
]

def main():
    feed = feedparser.parse(RSS_URL)
    # 创建Atom根节点
    feed_elem = Element('feed', {
        'xmlns': 'http://www.w3.org/2005/Atom',
        'xmlns:thr': 'http://purl.org/syndication/thread/1.0'
    })
    title_elem = SubElement(feed_elem, 'title', {'type': 'text'})
    title_elem.text = "The Verge"
    subtitle_elem = SubElement(feed_elem, 'subtitle', {'type': 'text'})
    subtitle_elem.text = "The Verge is about technology and how it makes us feel. Founded in 2011, we offer our audience everything from breaking news to reviews to award-winning features and investigations, on our site, in video, and in podcasts."
    link_elem = SubElement(feed_elem, 'link', {'rel': 'alternate', 'type': 'text/html', 'href': 'https://www.theverge.com'})
    id_elem = SubElement(feed_elem, 'id')
    id_elem.text = RSS_URL

    # 按标题筛选
    for entry in feed.entries:
        if entry.title in TARGET_TITLES:
            entry_elem = SubElement(feed_elem, 'entry')
            title = SubElement(entry_elem, 'title')
            title.text = entry.title
            link = SubElement(entry_elem, 'link', {'href': entry.link})
            id_ = SubElement(entry_elem, 'id')
            id_.text = entry.link
            updated = SubElement(entry_elem, 'updated')
            updated.text = entry.updated if hasattr(entry, 'updated') else entry.published
            summary = SubElement(entry_elem, 'summary', {'type': 'html'})
            summary.text = entry.summary if hasattr(entry, 'summary') else ''

    # 输出到文件
    tree = ElementTree(feed_elem)
    tree.write("rss.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()
