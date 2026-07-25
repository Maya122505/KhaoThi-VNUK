import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from khaothi_app.models import (
    User, Khoa, GiangVien, NhanVien, LopHanhChinh, SinhVien, KyThi, CaThi,
    HocPhan, LopHocPhan, LichThi, DanhSachThiSinh, PhanCongCoiThi, PhongThi,
    TuiBaiThi, TuiPhach, MaPhach, DiemThi, DoiSoatDiem, PhanCongChamThi,
    PhieuGiaoNhan, ChiTietGiaoNhan, DonPhucKhao, AuditLog
)

class Command(BaseCommand):
    help = 'Nạp dữ liệu mẫu toàn diện với số lượng lớn cho ứng dụng Khảo thí'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Bắt đầu quá trình nạp dữ liệu mẫu toàn diện...'))

        self.stdout.write('-> Bước 1/7: Xóa toàn bộ dữ liệu cũ...')
        self.clear_data()

        self.stdout.write('-> Bước 2/7: Tạo Khoa và các tài khoản người dùng cơ bản...')
        users, khoas = self.create_core_users_and_khoa()

        self.stdout.write('-> Bước 3/7: Tạo 40 Giảng viên, 100 Sinh viên, Lớp học...')
        giang_viens = self.create_giang_vien(40, khoas)
        sinh_viens = self.create_sinh_vien(100)

        self.stdout.write('-> Bước 4/7: Tạo 5 Kỳ thi, 10 Học phần, 30 Lịch thi...')
        ky_this = self.create_ky_thi(5)
        hoc_phans = self.create_hoc_phan(10, khoas)
        ca_this = self.create_ca_thi(10, ky_this)
        lich_this = self.create_lich_thi(30, ky_this, hoc_phans, ca_this, sinh_viens)

        self.stdout.write('-> Bước 5/7: Tạo dữ liệu Coi thi và 30 Túi bài thi...')
        self.create_phan_cong_coi_thi(lich_this, giang_viens)
        tui_bai_this = self.create_tui_bai_thi(lich_this)

        self.stdout.write('-> Bước 6/7: Tạo 30 Túi phách và dữ liệu chấm điểm chi tiết...')
        tui_phachs = self.create_tui_phach_and_diem(tui_bai_this, giang_viens)
        
        self.stdout.write('-> Bước 7/7: Tạo dữ liệu quy trình Giao nhận, Phúc khảo và Log...')
        self.create_phieu_giao_nhan(50, users, lich_this, tui_phachs)
        self.create_don_phuc_khao(30, sinh_viens, tui_phachs)
        self.create_audit_logs(users)

        self.stdout.write(self.style.SUCCESS('Hoàn tất việc nạp dữ liệu mẫu! Hệ thống đã sẵn sàng với dữ liệu lớn.'))

    def clear_data(self):
        AuditLog.objects.all().delete()
        ChiTietGiaoNhan.objects.all().delete()
        PhieuGiaoNhan.objects.all().delete()
        DonPhucKhao.objects.all().delete()
        PhanCongChamThi.objects.all().delete()
        DoiSoatDiem.objects.all().delete()
        DiemThi.objects.all().delete()
        MaPhach.objects.all().delete()
        TuiPhach.objects.all().delete()
        TuiBaiThi.objects.all().delete()
        PhanCongCoiThi.objects.all().delete()
        DanhSachThiSinh.objects.all().delete()
        LichThi.objects.all().delete()
        CaThi.objects.all().delete()
        LopHocPhan.objects.all().delete()
        HocPhan.objects.all().delete()
        KyThi.objects.all().delete()
        SinhVien.objects.all().delete()
        LopHanhChinh.objects.all().delete()
        GiangVien.objects.all().delete()
        NhanVien.objects.all().delete()
        Khoa.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_core_users_and_khoa(self):
        khoas = {
            'cntt': Khoa.objects.create(ma_khoa="CNTT", ten_khoa="Công nghệ thông tin"),
            'qtkd': Khoa.objects.create(ma_khoa="QTKD", ten_khoa="Quản trị kinh doanh"),
        }
        users = {}
        roles = {'tkt': 'Tổ Khảo thí', 'tkct': 'Thư ký Chấm thi', 'dvcm': 'Đơn vị Chuyên môn', 'gv': 'Giảng viên', 'ldp': 'Lãnh đạo phòng', 'cvht': 'Cố vấn học tập'}
        for role_code, role_name in roles.items():
            user, _ = User.objects.get_or_create(username=role_code, defaults={'full_name': role_name, 'role': role_code, 'is_staff': True})
            user.set_password('123')
            user.save()
            users[role_code] = user
            if role_code != 'gv':
                NhanVien.objects.create(user=user, ma_nhan_vien=f"NV_{role_code.upper()}", ho_ten=role_name, khoa=khoas['cntt'] if role_code == 'dvcm' else None)
        return users, khoas

    def create_giang_vien(self, count, khoas):
        giang_viens = []
        khoa_list = list(khoas.values())
        ten_giang_vien_list = [
            "TS. Nguyễn Văn An", "ThS. Trần Thị Bích", "PGS.TS. Lê Hoàng Nam", "TS. Phạm Minh Khoa",
            "ThS. Vũ Thị Hương", "TS. Đặng Quốc Hùng", "ThS. Hoàng Anh Tuấn", "TS. Bùi Minh Trí",
            "ThS. Ngô Thanh Sơn", "PGS.TS. Đỗ Đức Thành", "TS. Mai Phương Thảo", "ThS. Dương Văn Phúc",
            "TS. Lý Khánh Hòa", "ThS. Võ Văn Kiệt", "TS. Phan Thanh Bình", "ThS. Trịnh Minh Hải",
            "TS. Hồ Ngọc Hà", "ThS. Đinh Bảo Long", "TS. Nguyễn Thành Nam", "ThS. Cao Quốc Tuấn"
        ]
        for i in range(1, count + 1):
            name = ten_giang_vien_list[(i - 1) % len(ten_giang_vien_list)]
            if i > len(ten_giang_vien_list):
                name = f"{name} {i}"
            user, _ = User.objects.get_or_create(username=f'gv{i:02d}', defaults={'full_name': name, 'role': 'gv'})
            user.set_password('123')
            user.save()
            gv = GiangVien.objects.create(user=user, ma_giang_vien=f'GV{i:02d}', ho_ten=name, khoa=random.choice(khoa_list))
            giang_viens.append(gv)
        return giang_viens

    def create_sinh_vien(self, count):
        lhc, _ = LopHanhChinh.objects.get_or_create(ma_lop='24CS01', ten_lop='Công nghệ phần mềm 01 - Khóa 24')
        ten_sinh_vien_list = [
            "Nguyễn Thị Ánh Tuyết", "Trần Nhật Minh", "Lê Hoàng Phúc", "Phạm Đăng Khoa",
            "Hoàng Thị Thu Hà", "Nguyễn Đức Anh", "Đặng Minh Trí", "Bùi Ngọc Khánh",
            "Vũ Gia Bảo", "Ngô Hải Đăng", "Lý Minh Quân", "Đỗ Phương Linh",
            "Mai Thanh Hằng", "Dương Hoài Nam", "Trịnh Gia Huy", "Phan Quốc Bảo",
            "Hồ Mỹ Duyên", "Đinh Quang Hải", "Võ Thị Quỳnh Như", "Nguyễn Khánh Linh",
            "Lê Tuấn Anh", "Trần Bảo Ngọc", "Phạm Hoàng Yến", "Nguyễn Văn Tâm"
        ]
        sinh_viens = []
        for i in range(1, count + 1):
            name = ten_sinh_vien_list[(i - 1) % len(ten_sinh_vien_list)]
            if i > len(ten_sinh_vien_list):
                name = f"{name} ({i})"
            sv = SinhVien.objects.create(ma_sinh_vien=f'SV{i:03d}', ho_ten=name, lop_hanh_chinh=lhc, is_eligible=(i % 10 != 0))
            sinh_viens.append(sv)
        return sinh_viens

    def create_ky_thi(self, count):
        return [KyThi.objects.create(ma_ky_thi=f'CK-HK{i}-2324', ten_ky_thi=f'Thi cuối kỳ - HK {i} - 2023-2024', nam_hoc='2023-2024', hoc_ky=str(i), trang_thai='DangDienRa') for i in range(1, count + 1)]

    def create_hoc_phan(self, count, khoas):
        khoa_list = list(khoas.values())
        danh_sach_hoc_phan = [
            ("INT1001", "Nhập môn Lập trình"),
            ("INT2001", "Cấu trúc dữ liệu và Giải thuật"),
            ("INT3002", "Lập trình Web & Ứng dụng"),
            ("INT2004", "Hệ quản trị Cơ sở dữ liệu"),
            ("INT2005", "Mạng máy tính & An toàn thông tin"),
            ("INT3010", "Trí tuệ nhân tạo & Học máy"),
            ("BUS1001", "Quản trị Kinh doanh Đại cương"),
            ("MKT2001", "Marketing Căn bản & Kỹ thuật số"),
            ("ENG1003", "Tiếng Anh Giao tiếp Quốc tế 3"),
            ("INT3015", "Quản trị Dự án Phần mềm")
        ]
        hoc_phans = []
        for i in range(1, count + 1):
            ma_hp, ten_hp = danh_sach_hoc_phan[(i - 1) % len(danh_sach_hoc_phan)]
            if i > len(danh_sach_hoc_phan):
                ma_hp = f"{ma_hp}_{i}"
                ten_hp = f"{ten_hp} ({i})"
            hp = HocPhan.objects.create(ma_hoc_phan=ma_hp, ma_hp=ma_hp, ten_hoc_phan=ten_hp, khoa=random.choice(khoa_list))
            hoc_phans.append(hp)
        return hoc_phans

    def create_ca_thi(self, count, ky_this):
        return [CaThi.objects.create(ky_thi=random.choice(ky_this), ma_ca_thi=f'CA{i:03d}', ten_ca=f'Ca {i}', ngay_thi=timezone.now().date() + timezone.timedelta(days=i % 5), gio_bat_dau=f'{7 + (i%3)*2}:30', gio_ket_thuc=f'{9 + (i%3)*2}:00') for i in range(1, count + 1)]

    def create_lich_thi(self, count, ky_this, hoc_phans, ca_this, sinh_viens):
        phong_this = [PhongThi.objects.get_or_create(ma_phong=f'P{101+i}', ten_phong=f'Phòng {101+i}')[0] for i in range(10)]
        lich_this = []
        for i in range(1, count + 1):
            hp = random.choice(hoc_phans)
            lop_hp, _ = LopHocPhan.objects.get_or_create(ma_lop_hp=f'LHP-{hp.ma_hoc_phan}-{i:02d}', hoc_phan=hp, hoc_ky='1', nam_hoc='2023-2024')
            so_sv = random.randint(20, 40)
            lt = LichThi.objects.create(ma_lich_thi=f'LT-{i:03d}', ky_thi=random.choice(ky_this), lop_hp=lop_hp, ca_thi=random.choice(ca_this), phong_thi=random.choice(phong_this), ngay_thi=timezone.now().date() + timezone.timedelta(days=i % 5), so_luong_sv=so_sv, trang_thai_bai_thi='DaNhanBai')
            sv_this = random.sample(sinh_viens, so_sv)
            for j, sv in enumerate(sv_this):
                DanhSachThiSinh.objects.create(lich_thi=lt, sinh_vien=sv, sbd=f'SBD{lt.pk}{j+1:03d}')
            lich_this.append(lt)
        return lich_this

    def create_phan_cong_coi_thi(self, lich_this, giang_viens):
        for lt in lich_this:
            gvs = random.sample(giang_viens, 2)
            PhanCongCoiThi.objects.create(lich_thi=lt, can_bo=gvs[0], vai_tro='Cán bộ coi thi 1', is_confirmed=random.choice([True, False]))
            PhanCongCoiThi.objects.create(lich_thi=lt, can_bo=gvs[1], vai_tro='Cán bộ coi thi 2', is_confirmed=random.choice([True, False]))

    def create_tui_bai_thi(self, lich_this):
        return [TuiBaiThi.objects.create(ma_tui_bai=f'TBT-{lt.ma_lich_thi}', lich_thi=lt, so_luong_bai=lt.so_luong_sv, trang_thai='DaThuHoi') for lt in lich_this]

    def create_tui_phach_and_diem(self, tui_bai_this, giang_viens):
        tui_phachs = []
        for i, tbt in enumerate(tui_bai_this):
            trang_thai = random.choice(['MoiTao', 'DaGiaoDVCM', 'DangCham', 'ChoKhopDiem'])
            tp = TuiPhach.objects.create(ma_tui=f'TP-{i:03d}', hoc_phan=tbt.lich_thi.lop_hp.hoc_phan, so_luong_bai=tbt.so_luong_bai, trang_thai=trang_thai)
            tui_phachs.append(tp)
            
            danh_sach_thi_sinh = list(tbt.lich_thi.danh_sach_thi_sinh.all())
            for j, ts in enumerate(danh_sach_thi_sinh):
                MaPhach.objects.create(ma_phach=f"PH{tp.pk}{j+1:04d}", tui_phach=tp, thi_sinh=ts)

            if trang_thai in ['DangCham', 'ChoKhopDiem']:
                gvs = random.sample(giang_viens, 2)
                PhanCongChamThi.objects.create(tui_phach=tp, giang_vien=gvs[0], vai_tro='Grader 1')
                PhanCongChamThi.objects.create(tui_phach=tp, giang_vien=gvs[1], vai_tro='Grader 2')
                if trang_thai == 'ChoKhopDiem':
                    for mp in tp.danh_sach_phach.all():
                        diem1 = round(random.uniform(4.0, 9.5), 1)
                        diem2 = diem1 if random.random() > 0.3 else round(random.uniform(4.0, 9.5), 1)
                        DiemThi.objects.create(ma_phach=mp, lan_cham=1, diem=diem1, can_bo=gvs[0])
                        DiemThi.objects.create(ma_phach=mp, lan_cham=2, diem=diem2, can_bo=gvs[1])
                        DoiSoatDiem.objects.create(ma_phach=mp, diem_lan_1=diem1, diem_lan_2=diem2, chenh_lech=abs(diem1-diem2), trang_thai='Lech' if diem1 != diem2 else 'Khop')
        return tui_phachs

    def create_phieu_giao_nhan(self, count, users, lich_this, tui_phachs):
        user_tkt = users.get('tkt')
        user_tkct = users.get('tkct')
        user_dvcm = users.get('dvcm')
        user_gv = users.get('gv')

        flow_map = [
            ('TKT_TO_TKCT', user_tkt, user_tkct),
            ('TKCT_TO_TKT', user_tkct, user_tkt),
            ('TKT_TO_DVCM', user_tkt, user_dvcm),
            ('DVCM_TO_GV', user_dvcm, user_gv),
            ('GV_TO_DVCM', user_gv, user_dvcm),
            ('DVCM_TO_TKT', user_dvcm, user_tkt),
            ('TKT_TO_PK', user_tkt, user_dvcm),
        ]

        for i in range(1, count + 1):
            loai_code, default_giao, default_nhan = flow_map[(i - 1) % len(flow_map)]
            nguoi_giao = default_giao or list(users.values())[0]
            nguoi_nhan = default_nhan or list(users.values())[0]

            st = 'ChoXacNhan' if i % 3 != 0 else 'DaHoanTat'

            phieu = PhieuGiaoNhan.objects.create(
                ma_phieu=f'PGN-2026-{i:03d}',
                nguoi_giao=nguoi_giao,
                nguoi_nhan=nguoi_nhan,
                loai_phieu=loai_code,
                trang_thai=st
            )
            sample_size = random.randint(2, 5)
            if phieu.loai_phieu in ['TKT_TO_TKCT']:
                sampled_lichs = random.sample(list(lich_this), min(sample_size, len(lich_this)))
                for lt in sampled_lichs:
                    ChiTietGiaoNhan.objects.create(phieu=phieu, lich_thi=lt)
            else:
                sampled_tuis = random.sample(list(tui_phachs), min(sample_size, len(tui_phachs)))
                for tp in sampled_tuis:
                    ChiTietGiaoNhan.objects.create(phieu=phieu, tui_phach=tp)

    def create_don_phuc_khao(self, count, sinh_viens, tui_phachs):
        all_phachs = list(MaPhach.objects.select_related('thi_sinh__sinh_vien', 'tui_phach__hoc_phan', 'tui_phach').all())
        sampled = random.sample(all_phachs, min(count, len(all_phachs))) if all_phachs else []
        statuses = ['ChuaRutBai', 'ChuaRutBai', 'DangXuLy', 'DaHoanThanh']
        for i, mp in enumerate(sampled, 1):
            sv = mp.thi_sinh.sinh_vien if (mp.thi_sinh and mp.thi_sinh.sinh_vien) else random.choice(sinh_viens)
            hp = mp.tui_phach.hoc_phan if mp.tui_phach else None
            DonPhucKhao.objects.create(
                ma_don=f'PK-{i:03d}',
                sinh_vien=sv,
                hoc_phan=hp,
                ma_phach=mp,
                diem_goc=round(random.uniform(3.5, 5.5), 2),
                trang_thai=statuses[i % len(statuses)],
                ly_do='Mong xem xét và phúc khảo lại bài thi học phần'
            )
    
    def create_audit_logs(self, users):
        user_list = list(users.values())
        for i in range(30):
            AuditLog.objects.create(
                actor=random.choice(user_list),
                action=f"Hành động mẫu số {i+1} đã được thực hiện.",
                ip_address="127.0.0.1"
            )
