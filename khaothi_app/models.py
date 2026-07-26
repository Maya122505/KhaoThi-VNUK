from django.db import models
from django.contrib.auth.models import AbstractUser

# ===================================================================
# 1. MODELS: Người dùng và Phân quyền
# ===================================================================

class User(AbstractUser):
    """
    Mở rộng model User mặc định của Django để thêm vai trò.
    """
    ROLE_CHOICES = (
        ('tkt', 'Tổ Khảo thí'),
        ('tkct', 'Thư ký Chấm thi'),
        ('dvcm', 'Đơn vị Chuyên môn'),
        ('gv', 'Giảng viên'),
        ('ldp', 'Lãnh đạo phòng'),
        ('cvht', 'Cố vấn học tập / Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Họ và Tên")

    def __str__(self):
        return self.username


class Khoa(models.Model):
    """
    Khoa / Đơn vị quản lý chuyên môn trong trường. VD: CNTT, QTKD.
    """
    ma_khoa = models.CharField(max_length=50, primary_key=True)
    ten_khoa = models.CharField(max_length=255)

    def __str__(self):
        return self.ten_khoa


class GiangVien(models.Model):
    """
    Thông tin hồ sơ cá nhân của Giảng viên/Cán bộ, liên kết 1-1 với tài khoản User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='giang_vien_profile', null=True, blank=True)
    ma_giang_vien = models.CharField(max_length=50, primary_key=True)
    ho_ten = models.CharField(max_length=255)
    khoa = models.ForeignKey(Khoa, on_delete=models.PROTECT, related_name='giang_vien', null=True, blank=True)
    sdt = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.ho_ten


class NhanVien(models.Model):
    """
    Thông tin hồ sơ cá nhân của cán bộ hành chính hệ thống (TKT, LDP, DVCM, TKCT, v.v.).
    Liên kết 1-1 với tài khoản User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nhan_vien_profile', null=True, blank=True)
    ma_nhan_vien = models.CharField(max_length=50, primary_key=True)
    ho_ten = models.CharField(max_length=255)
    don_vi = models.CharField(max_length=255, null=True, blank=True)  # VD: Phòng Khảo thí
    khoa = models.ForeignKey(Khoa, on_delete=models.PROTECT, related_name='nhan_vien', null=True, blank=True)  # VD: Khoa CNTT
    sdt = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.ho_ten} ({self.ma_nhan_vien})"


# ===================================================================
# 2. STUDENT & CLASS MODELS: Sinh viên và Lớp
# ===================================================================

class LopHanhChinh(models.Model):
    """
    Lớp hành chính của sinh viên. VD: 24CS01.
    """
    ma_lop = models.CharField(max_length=50, primary_key=True)
    ten_lop = models.CharField(max_length=255)
    nganh = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.ten_lop


class SinhVien(models.Model):
    """
    Thông tin sinh viên và tình trạng công nợ học phí/đủ điều kiện.
    """
    ma_sinh_vien = models.CharField(max_length=50, primary_key=True)
    ho_ten = models.CharField(max_length=255)
    lop_hanh_chinh = models.ForeignKey(LopHanhChinh, on_delete=models.PROTECT, related_name='sinh_vien', null=True, blank=True)
    debt = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    is_eligible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ho_ten} ({self.ma_sinh_vien})"


# ===================================================================
# 3. EXAMINATION STRUCTURE MODELS: Cấu trúc kỳ thi, học phần, lịch thi
# ===================================================================

