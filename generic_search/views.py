from django.views.generic import ListView
from .utils.utils import query_document_index
# Create your views here.


class GeneralSearch(ListView):
    template_name = 'generic_search/index.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['page_title'] = 'Search'
        context['results_count'] = len(context['object_list'])
        return context

    def get_queryset(self):
        q = self.request.GET.get('q')
        results = query_document_index(q) if q and q != '' else []
        return results
