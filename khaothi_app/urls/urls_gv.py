from django.urls import path
from khaothi_app.views.views_gv import gv_view

app_name = 'gv'

urlpatterns = [
    path('', gv_view, name='dashboard'),
]
