from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import TuiPhach, GiangVien, NhanVien, PhanCongChamThi
from ..serializers import TuiPhachSerializer, GiangVienSerializer
from .views_common import ensure_actor_logged_in

def dvcm_view(request):
    """
    Đơn vị chuyên môn (DVCM) Portal view.
    """
    ensure_actor_logged_in(request, 'dvcm')
    return render(request, 'khaothi_app/dvcm/giaodienDVCM.html')

class DVCMDataAPI(APIView):
    """
    API cung cấp dữ liệu cho giao diện của Đơn vị Chuyên môn.
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Lấy thông tin khoa của nhân viên DVCM
        try:
            nhan_vien = NhanVien.objects.get(user=user)
            khoa_dvcm = nhan_vien.khoa
        except NhanVien.DoesNotExist:
            return Response({"error": "Không tìm thấy thông tin nhân viên cho người dùng này."}, status=status.HTTP_404_NOT_FOUND)

        if not khoa_dvcm:
            return Response({"error": "Người dùng không được gán vào khoa nào."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Lấy danh sách túi phách đang chờ phân công chấm
        tui_phach_cho_phan_cong = TuiPhach.objects.filter(
            trang_thai='DaGiaoDVCM',
            hoc_phan__khoa=khoa_dvcm
        ).select_related('hoc_phan')

        # 2. Lấy danh sách giảng viên thuộc khoa
        giang_vien_khoa = GiangVien.objects.filter(khoa=khoa_dvcm)

        # Serialize dữ liệu
        tui_phach_serializer = TuiPhachSerializer(tui_phach_cho_phan_cong, many=True)
        giang_vien_serializer = GiangVienSerializer(giang_vien_khoa, many=True)

        data = {
            'tui_phach_cho_phan_cong': tui_phach_serializer.data,
            'danh_sach_giang_vien': giang_vien_serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)


class PhanCongChamAPI(APIView):
    def post(self, request, *args, **kwargs):
        phan_congs = request.data.get('phan_congs', [])
        if not phan_congs:
            return Response({'error': 'Không có dữ liệu phân công'}, status=status.HTTP_400_BAD_REQUEST)
        
        for pc in phan_congs:
            tui_id = pc.get('tui_phach')
            gv1_id = pc.get('gv1')
            gv2_id = pc.get('gv2')

            tui = TuiPhach.objects.filter(ma_tui=tui_id).first()
            gv1 = GiangVien.objects.filter(ma_giang_vien=gv1_id).first()
            gv2 = GiangVien.objects.filter(ma_giang_vien=gv2_id).first()

            if tui:
                if gv1:
                    PhanCongChamThi.objects.update_or_create(
                        tui_phach=tui, vai_tro='Cán bộ chấm thi 1',
                        defaults={'giang_vien': gv1, 'loai_phan_cong': 'ChamChinh'}
                    )
                if gv2:
                    PhanCongChamThi.objects.update_or_create(
                        tui_phach=tui, vai_tro='Cán bộ chấm thi 2',
                        defaults={'giang_vien': gv2, 'loai_phan_cong': 'ChamChinh'}
                    )
                
                # Cập nhật trạng thái túi phách
                tui.trang_thai = 'DangCham'
                tui.save()

        return Response({'status': 'success', 'message': 'Phân công thành công'}, status=status.HTTP_201_CREATED)