class KyThi(models.Model):
    """
    Thông tin về một kỳ thi lớn. VD: Thi cuối kỳ HK III 2025-2026.
    """
    ma_ky_thi = models.CharField(max_length=50, primary_key=True)
    ten_ky_thi = models.CharField(max_length=255, verbose_name="Tên Kỳ thi")
    nam_hoc = models.CharField(max_length=20, verbose_name="Năm học")
    hoc_ky = models.CharField(max_length=20, verbose_name="Học kỳ")
    trang_thai = models.CharField(max_length=50, default='DangDienRa')
    dot_thi = models.CharField(max_length=50, blank=True, null=True)
    mo_ta = models.TextField(blank=True, null=True)
    ngay_bat_dau = models.DateField(verbose_name="Ngày bắt đầu", null=True, blank=True)
    ngay_ket_thuc = models.DateField(verbose_name="Ngày kết thúc", null=True, blank=True)

    def __str__(self):
        return self.ten_ky_thi


class HocPhan(models.Model):
    """
    Thông tin học phần/môn học.
    """
    ma_hoc_phan = models.CharField(max_length=50, primary_key=True)
    ma_hp = models.CharField(max_length=50, null=True, blank=True)
    ten_hoc_phan = models.CharField(max_length=255, verbose_name="Tên Học phần")
    so_tin_chi = models.PositiveIntegerField(default=3)
    khoa = models.ForeignKey(Khoa, on_delete=models.PROTECT, related_name='hoc_phan', null=True, blank=True)

    def __str__(self):
        return f"{self.ten_hoc_phan} ({self.ma_hoc_phan})"


class LopHocPhan(models.Model):
    """
    Lớp học phần thực tế mở trong học kỳ.
    """
    ma_lop_hp = models.CharField(max_length=50, primary_key=True)
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE, related_name='lop_hoc_phan')
    hoc_ky = models.CharField(max_length=20)
    nam_hoc = models.CharField(max_length=20)
    giang_vien = models.ForeignKey(GiangVien, on_delete=models.SET_NULL, null=True, blank=True, related_name='lop_hoc_phan')

    def __str__(self):
        return self.ma_lop_hp


class LopHocPhanSinhVien(models.Model):
    """
    Danh sách sinh viên học lớp học phần.
    """
    lop_hp = models.ForeignKey(LopHocPhan, on_delete=models.CASCADE, related_name='sinh_vien_lien_ket')
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name='lop_hp_lien_ket')
    is_eligible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('lop_hp', 'sinh_vien')


class CaThi(models.Model):
    """
    Một ca thi cụ thể trong kỳ thi.
    """
    ma_ca_thi = models.CharField(max_length=50, primary_key=True)
    ky_thi = models.ForeignKey(KyThi, on_delete=models.CASCADE, related_name='ca_thi', null=True, blank=True)
    ten_ca = models.CharField(max_length=100, verbose_name="Tên Ca thi")
    ngay_thi = models.DateField(verbose_name="Ngày thi", null=True, blank=True)
    gio_bat_dau = models.TimeField(verbose_name="Giờ bắt đầu")
    gio_ket_thuc = models.TimeField(verbose_name="Giờ kết thúc")
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.ten_ca} - {self.ngay_thi}"


class PhongThi(models.Model):
    """
    Phòng thi vật lý chuẩn bị cho thi.
    """
    ma_phong = models.CharField(max_length=50, primary_key=True)
    ten_phong = models.CharField(max_length=255)
    loai_phong = models.CharField(max_length=50, null=True, blank=True)
    suc_chua = models.PositiveIntegerField(default=0)
    vi_tri = models.CharField(max_length=255, null=True, blank=True)
    trang_thai = models.CharField(max_length=50, default='Khả dụng')
    ghi_chu = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.ten_phong


class LichThi(models.Model):
    """
    Lịch thi chi tiết ghép Lớp học phần + Ca thi + Phòng thi.
    """
    ma_lich_thi = models.CharField(max_length=50, primary_key=True)
    ky_thi = models.ForeignKey(KyThi, on_delete=models.CASCADE, related_name='lich_thi')
    lop_hp = models.ForeignKey(LopHocPhan, on_delete=models.CASCADE, related_name='lich_thi', null=True, blank=True)
    ca_thi = models.ForeignKey(CaThi, on_delete=models.CASCADE, related_name='lich_thi')
    phong_thi = models.ForeignKey(PhongThi, on_delete=models.CASCADE, related_name='lich_thi', null=True, blank=True)
    ngay_thi = models.DateField()
    so_luong_sv = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.ma_lich_thi


