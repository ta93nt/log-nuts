from django.urls import path
from . import views

app_name = 'lognuts'

urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('mypage/<int:pk>/', views.MypageView.as_view(), name='mypage'),
    path('mypage/<int:pk>/<int:year>/<int:month>/<int:day>/', views.MypageView.as_view(), name='mypage'),
    path('search_input/<int:pk>/', views.SearchInput.as_view(), name='search_input'),
    path('search_complete/<int:pk>/<int:id>/', views.SearchComplete.as_view(), name='search_complete'),
    path('manual_input/<int:pk>/', views.ManualInput.as_view(), name='manual_input'),
    path('manual_complete/<int:pk>/', views.ManualComplete.as_view(), name='manual_complete'),
]