from django.urls import path
from khaothi_app.views import views_cvht

app_name = 'cvht'

urlpatterns = [
    # Template View
    path('', views_cvht.cvht_view, name='dashboard'),

    # API Endpoints
    path('api/config/diem/', views_cvht.PhienBanCotDiemAPI.as_view(), name='api_config_diem'),
    path('api/config/phuc-khao/', views_cvht.CauHinhPhucKhaoAPI.as_view(), name='api_config_phuc_khao'),
    path('api/configs/', views_cvht.SystemConfigAPI.as_view(), name='api_system_configs'),
]
