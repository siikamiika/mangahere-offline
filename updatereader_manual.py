#!/usr/bin/env python3

from sys import argv
import os
from urllib.parse import quote

script_path = os.path.dirname(os.path.realpath(__file__))
mangadir = argv[1]
chapters = dict()

for d in os.listdir(mangadir):
    fp = os.path.join(mangadir, d)
    if os.path.isdir(fp):
        chapters[d] = sorted(os.listdir(fp))

with open(os.path.join(script_path, 'reader.html')) as html:
    base = html.read()

chapter_list = sorted(chapters)
for idx, chapter in enumerate(chapter_list):
    chapter_view = base
    for page in chapters[chapter]:
        if page == 'index.html': continue
        chapter_view += (
            '<a href="#{page}">{chapter}/{page}</a>'
            '<img class="page" id="{page}" src="{page}">'
        ).format(chapter=quote(chapter), page=quote(page))
    try:
        chapter_view += '<a id="next" href="../{c}/index.html">NEXT ({c})</a>'.format(c=chapter_list[idx+1])
    except: pass
    chapter_view += '<script>document.title = "{}"</script>'.format(mangadir.strip('/').strip('\\'))
    with open(os.path.join(mangadir, chapter, 'index.html'), 'w') as c:
        c.write(chapter_view)
