# -*- coding: utf-8 -*-
"""
tastypie.Resource definitions for ElasticSearch

"""

from tastypie.bundle import Bundle
from tastypie.resources import Resource
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http
from tastypie import fields

import pyes

class ElasticSearch(Resource):
    """
    ElasticSearch Resource
    """
    
    id = fields.CharField(attribute='get_id')
    # meta = fields.DictField(attribute='get_meta')
    items = fields.DictField(attribute='items')
    
    _es = None
    def es__get(self):
        if self._es is None:
            self._es = pyes.ES(server=self._meta.es_server,
                timeout=self._meta.es_timeout)
        return self._es
    es = property(es__get)
    
    
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj.id
        
        return kwargs
    
    def build_schema(self):
        return self.es.get_mapping(indices=self._meta.indices)
    
    def get_resource_uri(self, bundle_or_obj=None):
        obj = (bundle_or_obj.obj if
            isinstance(bundle_or_obj, Bundle) else bundle_or_obj)
        return obj.get('get_absolute_url')
    
    
    def get_object_list(self, request):
        offset = long(request.GET.get("offset", 0))
        limit = long(request.GET.get("limit", self._meta.limit))
        
        q = request.GET.get("q", "")
        doc_types = request.GET.get("doc_types", "").split(',')
        
        if q:
            query = pyes.StringQuery(q)
        else:
            query = pyes.MatchAllQuery()
        
        size = (limit + offset) - (1 if offset else 0)
        start = offset + (1 if offset>=limit else 0)
        
        # refresh the index before query
        self.es.refresh(self._meta.indices[0])
        
        results = self.es.search(
            query=query,
            doc_types=doc_types,
            indices=self._meta.indices,
            size=size,
            start=start
            )
        return results
    
    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)
    
    def obj_get(self, request=None, **kwargs):
        pk = kwargs.get('pk')
        
        # refresh the index before query
        self.es.refresh(self._meta.indices[0])
        
        search = pyes.query.IdsQuery(pk)
        results = self.es.search(search, indices=self._meta.indices)
        
        if results.total == 0:
            raise ImmediateHttpResponse(
                response=http.HttpNotFound("Nothing found with id='%s'" % pk))
        
        return results[0]
