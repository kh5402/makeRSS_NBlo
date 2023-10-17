import os
import re
import requests
import xml.dom.minidom
from xml.etree import ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from html import unescape
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring

def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

url_and_xmls = [
        {
            'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?page=0&ct=55387&cd=MEMBER',
            'xml': 'feed_Blog_Yumiki.xml',
            'include_phrase': [],
        },
        #{
        #    'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?page=0&ct=40001&cd=MEMBER',
        #    'xml': 'feed_Blog_Yumiki.xml',
        #    'include_phrase': ['弓木'],
        #},
        #{
        #    'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?page=0&ct=48010&cd=MEMBER',
        #    'xml': 'feed_Blog_Kanagawa.xml',
        #    'include_phrase': [],
        #},
        #{
        #    'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?page=0&ct=40005&cd=MEMBER',
        #    'xml': 'feed_Blog_Kanagawa.xml',
        #    'include_phrase': ['金川'],
        #},
        #{
        #    'url': 'https://www.nogizaka46.com/s/n46/diary/MEMBER/list?page=0&ct=55396&cd=MEMBER',
        #    'xml': 'feed_Blog_Nogizaka.xml',
        #    'include_phrase': [],
        #},
]

# 各XMLファイル名に対応するchannel要素を保存する辞書
xml_data = {}

page_number = 0  # ページ番号の初期化

for url_and_xml in url_and_xmls:
    url = url_and_xml['url']
    xml_file_name = url_and_xml['xml']
    include_phrase = url_and_xml.get('include_phrase', [])

    # xml_dataにchannel要素がなければ作成
    if xml_file_name not in xml_data:
        root = Element("rss", version="2.0")
        channel = SubElement(root, "channel")
        SubElement(channel, "title").text = "Latest Blogs"
        SubElement(channel, "description").text = "Nogizaka46 Latest Blog Posts"
        xml_data[xml_file_name] = {'root': root, 'channel': channel}
    else:
        channel = xml_data[xml_file_name]['channel']

    while url:
        print(f"Fetching URL: {url}")  # Debug
        response = requests.get(url)
        html_content = response.text

        # 記事のリンク、タイトル、日付を取得
        link_pattern = re.compile(r'<a class="bl--card js-pos a--op hv--thumb" href="([^"]+)">')
        title_pattern = re.compile(r'<p class="bl--card__ttl">([^<]+)</p>')
        date_pattern = re.compile(r'<p class="bl--card__date">([^<]+)</p>')

        links = link_pattern.findall(html_content)
        titles = title_pattern.findall(html_content)
        dates = date_pattern.findall(html_content)

        print(f"Found links: {links}")  # Debug
        print(f"Found titles: {titles}")  # Debug
        print(f"Found dates: {dates}")  # Debug

        for link, title, date in zip(links, titles, dates):
            if not include_phrase or any(phrase in title for phrase in include_phrase):
                item = SubElement(channel, "item")
                SubElement(item, "title").text = title
                SubElement(item, "link").text = f"https://www.nogizaka46.com{link}"
                SubElement(item, "pubDate").text = date

        for title in titles:
            if "該当するデータがございません" in title:
                url = None  # 次のページがないので、ループを終了
                break  # forループを抜ける
            
        if url:
            page_number += 1
            next_url = re.sub(r'page=\d+', f'page={page_number}', url)  # URL内のpage数を更新
            url = next_url
        else:
            break  # ループを抜ける
    else:
        url = None  # ページがなければNoneに設定

    print(f"Next URL: {url}")  # Debug

# 最後に各XMLファイルに書き出し
for xml_file_name, data in xml_data.items():
    root = data['root']
    xml_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(xml_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    with open(xml_file_name, 'wb') as f:
        f.write(pretty_xml.encode('utf-8'))

print("Done!")
