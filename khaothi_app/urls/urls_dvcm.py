from django.urls import path
from khaothi_app.views.views_dvcm import dvcm_view

app_name = 'dvcm'

urlpatterns = [
    path('', dvcm_view, name='dashboard'),
]
