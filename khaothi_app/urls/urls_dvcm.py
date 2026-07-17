from django.urls import path
from khaothi_app.views import views_dvcm

app_name = 'dvcm'

urlpatterns = [
    path('', views_dvcm.dvcm_view, name='dashboard'),
]