class DanhSachThiSinh(models.Model):
    """
    Danh sách thí sinh chi tiết được xếp vào từng phòng thi.
    """
    lich_thi = models.ForeignKey(LichThi, on_delete=models.CASCADE, related_name='danh_sach_thi_sinh')
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name='lich_thi_tham_gia')
    sbd = models.CharField(max_length=50)
    trang_thai_diem_danh = models.CharField(max_length=50, default='CoMat')
    sbd_ma_phach = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('lich_thi', 'sinh_vien')


# ===================================================================
# 4. COI THI MODELS: Công tác coi thi & vi phạm
# ===================================================================

class PhanCongCoiThi(models.Model):
    """
    Phân công cán bộ coi thi, tích hợp thống kê giờ thực tế.
    """
    lich_thi = models.ForeignKey(LichThi, on_delete=models.CASCADE, related_name='phan_cong_coi_thi')
    can_bo = models.ForeignKey(GiangVien, on_delete=models.CASCADE, related_name='phan_cong_coi_thi')
    vai_tro = models.CharField(max_length=100)
    actual_hours = models.DecimalField(max_digits=4, decimal_places=2, default=2.0)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('lich_thi', 'can_bo')


class BienBanViPham(models.Model):
    """
    Lập biên bản vi phạm quy chế thi của sinh viên tại phòng thi.
    """
    lich_thi = models.ForeignKey(LichThi, on_delete=models.CASCADE, related_name='bien_ban_vi_pham')
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name='bien_ban_vi_pham')
    noi_dung = models.TextField()
    hinh_thuc_xu_ly = models.CharField(max_length=100)
    nguoi_lap = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bien_ban_da_lap')

    class Meta:
        unique_together = ('lich_thi', 'sinh_vien')


# ===================================================================
# 5. DE THI & IN SAO MODELS: Quản lý Đề thi và Đợt in sao
# ===================================================================

class DeThi(models.Model):
    """
    Quản lý Đề thi của học phần.
    """
    ma_de_thi = models.CharField(max_length=50, primary_key=True)
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE, related_name='de_thi')
    trang_thai = models.CharField(max_length=50, default='MoiTao')

    def __str__(self):
        return self.ma_de_thi


class NopDeThi(models.Model):
    """
    Lịch sử giảng viên nộp đề thi.
    """
    de_thi = models.ForeignKey(DeThi, on_delete=models.CASCADE, related_name='nop_de_thi')
    nguoi_nop = models.ForeignKey(User, on_delete=models.PROTECT, related_name='de_thi_da_nop')
    thoi_gian_nop = models.DateTimeField(auto_now_add=True)
    tep_dinh_kem = models.CharField(max_length=255, null=True, blank=True)


class RaSoatDeThi(models.Model):
    """
    Nhật ký rà soát chất lượng đề thi của DVCM/Tổ Khảo thí.
    """
    de_thi = models.ForeignKey(DeThi, on_delete=models.CASCADE, related_name='ra_soat_de_thi')
    nguoi_rao_soat = models.ForeignKey(User, on_delete=models.PROTECT, related_name='de_thi_da_rao_soat')
    ket_qua = models.TextField()
    ghi_chu = models.TextField(null=True, blank=True)


