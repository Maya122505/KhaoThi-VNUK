from django.urls import path
from ..views import views_tkt

app_name = 'tkt'

urlpatterns = [
    # 1. Template Rendering Views
    path('', views_tkt.tkt_dashboard_view, name='dashboard'),
    path('ky-thi/', views_tkt.quan_ly_ky_thi_view, name='quan_ly_ky_thi'),
    path('lich-thi/', views_tkt.lap_lich_thi_view, name='lap_lich_thi'),
    path('nhap-diem/', views_tkt.nhap_diem_view, name='nhap_diem'),
    path('phuc-khao/', views_tkt.phuc_khao_view, name='phuc_khao'),
    path('giao-nhan/', views_tkt.giao_nhan_view, name='giao_nhan'),
    path('can-bo-coi-thi/', views_tkt.can_bo_coi_thi_view, name='can_bo_coi_thi'),

    # 2. API Endpoints for TKT actor
    # API cho Kỳ thi và Ca thi
    path('api/ky-thi/', views_tkt.KyThiAPI.as_view(), name='api_ky_thi'),
    path('api/ca-thi/', views_tkt.CaThiAPI.as_view(), name='api_ca_thi'),

    # API cho Lập lịch thi
    path('api/danh-sach-du-thi/', views_tkt.DanhSachDuThiAPI.as_view(), name='api_danh_sach_du_thi'),
    path('api/lich-thi/', views_tkt.LichThiAPI.as_view(), name='api_lich_thi'),

    # API cho Nhập điểm
    path('api/nhap-diem/sbd/', views_tkt.NhapDiemSBDAPI.as_view(), name='api_nhap_diem_sbd'),
    path('api/nhap-diem/phach/', views_tkt.NhapDiemPhachAPI.as_view(), name='api_nhap_diem_phach'),

    # API cho Phúc khảo
    path('api/don-phuc-khao/', views_tkt.DonPhucKhaoAPI.as_view(), name='api_don_phuc_khao'),
    path('api/don-phuc-khao/<str:pk>/', views_tkt.DonPhucKhaoDetailAPI.as_view(), name='api_don_phuc_khao_detail'),

    # API cho Giao nhận
    path('api/giao-nhan-data/', views_tkt.GiaoNhanDataAPI.as_view(), name='api_giao_nhan_data'),
    path('api/phieu-giao-nhan/', views_tkt.PhieuGiaoNhanAPI.as_view(), name='api_phieu_giao_nhan'),
    path('api/phieu-giao-nhan/<str:pk>/xac-nhan/', views_tkt.XacNhanPhieuAPI.as_view(), name='api_xac_nhan_phieu'),
    
    # API cho Quản lý Cán bộ coi thi
    path('api/can-bo-coi-thi/', views_tkt.CanBoCoiThiAPI.as_view(), name='api_can_bo_coi_thi'),
]
