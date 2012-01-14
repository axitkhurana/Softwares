import sys
import urllib
import os
import re
from xml.etree import ElementTree
from HTMLParser import HTMLParser

class ParseImgSrc(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.url = ''

    def handle_starttag(self, tag, attributes):
        if tag == 'img':
            for name, value in attributes:
                if name == 'src':
                    self.url = value


def download(url, path_dir, soft_name):
    """download from indirect url, takes cares of redirects and gets correct
    file extension"""
    temp_url = urllib.urlopen(url)
    temp_file, headers = urllib.urlretrieve(temp_url.url)
    file_extension = os.path.splitext(temp_file)[1]
    final_location = os.path.join(path_dir, soft_name, file_extension)
    os.rename(temp_file, final_location)

def parserss(rss_url):
    p = ParseImgSrc()
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
        img_url = p.url

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
            'img_url' : p.url,
            })
    #for a in soft_list:
    #    print a
    return soft_list

#if __name__ == "__main__":
#    parserss("http://www.filehippo.com/software/drivers/rss/")
