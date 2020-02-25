from django.urls import path
from . import views

app_name = 'lognuts'

urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('mypage/<int:pk>/', views.MypageView.as_view(), name='mypage'),
    path('mypage/<int:pk>/<int:year>/<int:month>/<int:day>/', views.MypageView.as_view(), name='mypage'),
    path('diary/<int:pk>/<int:year>/<int:month>/<int:day>/', views.DiaryView.as_view(), name='diary'),
    path('image_upload/<int:pk>/<int:year>/<int:month>/<int:day>/', views.ImageUpload.as_view(), name='image_upload'),
    path('image_add_food/<int:pk>/<int:year>/<int:month>/<int:day>/', views.ImageAddFood.as_view(), name='image_add_food'),
    path('image_complete/<int:pk>/<int:year>/<int:month>/<int:day>/', views.ImageComplete.as_view(), name='image_complete'),
    path('image_ranking/<int:pk>/', views.ImageRanking.as_view(), name='image_ranking'),
    path('search_input/<int:pk>/', views.SearchInput.as_view(), name='search_input'),
    path('search_confirm/<int:pk>/', views.SearchConfirm.as_view(), name='search_confirm'),
    path('search_complete/<int:pk>/', views.SearchComplete.as_view(), name='search_complete'),
    path('manual_input/<int:pk>/', views.ManualInput.as_view(), name='manual_input'),
    path('manual_complete/<int:pk>/', views.ManualComplete.as_view(), name='manual_complete'),
    path('history_input/<int:pk>/', views.HistoryInput.as_view(), name='history_input'),
    path('history_complete/<int:pk>/', views.HistoryComplete.as_view(), name='history_complete'),
]