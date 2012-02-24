from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.db.models import Q
from imgds.models import Software
from django.conf import settings
from constants import CATEGORIES, SOFTWARE_LOCATION
import urllib2
import urllib
import os

def index(request):
    """ returns a dictionary with key as category 
        & value as top 4 version entries accorrding to download
        count """
    top4={}
    for category in CATEGORIES:
        top4[category[0]] = Software.objects.filter(category=category[0]).order_by('-download_count')[:4]
    if request.method == 'POST':
        pass
    else:
        return render_to_response('index.html',
                {'categories':CATEGORIES,'top4':top4},
                context_instance=RequestContext(request))

def browse(request, category=None, softwareid=None):
    if not softwareid:
        softwares = Software.objects.filter(category =
            category).order_by('-download_count')
        if not softwares:
            raise Http404
        return render_to_response('results.html',
                {'softwares':softwares, 'query':category},
                context_instance=RequestContext(request))
    software = get_object_or_404(Software, pk=softwareid)
    return render_to_response('eachsoft.html',
                {'software':software, 'query':software.soft_name},
                context_instance=RequestContext(request))


def search(request):
    "view for search"
    query = request.GET.get('q', '').lower()
    results=[]
    if query:
        #TODO: use haystack search, profile vs 3 queries
        qset = (
                Q(soft_name__icontains=query) |
                Q(category__icontains=query) |
                Q(description__icontains=query)
               )
        results = Software.objects.filter(qset)
        soft_list = []
        cat_list = []
        desc_list = []
        for result in results:
            if query in result.soft_name.lower():
                soft_list.append(result)
            elif query in result.category.lower():
                cat_list.append(result)
            elif query in result.description.lower():
                desc_list.append(result)
        soft_list.sort(key = lambda software:software.download_count)
        cat_list.sort(key = lambda software:software.download_count)
        desc_list.sort(key = lambda software:software.download_count)
        result = soft_list + cat_list + desc_list
    else:
        result = None
    return render_to_response('results.html',
            {'softwares':result, 'query':query},
            context_instance=RequestContext(request))


