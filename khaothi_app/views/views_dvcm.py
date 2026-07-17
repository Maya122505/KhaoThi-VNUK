from django.shortcuts import render
from .views_common import ensure_actor_logged_in
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from khaothi_app.models import DeThi, NopDeThi, RaSoatDeThi, HocPhan, AuditLog

def dvcm_view(request):
    """
    Đơn vị chuyên môn (DVCM) Portal view.
    """
    ensure_actor_logged_in(request, 'dvcm')
    return render(request, 'khaothi_app/dvcm/giaodienDVCM.html')


class DeThiAPI(APIView):
    def get(self, request):
        dethi_list = []
        for dt in DeThi.objects.select_related('hoc_phan').prefetch_related('nop_de_thi__nguoi_nop', 'ra_soat_de_thi__nguoi_rao_soat').all():
            submissions = []
            for ndt in dt.nop_de_thi.all().order_by('-thoi_gian_nop'):
                submissions.append({
                    "nguoi_nop": ndt.nguoi_nop.ho_ten or ndt.nguoi_nop.username,
                    "thoi_gian_nop": ndt.thoi_gian_nop.strftime('%Y-%m-%d %H:%M:%S'),
                    "tep_dinh_kem": ndt.tep_dinh_kem
                })
            
            reviews = []
            for rs in dt.ra_soat_de_thi.all():
                reviews.append({
                    "nguoi_rao_soat": rs.nguoi_rao_soat.ho_ten or rs.nguoi_rao_soat.username,
                    "ket_qua": rs.ket_qua,
                    "ghi_chu": rs.ghi_chu or ""
                })
                
            dethi_list.append({
                "ma_de_thi": dt.ma_de_thi,
                "hoc_phan_id": dt.hoc_phan.ma_hoc_phan,
                "hoc_phan_ten": dt.hoc_phan.ten_hoc_phan,
                "trang_thai": dt.trang_thai,
                "submissions": submissions,
                "reviews": reviews
            })
        return Response(dethi_list)

    def post(self, request):
        hoc_phan_id = request.data.get('hoc_phan_id')
        tep_dinh_kem = request.data.get('tep_dinh_kem')
        ghi_chu = request.data.get('ghi_chu', '')

        # Exception flow 7b: Thiếu thông tin bắt buộc
        if not hoc_phan_id or not tep_dinh_kem:
            return Response({"error": "Vui lòng nhập đầy đủ thông tin đề thi."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Exception flow 4b: Định dạng tệp không hợp lệ
        valid_extensions = ('.pdf', '.docx', '.doc')
        if not tep_dinh_kem.lower().endswith(valid_extensions):
            return Response({"error": "Tệp đề thi không hợp lệ. Chỉ chấp nhận định dạng .pdf, .docx, .doc."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hoc_phan = HocPhan.objects.get(ma_hoc_phan=hoc_phan_id)
        except HocPhan.DoesNotExist:
            return Response({"error": "Học phần không tồn tại trên hệ thống."}, status=status.HTTP_400_BAD_REQUEST)

        # Tự động sinh mã đề thi
        count = DeThi.objects.filter(hoc_phan=hoc_phan).count()
        ma_de_thi = f"DT_{hoc_phan.ma_hoc_phan}_{count + 1}"

        try:
            # Tạo hoặc cập nhật DeThi
            de_thi, created = DeThi.objects.get_or_create(
                ma_de_thi=ma_de_thi,
                defaults={'hoc_phan': hoc_phan, 'trang_thai': 'ChoRaSoat'}
            )
            if not created:
                de_thi.trang_thai = 'ChoRaSoat'
                de_thi.save()

            # Tạo NopDeThi log
            NopDeThi.objects.create(
                de_thi=de_thi,
                nguoi_nop=request.user,
                tep_dinh_kem=f"{tep_dinh_kem} (Ghi chú: {ghi_chu})" if ghi_chu else tep_dinh_kem
            )

            # Ghi log lịch sử AuditLog
            AuditLog.objects.create(
                actor=request.user,
                action=f"Nộp đề thi {ma_de_thi} cho học phần {hoc_phan.ten_hoc_phan} ({tep_dinh_kem})."
            )

            return Response({
                "message": "Nộp đề thi thành công.",
                "ma_de_thi": ma_de_thi
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Không thể nộp đề thi. Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RaSoatDeThiAPI(APIView):
    def post(self, request):
        ma_de_thi = request.data.get('ma_de_thi')
        ket_qua = request.data.get('ket_qua')  # 'Dat' hoặc 'YeuCauChinhSua'
        nhan_xet = request.data.get('nhan_xet')
        ghi_chu = request.data.get('ghi_chu', '')

        if not ma_de_thi or not ket_qua or not nhan_xet:
            return Response({"error": "Vui lòng nhập đầy đủ thông tin rà soát."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            de_thi = DeThi.objects.get(ma_de_thi=ma_de_thi)
        except DeThi.DoesNotExist:
            return Response({"error": "Đề thi không tồn tại trên hệ thống."}, status=status.HTTP_404_NOT_FOUND)

        # Cập nhật trạng thái đề thi
        new_status = 'DaRaSoat' if ket_qua == 'Dat' else 'YeuCauChinhSua'
        
        try:
            de_thi.trang_thai = new_status
            de_thi.save()

            # Tạo bản ghi RaSoatDeThi
            RaSoatDeThi.objects.create(
                de_thi=de_thi,
                nguoi_rao_soat=request.user,
                ket_qua=nhan_xet,
                ghi_chu=ghi_chu
            )

            # Ghi log hệ thống
            result_str = "Đạt (Chờ duyệt)" if ket_qua == 'Dat' else "Yêu cầu chỉnh sửa"
            AuditLog.objects.create(
                actor=request.user,
                action=f"Rà soát đề thi {ma_de_thi}. Kết quả: {result_str}. Nhận xét: {nhan_xet}."
            )

            return Response({"message": "Lưu kết quả rà soát thành công."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Không thể lưu kết quả rà soát. Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
