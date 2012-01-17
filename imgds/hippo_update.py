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
    """<tr><td><a href="/download_adobe_air/"><img src="http://cache.filehippo.com/img/ex/1042__air.gif"style="width:32px;height:32px;margin-right:5px;" alt="Download Adobe Air 3.2.0.1320 Beta 2" border="0" /></a></td>
    <td><h2><a href="/download_adobe_air/">Adobe Air 3.2.0.1320 Beta 2</a></h2><em>Adobe Systems Inc - 14.21MB (Freeware)</em><div>The Adobe&#174; AIR, runtime enables you to have your favorite web applications with you all the time. Since applications built for Adobe AIR run on your d...</div>
    <div class="subprograms"><img src="http://cache.filehippo.com/img/d5.gif" align="bottom" alt="" /> <a href="/download_adobe_air/">Download</a></div></td><td></td></tr>"""
    p = ParseLinks()
    for table in soup.findAll('table'):
        for counter,td in enumerate(table.findAll('td')):
            if not counter % 2:
                p.feed(td.renderContents())
                img_url = p.img_url
                pieces = ('http://www.filehippo.com', p.a_url)
                a_url = '/'.join(s.strip('/') for s in pieces)
            else:
                soft_name_version = td.a.contents[0]
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
    #for a in soft_list:
    #    print a
    return soft_list

if __name__ == "__main__":
    parse_init("http://www.filehippo.com/software/internet/")
