# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from editor.forms import DatasetForm
from editor.models import Category, Source, Format, Dataset


class IndexView(View):
    template_name = 'editor/index.html'

    def get(self, request):
        return render(request, self.template_name)


class BaseTreeView(ListView):
    template_name = 'editor/tree.html'

    def get_context_data(self, **kwargs):
        kwargs['nodes'] = self.model.objects.all()
        kwargs['create_url'] = self.model.get_create_url()
        return kwargs


class BaseCreateView(CreateView):
    template_name = 'editor/tree.html'

    def get_context_data(self, **kwargs):
        kwargs['nodes'] = self.model.objects.all()
        kwargs['create_url'] = self.model.get_create_url()
        return kwargs

    def get_initial(self):
        initial = super(BaseCreateView, self).get_initial()
        try:
            parent_pk = int(self.request.GET.get('parent', 0))
            initial['parent'] = self.model.objects.get(pk=parent_pk)
        except (TypeError, ValueError, self.model.DoesNotExist):
            # TODO: add warning to logger because it is client side bug.
            pass
        return initial


class BaseUpdateView(UpdateView):
    template_name = 'editor/tree.html'

    def get_context_data(self, **kwargs):
        kwargs['nodes'] = self.model.objects.all()
        kwargs['create_url'] = self.model.get_create_url()
        return kwargs


class CategoryList(BaseTreeView):
    model = Category


class CategoryCreate(BaseCreateView):
    model = Category
    fields = ['name', 'parent']


class CategoryUpdate(BaseUpdateView):
    model = Category
    fields = ['name', 'parent']


class SourceList(BaseTreeView):
    model = Source


class SourceCreate(BaseCreateView):
    model = Source
    fields = ['name', 'parent', 'abbreviation', 'domain', 'homepage', 'about', 'categories']


class SourceUpdate(BaseUpdateView):
    model = Source
    fields = ['name', 'parent', 'abbreviation', 'domain', 'homepage', 'about', 'categories']

    def get_context_data(self, **kwargs):
        ctx = super(SourceUpdate, self).get_context_data(**kwargs)
        ctx['create_dataset_url'] = reverse(
            'dataset-create', kwargs={'source_pk': self.object.pk})
        return ctx


class FormatList(BaseTreeView):
    model = Format


class FormatCreate(BaseCreateView):
    model = Format
    fields = ['name', 'parent']


class FormatUpdate(BaseUpdateView):
    model = Format
    fields = ['name', 'parent']


class DatasetList(ListView):
    model = Dataset

    def get_queryset(self, *args, **kwargs):
        qs = super(DatasetList, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get('query')
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(source__name__icontains=query)
                | Q(page__icontains=query))

        return qs.select_related('source')


class DatasetCreate(CreateView):
    model = Dataset
    form_class = DatasetForm

    def dispatch(self, request, *args, **kwargs):
        self.source = get_object_or_404(Source, pk=self.kwargs['source_pk'])
        return super(DatasetCreate, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        form_kwargs = self.get_form_kwargs()
        form_kwargs['source'] = self.source
        return form_class(self.request.user, **form_kwargs)


class DatasetUpdate(UpdateView):
    model = Dataset
    form_class = DatasetForm

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(self.request.user, **self.get_form_kwargs())
