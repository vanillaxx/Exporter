from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('import/notoria/', views.import_notoria, name='import_notoria'),
    path('import/stooq/', views.import_stooq, name='import_stooq'),
    path('import/gpw/', views.import_gpw, name='import_gpw'),
    path('export', views.export, name='export'),
    path('manage/home', views.manage, name='manage_home'),
    path('manage/companies', views.get_companies, name='get_companies')
]
