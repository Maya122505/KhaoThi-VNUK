from django.urls import path
from khaothi_app.views.views_tkcoithi import tkcoithi_view

app_name = 'tkcoithi'

urlpatterns = [
    path('', tkcoithi_view, name='dashboard'),
]
