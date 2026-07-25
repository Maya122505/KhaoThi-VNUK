import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from khaothi_app.models import (
    HocPhan, PhienBanCotDiem, CauHinhPhucKhao, User, GiangVien, NhanVien, Khoa,
    LopHanhChinh, SinhVien, KyThi, CaThi, LopHocPhan, LopHocPhanSinhVien,
    PhongThi, LichThi, DanhSachThiSinh, PhanCongCoiThi, BienBanViPham,
    DeThi, NopDeThi, RaSoatDeThi, DotInSao, NhatKyInSao, TuiBaiThi, TuiPhach,
    ChiTietGiaoNhan, PhieuGiaoNhan, DonPhucKhao, CauHinhDiemHocPhan, DiemThanhPhan, AuditLog,
    CauHinhThoiGianDotThi, CauHinhHeThong, QuyetToanThuLao
)
from django.utils.dateparse import parse_datetime, parse_date, parse_time
from django.db import transaction
import json
from datetime import datetime

def ensure_actor_logged_in(request, username):
    """
    Đảm bảo đúng người dùng (actor) đã đăng nhập cho view.
    Tự động đăng nhập user được chỉ định nếu cần.
    Hữu ích cho việc demo và phát triển.
    """
    from django.contrib.auth import login
    if not request.user.is_authenticated or request.user.username != username:
        user = User.objects.filter(username=username).first()
        if user:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

def index_view(request):
    """
    View cho trang chủ, điều hướng đến các portal khác nhau.
    """
    return render(request, 'khaothi_app/index.html')

def login_view(request):
    """
    View cho trang đăng nhập.
    """
    return render(request, 'khaothi_app/login.html')

def logout_view(request):
    """
    Đăng xuất người dùng và chuyển hướng về trang đăng nhập.
    """
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')

def export_pdf_view(request):
    """
    Tạo và trả về một file PDF cho một phiếu bàn giao cụ thể.
    """
    p_id = request.GET.get('id')
    if not p_id:
        return HttpResponse("Thiếu mã phiếu bàn giao", status=400)
        
    pgn = PhieuGiaoNhan.objects.select_related('nguoi_giao', 'nguoi_nhan').prefetch_related('chi_tiet__lich_thi', 'chi_tiet__tui_phach').filter(ma_phieu=p_id).first()
    if not pgn:
        return HttpResponse(f"Không tìm thấy phiếu bàn giao {p_id}", status=404)
        
    chi_tiets = pgn.chi_tiet.all()
    rooms = [ct.lich_thi for ct in chi_tiets if ct.lich_thi]
    bags = [ct.tui_phach for ct in chi_tiets if ct.tui_phach]
    
    actor_names = {
        "tkt": "Tổ Khảo thí (VNUK)",
        "tkct": "Thư ký Chấm thi",
        "ldp": "Trưởng phòng Khảo thí",
        "dvcm": "Đơn vị Chuyên môn / Giáo vụ Khoa",
        "gv": "Giảng viên / CB Chấm thi",
        "tkcoithi": "Thư ký Ban Coi thi",
        "cvht": "Chuyên viên Hệ thống"
    }
    
    sender_name = actor_names.get(pgn.nguoi_giao.role, pgn.nguoi_giao.username)
    recipient_name = actor_names.get(pgn.nguoi_nhan.role, pgn.nguoi_nhan.username)
    
    context = {
        "phieu": pgn,
        "sender_name": sender_name,
        "recipient_name": recipient_name,
        "rooms": rooms,
        "bags": bags,
    }
    return render(request, 'khaothi_app/export_pdf.html', context)


@csrf_exempt
def log_client_error(request):
    """
    API endpoint để nhận và ghi lại lỗi từ phía client.
    """
    if request.method == 'POST':
        try:
            if not request.body:
                return JsonResponse({"status": "error", "message": "Empty body"}, status=200)
            data = json.loads(request.body)
            # Ghi lỗi ra file thay vì console để tránh bị buffer
            with open(r'c:\Users\ADMIN\Downloads\KhaoThi\client_error.txt', 'a', encoding='utf-8') as f:
                f.write("=== CLIENT ERROR ===\n")
                f.write(f"Message: {data.get('message')}\n")
                f.write(f"Source: {data.get('source')}:{data.get('line')}:{data.get('col')}\n")
                f.write(f"Stack: {data.get('stack')}\n")
                f.write("========================\n")
            return JsonResponse({"status": "logged"})
        except Exception as e:
            with open(r'c:\Users\ADMIN\Downloads\KhaoThi\client_error.txt', 'a', encoding='utf-8') as f:
                f.write(f"=== CLIENT ERROR (Unparsable) ===\n")
                f.write(str(request.body) + "\n")
            return JsonResponse({"status": "error", "message": str(e)}, status=200)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)


