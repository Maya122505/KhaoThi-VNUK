from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import PhienBanCotDiem, CauHinhPhucKhao, CauHinhThoiGianDotThi, CauHinhHeThong
from ..serializers import PhienBanCotDiemSerializer, CauHinhPhucKhaoSerializer
from django.utils.dateparse import parse_datetime
from .views_common import ensure_actor_logged_in

def cvht_view(request):
    """
    Chuyên viên Hệ thống (CVHT) Portal view.
    """
    ensure_actor_logged_in(request, 'cvht')
    return render(request, 'khaothi_app/cvht/giaodienCVHT.html')

class PhienBanCotDiemAPI(APIView):
    """
    API để quản lý Phiên bản Cột điểm.
    """
    def get(self, request, *args, **kwargs):
        configs = PhienBanCotDiem.objects.all()
        serializer = PhienBanCotDiemSerializer(configs, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Sử dụng update_or_create để vừa tạo mới vừa cập nhật
        serializer = PhienBanCotDiemSerializer(data=request.data)
        if serializer.is_valid():
            # Logic update_or_create cần xử lý trong service để tường minh hơn
            # Tạm thời làm trực tiếp ở view
            validated_data = serializer.validated_data
            instance, created = PhienBanCotDiem.objects.update_or_create(
                ma_phien_ban=validated_data.get('ma_phien_ban'),
                defaults=validated_data
            )
            return Response(PhienBanCotDiemSerializer(instance).data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CauHinhPhucKhaoAPI(APIView):
    """
    API để quản lý Cấu hình Phúc khảo.
    """
    def get(self, request, *args, **kwargs):
        configs = CauHinhPhucKhao.objects.all()
        serializer = CauHinhPhucKhaoSerializer(configs, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CauHinhPhucKhaoSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            instance, created = CauHinhPhucKhao.objects.update_or_create(
                ma_cau_hinh=validated_data.get('ma_cau_hinh'),
                defaults=validated_data
            )
            return Response(CauHinhPhucKhaoSerializer(instance).data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SystemConfigAPI(APIView):
    def post(self, request, *args, **kwargs):
        system_configs_data = request.data.get('systemConfigsData', {})
        system_globals = request.data.get('systemGlobals', {})

        # Lưu globals (VD: khóa cổng)
        for key, value in system_globals.items():
            CauHinhHeThong.objects.update_or_create(
                key=key,
                defaults={'value': str(value), 'nguoi_cap_nhat': request.user}
            )

        # Lưu configs theo dot thi
        nhap_diem_cfg = system_configs_data.get('nhapDiem', {})
        phuc_khao_cfg = system_configs_data.get('phucKhao', {})

        all_keys = set(nhap_diem_cfg.keys()).union(set(phuc_khao_cfg.keys()))
        for key in all_keys:
            parts = key.split('_')
            if len(parts) >= 3:
                nam_hoc, hoc_ky, dot_thi = parts[0], parts[1], parts[2]
                nd = nhap_diem_cfg.get(key, {})
                pk = phuc_khao_cfg.get(key, {})

                ch_obj, _ = CauHinhThoiGianDotThi.objects.get_or_create(
                    nam_hoc=nam_hoc,
                    hoc_ky=hoc_ky,
                    dot_thi=dot_thi
                )
                if nd.get('start'): ch_obj.tg_bat_dau_nhap = parse_datetime(nd.get('start'))
                if nd.get('end'): ch_obj.tg_khoa_cong_nhap = parse_datetime(nd.get('end'))
                if nd.get('publish'): ch_obj.tg_cong_bo_diem = parse_datetime(nd.get('publish'))
                if nd.get('nop_de'): ch_obj.tg_nop_de_thi = parse_datetime(nd.get('nop_de'))
                if nd.get('nhap_tp'): ch_obj.tg_nhap_diem_tp = parse_datetime(nd.get('nhap_tp'))
                if nd.get('trong_so'): ch_obj.tg_cau_hinh_trong_so = parse_datetime(nd.get('trong_so'))
                if nd.get('dieu_kien'): ch_obj.tg_chot_dieu_kien_thi = parse_datetime(nd.get('dieu_kien'))
                if nd.get('quy_doi'): ch_obj.tg_chot_quy_doi = parse_datetime(nd.get('quy_doi'))

                if pk.get('start'): ch_obj.tg_mo_nhan_don_pk = parse_datetime(pk.get('start'))
                if pk.get('end'): ch_obj.tg_khoa_nhan_don_pk = parse_datetime(pk.get('end'))
                if pk.get('deadline'): ch_obj.han_chot_cham_pk = parse_datetime(pk.get('deadline'))

                ch_obj.is_locked = True
                ch_obj.save()

        return Response({'status': 'success', 'message': 'Cập nhật cấu hình thành công'}, status=status.HTTP_200_OK)
