#!/usr/bin/env python3

from urllib.request import urlopen, urlretrieve, Request
from urllib.parse import quote
from sys import argv
from bs4 import BeautifulSoup as BS
import re
import os
import zlib
import json
import socket
from time import sleep

socket.setdefaulttimeout(30)

script_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(script_path, 'reader.html')) as html:
    chapter_base = html.read()

def update_reader(chapter, next):
    chapter_view = chapter_base
    chapter_dir = os.path.join(manga, chapter)
    for page in os.listdir(chapter_dir):
        if page == 'index.html': continue
        chapter_view += (
            '<a href="#{page}">{chapter}/{page}</a>'
            '<img class="page" id="{page}" src="{page}">'
        ).format(chapter=quote(chapter), page=quote(page))
    if next:
        chapter_view += '<a id="next" href="../{c}/index.html">NEXT ({c})</a>'.format(c=next)
    chapter_view += '<script>document.title = "{}"</script>'.format(manga)
    with open(os.path.join(chapter_dir, 'index.html'), 'w') as c:
        c.write(chapter_view)

def urlopen_retrier(url):
    headers = {
        'User-Agent':       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0',
        'Accept':           'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':  'en-US,en;q=0.5',
        'Accept-Encoding':  'gzip',
    }
    times = 0
    while times < 5:
        try:
            r = Request(url, headers=headers)
            return urlopen(r)
        except Exception as e:
            print(e)
            sleep(5)
            times += 1
    raise Exception('Aborted: 5 errors in a row. Chapter possibly incomplete.')

def decompress(data):
    try:
        if data[:2] == b'\x1f\x8b':
            return zlib.decompress(data, 16+zlib.MAX_WBITS)
        else:
            return data
    except Exception as e:
        print(e)
        return data

def search_manga(query):
    results = decompress(urlopen_retrier(
        'http://www.mangahere.co/ajax/search.php?query={}'.format(quote(query))
        ).read()).decode()
    results = json.loads(results)
    suggestions = ['{}: {}'.format(i, s) for i, s in enumerate(results['suggestions'])]
    choice_index = int(input(
        'Enter a number\n{}\n'.format('\n'.join(suggestions))
        ))
    return results['data'][choice_index], results['suggestions'][choice_index]

search = argv[1]
if search == 'url':
    choice_url = argv[2]
    choice = choice_url.split('/manga/')[-1]
else:
    choice_url, choice = search_manga(' '.join(argv[1:]))

manga = re.sub('[^a-zA-Z]+', '_', choice).lower().strip('_')
if not os.path.exists(manga):
    os.makedirs(manga)

chapterlist_page = decompress(urlopen_retrier(choice_url).read())
chapter_list = BS(chapterlist_page)
pattern = re.escape(choice_url)+'.*?c[0-9]+'
chapters = chapter_list.find_all(
        href=re.compile(pattern)
    )
chapters = [c['href'] for c in chapters]
prev_chapter = None

for c in sorted(chapters):
    chapter_name = re.search('(v[0-9]+/)?c[0-9]+', c).group(0).replace('/', '')
    chapter_dir = os.path.join(manga, chapter_name)
    if not os.path.exists(chapter_dir):
        os.makedirs(chapter_dir)
        if prev_chapter:
            update_reader(prev_chapter, chapter_name)
        prev_chapter = chapter_name
    else:
        prev_chapter = chapter_name
        continue
    print('\n\n\nDownloading {}\n\n\n'.format(chapter_name))
    chapter_page = decompress(urlopen_retrier(c).read())
    chapter = BS(chapter_page)
    pages = [o['value'] for o in chapter.find('div', {'class': 'go_page clearfix'}).find_all('option')]

    for pn, p in enumerate(pages):
        print(p)
        image_page = decompress(urlopen_retrier(p).read())
        img = BS(image_page).find(id='viewer').img['src']
        fn = os.path.join(chapter_dir, str(pn).zfill(3)+'.jpg')
        times = 0
        while True:
            try:
                urlretrieve(img, fn)
                break
            except Exception as e:
                print(e)
                sleep(5)
                times += 1
                if times > 5:
                    raise Exception('Aborted: 5 errors in a row. Chapter possibly incomplete.')

        print('Downloaded page '+img)
