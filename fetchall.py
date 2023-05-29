#!/usr/bin/env python

import urllib.request
import urllib.parse
from xml import sax
import re

STORAGE_API_URL = 'https://storage.googleapis.com/chromium-browser-official/'
NEXT_MARKER_URL = STORAGE_API_URL + '?%s'
VERSION_PATTERN = r'^chromium-((\d+(\.\d+)*){2})\.tar\.xz$'
MARKDOWN_FORMAT = '\n[%s](https://storage.googleapis.com/chromium-browser-official/chromium-%s.tar.xz)\n'

class AWSS3Handler(sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self.content = None
        self.nextmarker = None
        self.items = []

    def characters(self, content):
        if self.content:
            self.content += content
        else:
            self.content = content

    def endElement(self, name):
        if name == 'NextMarker':
            self.nextmarker = self.content
        elif name == 'Key':
            matched = re.match(VERSION_PATTERN, self.content)
            if matched:
                self.items.append(matched.group(1))
        self.content = None

if __name__ == '__main__':
    versions = []
    info = urllib.request.urlopen(STORAGE_API_URL).read()
    handler = AWSS3Handler()
    sax.parseString(info, handler)
    versions.extend(handler.items)
    while handler.nextmarker:
        params = urllib.parse.urlencode({'marker': handler.nextmarker[:-1]+'@'})
        info = urllib.request.urlopen(NEXT_MARKER_URL % params).read()
        handler = AWSS3Handler()
        sax.parseString(info, handler)
        versions.extend(handler.items)
    from datetime import datetime
    print('# Update Time: %s\n' % datetime.now())
    print('\n# Download\n')
    versions.sort(key=lambda x:tuple(int(v) for v in x.split('.')), reverse=True)
    for version in versions:
        print(MARKDOWN_FORMAT % (version,version))
    