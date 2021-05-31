from django.urls import path
from .views import my_view
from django.conf.urls import url

urlpatterns = [
    path('', my_view, name='my-view')
]
