from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from ..models import KyThi, CaThi, HocPhan, PhongThi, User, LichThi, DeThi, DotInSao, NhatKyInSao, BienBanGiamSatInSao, ChecklistInSao, AuditLog, DonPhucKhao, PhieuGiaoNhan
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
        ky_this = KyThi.objects.order_by('-ma_ky_thi').values()
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
            ca_this = CaThi.objects.filter(ky_thi_id=ky_thi_id).order_by('-ma_ca_thi').values()
        else:
            ca_this = CaThi.objects.order_by('-ma_ca_thi').values()
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
        API để lọc danh sách sinh viên đủ điều kiện thi theo học phần.
        """
        from ..models import LopHocPhan, DanhSachThiSinh, SinhVien
        hoc_phan_id = request.data.get('hoc_phan_id')
        if not hoc_phan_id:
            return Response({"error": "Vui lòng chọn học phần."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            lop_hps = LopHocPhan.objects.filter(hoc_phan__ma_hoc_phan=hoc_phan_id)
            result = []
            for lhp in lop_hps:
                for sv in lhp.sinh_vien.all():
                    result.append({
                        'msv': sv.ma_sinh_vien,
                        'name': sv.ho_ten,
                        'class': lhp.ma_lop_hp,
                        'eligible': True
                    })
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LichThiAPI(APIView):
    def get(self, request):
        """Lấy danh sách lịch thi, có thể lọc theo kỳ thi."""
        ky_thi_id = request.query_params.get('ky_thi_id')
        queryset = LichThi.objects.select_related('lop_hp__hoc_phan', 'ca_thi', 'phong_thi', 'ky_thi')
        if ky_thi_id:
            queryset = queryset.filter(ky_thi_id=ky_thi_id)
        
        result = []
        for lt in queryset.order_by('-ngay_thi'):
            result.append({
                "ma_lich_thi": lt.ma_lich_thi,
                "ky_thi": lt.ky_thi.ten_ky_thi,
                "hoc_phan": lt.lop_hp.hoc_phan.ten_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
                "ma_hoc_phan": lt.lop_hp.hoc_phan.ma_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
                "ca_thi": lt.ca_thi.ten_ca,
                "phong_thi": lt.phong_thi.ten_phong if lt.phong_thi else "Chưa phân công",
                "ngay_thi": str(lt.ngay_thi),
                "so_luong_sv": lt.so_luong_sv,
            })
        return Response(result)

    def post(self, request):
        """Lập lịch thi cho một học phần vào một ca thi, phòng thi cụ thể."""
        from ..models import LopHocPhan
        form = LapLichThiForm(request.data)
        if form.is_valid():
            ca_thi = form.cleaned_data['ca_thi']
            hoc_phan = form.cleaned_data['hoc_phan']
            phong_thi = form.cleaned_data['phong_thi']

            # Tìm lớp học phần liên kết
            lop_hp = LopHocPhan.objects.filter(hoc_phan=hoc_phan).first()
            if not lop_hp:
                return Response({"error": "Không tìm thấy lớp học phần cho học phần này."}, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra xung đột lịch
            conflict = LichThi.objects.filter(
                ngay_thi=ca_thi.ngay_thi,
                ca_thi=ca_thi,
                phong_thi=phong_thi
            ).exists()
            if conflict:
                return Response({"error": "Phòng thi đã được sử dụng trong ca thi này."}, status=status.HTTP_400_BAD_REQUEST)

            # Tạo mã lịch thi
            count = LichThi.objects.filter(ky_thi=ca_thi.ky_thi).count() + 1
            ma_lich = f"LT-{ca_thi.ky_thi.ma_ky_thi}-{count:03d}"

            so_luong = lop_hp.sinh_vien.count() if hasattr(lop_hp, 'sinh_vien') else 0
            lt = LichThi.objects.create(
                ma_lich_thi=ma_lich,
                ky_thi=ca_thi.ky_thi,
                lop_hp=lop_hp,
                ca_thi=ca_thi,
                phong_thi=phong_thi,
                ngay_thi=ca_thi.ngay_thi,
                so_luong_sv=so_luong
            )

            AuditLog.objects.create(
                actor=request.user if request.user.is_authenticated else None,
                action=f"Lập lịch thi {ma_lich} cho {hoc_phan.ten_hoc_phan} vào {ca_thi.ten_ca}."
            )

            return Response({"message": "Lập lịch thành công", "ma_lich_thi": ma_lich}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

# Các API khác sẽ được xây dựng theo cấu trúc tương tự...

class NhapDiemSBDAPI(APIView):
    def post(self, request):
        """Đối soát điểm nhập lần 2 theo SBD."""
        from ..models import DanhSachThiSinh
        ma_lop_thi = request.data.get('ma_lop_thi')
        du_lieu_diem = request.data.get('du_lieu_diem', {})

        if not ma_lop_thi:
            return Response({"error": "Vui lòng nhập mã lớp dự thi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = DoiSoatTKTService.doi_soat_diem_lan_2(ma_lop_thi, du_lieu_diem)
            if result:
                return Response(result)
            
            # Fallback: trả danh sách thí sinh trong lịch thi
            lich_this = LichThi.objects.filter(lop_hp__ma_lop_hp=ma_lop_thi)
            ds = []
            for lt in lich_this:
                for ts in lt.danh_sach_thi_sinh.select_related('sinh_vien').all():
                    ds.append({
                        "sbd": ts.sbd,
                        "ma_sv": ts.sinh_vien.ma_sinh_vien,
                        "ho_ten": ts.sinh_vien.ho_ten,
                        "diem_thi": getattr(ts, 'diem_thi', None),
                    })
            return Response({"danh_sach": ds, "message": "Tải danh sách thành công."})
        except Exception as e:
            return Response({"error": f"Lỗi đối soát điểm: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NhapDiemPhachAPI(APIView):
    def post(self, request):
        """Đối soát điểm nhập lần 2 theo mã phách."""
        from ..models import MaPhach
        ma_tui_phach = request.data.get('ma_tui_phach')
        mat_khau = request.data.get('mat_khau')
        du_lieu_diem = request.data.get('du_lieu_diem', {})

        if not ma_tui_phach:
            return Response({"error": "Vui lòng nhập mã túi phách."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Xác thực túi phách
            from ..models import TuiPhach
            tui = TuiPhach.objects.filter(ma_tui=ma_tui_phach).first()
            if not tui:
                return Response({"error": "Không tìm thấy túi phách."}, status=status.HTTP_404_NOT_FOUND)

            # Lấy danh sách mã phách trong túi
            ma_phach_list = MaPhach.objects.filter(tui_phach=tui).select_related('thi_sinh__sinh_vien')
            ds = []
            for mp in ma_phach_list:
                ts = mp.thi_sinh
                ds.append({
                    "ma_phach": mp.ma_phach,
                    "sbd": ts.sbd if ts else "",
                    "ho_ten": ts.sinh_vien.ho_ten if (ts and ts.sinh_vien) else "",
                    "diem_thi": ts.diem_thi if ts else None,
                })
            return Response({"danh_sach": ds, "message": "Tải danh sách thành công."})
        except Exception as e:
            return Response({"error": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DonPhucKhaoAPI(APIView):
    def get(self, request):
        """Lấy danh sách đơn phúc khảo."""
        from ..services.services_tkt import PhucKhaoService
        from ..serializers import DonPhucKhaoSerializer

        trang_thai = request.query_params.get('trang_thai')
        search = request.query_params.get('search')
        queryset = PhucKhaoService.lay_danh_sach_don(trang_thai=trang_thai, search=search)
        serializer = DonPhucKhaoSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Tạo đơn phúc khảo mới."""
        from ..services.services_tkt import PhucKhaoService
        try:
            don = PhucKhaoService.tao_don_phuc_khao(
                ma_don=request.data.get('ma_don', f"PK-{int(timezone.now().timestamp())}"),
                ma_sinh_vien=request.data.get('ma_sinh_vien'),
                ma_phach_str=request.data.get('ma_phach'),
                ma_lich_thi=request.data.get('ma_lich_thi'),
                ly_do=request.data.get('ly_do', ''),
                diem_goc=request.data.get('diem_goc'),
            )
            return Response({"message": "Tạo đơn phúc khảo thành công.", "ma_don": don.ma_don}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DonPhucKhaoDetailAPI(APIView):
    def put(self, request, pk):
        """Cập nhật điểm phúc khảo."""
        from ..services.services_tkt import PhucKhaoService
        try:
            action = request.data.get('action')
            if action == 'phe_duyet':
                don = PhucKhaoService.phe_duyet_phuc_khao(
                    ma_don=pk,
                    nguoi_duyet_user=request.user if request.user.is_authenticated else None
                )
                return Response({"message": "Phê duyệt phúc khảo thành công."})
            else:
                don = PhucKhaoService.luu_diem_phuc_khao(
                    ma_don=pk,
                    diem_1=request.data.get('diem_phuc_khao_1'),
                    diem_2=request.data.get('diem_phuc_khao_2'),
                    diem_cuoi=request.data.get('diem_phuc_khao_cuoi'),
                    trang_thai=request.data.get('trang_thai', 'DaXuLy'),
                )
                return Response({"message": "Cập nhật điểm phúc khảo thành công."})
        except DonPhucKhao.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn phúc khảo."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GiaoNhanDataAPI(APIView):
    def get(self, request):
        """Lấy dữ liệu giao nhận: phiếu giao nhận + danh sách users."""
        from ..models import PhieuGiaoNhan
        from ..serializers import PhieuGiaoNhanSerializer

        phieu_list = PhieuGiaoNhan.objects.select_related('nguoi_giao', 'nguoi_nhan').prefetch_related('chi_tiet').order_by('-ngay_giao')
        serializer = PhieuGiaoNhanSerializer(phieu_list, many=True)
        users = [{"id": u.id, "username": u.username, "full_name": u.full_name or u.username} for u in User.objects.all()]
        return Response({"phieu_list": serializer.data, "users": users})

class PhieuGiaoNhanAPI(APIView):
    def post(self, request):
        """Tạo phiếu giao nhận mới."""
        try:
            nguoi_giao = request.user if request.user.is_authenticated else User.objects.filter(role='tkt').first()
            if not nguoi_giao:
                return Response({"error": "Không xác định được người giao."}, status=status.HTTP_400_BAD_REQUEST)
            
            phieu = GiaoNhanTKTService.tao_phieu_giao_nhan(
                nguoi_giao=nguoi_giao,
                data=request.data.copy(),
                files=request.FILES
            )
            return Response({"message": "Tạo phiếu giao nhận thành công.", "ma_phieu": phieu.ma_phieu}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Lỗi tạo phiếu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class XacNhanPhieuAPI(APIView):
    def post(self, request, pk):
        """Xác nhận đã nhận phiếu giao nhận."""
        try:
            nguoi_xac_nhan = request.user if request.user.is_authenticated else None
            if not nguoi_xac_nhan:
                return Response({"error": "Bạn cần đăng nhập để xác nhận."}, status=status.HTTP_401_UNAUTHORIZED)
            
            phieu = GiaoNhanTKTService.xac_nhan_nhan_phieu(
                ma_phieu=pk,
                nguoi_xac_nhan=nguoi_xac_nhan
            )
            return Response({"message": "Xác nhận nhận phiếu thành công."})
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PhieuGiaoNhan.DoesNotExist:
            return Response({"error": "Không tìm thấy phiếu giao nhận."}, status=status.HTTP_404_NOT_FOUND)

class CanBoCoiThiAPI(APIView):
    def get(self, request):
        """Lấy danh sách cán bộ coi thi và phân công."""
        from ..models import PhanCongCoiThi, GiangVien
        from ..serializers import PhanCongCoiThiSerializer, GiangVienSerializer

        ky_thi_id = request.query_params.get('ky_thi_id')
        
        # Danh sách giảng viên
        giang_vien = GiangVien.objects.all()
        gv_serializer = GiangVienSerializer(giang_vien, many=True)

        # Danh sách phân công
        pc_query = PhanCongCoiThi.objects.select_related('can_bo', 'lich_thi__ca_thi', 'lich_thi__phong_thi')
        if ky_thi_id:
            pc_query = pc_query.filter(lich_thi__ky_thi_id=ky_thi_id)
        pc_serializer = PhanCongCoiThiSerializer(pc_query, many=True)

        return Response({
            "giang_vien": gv_serializer.data,
            "phan_cong": pc_serializer.data,
        })




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


STANDARD_QUALITY_CRITERIA = [
    ("TC_01", "Số lượng bản in chính xác & đủ đề dự phòng"),
    ("TC_02", "Chất lượng in rõ nét, không mờ nhòe/mất chữ/lệch trang"),
    ("TC_03", "Quy cách đóng ghim, thứ tự trang chính xác"),
    ("TC_04", "Đóng gói niêm phong túi đề thi & dán tem niêm phong đúng quy định"),
    ("TC_05", "Tiêu hủy toàn bộ bản in hỏng, in thử và bản in thừa"),
]

class DotInSaoAPI(APIView):
    def get(self, request):
        dots = []
        for dot in DotInSao.objects.select_related('ky_thi', 'ca_thi', 'phong_thi', 'hoc_phan', 'nguoi_tao', 'can_bo_giam_sat').prefetch_related('nhat_ky__nguoi_thuc_hien', 'nhat_ky__nguoi_giam_sat', 'nhat_ky__nguoi_kiem_tra', 'bien_ban_giam_sat__nguoi_xac_nhan', 'danh_sach_checklist__hoc_phan').order_by('-ma_dot_in_sao'):
            nk_data = None
            if hasattr(dot, 'nhat_ky'):
                nk = dot.nhat_ky
                nk_data = {
                    "thoi_gian_thuc_hien": nk.thoi_gian_thuc_hien.strftime('%Y-%m-%d %H:%M:%S') if nk.thoi_gian_thuc_hien else "",
                    "nguoi_thuc_hien": nk.nguoi_thuc_hien.username if nk.nguoi_thuc_hien else "",
                    "nguoi_thuc_hien_name": (nk.nguoi_thuc_hien.full_name or nk.nguoi_thuc_hien.username) if nk.nguoi_thuc_hien else "",
                    "nguoi_giam_sat": nk.nguoi_giam_sat.username if nk.nguoi_giam_sat else "",
                    "nguoi_giam_sat_name": (nk.nguoi_giam_sat.full_name or nk.nguoi_giam_sat.username) if nk.nguoi_giam_sat else "",
                    "so_luong_in_thuc_te": nk.so_luong_in_thuc_te,
                    "so_luong_niem_phong": nk.so_luong_niem_phong,
                    "ghi_chu": nk.ghi_chu or "",
                    "ket_qua_kiem_tra": nk.ket_qua_kiem_tra or "",
                    "nguoi_kiem_tra": nk.nguoi_kiem_tra.username if nk.nguoi_kiem_tra else "",
                    "nguoi_kiem_tra_name": (nk.nguoi_kiem_tra.full_name or nk.nguoi_kiem_tra.username) if nk.nguoi_kiem_tra else "",
                    "thoi_gian_kiem_tra": nk.thoi_gian_kiem_tra.strftime('%Y-%m-%d %H:%M:%S') if nk.thoi_gian_kiem_tra else "",
                    "ghi_chu_kiem_tra": nk.ghi_chu_kiem_tra or ""
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

            # Tự động tạo tiêu chí tiêu chuẩn nếu chưa có
            existing_checklists = list(dot.danh_sach_checklist.all())
            has_tieu_chi = any(c.loai_muc == 'TieuChi' for c in existing_checklists)
            if not has_tieu_chi:
                for code, title in STANDARD_QUALITY_CRITERIA:
                    c_item = ChecklistInSao.objects.create(
                        dot_in_sao=dot,
                        ma_muc=f"{code}_{dot.ma_dot_in_sao}",
                        ten_muc=title,
                        loai_muc='TieuChi',
                        da_dat=False,
                        trang_thai='ChuaIn'
                    )
                    existing_checklists.append(c_item)

            checklist_list = []
            for item in existing_checklists:
                checklist_list.append({
                    "id": item.id,
                    "ma_muc": item.ma_muc,
                    "ten_muc": item.ten_muc,
                    "nhom_de": item.nhom_de or "",
                    "loai_muc": item.loai_muc,
                    "da_dat": item.da_dat,
                    "hoc_phan_id": item.hoc_phan.ma_hoc_phan if item.hoc_phan else "",
                    "hoc_phan_ten": item.hoc_phan.ten_hoc_phan if item.hoc_phan else "",
                    "so_luong_can_in": item.so_luong_can_in,
                    "so_luong_da_in": item.so_luong_da_in,
                    "so_luong_niem_phong": item.so_luong_niem_phong,
                    "thoi_gian_thuc_hien": item.thoi_gian_thuc_hien.strftime('%Y-%m-%d %H:%M:%S') if item.thoi_gian_thuc_hien else "",
                    "trang_thai": item.trang_thai,
                    "ghi_chu": item.ghi_chu or ""
                })

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
                "nguoi_tao_name": (dot.nguoi_tao.full_name or dot.nguoi_tao.username) if dot.nguoi_tao else "N/A",
                "ngay_tao": dot.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if dot.ngay_tao else "",
                "thoi_gian_in_sao": dot.thoi_gian_in_sao.strftime('%Y-%m-%d %H:%M:%S') if dot.thoi_gian_in_sao else "",
                "noi_in_sao": dot.noi_in_sao or "",
                "so_luong_ban_in": dot.so_luong_ban_in,
                "can_bo_giam_sat_id": dot.can_bo_giam_sat.id if dot.can_bo_giam_sat else "",
                "can_bo_giam_sat_name": (dot.can_bo_giam_sat.full_name or dot.can_bo_giam_sat.username) if dot.can_bo_giam_sat else "",
                "ghi_chu": dot.ghi_chu or "",
                "trang_thai": dot.trang_thai,
                "nhat_ky": nk_data,
                "bien_ban_giam_sat": bb_data,
                "checklist": checklist_list
            })
            
        users = [{"id": u.id, "username": u.username, "full_name": u.full_name or u.username} for u in User.objects.filter(role__in=['tkt', 'gv', 'cvht', 'ldp'])]
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

            suffix = f"_{ca_thi.ma_ca_thi}" if ca_thi else ""
            if hoc_phan:
                suffix += f"_{hoc_phan.ma_hoc_phan}"
            
            count = DotInSao.objects.filter(ky_thi=ky_thi).count() + 1
            ma_dot_in_sao = f"DIS{suffix}_{count}"

            actor_user = request.user if (request.user and request.user.is_authenticated) else User.objects.filter(role='tkt').first()

            dot = DotInSao.objects.create(
                ma_dot_in_sao=ma_dot_in_sao,
                ky_thi=ky_thi,
                ca_thi=ca_thi,
                phong_thi=phong_thi,
                hoc_phan=hoc_phan,
                nguoi_tao=actor_user,
                thoi_gian_in_sao=thoi_gian_in_sao,
                noi_in_sao=noi_in_sao,
                so_luong_ban_in=int(so_luong_ban_in),
                can_bo_giam_sat=can_bo_giam_sat,
                ghi_chu=ghi_chu,
                trang_thai='ChoCapNhat'
            )

            # 1. Tạo mục checklist Nhóm đề / Học phần
            check_ten = hoc_phan.ten_hoc_phan if hoc_phan else "Đề thi tổng hợp"
            nhom = f"Nhóm đề 1 ({hoc_phan.ma_hoc_phan})" if hoc_phan else "Nhóm đề A"
            ChecklistInSao.objects.create(
                dot_in_sao=dot,
                ma_muc=f"CK_{ma_dot_in_sao}_1",
                ten_muc=check_ten,
                nhom_de=nhom,
                hoc_phan=hoc_phan,
                loai_muc='NhomDe',
                so_luong_can_in=int(so_luong_ban_in),
                so_luong_da_in=0,
                so_luong_niem_phong=0,
                trang_thai='ChuaIn'
            )

            # 2. Khởi tạo 5 tiêu chí chất lượng in sao tiêu chuẩn
            for code, title in STANDARD_QUALITY_CRITERIA:
                ChecklistInSao.objects.create(
                    dot_in_sao=dot,
                    ma_muc=f"{code}_{ma_dot_in_sao}",
                    ten_muc=title,
                    loai_muc='TieuChi',
                    da_dat=False,
                    trang_thai='ChuaIn'
                )

            if actor_user and actor_user.is_authenticated:
                AuditLog.objects.create(
                    actor=actor_user,
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
        nhom_de_list = request.data.get('nhom_de_list', [])
        tieu_chi_checked = request.data.get('tieu_chi_checked', [])

        # Exception flow 4b: Nếu dữ liệu nhập không hợp lệ -> "Thông tin nhật ký in sao không hợp lệ"
        if not ma_dot_in_sao or not so_luong_in_thuc_te or not so_luong_niem_phong or not thoi_gian_thuc_hien:
            return Response({"error": "Thông tin nhật ký in sao không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dot = DotInSao.objects.get(ma_dot_in_sao=ma_dot_in_sao)
            
            # Đã đối chiếu hoàn tất -> Khóa không cho chỉnh sửa
            if dot.trang_thai == 'HoanTat':
                return Response({"error": "Đợt in sao này đã hoàn tất đối chiếu, không thể chỉnh sửa nhật ký."}, status=status.HTTP_400_BAD_REQUEST)

            checklists = list(dot.danh_sach_checklist.all())
            
            # Exception flow 2b: Nếu checklist chưa được tạo đầy đủ -> "Chưa có danh sách checklist để cập nhật"
            if not checklists:
                check_ten = dot.hoc_phan.ten_hoc_phan if dot.hoc_phan else "Mục in sao"
                c_item = ChecklistInSao.objects.create(
                    dot_in_sao=dot,
                    ma_muc=f"CK_{dot.ma_dot_in_sao}_1",
                    ten_muc=check_ten,
                    nhom_de=f"Nhóm đề ({dot.hoc_phan.ma_hoc_phan if dot.hoc_phan else 'A'})",
                    hoc_phan=dot.hoc_phan,
                    loai_muc='NhomDe',
                    so_luong_can_in=dot.so_luong_ban_in,
                    trang_thai='ChuaIn'
                )
                checklists = [c_item]

            nguoi_giam_sat = None
            if nguoi_giam_sat_id:
                nguoi_giam_sat = User.objects.filter(id=nguoi_giam_sat_id).first()
            if not nguoi_giam_sat:
                nguoi_giam_sat = dot.can_bo_giam_sat or request.user

            actor_user = request.user if (request.user and request.user.is_authenticated) else dot.nguoi_tao
            dt_exec = thoi_gian_thuc_hien
            
            for ck in checklists:
                if ck.loai_muc == 'NhomDe':
                    if not nhom_de_list or ck.nhom_de in nhom_de_list or ck.ten_muc in nhom_de_list:
                        ck.so_luong_da_in = int(so_luong_in_thuc_te)
                        ck.so_luong_niem_phong = int(so_luong_niem_phong)
                        ck.trang_thai = 'DaInXong'
                        ck.ghi_chu = ghi_chu
                        ck.save()
                elif ck.loai_muc == 'TieuChi':
                    # Đánh dấu tiêu chí chất lượng nếu có trong mảng tích chọn
                    is_dat = (str(ck.id) in tieu_chi_checked or ck.ma_muc in tieu_chi_checked or ck.ten_muc in tieu_chi_checked or len(tieu_chi_checked) == 0)
                    ck.da_dat = is_dat
                    ck.trang_thai = 'DaInXong' if is_dat else 'ChuaIn'
                    ck.save()

            # Tạo hoặc cập nhật nhật ký in sao
            nk, created = NhatKyInSao.objects.update_or_create(
                dot_in_sao=dot,
                defaults={
                    "thoi_gian_thuc_hien": dt_exec,
                    "nguoi_thuc_hien": actor_user,
                    "nguoi_giam_sat": nguoi_giam_sat,
                    "so_luong_in_thuc_te": int(so_luong_in_thuc_te),
                    "so_luong_niem_phong": int(so_luong_niem_phong),
                    "ghi_chu": ghi_chu
                }
            )

            dot.trang_thai = 'DaCapNhat'
            dot.save()

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

            if actor_user and actor_user.is_authenticated:
                AuditLog.objects.create(
                    actor=actor_user,
                    action=f"Cập nhật nhật ký in sao cho đợt {ma_dot_in_sao}. Số lượng thực tế: {so_luong_in_thuc_te} bản."
                )

            return Response({"message": "Nhật ký in sao được lưu đầy đủ; trạng thái checklist được cập nhật."}, status=status.HTTP_200_OK)

        except DotInSao.DoesNotExist:
            # Exception flow 8b
            return Response({"error": "Không thể lưu nhật ký in sao"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Exception flow 8b
            return Response({"error": f"Không thể lưu nhật ký in sao: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class XacNhanGiamSatAPI(APIView):
    def post(self, request):
        ma_dot_in_sao = request.data.get('ma_dot_in_sao')
        ket_qua_kiem_tra = request.data.get('ket_qua_kiem_tra') # 'Khop' hoặc 'KhongKhop'
        trang_thai_xac_nhan = request.data.get('trang_thai_xac_nhan')
        nhan_xet_giam_sat = request.data.get('nhan_xet_giam_sat', '')
        ghi_chu_kiem_tra = request.data.get('ghi_chu_kiem_tra', '') or nhan_xet_giam_sat
        chu_ky_so = request.data.get('chu_ky_so', '')

        # Exception flow 6b: Nếu người kiểm tra không có quyền -> "Bạn không có quyền kiểm tra nhật ký in sao"
        if request.user and request.user.is_authenticated:
            if hasattr(request.user, 'role') and request.user.role not in ['tkt', 'ldp', 'cvht']:
                return Response({"error": "Bạn không có quyền kiểm tra nhật ký in sao"}, status=status.HTTP_403_FORBIDDEN)

        if not ket_qua_kiem_tra:
            if trang_thai_xac_nhan == 'DaXacNhan':
                ket_qua_kiem_tra = 'Khop'
            elif trang_thai_xac_nhan == 'TuChoi':
                ket_qua_kiem_tra = 'KhongKhop'

        if not ma_dot_in_sao or not ket_qua_kiem_tra:
            return Response({"error": "Thông tin kiểm tra nhật ký in sao chưa hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dot = DotInSao.objects.get(ma_dot_in_sao=ma_dot_in_sao)
            
            # Đã đối chiếu hoàn tất -> Khóa không cho thay đổi
            if dot.trang_thai == 'HoanTat':
                return Response({"error": "Đợt in sao này đã hoàn tất đối chiếu, không thể thay đổi kết quả kiểm tra."}, status=status.HTTP_400_BAD_REQUEST)

            nk = getattr(dot, 'nhat_ky', None)
            from django.utils import timezone
            now = timezone.now()

            # Main flow 7 & 8: Đánh dấu kết quả khớp hay không khớp
            if nk:
                nk.ket_qua_kiem_tra = ket_qua_kiem_tra
                nk.nguoi_kiem_tra = request.user if (request.user and request.user.is_authenticated) else None
                nk.thoi_gian_kiem_tra = now
                nk.ghi_chu_kiem_tra = ghi_chu_kiem_tra
                nk.save()

            bb, _ = BienBanGiamSatInSao.objects.get_or_create(dot_in_sao=dot)
            bb.nguoi_xac_nhan = request.user if (request.user and request.user.is_authenticated) else None
            bb.nhan_xet_giam_sat = ghi_chu_kiem_tra
            bb.ngay_xac_nhan = now

            if ket_qua_kiem_tra == 'Khop':
                dot.trang_thai = 'HoanTat'
                bb.trang_thai = 'DaXacNhan'
                bb.chu_ky_so = chu_ky_so or "VERIFIED_OK"
            else:
                # Alt flow 8a: Nếu phát hiện sai lệch -> chuyển đợt in sao về trạng thái cần xử lý lại
                dot.trang_thai = 'CanXuLyLai'
                bb.trang_thai = 'TuChoi'
                bb.chu_ky_so = ""

            dot.save()
            bb.save()

            res_str = "khớp (Hoàn tất)" if ket_qua_kiem_tra == 'Khop' else "không khớp (Cần xử lý lại)"
            if request.user and request.user.is_authenticated:
                AuditLog.objects.create(
                    actor=request.user,
                    action=f"Người kiểm tra xác nhận kết quả in sao đợt {ma_dot_in_sao}: {res_str}."
                )

            return Response({
                "message": f"Đã lưu kết quả kiểm tra thành công: {res_str}.",
                "trang_thai": dot.trang_thai
            }, status=status.HTTP_200_OK)

        except DotInSao.DoesNotExist:
            # Exception flow 8b
            return Response({"error": "Không thể lưu nhật ký in sao"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Exception flow 8b
            return Response({"error": f"Không thể lưu nhật ký in sao: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
