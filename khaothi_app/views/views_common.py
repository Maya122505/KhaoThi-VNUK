from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from khaothi_app.models import (
    AppState, HocPhan, PhienBanCotDiem, CauHinhPhucKhao, User, GiangVien, NhanVien, Khoa,
    LopHanhChinh, SinhVien, KyThi, CaThi, LopHocPhan, LopHocPhanSinhVien,
    PhongThi, LichThi, DanhSachThiSinh, PhanCongCoiThi, BienBanViPham,
    DeThi, NopDeThi, RaSoatDeThi, DotInSao, NhatKyInSao, BienBanGiamSatInSao, TuiBaiThi, TuiPhach,
    MaPhach, DiemThi, DoiSoatDiem, PhanCongChamThi, PhieuGiaoNhan,
    ChiTietGiaoNhan, DonPhucKhao, CauHinhDiemHocPhan, DiemThanhPhan, AuditLog
)
from django.utils.dateparse import parse_datetime, parse_date, parse_time
from django.db import transaction
import json
from datetime import datetime

def ensure_actor_logged_in(request, username):
    from django.contrib.auth import login
    from khaothi_app.models import User
    if not request.user.is_authenticated or request.user.username != username:
        user = User.objects.filter(username=username).first()
        if not user:
            role_map = {
                'ldp': ('ldp', 'Lãnh đạo phòng Khảo thí', 'ldp'),
                'tkt': ('tkt', 'Cán bộ Tổ Khảo thí', 'tkt'),
                'tkct': ('tkct', 'Thư ký Chấm thi', 'tkct'),
                'dvcm': ('dvcm', 'Đơn vị Chuyên môn', 'dvcm'),
                'cvht': ('cvht', 'Cố vấn Học tập', 'cvht'),
                'GV001': ('GV001', 'TS. Nguyễn Văn A', 'gv'),
            }
            u_info = role_map.get(username, (username, username, 'tkt'))
            user = User.objects.create_user(
                username=u_info[0],
                full_name=u_info[1],
                role=u_info[2]
            )
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)


