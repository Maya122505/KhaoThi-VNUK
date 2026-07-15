from django.urls import path, include
from khaothi_app.views import views_common

urlpatterns = [
    # =================================================
    # Common Views (Login, Index)
    # =================================================
    path('', views_common.index_view, name='index'),
    path('login/', views_common.login_view, name='login'),
    path('logout/', views_common.logout_view, name='logout'),
    path('api/get_state/', views_common.get_state, name='get_state'),
    path('api/save_state/', views_common.save_state, name='save_state'),
    path('export-pdf/', views_common.export_pdf_view, name='export_pdf'),

    # =================================================
    # Actor-specific URL Includes
    # =================================================
    # Mỗi actor sẽ có file urls riêng để quản lý các trang và API của mình
    path('tkt/', include('khaothi_app.urls.urls_tkt')),
    path('tkct/', include('khaothi_app.urls.urls_tkct')),
    path('ldp/', include('khaothi_app.urls.urls_ldp')),
    path('dvcm/', include('khaothi_app.urls.urls_dvcm')),
    path('gv/', include('khaothi_app.urls.urls_gv')),
    # path('tkcoithi/', include('khaothi_app.urls.urls_tkcoithi')), # Tạm thời comment lại nếu chưa dùng
    path('cvht/', include('khaothi_app.urls.urls_cvht')),

    # =================================================
    # API Endpoints (Nếu có API chung)
    # =================================================
    # Các API chung cho nhiều actor có thể được định nghĩa ở đây.
    # Tuy nhiên, để rõ ràng, nên đặt API vào file urls của actor chính sử dụng nó.
    # Ví dụ: path('api/some-general-data/', views_common.get_general_data, name='get_general_data'),
]
