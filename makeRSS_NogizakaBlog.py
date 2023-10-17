import os
import re
import requests
import xml.dom.minidom
from xml.etree import ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from html import unescape
from xml.etree.ElementTree import ElementTree, Element, tostring

def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

url_and_xmls = [
        {
            'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?ct=55387&cd=MEMBER',
            'xml': 'feed_Blog_Yumiki.xml',
            'include_phrase': [],
        },
        {
            'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?ct=40001&cd=MEMBER',
            'xml': 'feed_Blog_Yumiki.xml',
            'include_phrase': ['弓木'],
        },
        {
            'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?ct=48010&cd=MEMBER',
            'xml': 'feed_Blog_Kanagawa.xml',
            'include_phrase': [],
        },
        {
            'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?ct=40005&cd=MEMBER',
            'xml': 'feed_Blog_Kanagawa.xml',
            'include_phrase': ['金川'],
        },
        {
            'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?ima=5025&ct=55396',
            'xml': 'feed_Blog_Nogizaka.xml',
            'include_phrase': [],
        },
]

for url_and_xml in url_and_xmls:
    url = url_and_xml['url']
    xml_file_name = url_and_xml['xml']
    include_phrase = url_and_xml.get('include_phrase', [])

    # XMLの初期化
    root = Element("rss", version="2.0")
    channel = SubElement(root, "channel")
    SubElement(channel, "title").text = "Latest Blogs"
    SubElement(channel, "description").text = "Nogizaka46 Latest Blog Posts"

    while url:  # URLがNoneになるまで続ける
        print(f"Fetching URL: {url}")  # 確認用

        response = requests.get(url)
        html_content = response.text

        # 記事を見つける
        link_pattern = re.compile(r'<a class="bl--card js-pos a--op hv--thumb" href="([^"]+)">')
        title_pattern = re.compile(r'<p class="bl--card__ttl">([^<]+)</p>')
        date_pattern = re.compile(r'<p class="bl--card__date">([^<]+)</p>')

        links = link_pattern.findall(html_content)
        titles = title_pattern.findall(html_content)
        dates = date_pattern.findall(html_content)

        print(f"Found links: {links}")  # 確認用
        print(f"Found titles: {titles}")  # 確認用
        print(f"Found dates: {dates}")  # 確認用

        for link, title, date in zip(links, titles, dates):
            if any(phrase in title for phrase in include_phrase):
                item = SubElement(channel, "item")
                SubElement(item, "title").text = title
                SubElement(item, "link").text = f"https://www.nogizaka46.com{link}"
                SubElement(item, "pubDate").text = date

        # 次のページへ
        next_page_pattern = re.compile(r'<a href="(/s/n46/diary/MEMBER/list\?ima=\d+&amp;page=\d+&amp;ct=\d+&amp;cd=MEMBER)">')
        next_page_match = next_page_pattern.search(html_content)
        url = f"https://www.nogizaka46.com{next_page_match.group(1)}" if next_page_match else None

        print(f"Next URL: {url}")  # 確認用
    
    # XMLを保存
    # ElementTreeオブジェクトを作成
    tree = ElementTree(root)
    
    # XML文字列に変換
    ml_string = tostring(root)

    # minidomできれいにする
    dom = xml.dom.minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(encoding="utf-8")
    
    with open(xml_file_name, 'wb') as f:
        f.write(pretty_xml)
    
print("Done!")  # 確認用
