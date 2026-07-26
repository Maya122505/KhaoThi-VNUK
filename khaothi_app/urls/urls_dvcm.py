from django.urls import path
from khaothi_app.views import views_dvcm

app_name = 'dvcm'

urlpatterns = [
    # Template View
    path('', views_dvcm.dvcm_view, name='dashboard'),

    # API Endpoints
    path('api/data/', views_dvcm.DVCMDataAPI.as_view(), name='api_dvcm_data'),
    path('api/phan-cong-cham/', views_dvcm.PhanCongChamAPI.as_view(), name='api_phan_cong_cham'),
]
