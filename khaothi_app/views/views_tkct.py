from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import TuiBaiThi, TuiPhach, MaPhach, HocPhan
from ..serializers import TuiBaiThiSerializer, TuiPhachSerializer
from .views_common import ensure_actor_logged_in

def tkct_view(request):
    """
    Thư ký Chấm thi (TKCT) Portal view.
    """
    ensure_actor_logged_in(request, 'tkct')
    return render(request, 'khaothi_app/tkct/giaodienTKCT.html')

class TKCTDataAPI(APIView):
    """
    API cung cấp dữ liệu cho giao diện của Thư ký Chấm thi.
    """
    def get(self, request, *args, **kwargs):
        # Lấy danh sách túi bài thi đang chờ làm phách
        tui_bai_thi_cho_lam_phach = TuiBaiThi.objects.filter(trang_thai='DaThuHoi').select_related('lich_thi__lop_hp__hoc_phan')
        
        # Lấy danh sách túi phách đã được tạo
        tui_phach_da_tao = TuiPhach.objects.all().select_related('hoc_phan')

        # Serialize dữ liệu
        tui_bai_thi_serializer = TuiBaiThiSerializer(tui_bai_thi_cho_lam_phach, many=True)
        tui_phach_serializer = TuiPhachSerializer(tui_phach_da_tao, many=True)

        data = {
            'tui_bai_thi_cho_lam_phach': tui_bai_thi_serializer.data,
            'tui_phach_da_tao': tui_phach_serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)


class TuiPhachAPI(APIView):
    def post(self, request, *args, **kwargs):
        # Tạo túi phách mới từ các túi bài thi
        tui_bais = request.data.get('tui_bais', [])
        if not tui_bais:
            return Response({'error': 'Không có dữ liệu túi bài thi'}, status=status.HTTP_400_BAD_REQUEST)
        
        created_tuis = []
        for index, tui in enumerate(tui_bais):
            hoc_phan_ma = tui.get('subjectId')
            so_bai = tui.get('papers', 30)
            
            hoc_phan = HocPhan.objects.filter(ma_hoc_phan=hoc_phan_ma).first()
            ma_tui = f"TP_{hoc_phan_ma}_{index+1}" # Đơn giản hóa tạo mã túi
            
            tui_obj, _ = TuiPhach.objects.get_or_create(
                ma_tui=ma_tui,
                defaults={
                    'hoc_phan': hoc_phan,
                    'so_luong_bai': so_bai,
                    'trang_thai': 'MoiTao'
                }
            )
            created_tuis.append(tui_obj)
            
            # Cần sinh phách ảo ở đây nếu muốn đúng thực tế, nhưng state API GetStateAPI đang render phách ngẫu nhiên.
            # Dành cho seed_data xử lý tạo MaPhach.

        return Response({'status': 'success', 'message': 'Tạo phách thành công'}, status=status.HTTP_201_CREATED)