def safe_parse_date(date_str):
    """
    Hàm hỗ trợ ép kiểu ngày tháng an toàn từ nhiều định dạng khác nhau (DD/MM/YYYY, YYYY-MM-DD, etc.)
    Tránh ném lỗi ValueError hoặc trả về None làm hủy giao dịch lưu dữ liệu xuống cơ sở dữ liệu.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = date_str.strip()
    if not date_str:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    try:
        return parse_date(date_str)
    except Exception:
        return None


# Extended Mock Data for Seeding - Dynamically generated to have at least 50 entries
SUBJECTS_LIST = [
    ("ECO101", "Kinh tế vi mô"),
    ("PHI101", "Triết học Mác-Lênin"),
    ("MAT101", "Toán cao cấp"),
    ("MKT205", "Marketing căn bản"),
    ("CSE202", "Cơ sở dữ liệu"),
    ("CSE105", "Thiết kế Web"),
    ("LAW101", "Pháp luật đại cương"),
    ("BUS101", "Quản trị học"),
    ("ENG101", "Tiếng Anh GTQT 3"),
    ("ACC101", "Nguyên lý kế toán"),
    ("HIS101", "Lịch sử Đảng Cộng sản Việt Nam"),
    ("HCM101", "Tư tưởng Hồ Chí Minh"),
    ("PHY101", "Vật lý đại cương"),
    ("PHI102", "Kinh tế chính trị Mác-Lênin"),
    ("HIS102", "Đường lối cách mạng của Đảng Cộng sản Việt Nam"),
    ("PHI103", "Chủ nghĩa xã hội khoa học"),
    ("MAT102", "Đại số tuyến tính"),
    ("MAT103", "Xác suất thống kê"),
    ("GEO101", "Địa lý kinh tế"),
]

DEPARTMENTS = ["Công nghệ thông tin", "Quản trị kinh doanh", "Khoa học xã hội", "Ngôn ngữ Anh", "Khoa học Y sinh", "Khoa học Dữ liệu"]
LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
MIDDLE_NAMES = ["Văn", "Thị", "Minh", "Thanh", "Hoàng", "Ngọc", "Đức", "Hữu", "Anh", "Xuân", "Thu", "Hải", "Tuấn", "Quang"]
FIRST_NAMES = ["Hùng", "Lan", "Nam", "Hòa", "Hồng", "Tuấn", "Anh", "Bình", "Cường", "Trang", "Vy", "Linh", "Duy", "Sơn", "Tùng", "Yến", "Quyên", "Khánh"]

def generate_name(i):
    last = LAST_NAMES[i % len(LAST_NAMES)]
    mid = MIDDLE_NAMES[(i * 3) % len(MIDDLE_NAMES)]
    first = FIRST_NAMES[(i * 7) % len(FIRST_NAMES)]
    return f"{last} {mid} {first}"

# 1. Generate INITIAL_PHONG_THI_GOC (54 entries)
INITIAL_PHONG_THI_GOC = []
for i in range(1, 55):
    sub_code, sub_name = SUBJECTS_LIST[i % len(SUBJECTS_LIST)]
    status = "Chưa nhận bài"
    if i <= 10:
        status = "Đã ráp phách"
    elif i <= 20:
        status = "Đang chấm"
    elif i <= 30:
        status = "Đã nhập điểm"
    elif i <= 45:
        status = "Chưa làm phách"
    else:
        status = "Chưa nhận bài"
    
    INITIAL_PHONG_THI_GOC.append({
        "id": f"LHP-{i:03d}",
        "subjectId": sub_code,
        "subjectName": f"{sub_name} ({sub_code})",
        "papers": 30 + (i * 3) % 25,
        "status": status
    })

# 2. Generate INITIAL_CAN_BO_COI_THI (55 entries)
INITIAL_CAN_BO_COI_THI = []
for i in range(1, 56):
    dept = DEPARTMENTS[i % len(DEPARTMENTS)]
    sub_code1, sub_name1 = SUBJECTS_LIST[(i) % len(SUBJECTS_LIST)]
    sub_code2, sub_name2 = SUBJECTS_LIST[(i + 3) % len(SUBJECTS_LIST)]
    
    INITIAL_CAN_BO_COI_THI.append({
        "code": f"GV{i:03d}",
        "name": generate_name(i),
        "donVi": dept,
        "pricePerHour": 100000,
        "history": [
            { "date": "2026-07-15", "shift": "Ca 1 (07:30 - 09:30)", "subject": f"{sub_name1} ({sub_code1})", "room": f"P.{(100 + i % 10)}", "hours": 2, "role": "Coi thi 1", "confirmed": (i % 3 != 0) },
            { "date": "2026-07-17", "shift": "Ca 3 (13:30 - 15:30)", "subject": f"{sub_name2} ({sub_code2})", "room": f"P.{(200 + i % 10)}", "hours": 2, "role": "Coi thi 2", "confirmed": (i % 2 == 0) }
        ]
    })

# 3. Generate INITIAL_TUI_PHACH (52 entries)
INITIAL_TUI_PHACH = []
for i in range(1, 53):
    sub_code, sub_name = SUBJECTS_LIST[i % len(SUBJECTS_LIST)]
    papers = 30 + (i * 3) % 25
    phach_list = [f"PH{i:02d}{k:02d}" for k in range(1, papers + 1)]
    room_id = f"LHP-{i:03d}"
    
    scores_dict = {}
    status = "Đã khóa phách"
    if i <= 10:
        status = "Đã đối chiếu hợp lệ"
    elif i <= 25:
        status = "Đang chấm"
    elif i <= 40:
        status = "Chờ khớp điểm"
        for p in phach_list:
            scores_dict[p] = { "grader1": round(4.0 + (int(p[-2:]) * 0.15) % 6.0, 1), "grader2": round(4.0 + (int(p[-2:]) * 0.15) % 6.0, 1) }
            
    INITIAL_TUI_PHACH.append({
        "id": f"TP-{sub_code}-{i:03d}",
        "subjectId": sub_code,
        "subjectName": sub_name,
        "papers": papers,
        "rooms": [room_id],
        "status": status,
        "password": f"VNUK@{sub_code}_{i}12",
        "phachGoc": phach_list,
        "roomPhachMap": { room_id: phach_list },
        "grader1": f"GV{(i % 50) + 1:03d}",
        "grader2": f"GV{((i + 5) % 50) + 1:03d}",
        "scores": scores_dict
    })

# 4. Generate INITIAL_PHIEU_GIAO_NHAN (51 entries)
INITIAL_PHIEU_GIAO_NHAN = []
for i in range(1, 52):
    attachments = ["bien_ban_kiem_dem.pdf"]
    log = ""
    
    if i % 3 == 0:
        p_type = "Khảo thí bàn giao bài thi gốc cho Thư ký chấm thi (Loại 1)"
        flow = "Tổ Khảo thí ➔ Thư ký Chấm thi"
        sender = "tkt"
        recipient = "tkct"
        status = "Chờ bạn xác nhận" if i > 30 else "Đã hoàn tất"
        rooms = [f"LHP-{i:03d}"]
        bags = None
        qty = "1 phòng"
        if status == "Đã hoàn tất":
            log = "Đã ký số niêm phong nhận bài gốc thành công bởi Thư ký Chấm thi vào 2026-07-12 10:00:00"
    elif i % 3 == 1:
        p_type = "Giáo vụ bàn giao túi phách cho Giảng viên chấm thi (Loại 2)"
        flow = "Đơn vị Chuyên môn ➔ Giảng viên"
        sender = "dvcm"
        recipient = "gv"
        status = "Chờ bạn xác nhận" if i > 30 else "Đã hoàn tất"
        rooms = None
        sub_code, _ = SUBJECTS_LIST[i % len(SUBJECTS_LIST)]
        bags = [f"TP-{sub_code}-{i:03d}"]
        qty = "1 túi"
        if status == "Đã hoàn tất":
            log = f"Đã đóng con dấu điện tử bởi Giảng viên GV{(i % 50) + 1:03d} vào 2026-07-12 11:30:00"
    else:
        rooms = None
        sub_code, _ = SUBJECTS_LIST[i % len(SUBJECTS_LIST)]
        bags = [f"TP-{sub_code}-{i:03d}"]
        qty = "1 túi"
        if i % 9 == 2:
            p_type = "Giảng viên trả bài đã chấm cho Giáo vụ (Loại 1)"
            flow = "Giảng viên ➔ Đơn vị Chuyên môn"
            sender = "gv"
            recipient = "dvcm"
            status = "Chờ bạn xác nhận" if i > 30 else "Đã hoàn tất"
            if status == "Đã hoàn tất":
                log = "Đã tiếp nhận bài chấm bởi Giáo vụ ĐVCM vào 2026-07-12 14:00:00"
        elif i % 9 == 5:
            p_type = "Giáo vụ trả bài đã chấm về Tổ khảo thí để lưu trữ (Loại 2)"
            flow = "Đơn vị Chuyên môn ➔ Tổ Khảo thí"
            sender = "dvcm"
            recipient = "tkt"
            status = "Chờ bạn xác nhận" if i > 30 else "Đã hoàn tất"
            if status == "Đã hoàn tất":
                log = "Đã hoàn tất lưu trữ cất giữ bởi Tổ Khảo thí vào 2026-07-12 15:00:00"
        else:
            p_type = "Thư ký chấm thi trả túi bài thi về Tổ khảo thí (Loại 3)"
            flow = "Thư ký Chấm thi ➔ Tổ Khảo thí"
            sender = "tkct"
            recipient = "tkt"
            status = "Chờ bạn xác nhận" if i > 30 else "Đã hoàn tất"
            if status == "Đã hoàn tất":
                log = "Đã hoàn tất cất trữ túi bài thi bởi Tổ Khảo thí vào 2026-07-12 16:30:00"

    INITIAL_PHIEU_GIAO_NHAN.append({
        "id": f"PBG-2026-{i:03d}",
        "type": p_type,
        "flow": flow,
        "qty": qty,
        "status": status,
        "rooms": rooms,
        "bags": bags,
        "sender": sender,
        "recipient": recipient,
        "attachments": attachments,
        "log": log
    })

# 5. Generate INITIAL_PHUC_KHAO (50 entries)
INITIAL_PHUC_KHAO = []
for i in range(1, 51):
    sub_code, sub_name = SUBJECTS_LIST[i % len(SUBJECTS_LIST)]
    original_score = round(3.5 + (i * 0.25) % 5.0, 1)
    status = "Chờ xử lý"
    pt2 = None
    ptFinal = None
    file = ""
    
    if i % 2 == 0:
        status = "Đã xử lý"
        pt2 = original_score + 0.5 if original_score < 9.0 else original_score
        ptFinal = pt2
        file = f"bien_ban_phuc_khao_{sub_code.lower()}_{i}.pdf"

    INITIAL_PHUC_KHAO.append({
        "id": f"PK-{i:03d}",
        "phach": f"PH{i:04d}",
        "subjectName": f"{sub_name} ({sub_code})",
        "pt1": original_score,
        "pt2": pt2,
        "ptFinal": ptFinal,
        "originalPt1": original_score,
        "msv": f"SV{i:03d}",
        "name": generate_name(i + 100),
        "status": status,
        "file": file
    })

INITIAL_AUDIT_LOGS = [
    { "time": "2026-07-10 08:00:00", "actor": "Hệ thống", "action": "Khởi tạo thành công cơ sở dữ liệu học phần học kỳ II." },
    { "time": "2026-07-10 08:30:00", "actor": "Chuyên viên HT", "action": "Cập nhật danh sách 8 phòng thi chuẩn bị cho kỳ thi kết thúc học phần." },
    { "time": "2026-07-10 09:00:00", "actor": "Lãnh đạo phòng", "action": "Phê duyệt kế hoạch tổ chức thi học kỳ II năm học 2025-2026." },
    { "time": "2026-07-10 10:15:00", "actor": "Tổ Khảo thí", "action": "Tạo kỳ thi học kỳ K25 (KYTHI-HK2-K25)." },
    { "time": "2026-07-10 14:00:00", "actor": "Giảng viên", "action": "GV001 nộp đề thi chính thức học phần Kinh tế vi mô (ECO101) mã đề DE-ECO101-01." },
    { "time": "2026-07-10 14:30:00", "actor": "Giảng viên", "action": "GV002 nộp đề thi dự phòng học phần Marketing căn bản (MKT205) mã đề DE-MKT205-02." },
    { "time": "2026-07-10 15:00:00", "actor": "Tổ Khảo thí", "action": "Thực hiện rà soát chất lượng đề thi học phần Kinh tế vi mô (ECO101) - Đạt chuẩn." },
    { "time": "2026-07-11 08:00:00", "actor": "Tổ Khảo thí", "action": "Tạo đợt in sao đề thi DOTIN-001 phục vụ ca thi ngày 15/07/2026." },
    { "time": "2026-07-11 09:30:00", "actor": "Thư ký Coi thi", "action": "Nhật ký in sao ca sáng hoàn tất, số lượng bản in: 45 bản." },
    { "time": "2026-07-11 11:00:00", "actor": "Thư ký Coi thi", "action": "Lập biên bản giám sát in sao đề thi mã đợt DOTIN-001 - An toàn, bảo mật." },
    { "time": "2026-07-11 14:00:00", "actor": "Tổ Khảo thí", "action": "Cập nhật lịch thi chính thức lên bảng tin điện tử VNUK." },
    { "time": "2026-07-11 15:30:00", "actor": "Tổ Khảo thí", "action": "Phân công cán bộ coi thi ca 1 và ca 2 ngày 15/07/2026." },
    { "time": "2026-07-12 08:30:00", "actor": "Hệ thống", "action": "Đồng bộ danh sách 250 sinh viên đủ điều kiện dự thi từ cổng đào tạo." },
    { "time": "2026-07-12 09:15:12", "actor": "Tổ Khảo thí", "action": "Lập phiếu bàn giao gốc PBG-2026-001 gửi Thư ký làm phách." },
    { "time": "2026-07-12 09:45:00", "actor": "Tổ Khảo thí", "action": "Tạo túi phách TP-MKT205-001 và lập phiếu bàn giao cho Khoa (PBG-2026-002)." },
    { "time": "2026-07-12 10:02:15", "actor": "Đơn vị Chuyên môn", "action": "Giáo vụ Khoa QTKD ký xác nhận nhận phiếu bàn giao túi phách PBG-2026-002." },
    { "time": "2026-07-12 10:20:30", "actor": "Đơn vị Chuyên môn", "action": "Phân công Giám khảo 1 (GV002) và Giám khảo 2 (GV005) chấm túi phách TP-MKT205-001." },
    { "time": "2026-07-12 11:45:10", "actor": "Giảng viên", "action": "Giảng viên GV002 ký xác nhận nộp bảng điểm chấm thi cho túi TP-MKT205-001." },
    { "time": "2026-07-12 13:10:00", "actor": "Đơn vị Chuyên môn", "action": "Lập phiếu trả điểm PTD-2026-003 trả về Tổ Khảo thí." },
    { "time": "2026-07-12 14:30:45", "actor": "Tổ Khảo thí", "action": "Ký tiếp nhận điểm và lưu kho phiếu trả điểm PTD-2026-003." },
    { "time": "2026-07-12 15:12:00", "actor": "Thư ký Coi thi", "action": "Xác nhận phòng thi LHP-004 đã thi xong sỹ số 42 bài." },
    { "time": "2026-07-15 07:30:00", "actor": "Thư ký Coi thi", "action": "Điểm danh cán bộ coi thi ca 1 tại văn phòng Khảo thí." },
    { "time": "2026-07-15 08:00:00", "actor": "Cán bộ Coi thi", "action": "Cán bộ coi thi GV001 phát đề thi học phần Kinh tế vi mô tại phòng P.101." },
    { "time": "2026-07-15 09:30:00", "actor": "Cán bộ Coi thi", "action": "Lập biên bản vi phạm quy chế thi đối với sinh viên SV008 tại phòng P.101 - Cảnh cáo." },
    { "time": "2026-07-15 10:00:00", "actor": "Thư ký Coi thi", "action": "Tiếp nhận 2 túi bài thi từ phòng thi P.101 bàn giao về phòng bảo mật." },
    { "time": "2026-07-15 11:30:00", "actor": "Tổ Khảo thí", "action": "Thực hiện cắt phách và đánh mã phách tự động cho túi bài thi LHP-001." },
    { "time": "2026-07-15 14:00:00", "actor": "Giảng viên", "action": "GV003 đăng nhập hệ thống yêu cầu mở quyền chấm thi học phần ECO101." },
    { "time": "2026-07-16 08:30:00", "actor": "Tổ Khảo thí", "action": "Giao túi phách TP-ECO101-001 cho Giám khảo 1 (GV003) chấm độc lập lần 1." },
    { "time": "2026-07-16 10:00:00", "actor": "Giảng viên", "action": "GV003 chấm xong túi phách TP-ECO101-001, nhập điểm thô lên hệ thống." },
    { "time": "2026-07-16 14:00:00", "actor": "Tổ Khảo thí", "action": "Giao túi phách TP-ECO101-001 cho Giám khảo 2 (GV004) chấm độc lập lần 2." },
    { "time": "2026-07-16 16:30:00", "actor": "Giảng viên", "action": "GV004 chấm xong túi phách TP-ECO101-001, hoàn thành nhập điểm lần 2." },
    { "time": "2026-07-17 09:00:00", "actor": "Tổ Khảo thí", "action": "Hệ thống tự động đối soát điểm thi túi TP-ECO101-001: 2 bản điểm trùng khớp 100%." }
]

INITIAL_SYSTEM_CONFIGS = {
    "nhapDiem": {
        "ECO101": { "start": "2026-07-15T08:00", "end": "2026-07-22T17:00", "publish": "2026-07-25T09:00" },
        "PHI101": { "start": "2026-07-16T08:00", "end": "2026-07-23T17:00", "publish": "2026-07-26T09:00" }
    },
    "phucKhao": {
        "ECO101": { "start": "2026-07-25T09:00", "end": "2026-07-30T17:00", "deadline": "2026-08-05T17:00" },
        "PHI101": { "start": "2026-07-26T09:00", "end": "2026-07-31T17:00", "deadline": "2026-08-06T17:00" }
    },
    "phanCongPhongData": [
        {"id": "PC001", "ltId": "LT-ENG101", "subjectName": "Tiếng Anh GTQT 3", "date": "15/08/2026", "caThi": "Ca 1 (07:30 - 09:30)", "soLuong": 120, "roomNames": "P.101, P.102"},
        {"id": "PC002", "ltId": "LT-BUS201", "subjectName": "Quản trị dự án", "date": "16/08/2026", "caThi": "Ca 2 (09:45 - 11:45)", "soLuong": 90, "roomNames": "P.201, P.202"},
        {"id": "PC003", "ltId": "LT-CS101", "subjectName": "Nhập môn Lập trình", "date": "17/08/2026", "caThi": "Ca 3 (13:00 - 15:00)", "soLuong": 60, "roomNames": "P.301"}
    ]
}

INITIAL_KY_THI = [
    { "id": "KT-HK3-2026", "name": "Thi cuối kỳ học kỳ III", "year": "2025-2026", "semester": "Học kỳ III", "duration": "10/07/2026 - 20/07/2026", "dot": "Đợt 1", "mota": "Đợt thi kết thúc kỳ học hè.", "shiftsCount": 2 }
]

INITIAL_CA_THI = [
    { "id": "CT-001", "kyThiId": "KT-HK3-2026", "name": "Ca 1", "date": "2026-07-12", "start": "07:30", "end": "09:30", "note": "Thi viết tự luận" },
    { "id": "CT-002", "kyThiId": "KT-HK3-2026", "name": "Ca 2", "date": "2026-07-12", "start": "10:00", "end": "12:00", "note": "Thi viết tự luận" },
    { "id": "CT-003", "kyThiId": "KT-HK3-2026", "name": "Ca 1", "date": "2026-07-13", "start": "07:30", "end": "09:30", "note": "Thi trắc nghiệm máy" },
    { "id": "CT-004", "kyThiId": "KT-HK3-2026", "name": "Ca 2", "date": "2026-07-13", "start": "10:00", "end": "12:00", "note": "Thi trắc nghiệm máy" },
    { "id": "CT-005", "kyThiId": "KT-HK3-2026", "name": "Ca 1", "date": "2026-07-14", "start": "07:30", "end": "09:30", "note": "Thi viết tự luận" },
    { "id": "CT-006", "kyThiId": "KT-HK3-2026", "name": "Ca 2", "date": "2026-07-14", "start": "10:00", "end": "12:00", "note": "Thi viết tự luận" },
    { "id": "CT-007", "kyThiId": "KT-HK3-2026", "name": "Ca 1", "date": "2026-07-15", "start": "07:30", "end": "09:30", "note": "Thi trắc nghiệm máy" },
    { "id": "CT-008", "kyThiId": "KT-HK3-2026", "name": "Ca 2", "date": "2026-07-15", "start": "10:00", "end": "12:00", "note": "Thi trắc nghiệm máy" },
    { "id": "CT-009", "kyThiId": "KT-HK3-2026", "name": "Ca 1", "date": "2026-07-16", "start": "07:30", "end": "09:30", "note": "Thi viết tự luận" },
    { "id": "CT-010", "kyThiId": "KT-HK3-2026", "name": "Ca 2", "date": "2026-07-16", "start": "10:00", "end": "12:00", "note": "Thi viết tự luận" }
]

INITIAL_LICH_THI = [
    { "subjectName": "Tiếng Anh GTQT 3", "date": "2026-07-12", "shiftName": "Ca 1", "room": "P.101", "teacher": "Nguyễn Văn A" },
    { "subjectName": "Quản trị dự án", "date": "2026-07-12", "shiftName": "Ca 2", "room": "P.102", "teacher": "Trần Thị B" }
]

def get_initial_hoc_phi():
    last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
    mid_names = ["Văn", "Thị", "Hữu", "Đức", "Minh", "Quang", "Anh", "Hoài", "Khánh", "Ngọc", "Thu", "Phương", "Kim", "Thanh", "Bảo"]
    first_names = ["An", "Bình", "Cường", "Dũng", "Em", "Giang", "Hương", "Khanh", "Linh", "Minh", "Nam", "Oanh", "Phong", "Quân", "Sơn", "Trang", "Uyên", "Vy", "Yến", "Tùng", "Chi", "Đạt", "Hải", "Phương", "Lan", "Như"]
    
    classes = ["24CS01", "24CS02", "24ENG01", "24ENG02", "24BUS01", "24BUS02"]
    subjects = ["PHI101", "MAT101", "ENG101", "ECO101", "HIS101", "HCM101", "PHY101", "MAT103"]
    
    students = []
    import random
    rng = random.Random(42)
    
    for i in range(1, 101):
        msv = f"SV24{i:04d}"
        ln = rng.choice(last_names)
        mn = rng.choice(mid_names)
        fn = rng.choice(first_names)
        name = f"{ln} {mn} {fn}"
        cls = rng.choice(classes)
        sub = rng.choice(subjects)
        
        # Exactly 10 students will have a debt
        if i % 10 == 0:
            debt = rng.choice([1500000, 2000000, 2500000, 3000000, 3500000])
        else:
            debt = 0
            
        students.append({
            "msv": msv,
            "name": name,
            "class": cls,
            "subject": sub,
            "debt": debt
        })
    return students

INITIAL_HOC_PHI = get_initial_hoc_phi()

INITIAL_LOP_THI_DIEM = {
    "LOP-ENG101-01": [
        { "sbd": "SBD-001", "name": "Lê Văn Tám", "pt1": 7.5, "pt2": None, "ptFinal": None, "originalPt1": 7.5 },
        { "sbd": "SBD-002", "name": "Trần Thị Lan", "pt1": 6.0, "pt2": None, "ptFinal": None, "originalPt1": 6.0 },
        { "sbd": "SBD-003", "name": "Nguyễn Văn Hùng", "pt1": 8.5, "pt2": None, "ptFinal": None, "originalPt1": 8.5 },
        { "sbd": "SBD-004", "name": "Ngô Văn Khải", "pt1": 5.0, "pt2": None, "ptFinal": None, "originalPt1": 5.0 }
    ]
}

def index_view(request):
    return render(request, 'khaothi_app/index.html')

def login_view(request):
    return render(request, 'khaothi_app/login.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('index')



@transaction.atomic
def seed_database_relational():
    """
    Xóa dữ liệu cũ và gieo dữ liệu thực tế vào các bảng quan hệ SQLite.
    """
    state, _ = AppState.objects.get_or_create(key="global_state")
    state.system_configs = json.dumps(INITIAL_SYSTEM_CONFIGS)
    state.save()

    # Xóa sạch
    AuditLog.objects.all().delete()
    DonPhucKhao.objects.all().delete()
    ChiTietGiaoNhan.objects.all().delete()
    PhieuGiaoNhan.objects.all().delete()
    PhanCongChamThi.objects.all().delete()
    DoiSoatDiem.objects.all().delete()
    DiemThi.objects.all().delete()
    MaPhach.objects.all().delete()
    TuiPhach.objects.all().delete()
    TuiBaiThi.objects.all().delete()
    NhatKyInSao.objects.all().delete()
    DotInSao.objects.all().delete()
    RaSoatDeThi.objects.all().delete()
    NopDeThi.objects.all().delete()
    DeThi.objects.all().delete()
    BienBanViPham.objects.all().delete()
    PhanCongCoiThi.objects.all().delete()
    DanhSachThiSinh.objects.all().delete()
    LichThi.objects.all().delete()
    PhongThi.objects.all().delete()
    CaThi.objects.all().delete()
    LopHocPhanSinhVien.objects.all().delete()
    LopHocPhan.objects.all().delete()
    HocPhan.objects.all().delete()
    KyThi.objects.all().delete()
    SinhVien.objects.all().delete()
    LopHanhChinh.objects.all().delete()
    GiangVien.objects.all().delete()
    NhanVien.objects.all().delete()
    Khoa.objects.all().delete()

    # Seed 0: Khoa
    khoa_cntt = Khoa.objects.create(ma_khoa="CNTT", ten_khoa="Công nghệ thông tin")
    khoa_qtkd = Khoa.objects.create(ma_khoa="QTKD", ten_khoa="Quản trị kinh doanh")
    khoa_ta = Khoa.objects.create(ma_khoa="TA", ten_khoa="Tiếng Anh chuyên ngành")
    khoa_general = Khoa.objects.create(ma_khoa="ESD", ten_khoa="Đào tạo đại cương")

    # Giữ lại các tài khoản mặc định và chỉ xóa gv_profile
    # Seed 1: KyThi
    for kt in INITIAL_KY_THI:
        dates = kt["duration"].split(" - ")
        start_d = datetime.strptime(dates[0], "%d/%m/%Y").date() if len(dates) == 2 else None
        end_d = datetime.strptime(dates[1], "%d/%m/%Y").date() if len(dates) == 2 else None
        KyThi.objects.create(
            ma_ky_thi=kt["id"],
            ten_ky_thi=kt["name"],
            nam_hoc=kt["year"],
            hoc_ky=kt["semester"],
            dot_thi=kt["dot"],
            mo_ta=kt["mota"],
            ngay_bat_dau=start_d,
            ngay_ket_thuc=end_d
        )
        
    # Seed 2: CaThi
    for ct in INITIAL_CA_THI:
        CaThi.objects.create(
            ma_ca_thi=ct["id"],
            ky_thi_id=ct["kyThiId"],
            ten_ca=ct["name"],
            ngay_thi=parse_date(ct["date"]),
            gio_bat_dau=parse_time(ct["start"]),
            gio_ket_thuc=parse_time(ct["end"]),
            note=ct["note"]
        )
        
    # Seed 3: HocPhan
    for sub_code, sub_name in SUBJECTS_LIST:
        # Determine Khoa based on prefix
        if sub_code.startswith("CSE") or sub_code.startswith("MAT") or sub_code.startswith("DAT"):
            kh_id = "CNTT"
        elif sub_code.startswith("ECO") or sub_code.startswith("MKT") or sub_code.startswith("ACC") or sub_code.startswith("BUS"):
            kh_id = "QTKD"
        elif sub_code.startswith("ENG") or sub_code.startswith("TA"):
            kh_id = "TA"
        else:
            kh_id = "ESD"
        kh_obj = Khoa.objects.get(ma_khoa=kh_id)
        
        HocPhan.objects.get_or_create(
            ma_hoc_phan=sub_code,
            defaults={"ma_hp": sub_code, "ten_hoc_phan": sub_name, "so_tin_chi": 3, "khoa": kh_obj}
        )
        
    # Seed 4: GiangVien & User
    for cb in INITIAL_CAN_BO_COI_THI:
        user_obj, _ = User.objects.get_or_create(
            username=cb["code"].lower(),
            defaults={
                "role": "gv",
                "full_name": cb["name"],
                "email": f"{cb['code'].lower()}@vnuk.edu.vn"
            }
        )
        if not user_obj.password:
            user_obj.set_password("123456")
            user_obj.save()
            
        dv_name = cb["donVi"]
        if "Máy tính" in dv_name or "CNTT" in dv_name:
            kh_id = "CNTT"
        elif "Kinh doanh" in dv_name or "Kinh tế" in dv_name:
            kh_id = "QTKD"
        elif "Tiếng Anh" in dv_name or "English" in dv_name:
            kh_id = "TA"
        else:
            kh_id = "ESD"
        kh_obj = Khoa.objects.get(ma_khoa=kh_id)
            
        GiangVien.objects.create(
            user=user_obj,
            ma_giang_vien=cb["code"],
            ho_ten=cb["name"],
            khoa=kh_obj,
            sdt="0905123456"
        )
        
    # Seed 5: PhongThi
    for p_num in range(100, 220):
        PhongThi.objects.get_or_create(
            ma_phong=f"P.{p_num}",
            defaults={"ten_phong": f"Phòng {p_num}", "suc_chua": 40, "vi_tri": ["Toà nhà A", "Toà nhà B", "Toà nhà C"][p_num % 3]}
        )
        
    # Seed 6: LopHanhChinh & SinhVien & LopHocPhan
    classes = {}
    for hp in INITIAL_HOC_PHI:
        lhc, _ = LopHanhChinh.objects.get_or_create(ma_lop=hp["class"], defaults={"ten_lop": f"Lớp {hp['class']}"})
        sv = SinhVien.objects.create(
            ma_sinh_vien=hp["msv"],
            ho_ten=hp["name"],
            lop_hanh_chinh=lhc,
            debt=hp["debt"],
            is_eligible=(hp["debt"] == 0)
        )
        
    # Seed 7: PhongThiGoc & LichThi
    for i, ptg in enumerate(INITIAL_PHONG_THI_GOC, start=1):
        # Create LopHocPhan
        lhp = LopHocPhan.objects.create(
            ma_lop_hp=ptg["id"],
            hoc_phan_id=ptg["subjectId"],
            hoc_ky="Học kỳ III",
            nam_hoc="2025-2026"
        )
        
        # Distribute dates, shifts, and rooms to avoid fake/identical data
        ca_index = ((i % 5) * 2) + (i % 2) + 1  # 1 to 10
        ca_id = f"CT-{ca_index:03d}"
        cathi_item = INITIAL_CA_THI[ca_index - 1]
        
        phong_num = 100 + (i % 20)
        phong_id = f"P.{phong_num}"
        
        # Create LichThi
        lt = LichThi.objects.create(
            ma_lich_thi=ptg["id"],
            ky_thi_id="KT-HK3-2026",
            lop_hp=lhp,
            ca_thi_id=ca_id,
            phong_thi_id=phong_id,
            ngay_thi=parse_date(cathi_item["date"]),
            so_luong_sv=ptg["papers"]
        )
        
    # Seed 7.5: LopHocPhanSinhVien & DanhSachThiSinh mapping for realistic students
    students_by_subject = {}
    for hp in INITIAL_HOC_PHI:
        lhp_obj = LopHocPhan.objects.filter(hoc_phan_id=hp["subject"]).first()
        if not lhp_obj:
            lhp_obj = LopHocPhan.objects.first()
            
        if lhp_obj:
            sv_obj = SinhVien.objects.filter(ma_sinh_vien=hp["msv"]).first()
            if sv_obj:
                LopHocPhanSinhVien.objects.get_or_create(lop_hp=lhp_obj, sinh_vien=sv_obj)
                
                if hp["subject"] not in students_by_subject:
                    students_by_subject[hp["subject"]] = []
                students_by_subject[hp["subject"]].append(sv_obj)
                idx_val = len(students_by_subject[hp["subject"]])
                sbd_val = f"SBD-{hp['subject']}-{idx_val:03d}"
                
                lt_obj = LichThi.objects.filter(lop_hp=lhp_obj).first()
                if lt_obj:
                    DanhSachThiSinh.objects.get_or_create(
                        lich_thi=lt_obj,
                        sinh_vien=sv_obj,
                        defaults={"sbd": sbd_val, "trang_thai_diem_danh": "CoMat"}
                    )
        
    # Seed 8: Coi thi history
    for cb in INITIAL_CAN_BO_COI_THI:
        gv_obj = GiangVien.objects.get(ma_giang_vien=cb["code"])
        for hist in cb["history"]:
            # Find ca thi
            ct_name = hist["shift"].split(" (")[0]
            ct_obj = CaThi.objects.filter(ten_ca=ct_name, ngay_thi=parse_date(hist["date"])).first()
            if not ct_obj:
                ct_obj = CaThi.objects.first()
            # Find phong thi
            pt_obj, _ = PhongThi.objects.get_or_create(ma_phong=hist["room"], defaults={"ten_phong": hist["room"]})
            # Find sub_code
            sub_c = hist["subject"].split(" (")[-1][:-1] if "(" in hist["subject"] else hist["subject"]
            sub_name = hist["subject"].split(" (")[0] if "(" in hist["subject"] else hist["subject"]
            sub_obj, _ = HocPhan.objects.get_or_create(ma_hoc_phan=sub_c, defaults={"ten_hoc_phan": sub_name})
            lhp_obj, _ = LopHocPhan.objects.get_or_create(ma_lop_hp=f"LHP-{sub_c}", defaults={"hoc_phan": sub_obj, "hoc_ky": "Học kỳ III", "nam_hoc": "2025-2026"})
            
            # Create a mock LichThi for history if not exists
            lt_id = f"LT-{sub_c}-{gv_obj.ma_giang_vien}-{ct_obj.ma_ca_thi}"
            lt_obj, _ = LichThi.objects.get_or_create(
                ma_lich_thi=lt_id,
                defaults={
                    "ky_thi_id": "KT-HK3-2026",
                    "ca_thi": ct_obj,
                    "phong_thi": pt_obj,
                    "lop_hp": lhp_obj,
                    "ngay_thi": parse_date(hist["date"]),
                    "so_luong_sv": 30
                }
            )
            if not lt_obj.lop_hp:
                lt_obj.lop_hp = lhp_obj
                lt_obj.save()
            PhanCongCoiThi.objects.create(
                lich_thi=lt_obj,
                can_bo=gv_obj,
                vai_tro=hist["role"],
                actual_hours=hist["hours"],
                is_confirmed=hist["confirmed"]
            )

    # Seed 9: TuiBaiThi & TuiPhach & MaPhach & DiemThi & DoiSoatDiem
    for tp in INITIAL_TUI_PHACH:
        # Resolve ca thi or lich_thi
        lt_obj = LichThi.objects.filter(ma_lich_thi=tp["rooms"][0]).first() if tp["rooms"] else None
        
        # Create TuiBaiThi
        tui_bai_obj = None
        if lt_obj:
            tui_bai_obj = TuiBaiThi.objects.create(
                ma_tui_bai=f"TBT-{tp['id'].split('-')[-1]}",
                lich_thi=lt_obj,
                so_luong_bai=tp["papers"],
                trang_thai="DaDocPhach"
            )
            
        tui_obj = TuiPhach.objects.create(
            ma_tui=tp["id"],
            ca_thi_id="CT-001",
            tui_bai_thi=tui_bai_obj,
            so_luong_bai=tp["papers"],
            mat_khau_khoa=tp["password"],
            trang_thai=tp["status"]
        )
        
        # PhanCongChamThi
        if tp["grader1"]:
            gv1 = GiangVien.objects.filter(ma_giang_vien=tp["grader1"]).first()
            if gv1:
                PhanCongChamThi.objects.create(tui_phach=tui_obj, giang_vien=gv1, vai_tro="Grader 1", trang_thai="ChuaCham")
        if tp["grader2"]:
            gv2 = GiangVien.objects.filter(ma_giang_vien=tp["grader2"]).first()
            if gv2:
                PhanCongChamThi.objects.create(tui_phach=tui_obj, giang_vien=gv2, vai_tro="Grader 2", trang_thai="ChuaCham")

        # MaPhach & Diem
        for idx, phach in enumerate(tp["phachGoc"]):
            # Create a dummy student for each phach
            sv_id = f"SV-P{tp['id'].split('-')[-1]}-{idx:02d}"
            sv_obj, _ = SinhVien.objects.get_or_create(
                ma_sinh_vien=sv_id,
                defaults={"ho_ten": f"Sinh viên Phách {phach}", "is_eligible": True}
            )
            # Create DanhSachThiSinh
            ts_obj, _ = DanhSachThiSinh.objects.get_or_create(
                lich_thi=lt_obj,
                sinh_vien=sv_obj,
                defaults={"sbd": f"SBD-{idx:03d}", "trang_thai_diem_danh": "CoMat"}
            )
            mp_obj = MaPhach.objects.create(
                ma_phach=phach,
                tui_phach=tui_obj,
                thi_sinh=ts_obj,
                trang_thai="DaRop"
            )
            
            # Scores
            if phach in tp["scores"]:
                g1_score = tp["scores"][phach].get("grader1")
                g2_score = tp["scores"][phach].get("grader2")
                
                if g1_score is not None and tp["grader1"]:
                    gv1 = GiangVien.objects.filter(ma_giang_vien=tp["grader1"]).first()
                    if gv1:
                        DiemThi.objects.create(ma_phach=mp_obj, lan_cham=1, diem=g1_score, can_bo=gv1)
                if g2_score is not None and tp["grader2"]:
                    gv2 = GiangVien.objects.filter(ma_giang_vien=tp["grader2"]).first()
                    if gv2:
                        DiemThi.objects.create(ma_phach=mp_obj, lan_cham=2, diem=g2_score, can_bo=gv2)
                
                # DoiSoatDiem
                diff = abs(g1_score - g2_score) if (g1_score is not None and g2_score is not None) else 0.0
                ds_status = "Khop" if diff == 0 else "Lech"
                DoiSoatDiem.objects.create(
                    ma_phach=mp_obj,
                    diem_lan_1=g1_score,
                    diem_lan_2=g2_score,
                    chenh_lech=diff,
                    trang_thai=ds_status
                )
                
    # Seed 10: PhieuGiaoNhan & ChiTietGiaoNhan
    for pg in INITIAL_PHIEU_GIAO_NHAN:
        sender_user, _ = User.objects.get_or_create(username=pg["sender"], defaults={"role": pg["sender"], "full_name": pg["sender"].upper()})
        recipient_user, _ = User.objects.get_or_create(username=pg["recipient"], defaults={"role": pg["recipient"], "full_name": pg["recipient"].upper()})
        
        pg_obj = PhieuGiaoNhan.objects.create(
            ma_phieu=pg["id"],
            nguoi_giao=sender_user,
            nguoi_nhan=recipient_user,
            loai_phieu=pg["type"],
            tep_dinh_kem=pg["attachments"][0] if pg["attachments"] else "",
            log_xac_nhan=pg["log"],
            trang_thai=pg["status"]
        )
        
        # Details
        if pg["rooms"]:
            for r in pg["rooms"]:
                lt_obj = LichThi.objects.filter(ma_lich_thi=r).first()
                if lt_obj:
                    ChiTietGiaoNhan.objects.create(phieu=pg_obj, lich_thi=lt_obj, tinh_trang="Nguyên vẹn")
        if pg["bags"]:
            for b in pg["bags"]:
                tp_obj = TuiPhach.objects.filter(ma_tui=b).first()
                if tp_obj:
                    ChiTietGiaoNhan.objects.create(phieu=pg_obj, tui_phach=tp_obj, tinh_trang="Nguyên vẹn")

    # Seed 11: DonPhucKhao
    for pk in INITIAL_PHUC_KHAO:
        # Ensure student exists
        sv_obj, _ = SinhVien.objects.get_or_create(ma_sinh_vien=pk["msv"], defaults={"ho_ten": pk["name"]})
        # Ensure phach exists
        mp_obj = MaPhach.objects.filter(ma_phach=pk["phach"]).first()
        if not mp_obj:
            tp_obj = TuiPhach.objects.first()
            lt_obj = tp_obj.tui_bai_thi.lich_thi if (tp_obj and tp_obj.tui_bai_thi) else LichThi.objects.first()
            ts_obj, _ = DanhSachThiSinh.objects.get_or_create(
                lich_thi=lt_obj,
                sinh_vien=sv_obj,
                defaults={"sbd": "SBD-PK", "trang_thai_diem_danh": "CoMat"}
            )
            mp_obj = MaPhach.objects.create(ma_phach=pk["phach"], tui_phach=tp_obj, thi_sinh=ts_obj)
            
        DonPhucKhao.objects.create(
            ma_don=pk["id"],
            sinh_vien=sv_obj,
            ma_phach=mp_obj,
            diem_goc=pk["originalPt1"],
            diem_phuc_khao_1=pk["pt1"],
            diem_phuc_khao_2=pk["pt2"],
            diem_phuc_khao_cuoi=pk["ptFinal"],
            ly_do="Đơn phúc khảo trực tuyến sinh viên",
            file_bien_ban=pk["file"],
            trang_thai=pk["status"]
        )
        
    # Seed 12: AuditLog
    admin_user = User.objects.filter(role="cvht").first()
    if not admin_user:
        admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user, _ = User.objects.get_or_create(username="admin", defaults={"role": "cvht", "full_name": "System Administrator"})
        
    for log in INITIAL_AUDIT_LOGS:
        actor_user = User.objects.filter(full_name=log["actor"]).first()
        if not actor_user:
            actor_user = admin_user
        dt_val = datetime.strptime(log["time"], "%Y-%m-%d %H:%M:%S")
        
        # Use simple save since timestamp has auto_now_add. We can create and override timestamp after or just insert
        al = AuditLog.objects.create(
            actor=actor_user,
            action=log["action"]
        )
        AuditLog.objects.filter(id=al.id).update(timestamp=dt_val)

    # Seed 13: NhanVien profiles for administrative users
    for user in User.objects.exclude(role='gv').all():
        ma_nv = f"NV-{user.username.upper()}"
        NhanVien.objects.get_or_create(
            ma_nhan_vien=ma_nv,
            defaults={
                "user": user,
                "ho_ten": user.full_name or user.username.upper(),
                "don_vi": "Phòng ĐT&ĐBCLGD" if user.role in ['tkt', 'ldp'] else ("Khoa chuyên môn" if user.role == 'dvcm' else "Ban điều hành")
            }
        )

    # Seed 14: DeThi & NopDeThi
    MOCK_DETHI_LIST = [
        { "id": "DT001", "hocPhan": "Tiếng Anh GTQT 3", "nguoiNop": "TS. Nguyễn Văn Anh", "thoiGian": "2026-08-10 08:30:00", "fileName": "De_Thi_Tieng_Anh_GTQT_3_ChinhThuc.docx", "ghiChu": "Đề thi trắc nghiệm 60 phút, gồm 50 câu.", "trangThai": "ChoRaSoat" },
        { "id": "DT002", "hocPhan": "Quản trị dự án", "nguoiNop": "ThS. Trần Thị Mai", "thoiGian": "2026-08-10 09:15:00", "fileName": "De_Thi_Quan_Tri_Du_An_Hocky3.pdf", "ghiChu": "Đề thi tự luận 90 phút, 4 câu tình huống.", "trangThai": "ChoRaSoat" },
        { "id": "DT003", "hocPhan": "Nhập môn Lập trình", "nguoiNop": "TS. Lê Hoàng Nam", "thoiGian": "2026-08-10 10:45:00", "fileName": "De_Thi_Nhap_Mon_Lap_Trinh_Python.pdf", "ghiChu": "Thi thực hành lập trình 90 phút, 3 bài tập.", "trangThai": "ChoRaSoat" },
        { "id": "DT004", "hocPhan": "Kinh tế vĩ mô", "nguoiNop": "PGS.TS. Vũ Thị Lan", "thoiGian": "2026-08-11 13:20:00", "fileName": "De_Thi_Kinh_Te_Vi_Mo_KyI.docx", "ghiChu": "40 câu trắc nghiệm + 2 bài tập tính toán.", "trangThai": "ChoRaSoat" },
        { "id": "DT005", "hocPhan": "Cơ sở dữ liệu", "nguoiNop": "ThS. Hoàng Văn Đức", "thoiGian": "2026-08-11 14:00:00", "fileName": "De_Thi_Co_So_Du_Lieu_SQL.pdf", "ghiChu": "Thi tự luận + thực hành truy vấn SQL 75 phút.", "trangThai": "ChoRaSoat" },
        { "id": "DT006", "hocPhan": "Marketing căn bản", "nguoiNop": "TS. Phạm Minh Tuấn", "thoiGian": "2026-08-11 15:30:00", "fileName": "De_Thi_Marketing_Can_Ban.pdf", "ghiChu": "Đề thi 2 câu lý thuyết + 1 bài tập tình huống.", "trangThai": "ChoRaSoat" },
        { "id": "DT007", "hocPhan": "Tài chính doanh nghiệp", "nguoiNop": "TS. Đỗ Hoàng Yến", "thoiGian": "2026-08-12 08:00:00", "fileName": "De_Thi_Tai_Chinh_Doanh_Nghiep.pdf", "ghiChu": "Thi viết 90 phút, được dùng bảng số liệu.", "trangThai": "ChoRaSoat" },
        { "id": "DT008", "hocPhan": "Mạng máy tính", "nguoiNop": "ThS. Ngô Quang Vinh", "thoiGian": "2026-08-12 09:40:00", "fileName": "De_Thi_Mang_May_Tinh_CCNA.docx", "ghiChu": "Đề thi trắc nghiệm trên phần mềm 60 phút.", "trangThai": "ChoRaSoat" },
        { "id": "DT009", "hocPhan": "Xác suất thống kê", "nguoiNop": "PGS.TS. Bùi Minh Triết", "thoiGian": "2026-08-12 11:00:00", "fileName": "De_Thi_Xac_Suat_Thong_Ke.pdf", "ghiChu": "Thi tự luận 90 phút, gồm 5 bài tập.", "trangThai": "ChoRaSoat" },
        { "id": "DT010", "hocPhan": "Lập trình Web", "nguoiNop": "ThS. Nguyễn Thị Thu", "thoiGian": "2026-08-12 14:15:00", "fileName": "De_Thi_Lap_Trinh_Web_Vite_Nextjs.pdf", "ghiChu": "Thi thực hành xây dựng Web App 120 phút.", "trangThai": "ChoRaSoat" }
    ]
    for d_mock in MOCK_DETHI_LIST:
        hp_obj = HocPhan.objects.filter(ten_hoc_phan=d_mock["hocPhan"]).first()
        if not hp_obj:
            hp_code = "CSE301" if d_mock["id"] == "DT010" else f"GEN-{d_mock['id']}"
            hp_obj, _ = HocPhan.objects.get_or_create(ma_hoc_phan=hp_code, defaults={"ten_hoc_phan": d_mock["hocPhan"]})
            
        dethi_obj, _ = DeThi.objects.get_or_create(
            ma_de_thi=d_mock["id"],
            defaults={
                "hoc_phan": hp_obj,
                "trang_thai": d_mock["trangThai"]
            }
        )
        
        gv_user = User.objects.filter(full_name=d_mock["nguoiNop"]).first()
        if not gv_user:
            gv_user, _ = User.objects.get_or_create(
                username=d_mock["id"].lower(),
                defaults={"role": "gv", "full_name": d_mock["nguoiNop"]}
            )
            
        NopDeThi.objects.get_or_create(
            de_thi=dethi_obj,
            defaults={
                "nguoi_nop": gv_user,
                "tep_dinh_kem": d_mock["fileName"]
            }
        )


def get_state(request):
    """
    Truy vấn trực tiếp các bảng quan hệ SQLite và serialize thành định dạng JSON cho frontend.
    Đã được tối ưu hóa triệt để bằng cách prefetch và select_related để loại bỏ N+1 query.
    """
    state_instance, created = AppState.objects.get_or_create(key="global_state")
    
    # Chỉ thực hiện gieo dữ liệu (seed) khi chưa từng khởi tạo dữ liệu
    has_seeded = AppState.objects.filter(key="seeded_once").exists()
    if not has_seeded:
        seed_database_relational()
        AppState.objects.create(key="seeded_once")
        
    # 1. phongThiGocData
    phong_thi_goc_data = []
    for lt in LichThi.objects.select_related('lop_hp__hoc_phan').prefetch_related('tui_bai_thi__tui_phach').order_by('-ma_lich_thi'):
        tbt = getattr(lt, 'tui_bai_thi', None)
        status_str = "Chưa nhận bài"
        if tbt:
            tp_list = list(tbt.tui_phach.all())
            tp = tp_list[0] if tp_list else None
            status_str = tp.trang_thai if tp else "Chưa làm phách"
            
        phong_thi_goc_data.append({
            "id": lt.ma_lich_thi,
            "subjectId": lt.lop_hp.hoc_phan.ma_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
            "subjectName": f"{lt.lop_hp.hoc_phan.ten_hoc_phan} ({lt.lop_hp.hoc_phan.ma_hoc_phan})" if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
            "papers": lt.so_luong_sv,
            "status": status_str
        })
        
    # 2. tuiPhachData
    tui_phach_data = []
    for tp in TuiPhach.objects.select_related('tui_bai_thi__lich_thi__lop_hp__hoc_phan').prefetch_related('danh_sach_phach__doi_soat', 'phan_cong_cham__giang_vien').order_by('-ma_tui'):
        phach_list = [mp.ma_phach for mp in tp.danh_sach_phach.all()]
        scores_dict = {}
        
        for mp in tp.danh_sach_phach.all():
            ds = getattr(mp, 'doi_soat', None)
            if ds:
                scores_dict[mp.ma_phach] = {
                    "grader1": float(ds.diem_lan_1) if ds.diem_lan_1 is not None else None,
                    "grader2": float(ds.diem_lan_2) if ds.diem_lan_2 is not None else None
                }
                
        grader1 = ""
        grader2 = ""
        for pc in tp.phan_cong_cham.all():
            if pc.vai_tro == "Grader 1":
                grader1 = pc.giang_vien.ma_giang_vien
            elif pc.vai_tro == "Grader 2":
                grader2 = pc.giang_vien.ma_giang_vien
            
        tui_phach_data.append({
            "id": tp.ma_tui,
            "subjectId": tp.tui_bai_thi.lich_thi.lop_hp.hoc_phan.ma_hoc_phan if (tp.tui_bai_thi and tp.tui_bai_thi.lich_thi and tp.tui_bai_thi.lich_thi.lop_hp and tp.tui_bai_thi.lich_thi.lop_hp.hoc_phan) else "",
            "subjectName": tp.tui_bai_thi.lich_thi.lop_hp.hoc_phan.ten_hoc_phan if (tp.tui_bai_thi and tp.tui_bai_thi.lich_thi and tp.tui_bai_thi.lich_thi.lop_hp and tp.tui_bai_thi.lich_thi.lop_hp.hoc_phan) else "",
            "papers": tp.so_luong_bai,
            "rooms": [tp.tui_bai_thi.lich_thi.ma_lich_thi] if (tp.tui_bai_thi and tp.tui_bai_thi.lich_thi) else [],
            "status": tp.trang_thai,
            "password": tp.mat_khau_khoa or "",
            "phachGoc": phach_list,
            "roomPhachMap": {tp.tui_bai_thi.lich_thi.ma_lich_thi: phach_list} if (tp.tui_bai_thi and tp.tui_bai_thi.lich_thi) else {},
            "grader1": grader1,
            "grader2": grader2,
            "scores": scores_dict
        })
        
    # 3. phieuGiaoNhanData
    phieu_giao_nhan_data = []
    for pgn in PhieuGiaoNhan.objects.select_related('nguoi_giao', 'nguoi_nhan').prefetch_related('chi_tiet').order_by('-ma_phieu'):
        chi_tiets = list(pgn.chi_tiet.all())
        rooms = [ct.lich_thi_id for ct in chi_tiets if ct.lich_thi_id is not None]
        bags = [ct.tui_phach_id for ct in chi_tiets if ct.tui_phach_id is not None]
        phieu_giao_nhan_data.append({
            "id": pgn.ma_phieu,
            "type": pgn.loai_phieu,
            "flow": f"{pgn.nguoi_giao.username.upper()} ➔ {pgn.nguoi_nhan.username.upper()}",
            "qty": f"{len(rooms)} phòng" if rooms else f"{len(bags)} túi",
            "status": pgn.trang_thai,
            "rooms": rooms or None,
            "bags": bags or None,
            "sender": pgn.nguoi_giao.username,
            "recipient": pgn.nguoi_nhan.username,
            "attachments": [pgn.tep_dinh_kem] if pgn.tep_dinh_kem else [],
            "log": pgn.log_xac_nhan or ""
        })
        
    # 4. canBoCoiThiData
    can_bo_coi_thi_data = []
    for gv in GiangVien.objects.select_related('khoa').prefetch_related('phan_cong_coi_thi__lich_thi__ca_thi', 'phan_cong_coi_thi__lich_thi__lop_hp__hoc_phan', 'phan_cong_coi_thi__lich_thi__phong_thi').all():
        history = []
        for pc in gv.phan_cong_coi_thi.all():
            lt = pc.lich_thi
            history.append({
                "date": str(lt.ngay_thi),
                "shift": f"{lt.ca_thi.ten_ca} ({lt.ca_thi.gio_bat_dau.strftime('%H:%M')} - {lt.ca_thi.gio_ket_thuc.strftime('%H:%M')})",
                "subject": f"{lt.lop_hp.hoc_phan.ten_hoc_phan} ({lt.lop_hp.hoc_phan.ma_hoc_phan})" if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
                "room": lt.phong_thi.ten_phong,
                "hours": float(pc.actual_hours),
                "role": pc.vai_tro,
                "confirmed": pc.is_confirmed
            })
        can_bo_coi_thi_data.append({
            "code": gv.ma_giang_vien,
            "name": gv.ho_ten,
            "donVi": gv.khoa.ten_khoa if gv.khoa else "",
            "pricePerHour": 100000,
            "history": history
        })
        
    # 5. phucKhaoData
    phuc_khao_data = []
    for dpk in DonPhucKhao.objects.select_related('sinh_vien', 'ma_phach', 'lich_thi__lop_hp__hoc_phan').order_by('-ma_don'):
        phuc_khao_data.append({
            "id": dpk.ma_don,
            "phach": dpk.ma_phach.ma_phach if dpk.ma_phach else "",
            "subjectName": dpk.lich_thi.lop_hp.hoc_phan.ten_hoc_phan if (dpk.lich_thi and dpk.lich_thi.lop_hp and dpk.lich_thi.lop_hp.hoc_phan) else "",
            "pt1": float(dpk.diem_phuc_khao_1) if dpk.diem_phuc_khao_1 is not None else None,
            "pt2": float(dpk.diem_phuc_khao_2) if dpk.diem_phuc_khao_2 is not None else None,
            "ptFinal": float(dpk.diem_phuc_khao_cuoi) if dpk.diem_phuc_khao_cuoi is not None else None,
            "originalPt1": float(dpk.diem_goc) if dpk.diem_goc is not None else None,
            "msv": dpk.sinh_vien.ma_sinh_vien,
            "name": dpk.sinh_vien.ho_ten,
            "status": dpk.trang_thai,
            "file": dpk.file_bien_ban or ""
        })
        
    # 6. auditLogsData
    audit_logs_data = []
    for log in AuditLog.objects.select_related('actor').order_by('-timestamp').all()[:100]:
        audit_logs_data.append({
            "time": log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "actor": log.actor.full_name or log.actor.username,
            "action": log.action
        })
        
    # 7. kyThiData
    ky_thi_data = []
    for kt in KyThi.objects.prefetch_related('ca_thi').order_by('-ma_ky_thi'):
        ky_thi_data.append({
            "id": kt.ma_ky_thi,
            "name": kt.ten_ky_thi,
            "year": kt.nam_hoc,
            "semester": kt.hoc_ky,
            "duration": f"{kt.ngay_bat_dau.strftime('%d/%m/%Y') if kt.ngay_bat_dau else ''} - {kt.ngay_ket_thuc.strftime('%d/%m/%Y') if kt.ngay_ket_thuc else ''}",
            "dot": kt.dot_thi or "",
            "mota": kt.mo_ta or "",
            "shiftsCount": len(list(kt.ca_thi.all()))
        })
        
    # 8. caThiData
    ca_thi_data = []
    for ct in CaThi.objects.select_related('ky_thi').order_by('-ma_ca_thi'):
        ca_thi_data.append({
            "id": ct.ma_ca_thi,
            "kyThiId": ct.ky_thi.ma_ky_thi if ct.ky_thi else "",
            "name": ct.ten_ca,
            "date": str(ct.ngay_thi),
            "start": ct.gio_bat_dau.strftime('%H:%M'),
            "end": ct.gio_ket_thuc.strftime('%H:%M'),
            "note": ct.note or ""
        })
        
    # 9. lichThiData
    sys_configs_str = getattr(state_instance, 'system_configs', '{}')
    sys_configs = json.loads(sys_configs_str or '{}')
    lich_statuses = sys_configs.get("lichThiStatuses", {})
    de_statuses = sys_configs.get("deThiStatuses", {})

    lich_thi_data = []
    for lt in LichThi.objects.filter(lop_hp__isnull=False, lop_hp__hoc_phan__isnull=False).select_related('lop_hp__hoc_phan', 'ca_thi', 'phong_thi').prefetch_related('phan_cong_coi_thi__can_bo').order_by('-ma_lich_thi'):
        pc_list = list(lt.phan_cong_coi_thi.all())
        teacher_name = pc_list[0].can_bo.ho_ten if pc_list else ""
        teacher_id = pc_list[0].can_bo.ma_giang_vien if pc_list else ""
        teacher_display = f"{teacher_name} ({teacher_id})" if (teacher_name and teacher_id) else teacher_name
        
        st_info = lich_statuses.get(lt.ma_lich_thi, {})
        lich_thi_data.append({
            "id": lt.ma_lich_thi,
            "subjectCode": lt.lop_hp.hoc_phan.ma_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
            "subjectName": lt.lop_hp.hoc_phan.ten_hoc_phan if (lt.lop_hp and lt.lop_hp.hoc_phan) else "",
            "date": str(lt.ngay_thi),
            "shiftName": lt.ca_thi.ten_ca,
            "caThiId": lt.ca_thi.ma_ca_thi,
            "room": lt.phong_thi.ten_phong if lt.phong_thi else "",
            "teacher": teacher_display,
            "teacherId": teacher_id,
            "status": st_info.get("status", "Chờ duyệt"),
            "approver": st_info.get("approver", ""),
            "approvedAt": st_info.get("approvedAt", ""),
            "lyDoTuChoi": st_info.get("lyDoTuChoi", ""),
            "rejectedAt": st_info.get("rejectedAt", "")
        })
        
    # 10. hocPhiData
    if "hocPhiData" in sys_configs and sys_configs["hocPhiData"]:
        hoc_phi_data = sys_configs["hocPhiData"]
    else:
        hoc_phi_data = []
        sv_subjects = {}
        for lhp_sv in LopHocPhanSinhVien.objects.select_related('lop_hp__hoc_phan').all():
            if lhp_sv.sinh_vien_id and lhp_sv.lop_hp and lhp_sv.lop_hp.hoc_phan:
                sv_subjects[lhp_sv.sinh_vien_id] = lhp_sv.lop_hp.hoc_phan.ma_hoc_phan

        for ts in DanhSachThiSinh.objects.select_related('lich_thi__lop_hp__hoc_phan').all():
            if ts.sinh_vien_id and ts.lich_thi and ts.lich_thi.lop_hp and ts.lich_thi.lop_hp.hoc_phan:
                sv_subjects[ts.sinh_vien_id] = ts.lich_thi.lop_hp.hoc_phan.ma_hoc_phan

        for sv in SinhVien.objects.exclude(ma_sinh_vien__startswith="SV-P").select_related('lop_hanh_chinh').all():
            sub_code = sv_subjects.get(sv.ma_sinh_vien, "ENG101")
            hoc_phi_data.append({
                "msv": sv.ma_sinh_vien,
                "name": sv.ho_ten,
                "class": sv.lop_hanh_chinh.ma_lop if sv.lop_hanh_chinh else "24CS01",
                "subject": sub_code,
                "debt": float(sv.debt)
            })
        
    # 11. lopThiDiemData
    maphach_qs = MaPhach.objects.select_related('thi_sinh', 'doi_soat').all()
    mp_map = {}
    for mp in maphach_qs:
        if mp.thi_sinh:
            mp_map[(mp.thi_sinh.lich_thi_id, mp.thi_sinh.sinh_vien_id)] = mp

    lop_thi_diem_data = {}
    for lt in LichThi.objects.prefetch_related('danh_sach_thi_sinh__sinh_vien').all():
        students_list = []
        for ts in lt.danh_sach_thi_sinh.all():
            sv = ts.sinh_vien
            pt1 = None
            ptFinal = None
            mp = mp_map.get((lt.ma_lich_thi, sv.ma_sinh_vien))
            if mp:
                ds = getattr(mp, 'doi_soat', None)
                if ds:
                    pt1 = float(ds.diem_lan_1) if ds.diem_lan_1 is not None else None
                    ptFinal = float(ds.diem_lan_1) if (ds.diem_lan_1 is not None and ds.diem_lan_1 == ds.diem_lan_2) else None
            
            students_list.append({
                "sbd": ts.sbd,
                "name": sv.ho_ten,
                "pt1": pt1,
                "pt2": None,
                "ptFinal": ptFinal,
                "originalPt1": pt1
            })
        lop_thi_diem_data[lt.ma_lich_thi] = students_list

    # 12. phongThiData
    phong_thi_data = []
    for pt in PhongThi.objects.order_by('-ma_phong'):
        phong_thi_data.append({
            "id": pt.ma_phong,
            "ma": pt.ma_phong,
            "ten": pt.ten_phong,
            "sucChua": pt.suc_chua,
            "viTri": pt.vi_tri,
            "loai": pt.loai_phong,
            "trangThai": pt.trang_thai
        })

    # 13. inSaoData
    in_sao_data = []
    for dis in DotInSao.objects.select_related('ky_thi', 'ca_thi', 'phong_thi', 'hoc_phan', 'can_bo_giam_sat', 'bien_ban_giam_sat').prefetch_related('nhat_ky', 'danh_sach_checklist__hoc_phan').order_by('-ma_dot_in_sao'):
        nk = getattr(dis, 'nhat_ky', None)
        bb = getattr(dis, 'bien_ban_giam_sat', None)
        lt_obj = LichThi.objects.filter(ca_thi=dis.ca_thi, phong_thi=dis.phong_thi, lop_hp__hoc_phan=dis.hoc_phan).first()
        lt_id = lt_obj.ma_lich_thi if lt_obj else ""
        subject_name = dis.hoc_phan.ten_hoc_phan if dis.hoc_phan else "Đợt in sao mới"
        
        # Map DB status to Client display status
        db_status = dis.trang_thai
        client_status = "Chờ cập nhật"
        if db_status == "DaCapNhat":
            client_status = "Chờ xác nhận"
        elif db_status == "HoanTat":
            client_status = "Hoàn tất"
        elif db_status == "CanXuLyLai":
            client_status = "Cần xử lý lại"
        elif db_status == "TuChoi":
            client_status = "Từ chối xác nhận"
            
        checklist_items = []
        for ck in dis.danh_sach_checklist.all():
            checklist_items.append({
                "id": ck.id,
                "maMuc": ck.ma_muc,
                "tenMuc": ck.ten_muc,
                "nhomDe": ck.nhom_de or "",
                "soLuongCanIn": ck.so_luong_can_in,
                "soLuongDaIn": ck.so_luong_da_in,
                "soLuongNiemPhong": ck.so_luong_niem_phong,
                "trangThai": "Đã in xong" if ck.trang_thai == 'DaInXong' else "Chưa in",
                "ghiChu": ck.ghi_chu or ""
            })

        is_item = {
            "id": dis.ma_dot_in_sao,
            "ltId": lt_id,
            "subjectName": subject_name,
            "soLuong": dis.so_luong_ban_in,
            "ngay": dis.thoi_gian_in_sao.strftime('%Y-%m-%d') if dis.thoi_gian_in_sao else "",
            "noiIn": dis.noi_in_sao or "",
            "giamSat": dis.can_bo_giam_sat.username if dis.can_bo_giam_sat else "",
            "ghiChu": dis.ghi_chu or "",
            "trangThai": client_status,
            "chuKySo": bb.chu_ky_so if bb else "",
            "nhanXetGiamSat": bb.nhan_xet_giam_sat if bb else "",
            "checklist": checklist_items
        }
        if nk:
            is_item.update({
                "nkThoiGian": nk.thoi_gian_thuc_hien.strftime('%Y-%m-%dT%H:%M') if nk.thoi_gian_thuc_hien else "",
                "nkSoLuong": nk.so_luong_in_thuc_te,
                "nkNiemPhong": nk.so_luong_niem_phong,
                "nkNguoiIn": nk.nguoi_thuc_hien.username if nk.nguoi_thuc_hien else "",
                "nkGhiChu": nk.ghi_chu or "",
                "ketQuaKiemTra": nk.ket_qua_kiem_tra or "",
                "nguoiKiemTra": nk.nguoi_kiem_tra.username if nk.nguoi_kiem_tra else "",
                "ghiChuKiemTra": nk.ghi_chu_kiem_tra or ""
            })
        in_sao_data.append(is_item)

    # 14. deThiData
    de_thi_data = []
    for dt in DeThi.objects.select_related('hoc_phan').prefetch_related('nop_de_thi__nguoi_nop', 'ra_soat_de_thi__nguoi_rao_soat').order_by('-ma_de_thi'):
        nop = dt.nop_de_thi.first()
        rs = dt.ra_soat_de_thi.first()
        st_info = de_statuses.get(dt.ma_de_thi, {})
        default_st = {"ChoRaSoat": "Chờ rà soát", "Dat": "Đạt", "ChoChinhSua": "Chờ chỉnh sửa"}.get(dt.trang_thai, dt.trang_thai)
        de_thi_data.append({
            "id": dt.ma_de_thi,
            "hocPhan": dt.hoc_phan.ten_hoc_phan if dt.hoc_phan else "",
            "nguoiNop": nop.nguoi_nop.full_name if (nop and nop.nguoi_nop) else "",
            "thoiGian": nop.thoi_gian_nop.strftime('%H:%M %d/%m/%Y') if nop else "",
            "fileName": nop.tep_dinh_kem if nop else "",
            "ghiChu": rs.ghi_chu if rs else "",
            "trangThai": st_info.get("trangThai", default_st),
            "nhanXet": rs.ket_qua if rs else "",
            "approver": st_info.get("approver", ""),
            "approvedAt": st_info.get("approvedAt", ""),
            "lyDoTuChoi": st_info.get("lyDoTuChoi", ""),
            "rejectedAt": st_info.get("rejectedAt", "")
        })
        
    # 15. hocPhanData
    hoc_phan_data = []
    for hp in HocPhan.objects.order_by('ten_hoc_phan').all():
        hoc_phan_data.append({
            "code": hp.ma_hoc_phan,
            "name": hp.ten_hoc_phan
        })

    # System Configs (Đọc trực tiếp từ AppState)
    system_configs_str = getattr(state_instance, 'system_configs', '{}')
    if not system_configs_str or system_configs_str == '{}':
        system_configs_str = json.dumps(INITIAL_SYSTEM_CONFIGS)
        
    sys_configs = json.loads(system_configs_str)
    if not in_sao_data and "inSaoData" in sys_configs:
        in_sao_data = sys_configs["inSaoData"]

    phan_cong_phong_data = sys_configs.get("phanCongPhongData", [])
    don_gia_rules_data = sys_configs.get("donGiaRulesData", [])

    danh_sach_thi_data = json.loads(getattr(state_instance, 'danh_sach_thi_data', '[]') or '[]')
    if not danh_sach_thi_data:
        ds_list = []
        for lhp in LopHocPhan.objects.select_related('hoc_phan').prefetch_related('sinh_vien_lien_ket').all():
            total_sv = lhp.sinh_vien_lien_ket.count()
            if total_sv == 0:
                total_sv = 30
                eligible_sv = 28
                banned_sv = 2
            else:
                eligible_sv = lhp.sinh_vien_lien_ket.filter(is_eligible=True).count()
                banned_sv = total_sv - eligible_sv
                
            hp_code = lhp.hoc_phan.ma_hoc_phan if lhp.hoc_phan else lhp.ma_lop_hp
            hp_name = lhp.hoc_phan.ten_hoc_phan if lhp.hoc_phan else lhp.ma_lop_hp
            ds_list.append({
                "id": f"DS-{lhp.ma_lop_hp}",
                "subjectCode": hp_code,
                "subjectName": f"{hp_name} ({hp_code})",
                "totalStudents": total_sv,
                "eligibleStudents": eligible_sv,
                "bannedStudents": banned_sv,
                "creator": "Tổ Khảo thí",
                "createdAt": "09:30 18/07/2026",
                "status": "Chờ duyệt",
                "lyDoTuChoi": "",
                "approver": "",
                "approvedAt": ""
            })
        danh_sach_thi_data = ds_list

    return JsonResponse({
        "phongThiGocData": phong_thi_goc_data,
        "tuiPhachData": tui_phach_data,
        "phieuGiaoNhanData": phieu_giao_nhan_data,
        "canBoCoiThiData": can_bo_coi_thi_data,
        "phucKhaoData": phuc_khao_data,
        "auditLogsData": audit_logs_data,
        "systemConfigsData": sys_configs,
        "kyThiData": ky_thi_data,
        "caThiData": ca_thi_data,
        "lichThiData": lich_thi_data,
        "hocPhiData": hoc_phi_data,
        "lopThiDiemData": lop_thi_diem_data,
        "phongThiData": phong_thi_data,
        "phanCongPhongData": phan_cong_phong_data,
        "inSaoData": in_sao_data,
        "deThiData": de_thi_data,
        "hocPhanData": hoc_phan_data,
        "danhSachThiData": danh_sach_thi_data,
        "donGiaRulesData": don_gia_rules_data
    })


def sync_configs_to_db(configs_data):
    try:
        nhap_diem_configs = configs_data.get("nhapDiem", {})
        for sub_id, times in nhap_diem_configs.items():
            subject, _ = HocPhan.objects.get_or_create(
                ma_hoc_phan=sub_id,
                defaults={"ma_hp": sub_id, "ten_hoc_phan": f"Học phần {sub_id}", "so_tin_chi": 3}
            )
            start_dt = parse_datetime(times.get("start")) if times.get("start") else None
            end_dt = parse_datetime(times.get("end")) if times.get("end") else None
            publish_dt = parse_datetime(times.get("publish")) if times.get("publish") else None
            
            PhienBanCotDiem.objects.update_or_create(
                ma_phien_ban=f"PB-{sub_id}",
                defaults={
                    "ma_hoc_phan": subject,
                    "ten_phien_ban": f"Phiên bản Học phần {sub_id}",
                    "thoi_gian_ap_dung": start_dt,
                    "thoi_gian_ket_thuc": end_dt,
                    "thoi_gian_cong_bo": publish_dt,
                    "trang_thai": "ApDung"
                }
            )

        phuc_khao_configs = configs_data.get("phucKhao", {})
        for sub_id, times in phuc_khao_configs.items():
            subject, _ = HocPhan.objects.get_or_create(
                ma_hoc_phan=sub_id,
                defaults={"ma_hp": sub_id, "ten_hoc_phan": f"Học phần {sub_id}", "so_tin_chi": 3}
            )
            start_dt = parse_datetime(times.get("start")) if times.get("start") else None
            end_dt = parse_datetime(times.get("end")) if times.get("end") else None
            deadline_dt = parse_datetime(times.get("deadline")) if times.get("deadline") else None
            
            CauHinhPhucKhao.objects.update_or_create(
                ma_cau_hinh=f"CHPK-{sub_id}",
                defaults={
                    "ma_hoc_phan": subject,
                    "thoi_gian_mo_cong": start_dt,
                    "thoi_gian_khoa_cong": end_dt,
                    "han_chot_cham": deadline_dt,
                    "trang_thai": "KichHoat"
                }
            )
    except Exception as e:
        print("Lỗi đồng bộ cấu hình xuống Database:", e)


@csrf_exempt
@transaction.atomic
def save_state(request):
    """
    Nhận dữ liệu từ frontend và đồng bộ đồng thời vào các bảng quan hệ SQLite.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            state, _ = AppState.objects.get_or_create(key="global_state")
            
            # Reset dữ liệu
            if data.get("reset") is True:
                seed_database_relational()
                state.system_configs = json.dumps(INITIAL_SYSTEM_CONFIGS)
                state.save()
                sync_configs_to_db(INITIAL_SYSTEM_CONFIGS)
                return JsonResponse({"status": "success"})
                
            # 1. Đồng bộ phongThiGocData -> PhongThi, LopHocPhan
            if "phongThiGocData" in data:
                for ptg in data["phongThiGocData"]:
                    if ptg.get("subjectId") and ptg.get("subjectName"):
                        HocPhan.objects.get_or_create(ma_hoc_phan=ptg["subjectId"], defaults={"ten_hoc_phan": ptg["subjectName"].split(" (")[0]})
                        LopHocPhan.objects.get_or_create(ma_lop_hp=ptg["id"], defaults={"hoc_phan_id": ptg["subjectId"], "hoc_ky": "Học kỳ III", "nam_hoc": "2025-2026"})
                        # Cập nhật sỹ số nếu lịch thi đã tồn tại trong database
                        lt_obj = LichThi.objects.filter(ma_lich_thi=ptg["id"]).first()
                        if lt_obj and ptg.get("papers"):
                            lt_obj.so_luong_sv = ptg["papers"]
                            lt_obj.save()
                    
            # 2. Đồng bộ tuiPhachData -> TuiPhach, MaPhach, DiemThi, DoiSoatDiem, PhanCongChamThi
            if "tuiPhachData" in data:
                payload_ids = [tp["id"] for tp in data["tuiPhachData"] if tp.get("id")]
                deleted_tui_ids = list(TuiPhach.objects.exclude(ma_tui__in=payload_ids).values_list('ma_tui', flat=True))
                if deleted_tui_ids:
                    DonPhucKhao.objects.filter(ma_phach__tui_phach_id__in=deleted_tui_ids).delete()
                    DoiSoatDiem.objects.filter(ma_phach__tui_phach_id__in=deleted_tui_ids).delete()
                    DiemThi.objects.filter(ma_phach__tui_phach_id__in=deleted_tui_ids).delete()
                    PhanCongChamThi.objects.filter(tui_phach_id__in=deleted_tui_ids).delete()
                    MaPhach.objects.filter(tui_phach_id__in=deleted_tui_ids).delete()
                    ChiTietGiaoNhan.objects.filter(tui_phach_id__in=deleted_tui_ids).delete()
                    TuiPhach.objects.filter(ma_tui__in=deleted_tui_ids).delete()

                # Pre-fetch lookup tables to avoid N+1 queries in loops
                maphach_dict = {mp.ma_phach: mp for mp in MaPhach.objects.select_related('tui_phach', 'thi_sinh__sinh_vien').all()}
                diemthi_dict = {(dt.ma_phach_id, dt.lan_cham): dt for dt in DiemThi.objects.all()}
                doisoat_dict = {ds.ma_phach_id: ds for ds in DoiSoatDiem.objects.all()}
                giangvien_dict = {gv.ma_giang_vien: gv for gv in GiangVien.objects.select_related('user').all()}

                for tp in data["tuiPhachData"]:
                    lt_obj = LichThi.objects.filter(ma_lich_thi=tp["rooms"][0]).first() if tp["rooms"] else None
                    
                    # Resolve ca_thi_id dynamically
                    resolved_ca_thi_id = None
                    if lt_obj:
                        resolved_ca_thi_id = lt_obj.ca_thi_id
                    else:
                        if CaThi.objects.filter(ma_ca_thi="CT-001").exists():
                            resolved_ca_thi_id = "CT-001"
                        else:
                            first_ct = CaThi.objects.first()
                            resolved_ca_thi_id = first_ct.ma_ca_thi if first_ct else None
                            
                    # If we don't have a valid CaThi, skip this TuiPhach (since its CaThi has been deleted)
                    if not resolved_ca_thi_id:
                        continue
                        
                    # Create TuiBaiThi
                    tui_bai_obj = None
                    if lt_obj:
                        tui_bai_obj, _ = TuiBaiThi.objects.update_or_create(
                            ma_tui_bai=f"TBT-{tp['id'].split('-')[-1]}",
                            defaults={
                                "lich_thi": lt_obj,
                                "so_luong_bai": tp["papers"],
                                "trang_thai": "DaDocPhach"
                            }
                        )
                    
                    tui_obj, _ = TuiPhach.objects.update_or_create(
                        ma_tui=tp["id"],
                        defaults={
                            "ca_thi_id": resolved_ca_thi_id,
                            "tui_bai_thi": tui_bai_obj,
                            "so_luong_bai": tp["papers"],
                            "mat_khau_khoa": tp["password"],
                            "trang_thai": tp["status"]
                        }
                    )
                    
                    # Phan công chấm thi
                    if tp["grader1"]:
                        gv1 = giangvien_dict.get(tp["grader1"])
                        if gv1:
                            PhanCongChamThi.objects.update_or_create(tui_phach=tui_obj, giang_vien=gv1, vai_tro="Grader 1", defaults={"trang_thai": "DangCham" if tp["status"] == "Đang chấm" else "ChuaCham"})
                    if tp["grader2"]:
                        gv2 = giangvien_dict.get(tp["grader2"])
                        if gv2:
                            PhanCongChamThi.objects.update_or_create(tui_phach=tui_obj, giang_vien=gv2, vai_tro="Grader 2", defaults={"trang_thai": "DangCham" if tp["status"] == "Đang chấm" else "ChuaCham"})
                            
                    # Mã phách & Điểm thi
                    for idx, phach in enumerate(tp["phachGoc"]):
                        mp_obj = maphach_dict.get(phach)
                        if not mp_obj:
                            sv_id = f"SV-P{tp['id'].split('-')[-1]}-{idx:02d}"
                            sv_obj, _ = SinhVien.objects.get_or_create(ma_sinh_vien=sv_id, defaults={"ho_ten": f"Sinh viên {phach}"})
                            ts_obj, _ = DanhSachThiSinh.objects.get_or_create(
                                lich_thi=lt_obj,
                                sinh_vien=sv_obj,
                                defaults={"sbd": f"SBD-{idx:03d}"}
                            )
                            mp_obj = MaPhach.objects.create(
                                ma_phach=phach,
                                tui_phach=tui_obj,
                                thi_sinh=ts_obj,
                                trang_thai="DaRop"
                            )
                            maphach_dict[phach] = mp_obj
                        else:
                            if mp_obj.tui_phach_id != tui_obj.ma_tui or mp_obj.trang_thai != "DaRop":
                                mp_obj.tui_phach = tui_obj
                                mp_obj.trang_thai = "DaRop"
                                mp_obj.save()
                        
                        # Cập nhật điểm
                        if phach in tp["scores"]:
                            g1_s = tp["scores"][phach].get("grader1")
                            g2_s = tp["scores"][phach].get("grader2")
                            
                            gv1 = giangvien_dict.get(tp["grader1"]) if tp["grader1"] else None
                            gv2 = giangvien_dict.get(tp["grader2"]) if tp["grader2"] else None

                            if g1_s is not None and gv1:
                                dt_key = (mp_obj.ma_phach, 1)
                                existing_dt = diemthi_dict.get(dt_key)
                                if not existing_dt:
                                    DiemThi.objects.create(ma_phach=mp_obj, lan_cham=1, diem=g1_s, can_bo=gv1)
                                else:
                                    if existing_dt.diem != g1_s or existing_dt.can_bo_id != gv1.user_id:
                                        existing_dt.diem = g1_s
                                        existing_dt.can_bo = gv1
                                        existing_dt.save()

                            if g2_s is not None and gv2:
                                dt_key = (mp_obj.ma_phach, 2)
                                existing_dt = diemthi_dict.get(dt_key)
                                if not existing_dt:
                                    DiemThi.objects.create(ma_phach=mp_obj, lan_cham=2, diem=g2_s, can_bo=gv2)
                                else:
                                    if existing_dt.diem != g2_s or existing_dt.can_bo_id != gv2.user_id:
                                        existing_dt.diem = g2_s
                                        existing_dt.can_bo = gv2
                                        existing_dt.save()
                                    
                            diff = abs(g1_s - g2_s) if (g1_s is not None and g2_s is not None) else 0.0
                            ds_status = "Khop" if diff == 0 else "Lech"
                            
                            # Cập nhật đối soát
                            existing_ds = doisoat_dict.get(mp_obj.ma_phach)
                            if not existing_ds:
                                DoiSoatDiem.objects.create(
                                    ma_phach=mp_obj,
                                    diem_lan_1=g1_s,
                                    diem_lan_2=g2_s,
                                    chenh_lech=diff,
                                    trang_thai=ds_status
                                )
                            else:
                                if (existing_ds.diem_lan_1 != g1_s or 
                                    existing_ds.diem_lan_2 != g2_s or 
                                    existing_ds.chenh_lech != diff or 
                                    existing_ds.trang_thai != ds_status):
                                    existing_ds.diem_lan_1 = g1_s
                                    existing_ds.diem_lan_2 = g2_s
                                    existing_ds.chenh_lech = diff
                                    existing_ds.trang_thai = ds_status
                                    existing_ds.save()
                            
            # 3. Đồng bộ phieuGiaoNhanData -> PhieuGiaoNhan, ChiTietGiaoNhan
            if "phieuGiaoNhanData" in data:
                payload_ids = [pg["id"] for pg in data["phieuGiaoNhanData"] if pg.get("id")]
                deleted_phieu_ids = list(PhieuGiaoNhan.objects.exclude(ma_phieu__in=payload_ids).values_list('ma_phieu', flat=True))
                if deleted_phieu_ids:
                    ChiTietGiaoNhan.objects.filter(phieu_id__in=deleted_phieu_ids).delete()
                    PhieuGiaoNhan.objects.filter(ma_phieu__in=deleted_phieu_ids).delete()

                for pg in data["phieuGiaoNhanData"]:
                    sender_user, _ = User.objects.get_or_create(username=pg["sender"], defaults={"role": pg["sender"], "full_name": pg["sender"].upper()})
                    recipient_user, _ = User.objects.get_or_create(username=pg["recipient"], defaults={"role": pg["recipient"], "full_name": pg["recipient"].upper()})
                    
                    pg_obj, _ = PhieuGiaoNhan.objects.update_or_create(
                        ma_phieu=pg["id"],
                        defaults={
                            "nguoi_giao": sender_user,
                            "nguoi_nhan": recipient_user,
                            "loai_phieu": pg["type"],
                            "tep_dinh_kem": pg["attachments"][0] if pg["attachments"] else "",
                            "log_xac_nhan": pg["log"],
                            "trang_thai": pg["status"]
                        }
                    )
                    
                    # Xóa chi tiết cũ và tạo lại
                    ChiTietGiaoNhan.objects.filter(phieu=pg_obj).delete()
                    if pg["rooms"]:
                        for r in pg["rooms"]:
                            lt_obj = LichThi.objects.filter(ma_lich_thi=r).first()
                            if lt_obj:
                                ChiTietGiaoNhan.objects.create(phieu=pg_obj, lich_thi=lt_obj, tinh_trang="Nguyên vẹn")
                    if pg["bags"]:
                        for b in pg["bags"]:
                            tp_obj = TuiPhach.objects.filter(ma_tui=b).first()
                            if tp_obj:
                                ChiTietGiaoNhan.objects.create(phieu=pg_obj, tui_phach=tp_obj, tinh_trang="Nguyên vẹn")
                                
            # 4. Đồng bộ canBoCoiThiData -> GiangVien, PhanCongCoiThi
            if "canBoCoiThiData" in data:
                for cb in data["canBoCoiThiData"]:
                    gv_obj = GiangVien.objects.filter(ma_giang_vien=cb["code"]).first()
                    if gv_obj:
                        for hist in cb["history"]:
                            ct_name = hist["shift"].split(" (")[0]
                            ct_obj = CaThi.objects.filter(ten_ca=ct_name, ngay_thi=parse_date(hist["date"])).first()
                            if not ct_obj:
                                ct_obj = CaThi.objects.first()
                                
                            if ct_obj:
                                pt_obj, _ = PhongThi.objects.get_or_create(ma_phong=hist["room"], defaults={"ten_phong": hist["room"]})
                                sub_c = hist["subject"].split(" (")[-1][:-1] if "(" in hist["subject"] else hist["subject"]
                                sub_name = hist["subject"].split(" (")[0] if "(" in hist["subject"] else hist["subject"]
                                sub_obj, _ = HocPhan.objects.get_or_create(ma_hoc_phan=sub_c, defaults={"ten_hoc_phan": sub_name})
                                lhp_obj, _ = LopHocPhan.objects.get_or_create(ma_lop_hp=f"LHP-{sub_c}", defaults={"hoc_phan": sub_obj, "hoc_ky": "Học kỳ III", "nam_hoc": "2025-2026"})
                                
                                lt_id = f"LT-{sub_c}-{gv_obj.ma_giang_vien}-{ct_obj.ma_ca_thi}"
                                lt_obj, _ = LichThi.objects.get_or_create(
                                    ma_lich_thi=lt_id,
                                    defaults={
                                        "ky_thi_id": ct_obj.ky_thi_id,
                                        "ca_thi": ct_obj,
                                        "phong_thi": pt_obj,
                                        "lop_hp": lhp_obj,
                                        "ngay_thi": parse_date(hist["date"]),
                                        "so_luong_sv": 30
                                    }
                                )
                                if not lt_obj.lop_hp:
                                    lt_obj.lop_hp = lhp_obj
                                    lt_obj.save()
                                PhanCongCoiThi.objects.update_or_create(
                                    lich_thi=lt_obj,
                                    can_bo=gv_obj,
                                    defaults={
                                        "vai_tro": hist["role"],
                                        "actual_hours": hist["hours"],
                                        "is_confirmed": hist["confirmed"]
                                    }
                                )
                            
            # 5. Đồng bộ phucKhaoData -> DonPhucKhao
            if "phucKhaoData" in data:
                payload_ids = [pk["id"] for pk in data["phucKhaoData"] if pk.get("id")]
                DonPhucKhao.objects.exclude(ma_don__in=payload_ids).delete()
                for pk in data["phucKhaoData"]:
                    sv_obj, _ = SinhVien.objects.get_or_create(ma_sinh_vien=pk["msv"], defaults={"ho_ten": pk["name"]})
                    mp_obj = MaPhach.objects.filter(ma_phach=pk["phach"]).first()
                    
                    DonPhucKhao.objects.update_or_create(
                        ma_don=pk["id"],
                        defaults={
                            "sinh_vien": sv_obj,
                            "ma_phach": mp_obj,
                            "diem_goc": pk["originalPt1"],
                            "diem_phuc_khao_1": pk["pt1"],
                            "diem_phuc_khao_2": pk["pt2"],
                            "diem_phuc_khao_cuoi": pk["ptFinal"],
                            "file_bien_ban": pk["file"],
                            "trang_thai": pk["status"]
                        }
                    )
                    
            # 6. Đồng bộ auditLogsData -> AuditLog
            if "auditLogsData" in data:
                # Chỉ thêm các log mới chưa tồn tại
                for log in data["auditLogsData"]:
                    dt_val = datetime.strptime(log["time"], "%Y-%m-%d %H:%M:%S")
                    actor_user = User.objects.filter(full_name=log["actor"]).first()
                    if not actor_user:
                        actor_user, _ = User.objects.get_or_create(username="system", defaults={"role": "cvht", "full_name": "Hệ thống"})
                        
                    if not AuditLog.objects.filter(timestamp=dt_val, action=log["action"]).exists():
                        al = AuditLog.objects.create(
                            actor=actor_user,
                            action=log["action"]
                        )
                        AuditLog.objects.filter(id=al.id).update(timestamp=dt_val)
                        
            # 7. Đồng bộ hocPhiData -> SinhVien & system_configs
            if "hocPhiData" in data:
                for hp in data["hocPhiData"]:
                    if hp.get("msv"):
                        sv_obj, created = SinhVien.objects.get_or_create(
                            ma_sinh_vien=hp["msv"],
                            defaults={
                                "ho_ten": hp.get("name", hp["msv"]),
                                "debt": hp.get("debt", 0),
                                "is_eligible": (hp.get("debt", 0) == 0)
                            }
                        )
                        if not created:
                            sv_obj.debt = hp.get("debt", 0)
                            sv_obj.is_eligible = (hp.get("debt", 0) == 0)
                            if hp.get("name"):
                                sv_obj.ho_ten = hp["name"]
                            sv_obj.save()
                
                sys_cfgs = json.loads(getattr(state, 'system_configs', '{}') or '{}')
                sys_cfgs["hocPhiData"] = data["hocPhiData"]
                state.system_configs = json.dumps(sys_cfgs, ensure_ascii=False)
                state.save()
                        
            # 8. Đồng bộ kyThiData -> KyThi
            if "kyThiData" in data:
                payload_ids = [kt["id"] for kt in data["kyThiData"]]
                deleted_ky_thi_ids = list(KyThi.objects.exclude(ma_ky_thi__in=payload_ids).values_list('ma_ky_thi', flat=True))
                if deleted_ky_thi_ids:
                    # Xóa dọn dẹp các bảng phụ thuộc trước để tránh lỗi ProtectedError hoặc IntegrityError
                    BienBanViPham.objects.filter(lich_thi__ky_thi_id__in=deleted_ky_thi_ids).delete()
                    TuiPhach.objects.filter(tui_bai_thi__lich_thi__ky_thi_id__in=deleted_ky_thi_ids).delete()
                    TuiBaiThi.objects.filter(lich_thi__ky_thi_id__in=deleted_ky_thi_ids).delete()
                    DotInSao.objects.filter(ky_thi_id__in=deleted_ky_thi_ids).delete()
                    PhanCongCoiThi.objects.filter(lich_thi__ky_thi_id__in=deleted_ky_thi_ids).delete()
                    DanhSachThiSinh.objects.filter(lich_thi__ky_thi_id__in=deleted_ky_thi_ids).delete()
                    LichThi.objects.filter(ky_thi_id__in=deleted_ky_thi_ids).delete()
                    CaThi.objects.filter(ky_thi_id__in=deleted_ky_thi_ids).delete()
                    KyThi.objects.filter(ma_ky_thi__in=deleted_ky_thi_ids).delete()
                
                for kt in data["kyThiData"]:
                    duration_str = kt.get("duration", "")
                    start_d = None
                    end_d = None
                    if " - " in duration_str:
                        parts = duration_str.split(" - ")
                        start_d = safe_parse_date(parts[0])
                        end_d = safe_parse_date(parts[1])
                    else:
                        start_d = safe_parse_date(duration_str)

                    KyThi.objects.update_or_create(
                         ma_ky_thi=kt["id"],
                         defaults={
                             "ten_ky_thi": kt.get("name", ""),
                             "nam_hoc": kt.get("year", ""),
                             "hoc_ky": kt.get("semester", ""),
                             "dot_thi": kt.get("dot", ""),
                             "mo_ta": kt.get("mota", ""),
                             "ngay_bat_dau": start_d,
                             "ngay_ket_thuc": end_d
                         }
                    )
            
            # 9. Đồng bộ caThiData -> CaThi
            if "caThiData" in data:
                payload_ids = [ct["id"] for ct in data["caThiData"]]
                deleted_ca_thi_ids = list(CaThi.objects.exclude(ma_ca_thi__in=payload_ids).values_list('ma_ca_thi', flat=True))
                if deleted_ca_thi_ids:
                    # Xóa dọn dẹp liên kết ca thi
                    BienBanViPham.objects.filter(lich_thi__ca_thi_id__in=deleted_ca_thi_ids).delete()
                    TuiPhach.objects.filter(tui_bai_thi__lich_thi__ca_thi_id__in=deleted_ca_thi_ids).delete()
                    TuiBaiThi.objects.filter(lich_thi__ca_thi_id__in=deleted_ca_thi_ids).delete()
                    DotInSao.objects.filter(ca_thi_id__in=deleted_ca_thi_ids).delete()
                    PhanCongCoiThi.objects.filter(lich_thi__ca_thi_id__in=deleted_ca_thi_ids).delete()
                    DanhSachThiSinh.objects.filter(lich_thi__ca_thi_id__in=deleted_ca_thi_ids).delete()
                    LichThi.objects.filter(ca_thi_id__in=deleted_ca_thi_ids).delete()
                    CaThi.objects.filter(ma_ca_thi__in=deleted_ca_thi_ids).delete()
                
                for ct in data["caThiData"]:
                    ky_thi_obj = None
                    if ct.get("kyThiId"):
                        ky_thi_obj = KyThi.objects.filter(ma_ky_thi=ct.get("kyThiId")).first()
                    if not ky_thi_obj:
                        ky_thi_obj = KyThi.objects.first()

                    CaThi.objects.update_or_create(
                        ma_ca_thi=ct["id"],
                        defaults={
                            "ky_thi": ky_thi_obj,
                            "ten_ca": ct.get("name", ""),
                            "ngay_thi": safe_parse_date(ct.get("date")),
                            "gio_bat_dau": parse_time(ct.get("start")) if (ct.get("start") and parse_time(ct.get("start"))) else "00:00",
                            "gio_ket_thuc": parse_time(ct.get("end")) if (ct.get("end") and parse_time(ct.get("end"))) else "00:00",
                            "note": ct.get("note", "")
                        }
                    )
            
            # 10. Đồng bộ phongThiData -> PhongThi
            if "phongThiData" in data:
                payload_ids = [pt["id"] for pt in data["phongThiData"]]
                deleted_phong_ids = list(PhongThi.objects.exclude(ma_phong__in=payload_ids).values_list('ma_phong', flat=True))
                if deleted_phong_ids:
                    LichThi.objects.filter(phong_thi_id__in=deleted_phong_ids).update(phong_thi=None)
                    PhongThi.objects.filter(ma_phong__in=deleted_phong_ids).delete()
                
                for pt in data["phongThiData"]:
                    PhongThi.objects.update_or_create(
                        ma_phong=pt["id"],
                        defaults={
                            "ten_phong": pt.get("ten", ""),
                            "suc_chua": pt.get("sucChua", 0),
                            "vi_tri": pt.get("viTri", ""),
                            "loai_phong": pt.get("loai", "Phòng thường"),
                            "trang_thai": pt.get("trangThai", "Khả dụng"),
                            "ghi_chu": ""
                        }
                    )
            
            # 11. Đồng bộ inSaoData -> DotInSao, NhatKyInSao, BienBanGiamSatInSao
            if "inSaoData" in data:
                payload_ids = [isd["id"] for isd in data["inSaoData"]]
                deleted_in_sao_ids = list(DotInSao.objects.exclude(ma_dot_in_sao__in=payload_ids).values_list('ma_dot_in_sao', flat=True))
                if deleted_in_sao_ids:
                    BienBanGiamSatInSao.objects.filter(dot_in_sao_id__in=deleted_in_sao_ids).delete()
                    NhatKyInSao.objects.filter(dot_in_sao_id__in=deleted_in_sao_ids).delete()
                    DotInSao.objects.filter(ma_dot_in_sao__in=deleted_in_sao_ids).delete()
                
                req_user = getattr(request, 'user', None)
                if req_user and not req_user.is_authenticated:
                    req_user = None

                for isd in data["inSaoData"]:
                    user_sys = req_user or User.objects.filter(role="tkt").first()
                    if not user_sys:
                        user_sys, _ = User.objects.get_or_create(username="tkt_system", defaults={"role": "tkt", "full_name": "Tổ Khảo thí"})

                    lt_obj = LichThi.objects.filter(ma_lich_thi=isd.get("ltId")).first()
                    
                    client_status = isd.get("trangThai", "Chờ cập nhật")
                    db_status = "ChoCapNhat"
                    if client_status == "Chờ xác nhận":
                        db_status = "DaCapNhat"
                    elif client_status == "Hoàn tất":
                        db_status = "HoanTat"
                    elif client_status == "Cần xử lý lại":
                        db_status = "CanXuLyLai"
                    elif client_status == "Từ chối xác nhận":
                        db_status = "TuChoi"
                        
                    ky_thi_obj = lt_obj.ky_thi if (lt_obj and lt_obj.ky_thi) else KyThi.objects.first()
                    if not ky_thi_obj:
                        ky_thi_obj, _ = KyThi.objects.get_or_create(
                            ma_ky_thi="KT-HK3-2026",
                            defaults={"ten_ky_thi": "Thi cuối kỳ học kỳ III", "nam_hoc": "2025-2026", "hoc_ky": "Học kỳ III"}
                        )

                    hp_obj = lt_obj.lop_hp.hoc_phan if (lt_obj and lt_obj.lop_hp and lt_obj.lop_hp.hoc_phan) else None
                    if not hp_obj and isd.get("subjectName"):
                        hp_obj = HocPhan.objects.filter(ten_hoc_phan=isd.get("subjectName")).first()
                    if not hp_obj and isd.get("subjectName"):
                        hp_obj, _ = HocPhan.objects.get_or_create(ma_hoc_phan=f"HP-{isd['id']}", defaults={"ten_hoc_phan": isd.get("subjectName")})

                    giam_sat_user = User.objects.filter(username=isd.get("giamSat")).first() or User.objects.filter(full_name=isd.get("giamSat")).first() or user_sys

                    dt_time = None
                    if isd.get("ngay"):
                        dt_time = parse_datetime(isd.get("ngay") + "T00:00:00") if "T" not in isd.get("ngay") else parse_datetime(isd.get("ngay"))
                        if not dt_time:
                            d = safe_parse_date(isd.get("ngay"))
                            if d:
                                dt_time = datetime.combine(d, datetime.min.time())

                    dis_obj, _ = DotInSao.objects.update_or_create(
                        ma_dot_in_sao=isd["id"],
                        defaults={
                            "ky_thi": ky_thi_obj,
                            "ca_thi": lt_obj.ca_thi if (lt_obj and lt_obj.ca_thi) else None,
                            "phong_thi": lt_obj.phong_thi if (lt_obj and lt_obj.phong_thi) else None,
                            "hoc_phan": hp_obj,
                            "nguoi_tao": user_sys,
                            "so_luong_ban_in": int(isd.get("soLuong", 0) or 0),
                            "thoi_gian_in_sao": dt_time or timezone.now(),
                            "noi_in_sao": isd.get("noiIn", ""),
                            "can_bo_giam_sat": giam_sat_user,
                            "ghi_chu": isd.get("ghiChu", ""),
                            "trang_thai": db_status
                        }
                    )
                        
                    if client_status == "Hoàn tất":
                        from django.utils import timezone
                        BienBanGiamSatInSao.objects.update_or_create(
                            dot_in_sao=dis_obj,
                            defaults={
                                "trang_thai": "DaXacNhan",
                                "nguoi_xac_nhan": req_user,
                                "nhan_xet_giam_sat": isd.get("nhanXetGiamSat", ""),
                                "chu_ky_so": isd.get("chuKySo", ""),
                                "ngay_xac_nhan": timezone.now()
                            }
                        )
                    elif client_status == "Cần xử lý lại" or client_status == "Từ chối xác nhận":
                        from django.utils import timezone
                        BienBanGiamSatInSao.objects.update_or_create(
                            dot_in_sao=dis_obj,
                            defaults={
                                "trang_thai": "TuChoi",
                                "nguoi_xac_nhan": req_user,
                                "nhan_xet_giam_sat": isd.get("ghiChuKiemTra", "") or isd.get("nhanXetGiamSat", ""),
                                "chu_ky_so": "",
                                "ngay_xac_nhan": timezone.now()
                            }
                        )
                    elif client_status == "Chờ xác nhận":
                        BienBanGiamSatInSao.objects.update_or_create(
                            dot_in_sao=dis_obj,
                            defaults={
                                "trang_thai": "ChoXacNhan",
                                "nguoi_xac_nhan": None,
                                "nhan_xet_giam_sat": "",
                                "chu_ky_so": "",
                                "ngay_xac_nhan": None
                            }
                        )
                
                    if isd.get("nkThoiGian"):
                        from django.utils import timezone
                        NhatKyInSao.objects.update_or_create(
                            dot_in_sao=dis_obj,
                            defaults={
                                "thoi_gian_thuc_hien": parse_datetime(isd["nkThoiGian"]) or timezone.now(),
                                "nguoi_thuc_hien": User.objects.filter(username=isd.get("nkNguoiIn")).first() or user_sys,
                                "nguoi_giam_sat": user_sys,
                                "so_luong_in_thuc_te": int(isd.get("nkSoLuong", 0) or 0),
                                "so_luong_niem_phong": int(isd.get("nkNiemPhong", 0) or 0),
                                "ghi_chu": isd.get("nkGhiChu", ""),
                                "ket_qua_kiem_tra": isd.get("ketQuaKiemTra", ""),
                                "ghi_chu_kiem_tra": isd.get("ghiChuKiemTra", "")
                            }
                        )
            
            # 12. Đồng bộ deThiData -> DeThi, NopDeThi, RaSoatDeThi
            if "deThiData" in data:
                payload_ids = [dt["id"] for dt in data["deThiData"]]
                DeThi.objects.exclude(ma_de_thi__in=payload_ids).delete()
                
                for dt in data["deThiData"]:
                    hp_name = dt.get("hocPhan", "")
                    import re
                    match = re.search(r'\(([^)]+)\)', hp_name)
                    if match:
                        hp_code = match.group(1)
                    else:
                        hp_code = hp_name
                        
                    hp_obj, _ = HocPhan.objects.get_or_create(ma_hoc_phan=hp_code, defaults={"ten_hoc_phan": hp_name})
                    
                    # Map frontend display string -> DB enum value
                    trang_thai_map = {"Chờ rà soát": "ChoRaSoat", "Đạt": "Dat", "Chờ chỉnh sửa": "ChoChinhSua"}
                    trang_thai_val = trang_thai_map.get(dt.get("trangThai", ""), dt.get("trangThai", "ChoRaSoat"))
                    dethi_obj, _ = DeThi.objects.update_or_create(
                        ma_de_thi=dt["id"],
                        defaults={
                            "hoc_phan": hp_obj,
                            "trang_thai": trang_thai_val
                        }
                    )
                    
                    if dt.get("nguoiNop") or dt.get("fileName"):
                        gv_user = User.objects.filter(full_name=dt.get("nguoiNop")).first()
                        if not gv_user:
                            gv_user, _ = User.objects.get_or_create(username="gv_default", defaults={"role": "gv", "full_name": dt.get("nguoiNop") or "Giảng viên"})
                            
                        NopDeThi.objects.update_or_create(
                            de_thi=dethi_obj,
                            defaults={
                                "nguoi_nop": gv_user,
                                "tep_dinh_kem": dt.get("fileName", "")
                            }
                        )
                        
                    if dt.get("nhanXet") or dt.get("ghiChu"):
                        rs_user = User.objects.filter(role="dvcm").first()
                        if not rs_user:
                            rs_user, _ = User.objects.get_or_create(username="dvcm_default", defaults={"role": "dvcm", "full_name": "Giáo vụ Khoa"})
                            
                        RaSoatDeThi.objects.update_or_create(
                            de_thi=dethi_obj,
                            defaults={
                                "nguoi_rao_soat": rs_user,
                                "ket_qua": dt.get("nhanXet", ""),
                                "ghi_chu": dt.get("ghiChu", "")
                            }
                        )

                sys_cfgs = json.loads(getattr(state, 'system_configs', '{}') or '{}')
                de_statuses = sys_cfgs.get("deThiStatuses", {})
                for dt in data["deThiData"]:
                    if dt.get("id"):
                        de_statuses[dt["id"]] = {
                            "trangThai": dt.get("trangThai"),
                            "approver": dt.get("approver"),
                            "approvedAt": dt.get("approvedAt"),
                            "lyDoTuChoi": dt.get("lyDoTuChoi"),
                            "rejectedAt": dt.get("rejectedAt")
                        }
                sys_cfgs["deThiStatuses"] = de_statuses
                state.system_configs = json.dumps(sys_cfgs, ensure_ascii=False)
                state.save()

            # 13. Đồng bộ lichThiData -> LichThi, LopHocPhan, PhanCongCoiThi
            if "lichThiData" in data:
                payload_ids = [lt["id"] for lt in data["lichThiData"] if lt.get("id")]
                # Xóa dọn dẹp các lịch thi không nằm trong payload gửi lên
                deleted_lich_thi_ids = list(LichThi.objects.exclude(ma_lich_thi__in=payload_ids).values_list('ma_lich_thi', flat=True))
                if deleted_lich_thi_ids:
                    BienBanViPham.objects.filter(lich_thi_id__in=deleted_lich_thi_ids).delete()
                    TuiPhach.objects.filter(tui_bai_thi__lich_thi_id__in=deleted_lich_thi_ids).delete()
                    TuiBaiThi.objects.filter(lich_thi_id__in=deleted_lich_thi_ids).delete()
                    PhanCongCoiThi.objects.filter(lich_thi_id__in=deleted_lich_thi_ids).delete()
                    DanhSachThiSinh.objects.filter(lich_thi_id__in=deleted_lich_thi_ids).delete()
                    LichThi.objects.filter(ma_lich_thi__in=deleted_lich_thi_ids).delete()
                
                for lt in data["lichThiData"]:
                    lt_id = lt.get("id")
                    if not lt_id:
                        continue
                        
                    # 1. Tìm CaThi phù hợp
                    ca_thi_obj = None
                    if lt.get("caThiId"):
                        ca_thi_obj = CaThi.objects.filter(ma_ca_thi=lt.get("caThiId")).first()
                    if not ca_thi_obj:
                        ca_thi_obj = CaThi.objects.filter(
                            ngay_thi=safe_parse_date(lt.get("date")),
                            ten_ca=lt.get("shiftName")
                        ).first()
                    if not ca_thi_obj:
                        ca_thi_obj = CaThi.objects.first()
                        
                    if not ca_thi_obj:
                        continue
                        
                    # 2. Xử lý Kỳ thi đảm bảo không bị NULL (tránh lỗi NOT NULL constraint)
                    ky_thi_obj = ca_thi_obj.ky_thi if (ca_thi_obj and ca_thi_obj.ky_thi) else KyThi.objects.first()
                    if not ky_thi_obj:
                        ky_thi_obj, _ = KyThi.objects.get_or_create(
                            ma_ky_thi="KT-HK3-2026",
                            defaults={"ten_ky_thi": "Thi cuối kỳ học kỳ III", "nam_hoc": "2025-2026", "hoc_ky": "Học kỳ III"}
                        )
                        
                    # 3. Tìm/tạo Học phần
                    hp_obj = None
                    if lt.get("subjectCode"):
                        hp_obj = HocPhan.objects.filter(ma_hoc_phan=lt.get("subjectCode")).first()
                    if not hp_obj:
                        import re
                        subj_name = lt.get("subjectName", "")
                        match = re.search(r'\(([^)]+)\)', subj_name)
                        if match:
                            hp_code = match.group(1)
                            hp_obj = HocPhan.objects.filter(ma_hoc_phan=hp_code).first()
                        else:
                            hp_obj = HocPhan.objects.filter(ten_hoc_phan=subj_name).first()
                    if not hp_obj:
                        hp_code = lt.get("subjectCode") or "HP-UNKNOWN"
                        hp_name = lt.get("subjectName") or "Môn học chưa rõ"
                        hp_obj, _ = HocPhan.objects.get_or_create(ma_hoc_phan=hp_code, defaults={"ten_hoc_phan": hp_name})
                        
                    # 4. Tìm/tạo Lớp học phần
                    lhp_id = lt_id if lt_id.startswith("LHP-") else f"LHP-{hp_obj.ma_hoc_phan}"
                    lhp, _ = LopHocPhan.objects.get_or_create(
                        ma_lop_hp=lhp_id,
                        defaults={
                            "hoc_phan": hp_obj,
                            "hoc_ky": ky_thi_obj.hoc_ky,
                            "nam_hoc": ky_thi_obj.nam_hoc
                        }
                    )
                    
                    # 5. Tìm/tạo Phòng thi
                    pt_obj = None
                    room_name = lt.get("room")
                    if room_name:
                        pt_obj = PhongThi.objects.filter(ma_phong=room_name).first()
                        if not pt_obj:
                            pt_obj = PhongThi.objects.filter(ten_phong=room_name).first()
                        if not pt_obj:
                            pt_obj, _ = PhongThi.objects.get_or_create(ma_phong=room_name, defaults={"ten_phong": room_name, "suc_chua": 40})
                            
                    # 6. Lưu dữ liệu Lịch thi
                    parsed_date = safe_parse_date(lt.get("date")) or ca_thi_obj.ngay_thi or safe_parse_date("2026-07-12")
                    lt_obj, _ = LichThi.objects.update_or_create(
                        ma_lich_thi=lt_id,
                        defaults={
                            "ky_thi": ky_thi_obj,
                            "lop_hp": lhp,
                            "ca_thi": ca_thi_obj,
                            "phong_thi": pt_obj,
                            "ngay_thi": parsed_date,
                            "so_luong_sv": lt.get("papers") or 30
                        }
                    )
                    
                    # 7. Phân công giảng viên coi thi
                    gv_obj = None
                    teacher_val = lt.get("teacher", "")
                    if lt.get("teacherId"):
                        gv_obj = GiangVien.objects.filter(ma_giang_vien=lt.get("teacherId")).first()
                    if not gv_obj and teacher_val:
                        import re
                        match = re.search(r'\(([^)]+)\)', teacher_val)
                        if match:
                            gv_code = match.group(1)
                            gv_obj = GiangVien.objects.filter(ma_giang_vien=gv_code).first()
                        else:
                            gv_obj = GiangVien.objects.filter(ho_ten=teacher_val).first()
                            
                    if gv_obj:
                        PhanCongCoiThi.objects.update_or_create(
                            lich_thi=lt_obj,
                            can_bo=gv_obj,
                            defaults={
                                "vai_tro": "Coi thi 1",
                                "actual_hours": 2.0,
                                "is_confirmed": True
                            }
                        )

                sys_cfgs = json.loads(getattr(state, 'system_configs', '{}') or '{}')
                lich_statuses = sys_cfgs.get("lichThiStatuses", {})
                for lt in data["lichThiData"]:
                    if lt.get("id"):
                        lich_statuses[lt["id"]] = {
                            "status": lt.get("status"),
                            "approver": lt.get("approver"),
                            "approvedAt": lt.get("approvedAt"),
                            "lyDoTuChoi": lt.get("lyDoTuChoi"),
                            "rejectedAt": lt.get("rejectedAt")
                        }
                sys_cfgs["lichThiStatuses"] = lich_statuses
                state.system_configs = json.dumps(sys_cfgs, ensure_ascii=False)
                state.save()

            if "danhSachThiData" in data:
                state.danh_sach_thi_data = json.dumps(data["danhSachThiData"], ensure_ascii=False)
                state.save()

            if "donGiaRulesData" in data:
                sys_cfgs = json.loads(getattr(state, 'system_configs', '{}') or '{}')
                sys_cfgs["donGiaRulesData"] = data["donGiaRulesData"]
                state.system_configs = json.dumps(sys_cfgs, ensure_ascii=False)
                state.save()

            if "phanCongPhongData" in data:
                sys_cfgs = json.loads(getattr(state, 'system_configs', '{}') or '{}')
                sys_cfgs["phanCongPhongData"] = data["phanCongPhongData"]
                state.system_configs = json.dumps(sys_cfgs, ensure_ascii=False)
                state.save()

            if "inSaoData" in data:
                sys_cfgs = json.loads(getattr(state, 'system_configs', '{}') or '{}')
                sys_cfgs["inSaoData"] = data["inSaoData"]
                state.system_configs = json.dumps(sys_cfgs, ensure_ascii=False)
                state.save()

            # 7. Lưu cấu hình hệ thống trực tiếp vào AppState (chữ ký số và thời gian)
            if "systemConfigsData" in data:
                sys_cfgs = json.loads(getattr(state, 'system_configs', '{}') or '{}')
                sys_cfgs.update(data["systemConfigsData"])
                state.system_configs = json.dumps(sys_cfgs, ensure_ascii=False)
                state.save()
                sync_configs_to_db(data["systemConfigsData"])
                
            return JsonResponse({"status": "success"})
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)


