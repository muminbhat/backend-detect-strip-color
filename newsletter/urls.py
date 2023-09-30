from django.urls import path
from . import views

urlpatterns = [
path('post/', views.post_newsletter, name="add_newsletter"),
path('preflight/', views.handle_preflight, name='handle-preflight'),  # Use a different path

]