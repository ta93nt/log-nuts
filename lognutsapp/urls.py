from django.urls import path
from . import views

app_name = 'lognuts'

urlpatterns = [
     path('', views.TopView.as_view(), name='top'),
]