from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import KyThi, CaThi, HocPhan, PhongThi, User, LichThi, DeThi, DotInSao, NhatKyInSao, BienBanGiamSatInSao, AuditLog
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


class PhongThiAPI(APIView):
    def get(self, request):
        rooms = PhongThi.objects.all().values()
        return Response(list(rooms))

    def post(self, request):
        ten_phong = request.data.get('ten_phong')
        suc_chua = request.data.get('suc_chua')
        loai_phong = request.data.get('loai_phong', '')
        vi_tri = request.data.get('vi_tri', '')
        trang_thai = request.data.get('trang_thai', 'KhaDung')
        ghi_chu = request.data.get('ghi_chu', '')

        if not ten_phong or not suc_chua:
            return Response({"error": "Thông tin phòng thi không hợp lệ. Vui lòng kiểm tra lại."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            suc_chua = int(suc_chua)
            if suc_chua <= 0:
                raise ValueError()
        except ValueError:
            return Response({"error": "Sức chứa phải là số nguyên dương."}, status=status.HTTP_400_BAD_REQUEST)

        # Tự động sinh mã phòng: P.101, P.102,...
        max_num = 100
        for pt in PhongThi.objects.filter(ma_phong__startswith='P.'):
            try:
                num = int(pt.ma_phong.split('.')[1])
                if num > max_num:
                    max_num = num
            except:
                pass
        new_ma_phong = f"P.{max_num + 1}"

        try:
            room = PhongThi.objects.create(
                ma_phong=new_ma_phong,
                ten_phong=ten_phong,
                loai_phong=loai_phong,
                suc_chua=suc_chua,
                vi_tri=vi_tri,
                trang_thai=trang_thai,
                ghi_chu=ghi_chu
            )
            return Response({
                "message": "Thêm phòng thi thành công",
                "ma_phong": room.ma_phong,
                "ten_phong": room.ten_phong
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "Không thể lưu thông tin phòng thi. Vui lòng thử lại sau."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhanCongPhongAPI(APIView):
    def get(self, request):
        from ..models import LichThi
        # Lấy danh sách lịch thi chưa phân công
        lich_can_phan = []
        for lt in LichThi.objects.filter(phong_thi__isnull=True).select_related('lop_hp__hoc_phan', 'ca_thi'):
            lich_can_phan.append({
                "id": lt.ma_lich_thi,
                "subjectName": lt.lop_hp.hoc_phan.ten_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "Học phần",
                "subjectCode": lt.lop_hp.hoc_phan.ma_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
                "date": str(lt.ngay_thi),
                "shift": lt.ca_thi.ten_ca,
                "shift_id": lt.ca_thi.ma_ca_thi,
                "qty": lt.so_luong_sv
            })

        # Lấy danh sách lịch thi đã phân công
        lich_da_phan = []
        for lt in LichThi.objects.filter(phong_thi__isnull=False).select_related('lop_hp__hoc_phan', 'ca_thi', 'phong_thi'):
            # Tránh lấy các lịch thi phụ do split
            if "_P" in lt.ma_lich_thi:
                continue
            
            # Kiểm tra xem có phòng phụ nào liên kết không
            sub_lits = LichThi.objects.filter(ma_lich_thi__startswith=f"{lt.ma_lich_thi}_P")
            rooms = [lt.phong_thi.ten_phong]
            room_ids = [lt.phong_thi.ma_phong]
            total_students = lt.so_luong_sv
            for slt in sub_lits:
                if slt.phong_thi:
                    rooms.append(slt.phong_thi.ten_phong)
                    room_ids.append(slt.phong_thi.ma_phong)
                total_students += slt.so_luong_sv
                
            lich_da_phan.append({
                "id": lt.ma_lich_thi,
                "subjectName": lt.lop_hp.hoc_phan.ten_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "Học phần",
                "subjectCode": lt.lop_hp.hoc_phan.ma_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
                "date": str(lt.ngay_thi),
                "shift": lt.ca_thi.ten_ca,
                "shift_id": lt.ca_thi.ma_ca_thi,
                "rooms": ", ".join(rooms),
                "room_ids": room_ids,
                "qty": total_students
            })

        return Response({
            "lich_can_phan": lich_can_phan,
            "lich_da_phan": lich_da_phan
        })

    def post(self, request):
        from ..models import LichThi, PhongThi, DanhSachThiSinh, AuditLog
        from django.db import transaction

        lich_thi_id = request.data.get('lich_thi_id')
        room_ids = request.data.get('room_ids', [])

        if not lich_thi_id or not room_ids:
            return Response({"error": "Thiếu thông tin phân công phòng thi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                lt = LichThi.objects.select_for_update().get(ma_lich_thi=lich_thi_id)
                rooms = list(PhongThi.objects.filter(ma_phong__in=room_ids))

                if len(rooms) != len(room_ids):
                    return Response({"error": "Một hoặc nhiều phòng thi được chọn không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)

                # Rule: Kiểm tra khả dụng
                for r in rooms:
                    if r.trang_thai != 'KhaDung':
                        return Response({"error": f"Phòng thi {r.ten_phong} hiện không khả dụng."}, status=status.HTTP_400_BAD_REQUEST)

                # Rule: Sức chứa
                total_capacity = sum(r.suc_chua for r in rooms)
                if total_capacity < lt.so_luong_sv:
                    return Response({"error": "Sức chứa phòng không đủ cho số thí sinh đã phân công."}, status=status.HTTP_400_BAD_REQUEST)

                # Rule: Trùng lịch (Xung đột lịch trong cùng ngày thi và ca thi)
                for r in rooms:
                    conflicts = LichThi.objects.filter(
                        ngay_thi=lt.ngay_thi,
                        ca_thi=lt.ca_thi,
                        phong_thi=r
                    ).exclude(ma_lich_thi=lt.ma_lich_thi)
                    if conflicts.exists():
                        return Response({"error": f"Phòng thi {r.ten_phong} đã được sử dụng trong khung giờ này."}, status=status.HTTP_400_BAD_REQUEST)

                # Thực hiện phân công
                candidates = list(lt.danh_sach_thi_sinh.all())
                candidates.sort(key=lambda x: x.sbd)

                r1 = rooms[0]
                lt.phong_thi = r1
                
                if len(rooms) == 1:
                    lt.save()
                else:
                    # Phân chia nhiều phòng
                    cap1 = r1.suc_chua
                    lt.so_luong_sv = min(cap1, len(candidates))
                    lt.save()

                    curr_idx = cap1
                    for idx, r in enumerate(rooms[1:], start=2):
                        if curr_idx >= len(candidates):
                            break
                        
                        room_candidates = candidates[curr_idx : curr_idx + r.suc_chua]
                        curr_idx += r.suc_chua

                        # Tạo LichThi phụ
                        sub_lt_id = f"{lt.ma_lich_thi}_P{idx}"
                        sub_lt = LichThi.objects.create(
                            ma_lich_thi=sub_lt_id,
                            ky_thi=lt.ky_thi,
                            lop_hp=lt.lop_hp,
                            ca_thi=lt.ca_thi,
                            phong_thi=r,
                            ngay_thi=lt.ngay_thi,
                            so_luong_sv=len(room_candidates)
                        )

                        # Chuyển candidates sang LichThi mới
                        for c in room_candidates:
                            c.lich_thi = sub_lt
                            c.save()

                # Ghi log lịch sử
                AuditLog.objects.create(
                    actor=request.user,
                    action=f"Phân công phòng thi cho lịch {lt.ma_lich_thi} vào các phòng: {', '.join([r.ten_phong for r in rooms])}."
                )

                return Response({"message": "Phân công phòng thi thành công."}, status=status.HTTP_200_OK)

        except LichThi.DoesNotExist:
            return Response({"error": "Không tìm thấy thông tin lịch thi."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Không thể lưu thông tin phân công phòng thi. Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        from ..models import LichThi, DanhSachThiSinh, AuditLog
        from django.db import transaction

        lich_thi_id = request.data.get('lich_thi_id')
        room_ids = request.data.get('room_ids', [])

        if not lich_thi_id or not room_ids:
            return Response({"error": "Thiếu thông tin điều chỉnh phân bổ phòng."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                lt = LichThi.objects.select_for_update().get(ma_lich_thi=lich_thi_id)

                # Reset phân công cũ
                sub_lits = list(LichThi.objects.filter(ma_lich_thi__startswith=f"{lt.ma_lich_thi}_P"))
                for slt in sub_lits:
                    for c in slt.danh_sach_thi_sinh.all():
                        c.lich_thi = lt
                        c.save()
                
                for slt in sub_lits:
                    slt.delete()

                all_candidates_count = lt.danh_sach_thi_sinh.count()
                lt.so_luong_sv = all_candidates_count
                lt.phong_thi = None
                lt.save()

                # Cập nhật tham số
                request.data['lich_thi_id'] = lich_thi_id
                request.data['room_ids'] = room_ids
                
                # Ghi log lịch sử
                AuditLog.objects.create(
                    actor=request.user,
                    action=f"Điều chỉnh phân bổ phòng cho lịch {lt.ma_lich_thi}. Reset và phân công lại."
                )
                
            return self.post(request)

        except LichThi.DoesNotExist:
            return Response({"error": "Không tìm thấy dữ liệu phân bổ phòng thi."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Không thể lưu thay đổi phân bổ phòng thi. Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DotInSaoAPI(APIView):
    def get(self, request):
        dots = []
        for dot in DotInSao.objects.select_related('ky_thi', 'ca_thi', 'phong_thi', 'hoc_phan', 'nguoi_tao', 'can_bo_giam_sat').prefetch_related('nhat_ky__nguoi_thuc_hien', 'nhat_ky__nguoi_giam_sat', 'bien_ban_giam_sat__nguoi_xac_nhan').all():
            nk_data = None
            if hasattr(dot, 'nhat_ky'):
                nk = dot.nhat_ky
                nk_data = {
                    "thoi_gian_thuc_hien": nk.thoi_gian_thuc_hien.strftime('%Y-%m-%d %H:%M:%S') if nk.thoi_gian_thuc_hien else "",
                    "nguoi_thuc_hien": nk.nguoi_thuc_hien.username,
                    "nguoi_thuc_hien_name": nk.nguoi_thuc_hien.full_name or nk.nguoi_thuc_hien.username,
                    "nguoi_giam_sat": nk.nguoi_giam_sat.username,
                    "nguoi_giam_sat_name": nk.nguoi_giam_sat.full_name or nk.nguoi_giam_sat.username,
                    "so_luong_in_thuc_te": nk.so_luong_in_thuc_te,
                    "so_luong_niem_phong": nk.so_luong_niem_phong,
                    "ghi_chu": nk.ghi_chu or ""
                }
            
            bb_data = None
            if hasattr(dot, 'bien_ban_giam_sat'):
                bb = dot.bien_ban_giam_sat
                bb_data = {
                    "trang_thai": bb.trang_thai,
                    "nguoi_xac_nhan": bb.nguoi_xac_nhan.username if bb.nguoi_xac_nhan else "",
                    "nguoi_xac_nhan_name": (bb.nguoi_xac_nhan.full_name or bb.nguoi_xac_nhan.username) if bb.nguoi_xac_nhan else "",
                    "nhan_xet_giam_sat": bb.nhan_xet_giam_sat or "",
                    "chu_ky_so": bb.chu_ky_so or "",
                    "ngay_xac_nhan": bb.ngay_xac_nhan.strftime('%Y-%m-%d %H:%M:%S') if bb.ngay_xac_nhan else "",
                    "ghi_chu": bb.ghi_chu or ""
                }

            dots.append({
                "ma_dot_in_sao": dot.ma_dot_in_sao,
                "ky_thi_id": dot.ky_thi.ma_ky_thi,
                "ky_thi_ten": dot.ky_thi.ten_ky_thi,
                "ca_thi_id": dot.ca_thi.ma_ca_thi if dot.ca_thi else "",
                "ca_thi_ten": dot.ca_thi.ten_ca if dot.ca_thi else "",
                "phong_thi_id": dot.phong_thi.ma_phong if dot.phong_thi else "",
                "phong_thi_ten": dot.phong_thi.ten_phong if dot.phong_thi else "",
                "hoc_phan_id": dot.hoc_phan.ma_hoc_phan if dot.hoc_phan else "",
                "hoc_phan_ten": dot.hoc_phan.ten_hoc_phan if dot.hoc_phan else "",
                "nguoi_tao_name": dot.nguoi_tao.full_name or dot.nguoi_tao.username,
                "ngay_tao": dot.ngay_tao.strftime('%Y-%m-%d %H:%M:%S'),
                "thoi_gian_in_sao": dot.thoi_gian_in_sao.strftime('%Y-%m-%d %H:%M:%S') if dot.thoi_gian_in_sao else "",
                "noi_in_sao": dot.noi_in_sao or "",
                "so_luong_ban_in": dot.so_luong_ban_in,
                "can_bo_giam_sat_id": dot.can_bo_giam_sat.id if dot.can_bo_giam_sat else "",
                "can_bo_giam_sat_name": (dot.can_bo_giam_sat.full_name or dot.can_bo_giam_sat.username) if dot.can_bo_giam_sat else "",
                "ghi_chu": dot.ghi_chu or "",
                "trang_thai": dot.trang_thai,
                "nhat_ky": nk_data,
                "bien_ban_giam_sat": bb_data
            })
            
        users = [{"id": u.id, "username": u.username, "full_name": u.full_name or u.username} for u in User.objects.filter(role__in=['tkt', 'gv', 'cvht'])]
        return Response({"dots": dots, "users": users})

    def post(self, request):
        ky_thi_id = request.data.get('ky_thi_id')
        ca_thi_id = request.data.get('ca_thi_id')
        phong_thi_id = request.data.get('phong_thi_id')
        hoc_phan_id = request.data.get('hoc_phan_id')
        thoi_gian_in_sao = request.data.get('thoi_gian_in_sao')
        noi_in_sao = request.data.get('noi_in_sao')
        so_luong_ban_in = request.data.get('so_luong_ban_in')
        can_bo_giam_sat_id = request.data.get('can_bo_giam_sat_id')
        ghi_chu = request.data.get('ghi_chu', '')

        # Exception flow 7b: "Thông tin đợt in sao không hợp lệ"
        if not ky_thi_id or not so_luong_ban_in or not thoi_gian_in_sao or not noi_in_sao:
            return Response({"error": "Thông tin đợt in sao không hợp lệ. Vui lòng điền đầy đủ các trường bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ky_thi = KyThi.objects.get(ma_ky_thi=ky_thi_id)
            ca_thi = CaThi.objects.get(ma_ca_thi=ca_thi_id) if ca_thi_id else None
            phong_thi = PhongThi.objects.get(ma_phong=phong_thi_id) if phong_thi_id else None
            hoc_phan = HocPhan.objects.get(ma_hoc_phan=hoc_phan_id) if hoc_phan_id else None
            
            can_bo_giam_sat = None
            if can_bo_giam_sat_id:
                can_bo_giam_sat = User.objects.get(id=can_bo_giam_sat_id)

            # Tự động sinh mã đợt in sao
            suffix = f"_{ca_thi.ma_ca_thi}" if ca_thi else ""
            if hoc_phan:
                suffix += f"_{hoc_phan.ma_hoc_phan}"
            
            count = DotInSao.objects.filter(ky_thi=ky_thi).count() + 1
            ma_dot_in_sao = f"DIS{suffix}_{count}"

            # Lưu đợt in sao
            dot = DotInSao.objects.create(
                ma_dot_in_sao=ma_dot_in_sao,
                ky_thi=ky_thi,
                ca_thi=ca_thi,
                phong_thi=phong_thi,
                hoc_phan=hoc_phan,
                nguoi_tao=request.user,
                thoi_gian_in_sao=thoi_gian_in_sao,
                noi_in_sao=noi_in_sao,
                so_luong_ban_in=int(so_luong_ban_in),
                can_bo_giam_sat=can_bo_giam_sat,
                ghi_chu=ghi_chu,
                trang_thai='ChoCapNhat'
            )

            # Ghi log AuditLog
            AuditLog.objects.create(
                actor=request.user,
                action=f"Lập đợt in sao đề thi mới {ma_dot_in_sao} phục vụ kỳ thi {ky_thi.ten_ky_thi}."
            )

            return Response({
                "message": "Lưu đợt in sao thành công.",
                "ma_dot_in_sao": ma_dot_in_sao
            }, status=status.HTTP_201_CREATED)

        except KyThi.DoesNotExist:
            return Response({"error": "Không thể tạo đợt in sao đề thi. Kỳ thi không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Không thể tạo đợt in sao đề thi. Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NhatKyInSaoAPI(APIView):
    def post(self, request):
        ma_dot_in_sao = request.data.get('ma_dot_in_sao')
        so_luong_in_thuc_te = request.data.get('so_luong_in_thuc_te')
        so_luong_niem_phong = request.data.get('so_luong_niem_phong')
        thoi_gian_thuc_hien = request.data.get('thoi_gian_thuc_hien')
        nguoi_giam_sat_id = request.data.get('nguoi_giam_sat_id')
        ghi_chu = request.data.get('ghi_chu', '')

        # Exception flow 7b: Thông tin nhật ký in sao không hợp lệ
        if not ma_dot_in_sao or not so_luong_in_thuc_te or not so_luong_niem_phong or not thoi_gian_thuc_hien or not nguoi_giam_sat_id:
            return Response({"error": "Thông tin nhật ký in sao không hợp lệ. Vui lòng nhập đầy đủ các trường bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dot = DotInSao.objects.get(ma_dot_in_sao=ma_dot_in_sao)
            nguoi_giam_sat = User.objects.get(id=nguoi_giam_sat_id)

            # Tạo hoặc cập nhật nhật ký
            nk, created = NhatKyInSao.objects.update_or_create(
                dot_in_sao=dot,
                defaults={
                    "thoi_gian_thuc_hien": thoi_gian_thuc_hien,
                    "nguoi_thuc_hien": request.user,
                    "nguoi_giam_sat": nguoi_giam_sat,
                    "so_luong_in_thuc_te": int(so_luong_in_thuc_te),
                    "so_luong_niem_phong": int(so_luong_niem_phong),
                    "ghi_chu": ghi_chu
                }
            )

            # Cập nhật trạng thái đợt in sao sang DaCapNhat (Chờ xác nhận)
            dot.trang_thai = 'DaCapNhat'
            dot.save()

            # Tự động tạo Biên bản giám sát ở trạng thái ChoXacNhan
            BienBanGiamSatInSao.objects.update_or_create(
                dot_in_sao=dot,
                defaults={
                    "trang_thai": "ChoXacNhan",
                    "nguoi_xac_nhan": None,
                    "nhan_xet_giam_sat": "",
                    "chu_ky_so": "",
                    "ngay_xac_nhan": None
                }
            )

            # Ghi log AuditLog
            AuditLog.objects.create(
                actor=request.user,
                action=f"Cập nhật nhật ký in sao cho đợt {ma_dot_in_sao}. Số lượng thực tế: {so_luong_in_thuc_te} bản."
            )

            return Response({"message": "Cập nhật nhật ký in sao thành công."}, status=status.HTTP_200_OK)

        except DotInSao.DoesNotExist:
            return Response({"error": "Không thể lưu nhật ký in sao. Đợt in sao không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Không thể lưu nhật ký in sao. Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class XacNhanGiamSatAPI(APIView):
    def post(self, request):
        ma_dot_in_sao = request.data.get('ma_dot_in_sao')
        trang_thai_xac_nhan = request.data.get('trang_thai_xac_nhan') # 'DaXacNhan' hoặc 'TuChoi'
        nhan_xet_giam_sat = request.data.get('nhan_xet_giam_sat', '')
        chu_ky_so = request.data.get('chu_ky_so', '')
        ghi_chu = request.data.get('ghi_chu', '')

        # Exception flow 5b/6b: Kiểm tra dữ liệu biên bản
        if not ma_dot_in_sao or not trang_thai_xac_nhan:
            return Response({"error": "Thông tin xác nhận biên bản chưa hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)

        if trang_thai_xac_nhan == 'DaXacNhan' and not chu_ky_so:
            return Response({"error": "Biên bản giám sát chưa hợp lệ. Cần có chữ ký số để xác nhận."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dot = DotInSao.objects.get(ma_dot_in_sao=ma_dot_in_sao)
            
            # Cập nhật Biên bản giám sát
            bb = BienBanGiamSatInSao.objects.get(dot_in_sao=dot)
            bb.trang_thai = trang_thai_xac_nhan
            bb.nguoi_xac_nhan = request.user
            bb.nhan_xet_giam_sat = nhan_xet_giam_sat
            bb.chu_ky_so = chu_ky_so if trang_thai_xac_nhan == 'DaXacNhan' else ""
            from django.utils import timezone
            bb.ngay_xac_nhan = timezone.now() if trang_thai_xac_nhan == 'DaXacNhan' else None
            bb.ghi_chu = ghi_chu
            bb.save()

            # Cập nhật trạng thái DotInSao
            if trang_thai_xac_nhan == 'DaXacNhan':
                dot.trang_thai = 'HoanTat'
            else:
                dot.trang_thai = 'TuChoi'
            dot.save()

            # Ghi log AuditLog
            action_str = "xác nhận hoàn tất" if trang_thai_xac_nhan == 'DaXacNhan' else "từ chối xác nhận"
            AuditLog.objects.create(
                actor=request.user,
                action=f"Cán bộ giám sát {action_str} biên bản cho đợt in sao {ma_dot_in_sao}."
            )

            return Response({"message": f"Đã ghi nhận kết quả {action_str} thành công."}, status=status.HTTP_200_OK)

        except (DotInSao.DoesNotExist, BienBanGiamSatInSao.DoesNotExist) as e:
            return Response({"error": "Không có biên bản giám sát chờ xác nhận hoặc dữ liệu không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Không thể xác nhận biên bản giám sát. Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
