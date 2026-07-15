from django.urls import path
from khaothi_app.views.views_cvht import cvht_view

app_name = 'cvht'

urlpatterns = [
    path('', cvht_view, name='dashboard'),
]
