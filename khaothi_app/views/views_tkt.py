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

from ..services.services_tkt import DoiSoatTKTService, GiaoNhanTKTService, PhucKhaoService
from ..models import DonPhucKhao

class DonPhucKhaoAPI(APIView):
    def get(self, request):
        """
        Lấy danh sách các đơn phúc khảo từ CSDL.
        """
        trang_thai = request.query_params.get('trang_thai')
        search = request.query_params.get('search')
        danh_sach = PhucKhaoService.lay_danh_sach_don(trang_thai=trang_thai, search=search)
        
        result = []
        for dpk in danh_sach:
            ten_hp = ""
            if dpk.hoc_phan:
                ten_hp = dpk.hoc_phan.ten_hoc_phan
            elif dpk.lich_thi and dpk.lich_thi.lop_hp and dpk.lich_thi.lop_hp.hoc_phan:
                ten_hp = dpk.lich_thi.lop_hp.hoc_phan.ten_hoc_phan

            result.append({
                "id": dpk.ma_don,
                "phach": dpk.ma_phach.ma_phach if dpk.ma_phach else "",
                "subjectName": ten_hp,
                "pt1": float(dpk.diem_phuc_khao_1) if dpk.diem_phuc_khao_1 is not None else None,
                "pt2": float(dpk.diem_phuc_khao_2) if dpk.diem_phuc_khao_2 is not None else None,
                "ptFinal": float(dpk.diem_phuc_khao_cuoi) if dpk.diem_phuc_khao_cuoi is not None else None,
                "originalPt1": float(dpk.diem_goc) if dpk.diem_goc is not None else None,
                "msv": dpk.sinh_vien.ma_sinh_vien,
                "name": dpk.sinh_vien.ho_ten,
                "status": dpk.trang_thai,
                "file": dpk.file_bien_ban or "",
                "ly_do": dpk.ly_do or "",
                "ngay_tao": dpk.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if dpk.ngay_tao else None,
                "ngay_duyet": dpk.ngay_duyet.strftime('%Y-%m-%d %H:%M:%S') if dpk.ngay_duyet else None,
                "nguoi_duyet": dpk.nguoi_duyet.full_name or dpk.nguoi_duyet.username if dpk.nguoi_duyet else None
            })
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Nộp/tạo đơn phúc khảo mới trực tiếp vào CSDL.
        """
        data = request.data
        ma_don = data.get('id') or data.get('ma_don')
        ma_sinh_vien = data.get('msv') or data.get('ma_sinh_vien')
        ma_phach_str = data.get('phach') or data.get('ma_phach')
        ma_lich_thi = data.get('ma_lich_thi')
        ly_do = data.get('ly_do', 'Đơn phúc khảo sinh viên')
        diem_goc = data.get('originalPt1') or data.get('diem_goc')

        if not ma_don or not ma_sinh_vien:
            return Response({"error": "Thiếu ma_don hoặc ma_sinh_vien"}, status=status.HTTP_400_BAD_REQUEST)

        don = PhucKhaoService.tao_don_phuc_khao(
            ma_don=ma_don,
            ma_sinh_vien=ma_sinh_vien,
            ma_phach_str=ma_phach_str,
            ma_lich_thi=ma_lich_thi,
            ly_do=ly_do,
            diem_goc=diem_goc
        )
        return Response({"message": "Tạo đơn phúc khảo thành công", "ma_don": don.ma_don}, status=status.HTTP_201_CREATED)

class DonPhucKhaoDetailAPI(APIView):
    def get(self, request, pk):
        """
        Lấy thông tin chi tiết một đơn phúc khảo từ CSDL.
        """
        try:
            dpk = DonPhucKhao.objects.select_related('sinh_vien', 'ma_phach', 'lich_thi__lop_hp__hoc_phan', 'hoc_phan', 'nguoi_duyet').get(ma_don=pk)
            ten_hp = ""
            if dpk.hoc_phan:
                ten_hp = dpk.hoc_phan.ten_hoc_phan
            elif dpk.lich_thi and dpk.lich_thi.lop_hp and dpk.lich_thi.lop_hp.hoc_phan:
                ten_hp = dpk.lich_thi.lop_hp.hoc_phan.ten_hoc_phan

            data = {
                "id": dpk.ma_don,
                "phach": dpk.ma_phach.ma_phach if dpk.ma_phach else "",
                "subjectName": ten_hp,
                "pt1": float(dpk.diem_phuc_khao_1) if dpk.diem_phuc_khao_1 is not None else None,
                "pt2": float(dpk.diem_phuc_khao_2) if dpk.diem_phuc_khao_2 is not None else None,
                "ptFinal": float(dpk.diem_phuc_khao_cuoi) if dpk.diem_phuc_khao_cuoi is not None else None,
                "originalPt1": float(dpk.diem_goc) if dpk.diem_goc is not None else None,
                "msv": dpk.sinh_vien.ma_sinh_vien,
                "name": dpk.sinh_vien.ho_ten,
                "status": dpk.trang_thai,
                "file": dpk.file_bien_ban or "",
                "ly_do": dpk.ly_do or "",
                "ngay_tao": dpk.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if dpk.ngay_tao else None,
                "ngay_duyet": dpk.ngay_duyet.strftime('%Y-%m-%d %H:%M:%S') if dpk.ngay_duyet else None,
                "nguoi_duyet": dpk.nguoi_duyet.full_name or dpk.nguoi_duyet.username if dpk.nguoi_duyet else None
            }
            return Response(data, status=status.HTTP_200_OK)
        except DonPhucKhao.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn phúc khảo"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        """
        Cập nhật điểm phúc khảo hoặc phê duyệt đơn phúc khảo.
        """
        action = request.data.get('action')
        if action == 'approve':
            user = request.user if request.user.is_authenticated else None
            don = PhucKhaoService.phe_duyet_phuc_khao(pk, nguoi_duyet_user=user)
            return Response({"message": "Đã phê duyệt đơn phúc khảo", "ma_don": don.ma_don, "status": don.trang_thai}, status=status.HTTP_200_OK)
        else:
            pt1 = request.data.get('pt1') or request.data.get('diem_phuc_khao_1')
            pt2 = request.data.get('pt2') or request.data.get('diem_phuc_khao_2')
            ptFinal = request.data.get('ptFinal') or request.data.get('diem_phuc_khao_cuoi') or request.data.get('oldPt')
            file_bien_ban = request.data.get('file') or request.data.get('file_bien_ban')
            trang_thai = request.data.get('status') or request.data.get('trang_thai', 'DaXuLy')

            don = PhucKhaoService.luu_diem_phuc_khao(
                ma_don=pk,
                diem_1=pt1,
                diem_2=pt2,
                diem_cuoi=ptFinal,
                file_bien_ban=file_bien_ban,
                trang_thai=trang_thai
            )
            return Response({"message": "Cập nhật điểm phúc khảo thành công", "ma_don": don.ma_don, "status": don.trang_thai}, status=status.HTTP_200_OK)


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
