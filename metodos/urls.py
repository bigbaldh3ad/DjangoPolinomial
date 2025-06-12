from django.urls import path
from . import views

app_name = 'metodos'

urlpatterns = [
    path('', views.home, name='home'),  
    path('metodos/', views.index, name='index'),  
]
