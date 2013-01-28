from tastypie.paginator import Paginator as TastypiePaginator


class Paginator(TastypiePaginator):
    def get_offset(self):
        return self.objects.start

    def get_slice(self, limit, offset):
        return self.objects

    def get_count(self):
        return self.objects.total