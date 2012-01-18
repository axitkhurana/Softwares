import sys
import urllib
import urllib2
import os
import re
import html5lib
from BeautifulSoup import BeautifulSoup
from xml.etree import ElementTree
from HTMLParser import HTMLParser

class ParseLinks(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.img_url = ''
        self.a_url = ''

    def handle_starttag(self, tag, attributes):
        if tag == 'img':
            for name, value in attributes:
                if name == 'src':
                    self.img_url = value
        elif tag == 'a':
            for name, value in attributes:
                if name == 'href':
                    self.a_url = value

def meta_redirect(content):
    soup  = BeautifulSoup(content)
    result=soup.find("meta",attrs={"http-equiv":"Refresh"})
    if result:
        wait,text=result["content"].split(";")
        text = text.strip()
        if text.lower().startswith("url="):
            url=text[4:]
            return url
    return None

def parse_init(html_url):
    html = urllib.urlopen(html_url).read()
    soup = BeautifulSoup(html)
    soft_list = []
    """<td><a href="/download_itunes/">
        <img src="http://cache.filehippo.com/img/ex/1906__iTunes_icon.png"
            style="width:32px;height:32px;margin-right:5px;" alt="Download iTunes"
    border="0"/></a></td>
        <td><h2><a href="/download_itunes/">iTunes</a></h2><em>Apple Inc -
    (Freeware)</em><div>iTunes is a free application for Mac and PC. It plays
    all your digital music and video. It syncs content to your iPod, iPhone, and
    Apple TV. And it's ...</div><div class="subprograms"><img
    src="http://cache.filehippo.com/img/d5.gif" align="bottom" alt="" /> <a
    class="title" href="/download_itunes_32/">iTunes 10.5.2 (32-bit)</a> - <a
    href="/download_itunes_32/">Download</a><br/><img
    src="http://cache.filehippo.com/img/d5.gif" align="bottom" alt="" /> <a
    class="title" href="/download_itunes_64/">iTunes 10.5.2 (64-bit)</a> - <a
    href="/download_itunes_64/">Download</a><br/></div></td><td></td>"""
    p = ParseLinks()
    for table in soup.findAll('table'):
        for counter,td in enumerate(table.findAll('td')):
            if counter == 0:
                img_url = td.img['src']
            elif counter == 1:
                data = td.findAll('a', {'class':'title'})
                if not data:
                    data = td.findAll('a')[:1]
                    #[<a href="/download_adobe_media_player/">Adobe Media Player#1.7</a>,
                    #<a href="/download_adobe_media_player/">Download</a>][:1]
                for soft in data:
                    temp_url = soft['href']
                    pieces = ('http://www.filehippo.com', temp_url)
                    a_url = '/'.join(s.strip('/') for s in pieces)
                    soft_name_version = soft.contents[0]
                    description = td.div.contents[0]
                    #split software at first occurrence of a number to get version
                    try:
                        split_pt = re.search('\d',soft_name_version).start()
                    except AttributeError:
                        # catch error if no number in string
                        split_pt = len(soft_name_version)+1
                    soft_list.append({
                        'soft_name': soft_name_version[:split_pt - 1],
                        'version': soft_name_version[split_pt:],
                        'url' : a_url,
                        'description' : description,
                        'img_url' : img_url,
                        })
    return soft_list

def download(url, path_dir, soft_name):
    """download from indirect url, takes cares of redirects and gets correct
    file extension"""
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    div = soup.find('div', {'id': 'dlbox'})
    pieces = (url, div.a['href'])
    temp_url = '/'.join(s.strip('/') for s in pieces)
    temp_html = urllib2.urlopen(temp_url)
    temp2_url = meta_redirect(temp_html.read())
    pieces = ('http://www.filehippo.com', temp2_url)
    final_url = '/'.join(s.strip('/') for s in pieces)
    final_file = urllib.urlopen(final_url)
    temp_file, headers = urllib.urlretrieve(final_file.url)
    file_extension = os.path.splitext(temp_file)[1]
    file_name = " ".join([soft_name,file_extension])
    final_location = os.path.join(path_dir, file_name)
    os.rename(temp_file, final_location)
    return file_name

def parse_rss(rss_url):
    p = ParseLinks()
    rss = ElementTree.parse(urllib.urlopen(rss_url))

    soft_list = []
    if sys.version_info < (2,7):
        iterator = rss.getiterator #depricated since 2.7
    else:
        iterator = rss.iter
    for node in iterator('item'):
        nodes = list(node)
        #nodes are of form [title, general link, description, content, pubdate, exact url]
        soft_name_version = nodes[0].text

        #to find img url
        p.feed(nodes[3].text)
        img_url = p.img_url

        #split software at first occurrence of a number to get version
        try:
            split_pt = re.search('\d',soft_name_version).start()
        except AttributeError:
            # catch error if no number in string
            split_pt = len(soft_name_version)+1
        soft_list.append({
            'soft_name': soft_name_version[:split_pt - 1],
            'version': soft_name_version[split_pt:],
            'url' : nodes[5].text,
            'description' : nodes[2].text,
            'img_url' : img_url,
            })
    return soft_list
