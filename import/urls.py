from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('balance_sheet/', views.balance_sheet, name='balance_sheet')
]