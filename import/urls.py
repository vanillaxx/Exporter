from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('notoria/', views.notoria, name='notoria')
]