class GetStateAPI(APIView):
    """
    API DRF đồng bộ dữ liệu động từ Django ORM CSDL cho Frontend JavaScript.
    Cung cấp đầy đủ các trường thuộc tính để hiển thị giao diện không bị undefined.
    """
    def get(self, request, *args, **kwargs):
        ky_this = list(KyThi.objects.values())
        ca_this = list(CaThi.objects.values())
        
        lich_this = []
        for l in LichThi.objects.select_related('lop_hp__hoc_phan', 'ca_thi', 'phong_thi').all():
            hp = l.lop_hp.hoc_phan if (l.lop_hp and l.lop_hp.hoc_phan) else None
            hp_code = hp.ma_hoc_phan if hp else 'SUB001'
            hp_name = hp.ten_hoc_phan if hp else 'Học phần'
            lich_this.append({
                'id': l.ma_lich_thi,
                'code': l.ma_lich_thi,
                'mon': hp_name,
                'ten_mon': hp_name,
                'ma_hp': hp_code,
                'subjectId': hp_code,
                'subjectName': hp_name,
                'ca': l.ca_thi.ten_ca if l.ca_thi else '',
                'phong': l.phong_thi.ten_phong if l.phong_thi else '',
                'sl': l.so_luong_sv,
                'papers': l.so_luong_sv,
                'trang_thai': l.trang_thai_bai_thi,
                'status': l.trang_thai_bai_thi,
            })
            
        phong_this = []
        # Chỉ trả về những phòng thi (LichThi) đã được TKT bàn giao cho TKCT
        lich_thi_da_giao = LichThi.objects.filter(
            giao_nhan_chi_tiet__phieu__loai_phieu='TKT_TO_TKCT',
            giao_nhan_chi_tiet__phieu__trang_thai='DaHoanTat'
        ).select_related('lop_hp__hoc_phan__khoa', 'phong_thi').distinct()
        for l in lich_thi_da_giao:
            hp = l.lop_hp.hoc_phan if (l.lop_hp and l.lop_hp.hoc_phan) else None
            hp_code = hp.ma_hoc_phan if hp else 'SUB001'
            hp_name = hp.ten_hoc_phan if hp else 'Học phần'
            khoa_name = hp.khoa.ten_khoa if (hp and hp.khoa) else 'CNTT'
            phong_name = l.phong_thi.ten_phong if l.phong_thi else l.ma_lich_thi
            phong_this.append({
                'id': l.ma_lich_thi,
                'ma_lich_thi': l.ma_lich_thi,
                'ma_phong': l.phong_thi.ma_phong if l.phong_thi else l.ma_lich_thi,
                'name': phong_name,
                'phong': phong_name,
                'subjectId': hp_code,
                'subjectName': hp_name,
                'mon': hp_name,
                'ten_mon': hp_name,
                'ma_hp': hp_code,
                'papers': l.so_luong_sv or 30,
                'sl': l.so_luong_sv or 30,
                'so_bai': l.so_luong_sv or 30,
                'status': 'Chưa làm phách',
                'khoa': khoa_name,
            })
            
        tui_phachs = []
        from khaothi_app.models import PhanCongChamThi
        for t in TuiPhach.objects.select_related('hoc_phan', 'nguoi_duyet_khoa', 'nguoi_duyet_diem').prefetch_related(
            'danh_sach_phach__thi_sinh__sinh_vien',
            'danh_sach_phach__thi_sinh__lich_thi__phong_thi',
            'phan_cong_cham__giang_vien'
        ).all():
            hp = t.hoc_phan
            hp_code = hp.ma_hoc_phan if hp else 'SUB001'
            hp_name = hp.ten_hoc_phan if hp else 'Học phần'
            
            phach_list = []
            phach_student_map = {}
            rooms_set = set()
            
            ma_phachs = list(t.danh_sach_phach.all())
            n = len(ma_phachs)
            import random
            # Deterministic pseudo-random seed per bag for consistent shuffled phách codes
            seed_val = sum(ord(c) for c in str(t.ma_tui))
            rng = random.Random(seed_val)
            pool = rng.sample(range(100, 1000), max(n, 1))
            
            for idx, mp in enumerate(ma_phachs):
                # Randomized 3-digit phách code (e.g. P-482, P-109, P-753) for anonymization
                phach_code = f"P-{pool[idx]:03d}"
                phach_list.append(phach_code)
                ts = mp.thi_sinh
                if ts:
                    if ts.lich_thi and ts.lich_thi.phong_thi:
                        rooms_set.add(ts.lich_thi.phong_thi.ten_phong)
                    sv_name = ts.sinh_vien.ho_ten if (ts.sinh_vien and ts.sinh_vien.ho_ten) else 'Sinh viên'
                    sbd_code = ts.sbd or f"SBD-{(idx + 1):03d}"
                    phach_student_map[phach_code] = {
                        'sbd': sbd_code,
                        'name': sv_name
                    }
            
            rooms = list(rooms_set)
            if not rooms:
                rooms = list(LichThi.objects.filter(lop_hp__hoc_phan=hp).values_list('phong_thi__ten_phong', flat=True)[:1])
                if not rooms:
                    rooms = ['Phòng 101']
            
            so_bai = len(phach_list) if phach_list else (t.so_luong_bai or 30)

            status_ui = 'Đã tạo phách'
            if t.trang_thai in ['DaKhopDiem', 'DaDoiChieu', 'ChoKhopDiem']:
                status_ui = 'Đã đối chiếu hợp lệ'
            elif t.trang_thai in ['KhoaDaPheDuyet']:
                status_ui = 'Khoa đã phê duyệt'
            elif t.trang_thai in ['DaDuyet', 'DaDuyetBangDiem']:
                status_ui = 'Đã duyệt bảng điểm'
            elif t.trang_thai in ['DaTraVeTKT', 'DaKhoa']:
                status_ui = 'Đã khóa phách'

            # Lấy grader thực tế từ PhanCongChamThi
            phan_congs = list(t.phan_cong_cham.filter(loai_phan_cong='ChamChinh').select_related('giang_vien'))
            grader1_str = 'GV001 - Nguyễn Văn A'
            grader2_str = 'GV002 - Trần Thị B'
            if len(phan_congs) >= 1:
                gv1 = phan_congs[0].giang_vien
                grader1_str = f"{gv1.ma_giang_vien} - {gv1.ho_ten}"
            if len(phan_congs) >= 2:
                gv2 = phan_congs[1].giang_vien
                grader2_str = f"{gv2.ma_giang_vien} - {gv2.ho_ten}"

            tui_phachs.append({
                'id': t.ma_tui,
                'ma_tui': t.ma_tui,
                'subjectId': hp_code,
                'subjectName': hp_name,
                'mon': hp_name,
                'ten_mon': hp_name,
                'papers': so_bai,
                'so_bai': so_bai,
                'rooms': rooms,
                'phachGoc': phach_list,
                'phachStudentMap': phach_student_map,
                'password': f"VNUK@{hp_code}_{t.pk}",
                'status': status_ui,
                'trang_thai': t.trang_thai,
                'grader1': grader1_str,
                'grader2': grader2_str,
                # Audit fields mới
                'nguoi_duyet_khoa': t.nguoi_duyet_khoa.full_name if t.nguoi_duyet_khoa else None,
                'ngay_duyet_khoa': str(t.ngay_duyet_khoa) if t.ngay_duyet_khoa else None,
                'nguoi_duyet_diem': t.nguoi_duyet_diem.full_name if t.nguoi_duyet_diem else None,
                'ngay_duyet_diem': str(t.ngay_duyet_diem) if t.ngay_duyet_diem else None,
                'created_at': str(t.created_at) if t.created_at else None,
            })
            
        phieu_giao_nhan = []
        for p in PhieuGiaoNhan.objects.select_related('nguoi_giao', 'nguoi_nhan').prefetch_related('chi_tiet').all():
            sender_role = p.nguoi_giao.role if (p.nguoi_giao and hasattr(p.nguoi_giao, 'role') and p.nguoi_giao.role) else (p.nguoi_giao.username if p.nguoi_giao else '')
            receiver_role = p.nguoi_nhan.role if (p.nguoi_nhan and hasattr(p.nguoi_nhan, 'role') and p.nguoi_nhan.role) else (p.nguoi_nhan.username if p.nguoi_nhan else '')
            phieu_giao_nhan.append({
                'id': p.ma_phieu,
                'ma_phieu': p.ma_phieu,
                'sender': sender_role,
                'sender_name': p.nguoi_giao.full_name if p.nguoi_giao else 'Bên giao',
                'receiver': receiver_role,
                'recipient': receiver_role,
                'receiver_name': p.nguoi_nhan.full_name if p.nguoi_nhan else 'Bên nhận',
                'recipient_name': p.nguoi_nhan.full_name if p.nguoi_nhan else 'Bên nhận',
                'flow': f"{p.nguoi_giao.full_name if p.nguoi_giao else 'Bên giao'} ➔ {p.nguoi_nhan.full_name if p.nguoi_nhan else 'Bên nhận'}",
                'qty': p.chi_tiet.count() or 1,
                'status': 'Chờ bạn xác nhận' if p.trang_thai == 'ChoXacNhan' else 'Đã hoàn tất',
                'trang_thai': p.trang_thai,
                'date': str(p.ngay_giao),
                'rejectReason': '',
            })
            
        can_bo_coi_thi = []
        for pc in PhanCongCoiThi.objects.select_related('can_bo__khoa').all():
            can_bo_coi_thi.append({
                'id': pc.can_bo.ma_giang_vien,
                'name': pc.can_bo.ho_ten,
                'ho_ten': pc.can_bo.ho_ten,
                'khoa': pc.can_bo.khoa.ten_khoa if pc.can_bo.khoa else '',
                'vai_tro': pc.vai_tro,
                'actual_hours': float(pc.actual_hours),
                'is_confirmed': pc.is_confirmed,
            })

        phuc_khao = []
        for pk in DonPhucKhao.objects.select_related('sinh_vien', 'hoc_phan').all():
            phuc_khao.append({
                'id': pk.ma_don,
                'ma_don': pk.ma_don,
                'studentName': pk.sinh_vien.ho_ten if pk.sinh_vien else '',
                'sinh_vien': pk.sinh_vien.ho_ten if pk.sinh_vien else '',
                'subjectName': pk.hoc_phan.ten_hoc_phan if pk.hoc_phan else '',
                'mon': pk.hoc_phan.ten_hoc_phan if pk.hoc_phan else '',
                'status': pk.trang_thai,
            })

        hoc_phans = list(HocPhan.objects.values())

        system_configs = {'nhapDiem': {}, 'phucKhao': {}}
        for ch in CauHinhThoiGianDotThi.objects.all():
            key = f"{ch.nam_hoc}_{ch.hoc_ky}_{ch.dot_thi}"
            # Lấy toàn bộ cấu hình mới
            system_configs['nhapDiem'][key] = {
                'start': ch.tg_bat_dau_nhap.strftime('%Y-%m-%dT%H:%M') if ch.tg_bat_dau_nhap else '',
                'end': ch.tg_khoa_cong_nhap.strftime('%Y-%m-%dT%H:%M') if ch.tg_khoa_cong_nhap else '',
                'publish': ch.tg_cong_bo_diem.strftime('%Y-%m-%dT%H:%M') if ch.tg_cong_bo_diem else '',
                'nop_de': ch.tg_nop_de_thi.strftime('%Y-%m-%dT%H:%M') if ch.tg_nop_de_thi else '',
                'nhap_tp': ch.tg_nhap_diem_tp.strftime('%Y-%m-%dT%H:%M') if ch.tg_nhap_diem_tp else '',
                'trong_so': ch.tg_cau_hinh_trong_so.strftime('%Y-%m-%dT%H:%M') if ch.tg_cau_hinh_trong_so else '',
                'dieu_kien': ch.tg_chot_dieu_kien_thi.strftime('%Y-%m-%dT%H:%M') if ch.tg_chot_dieu_kien_thi else '',
                'quy_doi': ch.tg_chot_quy_doi.strftime('%Y-%m-%dT%H:%M') if ch.tg_chot_quy_doi else '',
            }
            system_configs['phucKhao'][key] = {
                'start': ch.tg_mo_nhan_don_pk.strftime('%Y-%m-%dT%H:%M') if ch.tg_mo_nhan_don_pk else '',
                'end': ch.tg_khoa_nhan_don_pk.strftime('%Y-%m-%dT%H:%M') if ch.tg_khoa_nhan_don_pk else '',
                'deadline': ch.han_chot_cham_pk.strftime('%Y-%m-%dT%H:%M') if ch.han_chot_cham_pk else '',
            }
        
        system_globals = {}
        for config in CauHinhHeThong.objects.all():
            system_globals[config.key] = config.value

        logs = []
        for log in AuditLog.objects.select_related('actor').order_by('-timestamp')[:50]:
            logs.append({
                'id': log.id,
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'actor': log.actor.username,
                'actor_name': log.actor.full_name or log.actor.username,
                'action': log.action,
                'ip': log.ip_address
            })

        data = {
            'kyThiData': ky_this,
            'caThiData': ca_this,
            'lichThiData': lich_this,
            'hocPhiData': hoc_phans,
            'lopThiDiemData': [],
            'phongThiGocData': phong_this,
            'tuiPhachData': tui_phachs,
            'phieuGiaoNhanData': phieu_giao_nhan,
            'canBoCoiThiData': can_bo_coi_thi,
            'phucKhaoData': phuc_khao,
            'systemConfigsData': system_configs,
            'systemGlobals': system_globals,
            'auditLogs': logs
        }
        return Response(data, status=status.HTTP_200_OK)


from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class SaveStateAPI(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, *args, **kwargs):
        return Response({'status': 'success', 'message': 'Deprecated. Use specific APIs.'}, status=status.HTTP_200_OK)
