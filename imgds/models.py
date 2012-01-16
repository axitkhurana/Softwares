from django.db import models
from datetime import datetime
from constants import CATEGORIES
import os

#def get_upload_path(instance, filename):
#    return os.path.join("%s" % instance.owner.soft, "car_%s" % instance.slug,
#            filename)

class Software(models.Model):
    soft_name = models.CharField('Software Name', max_length = 100)
    category = models.CharField(max_length = 80, choices = CATEGORIES)
    image = models.ImageField(upload_to='software_pics')
    url = models.URLField('URL', )
    version = models.CharField('Version', max_length = 100, null=True,
            blank=True)
    description = models.TextField(null = True, blank=True)
    date_added = models.DateTimeField('Date Added', default=datetime.now())
    download_count = models.IntegerField('Downloads', default=0)
    added_by = models.CharField('Uploaded By', max_length=20) #default value
    soft_file = models.FileField('File', upload_to='software')
    def __unicode__(self):
        return '%s %s' % (self.soft_name, self.version)
