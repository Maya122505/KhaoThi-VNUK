from django.urls import path
from khaothi_app.views import views_tkct

app_name = 'tkct'

urlpatterns = [
    # Template View
    path('', views_tkct.tkct_view, name='dashboard'),

    # API Endpoints
    path('api/data/', views_tkct.TKCTDataAPI.as_view(), name='api_tkct_data'),
    path('api/tui-phach/', views_tkct.TuiPhachAPI.as_view(), name='api_tui_phach'),
]
