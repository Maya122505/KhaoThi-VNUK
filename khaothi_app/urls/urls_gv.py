from django.urls import path
from khaothi_app.views.views_gv import gv_view, NopDiemAPI

app_name = 'gv'

urlpatterns = [
    path('', gv_view, name='dashboard'),
    path('api/nop-diem/', NopDiemAPI.as_view(), name='api_nop_diem'),
]
