from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import KyThi, CaThi, HocPhan, PhongThi, User
from ..forms.forms_tkt import KyThiForm, CaThiForm, LapLichThiForm
from ..services.services_tkt import DoiSoatTKTService, GiaoNhanTKTService

# ===================================================================
# 1. Template Rendering Views
# ===================================================================
# Các view này chỉ trả về template HTML. Dữ liệu sẽ được load bằng JS qua API.

def tkt_dashboard_view(request):
    from .views_common import ensure_actor_logged_in
    ensure_actor_logged_in(request, 'tkt')
    return render(request, 'khaothi_app/tkt/giaodienTKT.html')

def quan_ly_ky_thi_view(request):
    # View này có thể được gộp vào dashboard chính hoặc để riêng
    return render(request, 'khaothi_app/tkt/partials/_view_ky_thi.html')

def lap_lich_thi_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_danh_sach_lich.html')

def nhap_diem_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_nhap_diem.html')

def phuc_khao_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_phuc_khao.html')

def giao_nhan_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_giao_nhan.html')

def can_bo_coi_thi_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_gio_coi.html')

# ===================================================================
# 2. API Endpoints
# ===================================================================
# Sử dụng Django REST Framework để xử lý API một cách chuyên nghiệp

class KyThiAPI(APIView):
    def get(self, request):
        """Lấy danh sách các kỳ thi."""
        ky_this = KyThi.objects.all().values()
        return Response(list(ky_this))

    def post(self, request):
        """Tạo một kỳ thi mới."""
        form = KyThiForm(request.data)
        if form.is_valid():
            ky_thi = form.save()
            return Response(KyThiForm(instance=ky_thi).data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class CaThiAPI(APIView):
    def get(self, request):
        """Lấy danh sách các ca thi, có thể lọc theo kỳ thi."""
        ky_thi_id = request.query_params.get('ky_thi_id')
        if ky_thi_id:
            ca_this = CaThi.objects.filter(ky_thi_id=ky_thi_id).values()
        else:
            ca_this = CaThi.objects.all().values()
        return Response(list(ca_this))

    def post(self, request):
        """Tạo một ca thi mới."""
        form = CaThiForm(request.data)
        if form.is_valid():
            ca_thi = form.save()
            # Cập nhật số lượng ca thi trong Kỳ Thi
            ky_thi = ca_thi.ky_thi
            ky_thi.shiftsCount = ky_thi.ca_thi.count()
            ky_thi.save()
            return Response(CaThiForm(instance=ca_thi).data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class DanhSachDuThiAPI(APIView):
    def post(self, request):
        """
        API để xử lý việc đồng bộ và lọc danh sách sinh viên đủ điều kiện thi.
        """
        hoc_phan_id = request.data.get('hoc_phan_id')
        # TODO: Gọi service để xử lý logic đồng bộ học phí và trả về danh sách
        # fake_data = [
        #     {'msv': 'SV001', 'name': 'Lê Văn Tám', 'class': '24CS01', 'debt': 0, 'eligible': True},
        #     {'msv': 'SV003', 'name': 'Phạm Hồng Thái', 'class': '24CS01', 'debt': 15000000, 'eligible': False},
        # ]
        # return Response(fake_data)
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class LichThiAPI(APIView):
    def get(self, request):
        # TODO: Lấy danh sách lịch thi đã được tạo
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def post(self, request):
        """Lập lịch thi cho một học phần vào một ca thi, phòng thi cụ thể."""
        form = LapLichThiForm(request.data)
        if form.is_valid():
            # TODO: Gọi service để xử lý việc lập lịch, kiểm tra xung đột
            # service.lap_lich_thi(...)
            return Response({"message": "Lập lịch thành công"}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

# Các API khác sẽ được xây dựng theo cấu trúc tương tự...

class NhapDiemSBDAPI(APIView):
    def post(self, request):
        # TODO: Validate bằng form và gọi DoiSoatTKTService.doi_soat_diem_lan_2
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class NhapDiemPhachAPI(APIView):
    def post(self, request):
        # TODO: Validate và gọi service
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class DonPhucKhaoAPI(APIView):
    def get(self, request):
        # TODO: Lấy danh sách đơn phúc khảo
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class DonPhucKhaoDetailAPI(APIView):
    def put(self, request, pk):
        # TODO: Cập nhật điểm phúc khảo
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class PhieuGiaoNhanAPI(APIView):
    def post(self, request):
        # TODO: Validate và gọi GiaoNhanTKTService.tao_phieu_giao_nhan
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class XacNhanPhieuAPI(APIView):
    def post(self, request, pk):
        # TODO: Gọi GiaoNhanTKTService.xac_nhan_nhan_phieu
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class CanBoCoiThiAPI(APIView):
    def get(self, request):
        # TODO: Lấy danh sách cán bộ coi thi và lịch sử coi thi của họ
        return Response({"message": "Chức năng đang được phát triển"}, status=status.HTTP_501_NOT_IMPLEMENTED)
