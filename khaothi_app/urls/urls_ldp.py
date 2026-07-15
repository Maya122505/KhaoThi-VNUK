from django.urls import path
from khaothi_app.views.views_ldp import ldp_view

app_name = 'ldp'

urlpatterns = [
    path('', ldp_view, name='dashboard'),
]
