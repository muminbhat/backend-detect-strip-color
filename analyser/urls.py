from django.urls import path
from . import views

urlpatterns = [
    path('samples/', views.sample_list, name='all_samples')
]