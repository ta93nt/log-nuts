from django.shortcuts import render
from django.views import generic


class TopView(generic.TemplateView):
    template_name = 'lognutsapp/top.html' 