class DotInSao(models.Model):
    """
    Đợt in sao đề thi phục vụ cho các ca thi.
    """
    ma_dot_in_sao = models.CharField(max_length=50, primary_key=True)
    ky_thi = models.ForeignKey(KyThi, on_delete=models.PROTECT, related_name='dot_in_sao')
    ca_thi = models.ForeignKey(CaThi, on_delete=models.PROTECT, related_name='dot_in_sao', null=True, blank=True)
    phong_thi = models.ForeignKey(PhongThi, on_delete=models.PROTECT, related_name='dot_in_sao', null=True, blank=True)
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.PROTECT, related_name='dot_in_sao', null=True, blank=True)
    nguoi_tao = models.ForeignKey(User, on_delete=models.PROTECT, related_name='dot_in_sao_da_tao')
    ngay_tao = models.DateTimeField(auto_now_add=True)
    thoi_gian_in_sao = models.DateTimeField(null=True, blank=True, verbose_name='Thời gian in sao dự kiến')
    noi_in_sao = models.CharField(max_length=255, null=True, blank=True)
    so_luong_ban_in = models.PositiveIntegerField(default=0)
    can_bo_giam_sat = models.ForeignKey(User, on_delete=models.PROTECT, related_name='dot_in_sao_duoc_giam_sat', null=True, blank=True)
    ghi_chu = models.TextField(null=True, blank=True)
    trang_thai = models.CharField(
        max_length=50, 
        default='ChoCapNhat',
        choices=[
            ('ChoCapNhat', 'Chờ cập nhật nhật ký'), 
            ('DaCapNhat', 'Đã cập nhật nhật ký (Chờ xác nhận)'), 
            ('HoanTat', 'Hoàn tất'), 
            ('CanXuLyLai', 'Cần xử lý lại'),
            ('TuChoi', 'Từ chối xác nhận')
        ]
    )

    def __str__(self):
        return self.ma_dot_in_sao


class NhatKyInSao(models.Model):
    """
    Nhật ký thực hiện in sao và giám sát.
    """
    dot_in_sao = models.OneToOneField(DotInSao, on_delete=models.CASCADE, related_name='nhat_ky')
    thoi_gian_thuc_hien = models.DateTimeField(verbose_name='Thời gian thực hiện in sao')
    ngay_cap_nhat = models.DateTimeField(auto_now_add=True)
    nguoi_thuc_hien = models.ForeignKey(User, on_delete=models.PROTECT, related_name='nhat_ky_in_sao_da_lam')
    nguoi_giam_sat = models.ForeignKey(User, on_delete=models.PROTECT, related_name='nhat_ky_in_sao_da_giam_sat')
    so_luong_in_thuc_te = models.PositiveIntegerField(default=0)
    so_luong_niem_phong = models.PositiveIntegerField(default=0)
    ghi_chu = models.TextField(null=True, blank=True)
    
    # Kết quả kiểm tra chất lượng đề sau in sao
    ket_qua_kiem_tra = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[('Khop', 'Khớp'), ('KhongKhop', 'Không khớp')]
    )
    nguoi_kiem_tra = models.ForeignKey(User, on_delete=models.PROTECT, related_name='nhat_ky_in_sao_da_kiem_tra', null=True, blank=True)
    thoi_gian_kiem_tra = models.DateTimeField(null=True, blank=True)
    ghi_chu_kiem_tra = models.TextField(null=True, blank=True)


class ChecklistInSao(models.Model):
    """
    Danh sách checklist chi tiết từng học phần/nhóm đề hoặc tiêu chí chất lượng thuộc đợt in sao.
    """
    LOAI_MUC_CHOICES = (
        ('NhomDe', 'Nhóm đề / Học phần'),
        ('TieuChi', 'Tiêu chí chất lượng'),
    )
    dot_in_sao = models.ForeignKey(DotInSao, on_delete=models.CASCADE, related_name='danh_sach_checklist')
    ma_muc = models.CharField(max_length=50)
    ten_muc = models.CharField(max_length=255, verbose_name="Tên học phần / Tiêu chí checklist")
    nhom_de = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nhóm đề")
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.PROTECT, related_name='checklist_in_sao', null=True, blank=True)
    loai_muc = models.CharField(max_length=20, choices=LOAI_MUC_CHOICES, default='NhomDe')
    so_luong_can_in = models.PositiveIntegerField(default=0)
    so_luong_da_in = models.PositiveIntegerField(default=0)
    so_luong_niem_phong = models.PositiveIntegerField(default=0)
    da_dat = models.BooleanField(default=False, verbose_name="Đạt tiêu chí chất lượng")
    thoi_gian_thuc_hien = models.DateTimeField(null=True, blank=True)
    trang_thai = models.CharField(
        max_length=50,
        default='ChuaIn',
        choices=[('ChuaIn', 'Chưa in'), ('DaInXong', 'Đã in xong')]
    )
    ghi_chu = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.dot_in_sao.ma_dot_in_sao} - {self.ten_muc}"


