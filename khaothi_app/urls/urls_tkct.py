from django.urls import path
from khaothi_app.views.views_tkct import tkct_view

app_name = 'tkct'

urlpatterns = [
    path('', tkct_view, name='dashboard'),
]
