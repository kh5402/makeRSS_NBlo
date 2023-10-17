import os
import re
import requests
from xml.etree import ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from html import unescape

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
    include_phrase = url_and_xml['include_phrase']

    existing_links = set()
    
    if os.path.exists(xml_file_name):
        tree = ET.parse(xml_file_name)
        root = tree.getroot()
    else:
        root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(root, "channel")
        ET.SubElement(channel, "title").text = "Latest Blogs"
        ET.SubElement(channel, "description").text = "Nogizaka46 Latest Blog Posts"

    for item in root.findall(".//item/link"):
        existing_links.add(item.text)

    response = requests.get(url)
    html_content = unescape(response.text)
    article_pattern = re.compile(r'<a class="bl--card js-pos a--op hv--thumb" href="([^"]+)">')
    title_pattern = re.compile(r'<p class="bl--card__ttl">([^<]+)<\/p>')
    date_pattern = re.compile(r'<p class="bl--card__date">([^<]+)<\/p>')

    for link_match, title_match, date_match in zip(article_pattern.findall(html_content), title_pattern.findall(html_content), date_pattern.findall(html_content)):
        link = "https://www.nogizaka46.com" + link_match
        title = title_match
        date = date_match

        if any(phrase in title for phrase in include_phrase):
            if link in existing_links:
                continue

            channel = root.find("channel")
            new_item = ET.SubElement(channel, "item")
            ET.SubElement(new_item, "title").text = title
            ET.SubElement(new_item, "link").text = link
            ET.SubElement(new_item, "pubDate").text = date

    tree = ET.ElementTree(root)
    with open(xml_file_name, 'wb') as f:
        f.write(prettify(root).encode('utf-8'))