class BienBanGiamSatInSao(models.Model):
    """
    Biên bản giám sát đợt in sao đề thi.
    """
    dot_in_sao = models.OneToOneField(DotInSao, on_delete=models.CASCADE, related_name='bien_ban_giam_sat')
    trang_thai = models.CharField(
        max_length=50,
        default='ChoXacNhan',
        choices=[
            ('ChoXacNhan', 'Chờ xác nhận'),
            ('DaXacNhan', 'Đã xác nhận'),
            ('TuChoi', 'Từ chối xác nhận')
        ]
    )
    nguoi_xac_nhan = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bien_ban_giam_sat_da_ky', null=True, blank=True)
    nhan_xet_giam_sat = models.TextField(null=True, blank=True, verbose_name='Ý kiến nhận xét giám sát')
    chu_ky_so = models.TextField(null=True, blank=True, verbose_name='Chuỗi chữ ký số xác nhận')
    ngay_xac_nhan = models.DateTimeField(null=True, blank=True)
    ghi_chu = models.TextField(null=True, blank=True)


# ===================================================================
# 6. GRADING PROCESS MODELS: Quy trình làm phách & Chấm thi
# ===================================================================

class TuiBaiThi(models.Model):
    """
    Túi bài thi gốc thu hồi từ phòng thi (LichThi) trước khi dọc phách.
    """
    ma_tui_bai = models.CharField(max_length=50, primary_key=True)
    lich_thi = models.OneToOneField(LichThi, on_delete=models.CASCADE, related_name='tui_bai_thi')
    so_luong_bai = models.PositiveIntegerField(default=0)
    trang_thai = models.CharField(max_length=50, default='DaThuHoi') # DaThuHoi, DaDocPhach

    def __str__(self):
        return self.ma_tui_bai


class TuiPhach(models.Model):
    """
    Một túi phách (bài thi đã dọc phách) giao cho Giám khảo chấm.
    Được tạo ra từ một túi bài thi gốc.
    """
    ma_tui = models.CharField(max_length=50, primary_key=True)
    ca_thi = models.ForeignKey(CaThi, on_delete=models.CASCADE, related_name='tui_phach', null=True, blank=True)
    tui_bai_thi = models.ForeignKey(TuiBaiThi, on_delete=models.SET_NULL, null=True, blank=True, related_name='tui_phach')
    so_luong_bai = models.PositiveIntegerField(default=0)
    mat_khau_khoa = models.CharField(max_length=128, null=True, blank=True)
    trang_thai = models.CharField(max_length=50, default='MoiTao')

    def __str__(self):
        return self.ma_tui


class MaPhach(models.Model):
    """
    Liên kết mã phách bí mật với Thí sinh trong phòng thi và Túi phách.
    """
    ma_phach = models.CharField(max_length=50, primary_key=True)
    tui_phach = models.ForeignKey(TuiPhach, on_delete=models.CASCADE, related_name='danh_sach_phach')
    thi_sinh = models.OneToOneField(DanhSachThiSinh, on_delete=models.CASCADE, related_name='ma_phach', null=True, blank=True)
    trang_thai = models.CharField(max_length=50, default='MoiTao')

    def __str__(self):
        return self.ma_phach


