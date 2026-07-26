from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import KyThi, TuiPhach, QuyetToanThuLao, DonPhucKhao
from ..serializers import KyThiSerializer
from django.utils import timezone
from .views_common import ensure_actor_logged_in

def ldp_view(request):
    """
    Lãnh đạo phòng (LDP) Portal view.
    """
    ensure_actor_logged_in(request, 'ldp')
    return render(request, 'khaothi_app/ldp/giaodienLDP.html')

class KyThiPheDuyetAPI(APIView):
    """
    API cho LDP xem và phê duyệt các Kỳ thi.
    """
    def get(self, request, *args, **kwargs):
        """
        Lấy danh sách tất cả các kỳ thi.
        """
        ky_this = KyThi.objects.all()
        serializer = KyThiSerializer(ky_this, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Phê duyệt một kỳ thi.
        """
        ky_thi_id = request.data.get('ma_ky_thi')
        if not ky_thi_id:
            return Response({"error": "Thiếu mã kỳ thi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ky_thi = KyThi.objects.get(ma_ky_thi=ky_thi_id)
            ky_thi.trang_thai = 'DaPheDuyet'
            ky_thi.save()
            serializer = KyThiSerializer(ky_thi)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KyThi.DoesNotExist:
            return Response({"error": "Không tìm thấy kỳ thi."}, status=status.HTTP_404_NOT_FOUND)


class PheDuyetAPI(APIView):
    def post(self, request, *args, **kwargs):
        mat_khau = request.data.get('password')
        loai_phe_duyet = request.data.get('type') # 'diem', 'phuc_khao', 'thu_lao'
        targets = request.data.get('targets', [])

        if not request.user.check_password(mat_khau):
            return Response({'error': 'Mật khẩu không chính xác'}, status=status.HTTP_401_UNAUTHORIZED)
        
        now = timezone.now()
        
        if loai_phe_duyet == 'diem':
            TuiPhach.objects.filter(ma_tui__in=targets).update(nguoi_duyet_diem=request.user, ngay_duyet_diem=now, trang_thai='DaKhoa')
        elif loai_phe_duyet == 'phuc_khao':
            DonPhucKhao.objects.filter(ma_don__in=targets).update(nguoi_duyet=request.user, ngay_duyet=now, trang_thai='DaHoanThanh')
        elif loai_phe_duyet == 'thu_lao':
            # Simplified logic for demo
            QuyetToanThuLao.objects.filter(ma_quyet_toan__in=targets).update(nguoi_duyet=request.user, ngay_duyet=now)
        else:
            return Response({'error': 'Loại phê duyệt không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'success', 'message': 'Phê duyệt thành công'}, status=status.HTTP_200_OK)
