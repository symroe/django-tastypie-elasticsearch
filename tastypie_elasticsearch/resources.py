# -*- coding: utf-8 -*-
"""
tastypie.Resource definitions for ElasticSearch
"""

import json

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
    
    def build_facets(self, request):
        facets = []
        for facet in getattr(self._meta, 'term_facets', []):
            facets.append(pyes.facets.TermFacet(facet))
        return facets
    
    def add_filters(self, query, request):
        return query

    def get_object_list(self, request, qs=None, count=False, facets=[], filters=None):
        if qs:
            query = request.GET.copy()
            query.update(qs)
            request.GET = query
                
        q = request.GET.get("q", "")
        doc_types = request.GET.get("doc_types", "").split(',')

        if q:
            query = pyes.StringQuery(q)
        else:
            query = pyes.MatchAllQuery()

        # applying filters
        if filters:
            query = pyes.FilteredQuery(query, filters)

        if not count:
            offset = long(request.GET.get("offset", 0))
            limit = long(request.GET.get("limit", self._meta.limit))

            query = query.search()

            # applying facets
            if facets:
                query.facet.facets += facets

            # refresh the index before query
            self.es.refresh(self._meta.indices[0])

            results = self.es.search(
                query=query,
                doc_types=doc_types,
                indices=self._meta.indices,
                size=limit,
                start=offset
            )


            self.query_facets = results.facets
        else:
            # refresh the index before query
            self.es.refresh(self._meta.indices[0])

            results = self.es.count(
                query=query,
                doc_types=doc_types,
                indices=self._meta.indices
            )
        return results
    
    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request, **kwargs)
    
    def get_list(self, request=None, **kwargs):
        resp = super(ElasticSearch, self).get_list(request, **kwargs)
        data = json.loads(resp.content)
        data['meta']['facets'] = self.query_facets
        return self.create_response(request, data)
    
    
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
