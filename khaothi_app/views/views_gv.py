from django.shortcuts import render
from .views_common import ensure_actor_logged_in

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import DiemThi, MaPhach, GiangVien, TuiPhach

def gv_view(request):
    """
    Giảng viên / Cán bộ chấm thi Portal view.
    """
    ensure_actor_logged_in(request, 'gv01') # Updated for consistent fake login
    return render(request, 'khaothi_app/gv/giaodienGV.html')

class NopDiemAPI(APIView):
    def post(self, request, *args, **kwargs):
        diem_data = request.data.get('diem_data', [])
        lan_cham = int(request.data.get('lan_cham', 1))
        tui_id = request.data.get('tui_phach')
        gv = GiangVien.objects.filter(user=request.user).first()
        
        if not gv:
            return Response({'error': 'Người dùng không phải là Giảng viên'}, status=status.HTTP_403_FORBIDDEN)

        for d in diem_data:
            ma_phach_id = d.get('ma_phach')
            diem_so = d.get('diem')
            
            phach = MaPhach.objects.filter(ma_phach=ma_phach_id).first()
            if phach and diem_so is not None:
                DiemThi.objects.update_or_create(
                    ma_phach=phach, lan_cham=lan_cham,
                    defaults={'diem': diem_so, 'can_bo': gv}
                )
        
        # Cập nhật trạng thái túi phách
        tui = TuiPhach.objects.filter(ma_tui=tui_id).first()
        if tui:
            tui.trang_thai = 'ChoKhopDiem'
            tui.save()

        return Response({'status': 'success', 'message': 'Nộp điểm thành công'}, status=status.HTTP_201_CREATED)
