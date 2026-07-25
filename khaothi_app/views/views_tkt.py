from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..models import KyThi, CaThi, HocPhan, PhongThi, User, LichThi, PhieuGiaoNhan, DonPhucKhao, PhanCongCoiThi
from ..forms.forms_tkt import KyThiForm, CaThiForm, LapLichThiForm, PhieuGiaoNhanForm
from ..services.services_tkt import DoiSoatTKTService, GiaoNhanTKTService, PhucKhaoService
from ..serializers import (
    LichThiSerializer, PhieuGiaoNhanSerializer, DonPhucKhaoSerializer, KyThiSerializer,
    CaThiSerializer, PhanCongCoiThiSerializer
)

# ===================================================================
# 1. Template Rendering Views
# ===================================================================

def tkt_dashboard_view(request):
    from .views_common import ensure_actor_logged_in
    ensure_actor_logged_in(request, 'tkt')
    return render(request, 'khaothi_app/tkt/giaodienTKT.html')

def quan_ly_ky_thi_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_ky_thi.html')

def lap_lich_thi_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_danh_sach_lich.html')

def nhap_diem_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_nhap_diem.html')

def phuc_khao_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_phuc_khao.html')

def giao_nhan_view(request):
    form = PhieuGiaoNhanForm()
    return render(request, 'khaothi_app/tkt/partials/_view_giao_nhan.html', {'form': form})

def can_bo_coi_thi_view(request):
    return render(request, 'khaothi_app/tkt/partials/_view_gio_coi.html')

# ===================================================================
# 2. API Endpoints
# ===================================================================

class GiaoNhanDataAPI(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        lich_thi_co_the_ban_giao = LichThi.objects.filter(
            trang_thai_bai_thi__in=['ChuaNhanBai', 'DaNhanBai']
        ).select_related('lop_hp__hoc_phan', 'ca_thi', 'phong_thi')
        phieu_cho_xac_nhan = PhieuGiaoNhan.objects.filter(
            trang_thai='ChoXacNhan'
        ).select_related('nguoi_giao', 'nguoi_nhan').prefetch_related('chi_tiet__lich_thi', 'chi_tiet__tui_phach')
        lich_su_phieu = PhieuGiaoNhan.objects.all().select_related('nguoi_giao', 'nguoi_nhan').prefetch_related('chi_tiet__lich_thi', 'chi_tiet__tui_phach').order_by('-ngay_giao')

        lich_thi_serializer = LichThiSerializer(lich_thi_co_the_ban_giao, many=True)
        phieu_cho_xac_nhan_serializer = PhieuGiaoNhanSerializer(phieu_cho_xac_nhan, many=True)
        lich_su_phieu_serializer = PhieuGiaoNhanSerializer(lich_su_phieu, many=True)

        data = {
            'lich_thi_ban_giao': lich_thi_serializer.data,
            'phieu_cho_xac_nhan': phieu_cho_xac_nhan_serializer.data,
            'lich_su_phieu': lich_su_phieu_serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)

class KyThiAPI(APIView):
    def get(self, request):
        ky_this = KyThi.objects.all()
        serializer = KyThiSerializer(ky_this, many=True)
        return Response(serializer.data)

    def post(self, request):
        form = KyThiForm(request.data)
        if form.is_valid():
            ky_thi = form.save()
            serializer = KyThiSerializer(ky_thi)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class CaThiAPI(APIView):
    def get(self, request):
        ky_thi_id = request.query_params.get('ky_thi_id')
        if ky_thi_id:
            ca_this = CaThi.objects.filter(ky_thi_id=ky_thi_id)
        else:
            ca_this = CaThi.objects.all()
        serializer = CaThiSerializer(ca_this, many=True)
        return Response(serializer.data)

    def post(self, request):
        form = CaThiForm(request.data)
        if form.is_valid():
            ca_thi = form.save()
            serializer = CaThiSerializer(ca_thi)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class LichThiAPI(APIView):
    def get(self, request):
        lich_this = LichThi.objects.all().select_related('lop_hp__hoc_phan', 'ca_thi', 'phong_thi')
        serializer = LichThiSerializer(lich_this, many=True)
        return Response(serializer.data)

    def post(self, request):
        form = LapLichThiForm(request.data)
        if form.is_valid():
            # TODO: Chuyển logic này vào service
            # service.lap_lich_thi(form.cleaned_data)
            return Response({"message": "Lập lịch thành công (chưa có logic)"}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class DonPhucKhaoAPI(APIView):
    def get(self, request):
        trang_thai = request.query_params.get('trang_thai')
        search = request.query_params.get('search')
        danh_sach = PhucKhaoService.lay_danh_sach_don(trang_thai=trang_thai, search=search)
        serializer = DonPhucKhaoSerializer(danh_sach, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            don = PhucKhaoService.tao_don_phuc_khao(**request.data)
            serializer = DonPhucKhaoSerializer(don)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (ValueError, TypeError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DonPhucKhaoDetailAPI(APIView):
    def get(self, request, pk):
        try:
            don = DonPhucKhao.objects.get(ma_don=pk)
            serializer = DonPhucKhaoSerializer(don)
            return Response(serializer.data)
        except DonPhucKhao.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn phúc khảo"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            action = request.data.pop('action', None)
            if action == 'approve':
                don = PhucKhaoService.phe_duyet_phuc_khao(pk, nguoi_duyet_user=request.user)
            else:
                don = PhucKhaoService.luu_diem_phuc_khao(ma_don=pk, **request.data)
            
            serializer = DonPhucKhaoSerializer(don)
            return Response(serializer.data)
        except DonPhucKhao.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn phúc khảo"}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PhieuGiaoNhanAPI(APIView):
    def post(self, request, *args, **kwargs):
        try:
            phieu = GiaoNhanTKTService.tao_phieu_giao_nhan(
                nguoi_giao=request.user,
                data=request.data.copy(),
                files=request.FILES
            )
            serializer = PhieuGiaoNhanSerializer(phieu)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Lỗi không xác định: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class XacNhanPhieuAPI(APIView):
    def post(self, request, pk):
        try:
            phieu = GiaoNhanTKTService.xac_nhan_nhan_phieu(ma_phieu=pk, nguoi_xac_nhan=request.user)
            serializer = PhieuGiaoNhanSerializer(phieu)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PhieuGiaoNhan.DoesNotExist:
            return Response({"error": "Không tìm thấy phiếu giao nhận."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

class CanBoCoiThiAPI(APIView):
    def get(self, request):
        phan_cong_list = PhanCongCoiThi.objects.all().select_related('can_bo__khoa', 'lich_thi__lop_hp__hoc_phan')
        serializer = PhanCongCoiThiSerializer(phan_cong_list, many=True)
        return Response(serializer.data)

class DanhSachDuThiAPI(APIView):
    def get(self, request):
        return Response([])

class NhapDiemSBDAPI(APIView):
    def post(self, request):
        return Response({})

class NhapDiemPhachAPI(APIView):
    def post(self, request):
        return Response({})