class DiemThi(models.Model):
    """
    Lưu điểm chi tiết các lần chấm của Giám khảo trên mã phách (Tách biệt hoàn toàn).
    """
    ma_phach = models.ForeignKey(MaPhach, on_delete=models.CASCADE, related_name='diem_thi')
    lan_cham = models.PositiveIntegerField()
    diem = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    can_bo = models.ForeignKey(GiangVien, on_delete=models.PROTECT, related_name='diem_thi_da_cham')

    class Meta:
        unique_together = ('ma_phach', 'lan_cham')


class DoiSoatDiem(models.Model):
    """
    Đối soát điểm nhập giữa các lần chấm để tìm chênh lệch.
    """
    ma_phach = models.OneToOneField(MaPhach, on_delete=models.CASCADE, primary_key=True, related_name='doi_soat')
    diem_lan_1 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    diem_lan_2 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    chenh_lech = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    trang_thai = models.CharField(max_length=50, default='ChuaDoiSoat')


class PhanCongChamThi(models.Model):
    """
    Phân công cán bộ chấm thi độc lập cho từng túi phách.
    """
    tui_phach = models.ForeignKey(TuiPhach, on_delete=models.CASCADE, related_name='phan_cong_cham')
    giang_vien = models.ForeignKey(GiangVien, on_delete=models.CASCADE, related_name='phan_cong_cham')
    vai_tro = models.CharField(max_length=50) # VD: Grader 1, Grader 2
    trang_thai = models.CharField(max_length=50, default='ChuaCham')

    class Meta:
        unique_together = ('tui_phach', 'giang_vien', 'vai_tro')


# ===================================================================
# 7. HANDOVER MODELS: Quy trình giao nhận đồ sau thi/chấm thi
# ===================================================================

class PhieuGiaoNhan(models.Model):
    """
    Lưu vết phiếu bàn giao và log lịch sử ký xác nhận số.
    """
    ma_phieu = models.CharField(max_length=50, primary_key=True)
    nguoi_giao = models.ForeignKey(User, on_delete=models.PROTECT, related_name='phieu_giao_set')
    nguoi_nhan = models.ForeignKey(User, on_delete=models.PROTECT, related_name='phieu_nhan_set')
    ngay_giao = models.DateTimeField(auto_now_add=True)
    loai_phieu = models.CharField(max_length=255)
    chu_ky_so = models.CharField(max_length=255, null=True, blank=True)
    tep_dinh_kem = models.CharField(max_length=255, null=True, blank=True)
    log_xac_nhan = models.TextField(null=True, blank=True)
    trang_thai = models.CharField(max_length=50, default='ChoXacNhan')

    def __str__(self):
        return self.ma_phieu


class ChiTietGiaoNhan(models.Model):
    """
    Chi tiết đính kèm của Phiếu bàn giao (hỗ trợ cả Túi phách và Phòng thi gốc).
    """
    phieu = models.ForeignKey(PhieuGiaoNhan, on_delete=models.CASCADE, related_name='chi_tiet')
    tui_phach = models.ForeignKey(TuiPhach, on_delete=models.CASCADE, related_name='giao_nhan_chi_tiet', null=True, blank=True)
    lich_thi = models.ForeignKey(LichThi, on_delete=models.CASCADE, related_name='giao_nhan_chi_tiet', null=True, blank=True)
    tinh_trang = models.CharField(max_length=255, null=True, blank=True)


# ===================================================================
# 8. APPEAL & CONFIG MODELS: Phúc khảo và Điểm thành phần
# ===================================================================

class DonPhucKhao(models.Model):
    """
    Đơn phúc khảo bài thi của sinh viên.
    """
    ma_don = models.CharField(max_length=50, primary_key=True)
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name='don_phuc_khao')
    lich_thi = models.ForeignKey(LichThi, on_delete=models.CASCADE, related_name='don_phuc_khao', null=True, blank=True)
    ma_phach = models.ForeignKey(MaPhach, on_delete=models.CASCADE, related_name='don_phuc_khao', null=True, blank=True)
    diem_goc = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    diem_phuc_khao_1 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    diem_phuc_khao_2 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    diem_phuc_khao_cuoi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ly_do = models.TextField()
    file_bien_ban = models.CharField(max_length=255, null=True, blank=True)
    trang_thai = models.CharField(max_length=50, default='ChoXuLy')