def export_pdf_view(request):
    from django.http import HttpResponse
    p_id = request.GET.get('id')
    if not p_id:
        return HttpResponse("Thiếu mã phiếu bàn giao", status=400)
        
    pgn = PhieuGiaoNhan.objects.filter(ma_phieu=p_id).first()
    if not pgn:
        return HttpResponse(f"Không tìm thấy phiếu bàn giao {p_id}", status=404)
        
    rooms = list(pgn.chi_tiet.filter(lich_thi__isnull=False).values_list('lich_thi_id', flat=True))
    bags = list(pgn.chi_tiet.filter(tui_phach__isnull=False).values_list('tui_phach_id', flat=True))
    
    phieu = {
        "id": pgn.ma_phieu,
        "type": pgn.loai_phieu,
        "flow": f"{pgn.nguoi_giao.username.upper()} ➔ {pgn.nguoi_nhan.username.upper()}",
        "qty": f"{len(rooms)} phòng" if rooms else f"{len(bags)} túi",
        "status": pgn.trang_thai,
        "rooms": rooms or None,
        "bags": bags or None,
        "sender": pgn.nguoi_giao.username,
        "recipient": pgn.nguoi_nhan.username,
        "attachments": [pgn.tep_dinh_kem] if pgn.tep_dinh_kem else [],
        "log": pgn.log_xac_nhan or ""
    }
    
    actor_names = {
        "tkt": "Tổ Khảo thí (VNUK)",
        "tkct": "Thư ký Chấm thi",
        "ldp": "Trưởng phòng Khảo thí",
        "dvcm": "Đơn vị Chuyên môn / Giáo vụ Khoa",
        "gv": "Giảng viên / CB Chấm thi",
        "tkcoithi": "Thư ký Ban Coi thi",
        "cvht": "Chuyên viên Hệ thống"
    }
    
    sender_name = actor_names.get(phieu.get('sender'), phieu.get('sender', 'Không rõ'))
    recipient_name = actor_names.get(phieu.get('recipient'), phieu.get('recipient', 'Không rõ'))
    
    context = {
        "phieu": phieu,
        "sender_name": sender_name,
        "recipient_name": recipient_name
    }
    return render(request, 'khaothi_app/export_pdf.html', context)


@csrf_exempt
def log_client_error(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            source = data.get('source')
            line = data.get('line')
            col = data.get('col')
            stack = data.get('stack')
            
            print(f"--- CLIENT ERROR LOG ---")
            print(f"Message: {message}")
            print(f"Source: {source} (Line: {line}, Col: {col})")
            print(f"Stack Trace:\n{stack}")
            print(f"------------------------")
            
            if request.user.is_authenticated:
                AuditLog.objects.create(
                    actor=request.user,
                    action=f"Client-side error: {message} at {source}:{line}:{col}"
                )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

