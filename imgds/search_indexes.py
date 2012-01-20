from datetime import datetime
from haystack.indexes import *
from haystack import site
from imgds.models import Software

class SoftwareIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    soft_name = CharField(model_attr='soft_name')
    category = CharField(model_attr='category')
    version  = CharField(model_attr='version')
    description = CharField(model_attr='description')

    def index_queryset(self):
        return Software.objects.filter(date_added__lte=datetime.now())

site.register(Software, SoftwareIndex)