class CauHinhDiemHocPhan(models.Model):
    """
    Cấu hình trọng số và hạn đóng/mở cổng nhập điểm học phần.
    """
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE, related_name='cau_hinh_diem')
    ten_cot_diem = models.CharField(max_length=255)
    trong_so = models.DecimalField(max_digits=5, decimal_places=2)
    thoi_gian_mo_cong = models.DateTimeField(null=True, blank=True)
    thoi_gian_khoa_cong = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('hoc_phan', 'ten_cot_diem')


class DiemThanhPhan(models.Model):
    """
    Bảng điểm thành phần chi tiết của sinh viên.
    """
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name='diem_thanh_phan')
    lop_hp = models.ForeignKey(LopHocPhan, on_delete=models.CASCADE, related_name='diem_thanh_phan')
    cau_hinh = models.ForeignKey(CauHinhDiemHocPhan, on_delete=models.CASCADE, related_name='diem_thanh_phan')
    diem = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        unique_together = ('sinh_vien', 'lop_hp', 'cau_hinh')


# ===================================================================
# 9. SYSTEM CONFIGS, LOGS & COMPATIBILITY
# ===================================================================

class AuditLog(models.Model):
    """
    Nhật ký hệ thống, chỉ ghi (Append-only) phục vụ giám sát kỹ thuật.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='audit_logs')
    action = models.TextField()
    ip_address = models.CharField(max_length=50, null=True, blank=True)


class AppState(models.Model):
    """
    Model lưu trữ trạng thái đồng bộ JSON toàn cục cho toàn bộ hệ thống (Để tương thích ngược).
    """
    key = models.CharField(default='global_state', max_length=50, unique=True)
    phong_thi_goc = models.TextField(default='[]')
    tui_phach = models.TextField(default='[]')
    phieu_giao_nhan = models.TextField(default='[]')
    can_bo_coi_thi = models.TextField(default='[]')
    phuc_khao = models.TextField(default='[]')
    audit_logs = models.TextField(default='[]')
    system_configs = models.TextField(default='{}')
    ky_thi = models.TextField(default='[]')
    ca_thi = models.TextField(default='[]')
    lich_thi = models.TextField(default='[]')
    hoc_phi = models.TextField(default='[]')
    lop_thi_diem = models.TextField(default='{}')

    def __str__(self):
        return f"AppState - {self.key}"


# Giữ lại các model phiên bản cấu hình ban đầu để tương thích ngược nếu có views gọi import
class PhienBanCotDiem(models.Model):
    ma_phien_ban = models.CharField(max_length=50, primary_key=True)
    ten_phien_ban = models.CharField(max_length=255)
    thoi_gian_ap_dung = models.DateTimeField(blank=True, null=True)
    thoi_gian_ket_thuc = models.DateTimeField(blank=True, null=True)
    thoi_gian_cong_bo = models.DateTimeField(blank=True, null=True)
    trang_thai = models.CharField(default='ApDung', max_length=50)
    ma_hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE)

    def __str__(self):
        return self.ten_phien_ban


class CauHinhPhucKhao(models.Model):
    ma_cau_hinh = models.CharField(max_length=50, primary_key=True)
    thoi_gian_mo_cong = models.DateTimeField(blank=True, null=True)
    thoi_gian_khoa_cong = models.DateTimeField(blank=True, null=True)
    han_chot_cham = models.DateTimeField(blank=True, null=True)
    trang_thai = models.CharField(default='KichHoat', max_length=50)
    ma_hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE)

    def __str__(self):
        return self.ma_cau_hinh
