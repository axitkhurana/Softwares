from django.http import HttpResponse
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from imgds.models import Software
from hippo_update import download, parse_rss, parse_init
from django.conf import settings
from constants import CATEGORIES, SOFTWARE_LOCATION
import urllib2
import urllib
import os

def index(request):
    pass

def pullfromfilehippo(request, category=None, init=None):
    base_url = 'http://www.filehippo.com/software/%s/'
    if not init:
        # download rss file if not initalizing
        base_url = base_url + 'rss/'
    url = base_url % category
    if init:
        soft_list = parse_init(url)
    else:
        soft_list = parse_rss(url)
    for soft in soft_list:
        if not Software.objects.filter(soft_name=soft['soft_name'],
                version=soft['version']):

            #for software file
            path_dir = os.path.join(settings.MEDIA_ROOT, SOFTWARE_LOCATION)

            file_name = download(soft['url'], path_dir,
                    soft['soft_name']+soft['version'])
            new_software = Software(soft_name=soft['soft_name'],
                   category='internet', url=soft['url'],
                   version=soft['version'],
                   description=soft['description'],
                   added_by='filehippo',
                   soft_file=os.path.join(SOFTWARE_LOCATION, file_name))

            #for image
            temp_file, headers = urllib.urlretrieve(soft['img_url'])
            file_extension = os.path.splitext(temp_file)[1]

            image = urllib2.urlopen(soft['img_url']).read()
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(image)
            img_temp.flush()
            filename = soft['soft_name'] + file_extension
            new_software.image.save(filename, File(img_temp), save=True)
    return HttpResponse("Completed")
