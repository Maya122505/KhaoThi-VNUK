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

    # 2. Các API Endpoints dành cho vai trò Tổ Khảo thí (TKT)
    # API cho Kỳ thi và Ca thi
    path('api/ky-thi/', views_tkt.KyThiAPI.as_view(), name='api_ky_thi'),
    path('api/ca-thi/', views_tkt.CaThiAPI.as_view(), name='api_ca_thi'),

    # API cho Lập lịch thi và phòng thi
    path('api/danh-sach-du-thi/', views_tkt.DanhSachDuThiAPI.as_view(), name='api_danh_sach_du_thi'),
    path('api/lich-thi/', views_tkt.LichThiAPI.as_view(), name='api_lich_thi'),
    path('api/phong-thi/', views_tkt.PhongThiAPI.as_view(), name='api_phong_thi'),
    path('api/phan-cong-phong/', views_tkt.PhanCongPhongAPI.as_view(), name='api_phan_cong_phong'),

    # API cho Nhập điểm
    path('api/nhap-diem/sbd/', views_tkt.NhapDiemSBDAPI.as_view(), name='api_nhap_diem_sbd'),
    path('api/nhap-diem/phach/', views_tkt.NhapDiemPhachAPI.as_view(), name='api_nhap_diem_phach'),

    # API cho Phúc khảo
    path('api/don-phuc-khao/', views_tkt.DonPhucKhaoAPI.as_view(), name='api_don_phuc_khao'),
    path('api/don-phuc-khao/<str:pk>/', views_tkt.DonPhucKhaoDetailAPI.as_view(), name='api_don_phuc_khao_detail'),

    # API cho Giao nhận
    path('api/phieu-giao-nhan/', views_tkt.PhieuGiaoNhanAPI.as_view(), name='api_phieu_giao_nhan'),
    path('api/phieu-giao-nhan/<str:pk>/xac-nhan/', views_tkt.XacNhanPhieuAPI.as_view(), name='api_xac_nhan_phieu'),
    
    # API cho Quản lý Cán bộ coi thi
    path('api/can-bo-coi-thi/', views_tkt.CanBoCoiThiAPI.as_view(), name='api_can_bo_coi_thi'),

    # API cho In sao & Giám sát đề thi
    path('api/dot-in-sao/', views_tkt.DotInSaoAPI.as_view(), name='api_dot_in_sao'),
    path('api/nhat-ky-in-sao/', views_tkt.NhatKyInSaoAPI.as_view(), name='api_nhat_ky_in_sao'),
    path('api/xac-nhan-giam-sat/', views_tkt.XacNhanGiamSatAPI.as_view(), name='api_xac_nhan_giam_sat'),
]
