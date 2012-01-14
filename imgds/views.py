from django.http import HttpResponse
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from imgds.models import Software
from update import download, parserss
from constants import CATEGORIES
import urllib2
import urllib
import os

def index(request):
    pass

def pullfromfilehippo(request):
    for category in CATEGORIES:
        rss_url = 'http://www.filehippo.com/software/%s/rss/' % category[0]
        soft_list = parserss(rss_url)
        for soft in soft_list:
            if not Software.objects.filter(soft_name=soft['soft_name'],
                    version=soft['version']):
                new_software = Software(soft_name=soft['soft_name'],
                       category=category[0], url=soft['url'],
                       version=soft['version'],
                       description=soft['description'],
                       added_by='filehippo')
                #for image
                temp_file, headers = urllib.urlretrieve(soft['img_url'])
                file_extension = os.path.splitext(temp_file)[1]

                image = urllib2.urlopen(soft['img_url']).read()
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(image)
                img_temp.flush()
                filename = '%s%s' % (soft['soft_name'], file_extension)
                new_software.image.save(filename, File(img_temp), save=True)
    return HttpResponse("Completed")
