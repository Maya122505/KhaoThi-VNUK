from django.urls import path
from khaothi_app.views import views_ldp

app_name = 'ldp'

urlpatterns = [
    # Template View
    path('', views_ldp.ldp_view, name='dashboard'),

    # API Endpoints
    path('api/ky-thi/phe-duyet/', views_ldp.KyThiPheDuyetAPI.as_view(), name='api_ky_thi_phe_duyet'),
    path('api/phe-duyet/', views_ldp.PheDuyetAPI.as_view(), name='api_phe_duyet'),
]
