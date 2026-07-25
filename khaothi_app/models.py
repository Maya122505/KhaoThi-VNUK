from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ===================================================================
# 0. ABSTRACT MIXINS: Tái sử dụng cho Audit Timestamps
# ===================================================================

class TimestampMixin(models.Model):
    """Abstract mixin tự động thêm created_at và updated_at cho mọi model kế thừa."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        abstract = True

# ===================================================================
# 1. CORE MODELS: Người dùng và Phân quyền
# ===================================================================

class User(AbstractUser):
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
    ma_khoa = models.CharField(max_length=50, primary_key=True)
    ten_khoa = models.CharField(max_length=255)

    def __str__(self):
        return self.ten_khoa


class BoMon(models.Model):
    """Bộ môn trực thuộc Khoa (VD: Bộ môn CNTT, Bộ môn Khoa học Máy tính)"""
    ma_bo_mon = models.CharField(max_length=50, primary_key=True)
    ten_bo_mon = models.CharField(max_length=255)
    khoa = models.ForeignKey(Khoa, on_delete=models.CASCADE, related_name='bo_mon')

    class Meta:
        verbose_name = "Bộ môn"
        verbose_name_plural = "Bộ môn"

    def __str__(self):
        return f"{self.ten_bo_mon} ({self.khoa.ten_khoa})"


class GiangVien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='giang_vien_profile', null=True, blank=True)
    ma_giang_vien = models.CharField(max_length=50, primary_key=True)
    ho_ten = models.CharField(max_length=255)
    khoa = models.ForeignKey(Khoa, on_delete=models.PROTECT, related_name='giang_vien', null=True, blank=True)
    bo_mon = models.ForeignKey(BoMon, on_delete=models.SET_NULL, related_name='giang_vien', null=True, blank=True)
    sdt = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.ho_ten


class NhanVien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nhan_vien_profile', null=True, blank=True)
    ma_nhan_vien = models.CharField(max_length=50, primary_key=True)
    ho_ten = models.CharField(max_length=255)
    don_vi = models.CharField(max_length=255, null=True, blank=True)
    khoa = models.ForeignKey(Khoa, on_delete=models.PROTECT, related_name='nhan_vien', null=True, blank=True)
    sdt = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.ho_ten} ({self.ma_nhan_vien})"


# ===================================================================
# 2. STUDENT & CLASS MODELS: Sinh viên và Lớp
# ===================================================================

class LopHanhChinh(models.Model):
    ma_lop = models.CharField(max_length=50, primary_key=True)
    ten_lop = models.CharField(max_length=255)
    nganh = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.ten_lop


class SinhVien(models.Model):
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

class KyThi(TimestampMixin):
    STATUS_CHOICES = (
        ('MoiTao', 'Mới tạo'),
        ('DangDienRa', 'Đang diễn ra'),
        ('DaPheDuyet', 'Đã phê duyệt'),
        ('DaKetThuc', 'Đã kết thúc'),
    )
    ma_ky_thi = models.CharField(max_length=50, primary_key=True)
    ten_ky_thi = models.CharField(max_length=255, verbose_name="Tên Kỳ thi")
    nam_hoc = models.CharField(max_length=20, verbose_name="Năm học")
    hoc_ky = models.CharField(max_length=20, verbose_name="Học kỳ")
    trang_thai = models.CharField(max_length=50, choices=STATUS_CHOICES, default='MoiTao')
    dot_thi = models.CharField(max_length=50, blank=True, null=True)
    mo_ta = models.TextField(blank=True, null=True)
    ngay_bat_dau = models.DateField(verbose_name="Ngày bắt đầu", null=True, blank=True)
    ngay_ket_thuc = models.DateField(verbose_name="Ngày kết thúc", null=True, blank=True)
    
    nguoi_tao = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='ky_thi_da_tao', null=True, blank=True, verbose_name="Người tạo")
    nguoi_phe_duyet = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='ky_thi_da_phe_duyet', null=True, blank=True)
    ngay_phe_duyet = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ten_ky_thi


class HocPhan(models.Model):
    ma_hoc_phan = models.CharField(max_length=50, primary_key=True)
    ma_hp = models.CharField(max_length=50, null=True, blank=True)
    ten_hoc_phan = models.CharField(max_length=255, verbose_name="Tên Học phần")
    so_tin_chi = models.PositiveIntegerField(default=3)
    khoa = models.ForeignKey(Khoa, on_delete=models.PROTECT, related_name='hoc_phan', null=True, blank=True)
    bo_mon = models.ForeignKey(BoMon, on_delete=models.SET_NULL, related_name='hoc_phan', null=True, blank=True)

    def __str__(self):
        return f"{self.ten_hoc_phan} ({self.ma_hoc_phan})"


class LopHocPhan(models.Model):
    ma_lop_hp = models.CharField(max_length=50, primary_key=True)
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE, related_name='lop_hoc_phan')
    hoc_ky = models.CharField(max_length=20)
    nam_hoc = models.CharField(max_length=20)
    giang_vien = models.ForeignKey(GiangVien, on_delete=models.SET_NULL, null=True, blank=True, related_name='lop_hoc_phan')

    def __str__(self):
        if self.hoc_phan and self.hoc_phan.ten_hoc_phan:
            return f"{self.hoc_phan.ten_hoc_phan} ({self.ma_lop_hp})"
        return self.ma_lop_hp


class LopHocPhanSinhVien(models.Model):
    lop_hp = models.ForeignKey(LopHocPhan, on_delete=models.CASCADE, related_name='sinh_vien_lien_ket')
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name='lop_hp_lien_ket')
    is_eligible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('lop_hp', 'sinh_vien')


class CaThi(TimestampMixin):
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
    ma_phong = models.CharField(max_length=50, primary_key=True)
    ten_phong = models.CharField(max_length=255)
    loai_phong = models.CharField(max_length=50, null=True, blank=True)
    suc_chua = models.PositiveIntegerField(default=0)
    vi_tri = models.CharField(max_length=255, null=True, blank=True)
    trang_thai = models.CharField(max_length=50, default='KhaDung')
    ghi_chu = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.ten_phong


class LichThi(TimestampMixin):
    ma_lich_thi = models.CharField(max_length=50, primary_key=True)
    ky_thi = models.ForeignKey(KyThi, on_delete=models.CASCADE, related_name='lich_thi')
    lop_hp = models.ForeignKey(LopHocPhan, on_delete=models.CASCADE, related_name='lich_thi', null=True, blank=True)
    ca_thi = models.ForeignKey(CaThi, on_delete=models.CASCADE, related_name='lich_thi')
    phong_thi = models.ForeignKey(PhongThi, on_delete=models.CASCADE, related_name='lich_thi')
    ngay_thi = models.DateField()
    so_luong_sv = models.PositiveIntegerField(default=0)
    
    STATUS_CHOICES = (
        ('ChuaNhanBai', 'Chưa nhận bài'),
        ('DaNhanBai', 'Đã nhận bài'),
        ('DaBanGiao', 'Đã bàn giao cho Thư ký'),
        ('DaLamPhach', 'Đã làm phách'),
        ('DaTraVe', 'Đã trả về từ Thư ký'),
    )
    trang_thai_bai_thi = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ChuaNhanBai')

    def __str__(self):
        return self.ma_lich_thi


class DanhSachThiSinh(models.Model):
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

class PhanCongCoiThi(TimestampMixin):
    lich_thi = models.ForeignKey(LichThi, on_delete=models.CASCADE, related_name='phan_cong_coi_thi')
    can_bo = models.ForeignKey(GiangVien, on_delete=models.CASCADE, related_name='phan_cong_coi_thi')
    vai_tro = models.CharField(max_length=100)
    actual_hours = models.DecimalField(max_digits=4, decimal_places=2, default=2.0)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=100000.0)
    is_confirmed = models.BooleanField(default=False)
    ngay_xac_nhan = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xác nhận")

    class Meta:
        unique_together = ('lich_thi', 'can_bo')


class BienBanViPham(TimestampMixin):
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

class DeThi(TimestampMixin):
    ma_de_thi = models.CharField(max_length=50, primary_key=True)
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE, related_name='de_thi')
    trang_thai = models.CharField(max_length=50, default='MoiTao')

    def __str__(self):
        return self.ma_de_thi


class NopDeThi(models.Model):
    de_thi = models.ForeignKey(DeThi, on_delete=models.CASCADE, related_name='nop_de_thi')
    nguoi_nop = models.ForeignKey(User, on_delete=models.PROTECT, related_name='de_thi_da_nop')
    thoi_gian_nop = models.DateTimeField(auto_now_add=True)
    tep_dinh_kem = models.CharField(max_length=255, null=True, blank=True)


class RaSoatDeThi(models.Model):
    de_thi = models.ForeignKey(DeThi, on_delete=models.CASCADE, related_name='ra_soat_de_thi')
    nguoi_rao_soat = models.ForeignKey(User, on_delete=models.PROTECT, related_name='de_thi_da_rao_soat')
    ket_qua = models.TextField()
    ghi_chu = models.TextField(null=True, blank=True)


class DotInSao(TimestampMixin):
    ma_dot_in_sao = models.CharField(max_length=50, primary_key=True)
    de_thi = models.ForeignKey(DeThi, on_delete=models.CASCADE, related_name='dot_in_sao')
    thoi_gian = models.DateTimeField()
    so_luong_ban_in = models.PositiveIntegerField(default=0)
    trang_thai = models.CharField(max_length=50, default='ChuaIn')


class NhatKyInSao(models.Model):
    dot_in_sao = models.ForeignKey(DotInSao, on_delete=models.CASCADE, related_name='nhat_ky')
    thoi_gian = models.DateTimeField(auto_now_add=True)
    nguoi_thuc_hien = models.ForeignKey(User, on_delete=models.PROTECT, related_name='nhat_ky_in_sao_thuc_hien')
    nguoi_giam_sat = models.ForeignKey(User, on_delete=models.PROTECT, related_name='nhat_ky_in_sao_giam_sat')
    so_ban_in = models.PositiveIntegerField(default=0)
    ghi_chu = models.TextField(null=True, blank=True)
    bien_ban_file = models.CharField(max_length=255, null=True, blank=True)


# ===================================================================
# 6. GRADING PROCESS MODELS: Quy trình làm phách & Chấm thi
# ===================================================================

class TuiBaiThi(TimestampMixin):
    ma_tui_bai = models.CharField(max_length=50, primary_key=True)
    lich_thi = models.OneToOneField(LichThi, on_delete=models.CASCADE, related_name='tui_bai_thi')
    so_luong_bai = models.PositiveIntegerField(default=0)
    trang_thai = models.CharField(max_length=50, default='DaThuHoi')

    def __str__(self):
        return self.ma_tui_bai


class TuiPhach(TimestampMixin):
    STATUS_CHOICES = (
        ('MoiTao', 'Mới tạo'),
        ('DaGiaoDVCM', 'Đã giao cho ĐVCM'),
        ('DangCham', 'Đang chấm'),
        ('ChoKhopDiem', 'Chờ khớp điểm'),
        ('DaKhopDiem', 'Đã khớp điểm'),
        ('DaTraVeTKT', 'Đã trả về TKT'),
        ('DaDoiChieu', 'Đã đối chiếu hợp lệ'),
        ('KhoaDaPheDuyet', 'Khoa đã phê duyệt'),
        ('DaDuyetBangDiem', 'Đã duyệt bảng điểm (LĐP)'),
        ('DaKhoa', 'Đã khóa phách'),
    )
    ma_tui = models.CharField(max_length=50, primary_key=True)
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE, related_name='tui_phach', null=True, blank=True)
    ky_thi = models.ForeignKey('KyThi', on_delete=models.SET_NULL, related_name='tui_phach', null=True, blank=True, verbose_name="Kỳ thi")
    so_luong_bai = models.PositiveIntegerField(default=0)
    mat_khau_khoa = models.CharField(max_length=128, null=True, blank=True)
    trang_thai = models.CharField(max_length=50, choices=STATUS_CHOICES, default='MoiTao')

    # Phê duyệt cấp Khoa (ĐVCM)
    nguoi_duyet_khoa = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tui_phach_khoa_duyet', null=True, blank=True, verbose_name="Người duyệt cấp Khoa")
    ngay_duyet_khoa = models.DateTimeField(null=True, blank=True, verbose_name="Ngày duyệt cấp Khoa")

    # Phê duyệt cấp Lãnh đạo phòng (LĐP)
    nguoi_duyet_diem = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tui_phach_da_duyet', null=True, blank=True, verbose_name="Người duyệt cấp LĐP")
    ngay_duyet_diem = models.DateTimeField(null=True, blank=True, verbose_name="Ngày duyệt cấp LĐP")

    class Meta:
        indexes = [
            models.Index(fields=['trang_thai'], name='idx_tuiphach_trangthai'),
        ]

    def __str__(self):
        return self.ma_tui


class MaPhach(TimestampMixin):
    ma_phach = models.CharField(max_length=50, primary_key=True)
    tui_phach = models.ForeignKey(TuiPhach, on_delete=models.CASCADE, related_name='danh_sach_phach')
    thi_sinh = models.OneToOneField(DanhSachThiSinh, on_delete=models.CASCADE, related_name='ma_phach', null=True, blank=True)
    trang_thai = models.CharField(max_length=50, default='MoiTao')

    def __str__(self):
        return self.ma_phach


class DiemThi(TimestampMixin):
    ma_phach = models.ForeignKey(MaPhach, on_delete=models.CASCADE, related_name='diem_thi')
    lan_cham = models.PositiveIntegerField()
    diem = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    can_bo = models.ForeignKey(GiangVien, on_delete=models.PROTECT, related_name='diem_thi_da_cham')
    nguoi_nhap = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='diem_thi_da_nhap', null=True, blank=True, verbose_name="Người nhập điểm")

    class Meta:
        unique_together = ('ma_phach', 'lan_cham')


class DoiSoatDiem(TimestampMixin):
    ma_phach = models.OneToOneField(MaPhach, on_delete=models.CASCADE, primary_key=True, related_name='doi_soat')
    diem_lan_1 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    diem_lan_2 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    chenh_lech = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    diem_cuoi_cung = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Điểm cuối cùng")
    nguoi_doi_soat = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='doi_soat_da_thuc_hien', null=True, blank=True, verbose_name="Người đối soát")
    ngay_doi_soat = models.DateTimeField(null=True, blank=True, verbose_name="Ngày đối soát")
    trang_thai = models.CharField(max_length=50, default='ChuaDoiSoat')


class PhanCongChamThi(TimestampMixin):
    LOAI_PHAN_CONG_CHOICES = (
        ('ChamChinh', 'Chấm thi chính'),
        ('PhucKhao', 'Chấm phúc khảo'),
    )
    tui_phach = models.ForeignKey(TuiPhach, on_delete=models.CASCADE, related_name='phan_cong_cham', null=True, blank=True)
    don_phuc_khao = models.ForeignKey('DonPhucKhao', on_delete=models.CASCADE, related_name='phan_cong_cham', null=True, blank=True)
    giang_vien = models.ForeignKey(GiangVien, on_delete=models.CASCADE, related_name='phan_cong_cham')
    loai_phan_cong = models.CharField(max_length=50, choices=LOAI_PHAN_CONG_CHOICES, default='ChamChinh', verbose_name="Loại phân công")
    vai_tro = models.CharField(max_length=50)
    trang_thai = models.CharField(max_length=50, default='ChuaCham')
    ngay_phan_cong = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Phân công Chấm thi"
        verbose_name_plural = "Phân công Chấm thi"

    def __str__(self):
        return f"{self.giang_vien} - {self.loai_phan_cong} ({self.vai_tro})"


# ===================================================================
# 7. HANDOVER MODELS: Quy trình giao nhận đồ sau thi/chấm thi
# ===================================================================

class PhieuGiaoNhan(models.Model):
    LOAI_PHIEU_CHOICES = (
        ('TKT_TO_TKCT', 'TKT bàn giao bài thi gốc cho Thư ký'),
        ('TKCT_TO_TKT', 'Thư ký trả bài thi (đã rọc phách) về TKT'),
        ('TKT_TO_DVCM', 'TKT bàn giao túi phách cho ĐVCM'),
        ('DVCM_TO_GV', 'ĐVCM bàn giao túi phách cho Giảng viên'),
        ('GV_TO_DVCM', 'Giảng viên trả túi phách (đã chấm) cho ĐVCM'),
        ('DVCM_TO_TKT', 'ĐVCM trả túi phách (đã có điểm) về TKT'),
        ('TKT_TO_PK', 'TKT bàn giao hồ sơ phúc khảo cho ĐVCM'),
    )
    STATUS_CHOICES = (
        ('ChoXacNhan', 'Chờ xác nhận'),
        ('DaXacNhan', 'Đã xác nhận'),
        ('DaHoanTat', 'Đã hoàn tất'),
        ('DaHuy', 'Đã hủy'),
    )
    ma_phieu = models.CharField(max_length=50, primary_key=True)
    nguoi_giao = models.ForeignKey(User, on_delete=models.PROTECT, related_name='phieu_giao_set')
    nguoi_nhan = models.ForeignKey(User, on_delete=models.PROTECT, related_name='phieu_nhan_set')
    ngay_giao = models.DateTimeField(auto_now_add=True)
    loai_phieu = models.CharField(max_length=50, choices=LOAI_PHIEU_CHOICES)
    bien_ban_giao_nhan = models.FileField(upload_to='bien_ban_giao_nhan/', null=True, blank=True, verbose_name="Biên bản giao nhận (đã ký)")
    log_xac_nhan = models.TextField(null=True, blank=True)
    trang_thai = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ChoXacNhan')
    ghi_chu = models.TextField(null=True, blank=True, verbose_name="Ghi chú")

    # Trường xác nhận bên nhận
    nguoi_xac_nhan = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='phieu_xac_nhan_set', null=True, blank=True, verbose_name="Người xác nhận")
    ngay_xac_nhan = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xác nhận")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        indexes = [
            models.Index(fields=['loai_phieu', 'trang_thai'], name='idx_pgn_loai_tt'),
        ]

    def __str__(self):
        return self.ma_phieu


class ChiTietGiaoNhan(models.Model):
    phieu = models.ForeignKey(PhieuGiaoNhan, on_delete=models.CASCADE, related_name='chi_tiet')
    tui_phach = models.ForeignKey(TuiPhach, on_delete=models.CASCADE, related_name='giao_nhan_chi_tiet', null=True, blank=True)
    lich_thi = models.ForeignKey(LichThi, on_delete=models.CASCADE, related_name='giao_nhan_chi_tiet', null=True, blank=True)
    tinh_trang = models.CharField(max_length=255, null=True, blank=True)


# ===================================================================
# 8. APPEAL & CONFIG MODELS: Phúc khảo và Điểm thành phần
# ===================================================================

class DonPhucKhao(models.Model):
    ma_don = models.CharField(max_length=50, primary_key=True)
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name='don_phuc_khao')
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.SET_NULL, related_name='don_phuc_khao', null=True, blank=True)
    lich_thi = models.ForeignKey(LichThi, on_delete=models.CASCADE, related_name='don_phuc_khao', null=True, blank=True)
    ma_phach = models.ForeignKey(MaPhach, on_delete=models.CASCADE, related_name='don_phuc_khao', null=True, blank=True)

    # FK workflow: liên kết với túi bài thi gốc & túi phách
    tui_bai_thi = models.ForeignKey(TuiBaiThi, on_delete=models.SET_NULL, related_name='don_phuc_khao', null=True, blank=True, verbose_name="Túi bài thi gốc")
    tui_phach = models.ForeignKey(TuiPhach, on_delete=models.SET_NULL, related_name='don_phuc_khao', null=True, blank=True, verbose_name="Túi phách liên quan")

    diem_goc = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    diem_phuc_khao_1 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    diem_phuc_khao_2 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    diem_phuc_khao_cuoi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ly_do = models.TextField(blank=True, default='')
    file_bien_ban = models.CharField(max_length=255, null=True, blank=True)
    trang_thai = models.CharField(max_length=50, default='ChoXuLy')
    nguoi_duyet = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='duyet_phuc_khao', null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ngay_duyet = models.DateTimeField(null=True, blank=True)
    ngay_rut_bai = models.DateTimeField(null=True, blank=True, verbose_name="Ngày rút bài thi")
    ngay_hoan_thanh = models.DateTimeField(null=True, blank=True, verbose_name="Ngày hoàn thành PK")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        indexes = [
            models.Index(fields=['trang_thai'], name='idx_donpk_trangthai'),
        ]



class CauHinhDiemHocPhan(models.Model):
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE, related_name='cau_hinh_diem')
    ten_cot_diem = models.CharField(max_length=255)
    trong_so = models.DecimalField(max_digits=5, decimal_places=2)
    thoi_gian_mo_cong = models.DateTimeField(null=True, blank=True)
    thoi_gian_khoa_cong = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('hoc_phan', 'ten_cot_diem')


class DiemThanhPhan(models.Model):
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
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='audit_logs')
    action = models.TextField()
    ip_address = models.CharField(max_length=50, null=True, blank=True)


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


class QuyetToanThuLao(TimestampMixin):
    ma_quyet_toan = models.CharField(max_length=50, primary_key=True)
    ky_thi = models.ForeignKey(KyThi, on_delete=models.CASCADE, related_name='quyet_toan_thu_lao')
    tong_so_ca = models.PositiveIntegerField(default=0)
    tong_so_gio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nguoi_duyet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ngay_duyet = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.ma_quyet_toan


class CauHinhHeThong(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    value = models.TextField(blank=True, null=True)
    nguoi_cap_nhat = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key


class CauHinhPhucKhao(models.Model):
    ma_cau_hinh = models.CharField(max_length=50, primary_key=True)
    thoi_gian_mo_cong = models.DateTimeField(blank=True, null=True)
    thoi_gian_khoa_cong = models.DateTimeField(blank=True, null=True)
    han_chot_cham = models.DateTimeField(blank=True, null=True)
    trang_thai = models.CharField(default='KichHoat', max_length=50)
    ma_hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE)

    def __str__(self):
        return self.ma_cau_hinh


class CauHinhThoiGianDotThi(models.Model):
    """Cấu hình mốc thời gian Nhập điểm, Công bố điểm & Phúc khảo theo Năm học - Học kỳ - Đợt thi (Đã chuẩn hóa & Liên kết CSDL)"""
    ky_thi = models.ForeignKey(KyThi, on_delete=models.CASCADE, null=True, blank=True, related_name='cau_hinh_thoi_gian', verbose_name="Kỳ thi liên kết")
    nam_hoc = models.CharField(max_length=20, db_index=True, verbose_name="Năm học")
    hoc_ky = models.CharField(max_length=20, db_index=True, verbose_name="Học kỳ")
    dot_thi = models.CharField(max_length=20, db_index=True, verbose_name="Đợt thi")

    # Mốc thời gian Nhập & Công bố điểm
    tg_bat_dau_nhap = models.DateTimeField(null=True, blank=True, verbose_name="Bắt đầu nhập điểm")
    tg_khoa_cong_nhap = models.DateTimeField(null=True, blank=True, verbose_name="Khóa cổng nhập điểm")
    tg_cong_bo_diem = models.DateTimeField(null=True, blank=True, verbose_name="Tự động công bố điểm")

    # Mốc thời gian Phúc khảo
    tg_mo_nhan_don_pk = models.DateTimeField(null=True, blank=True, verbose_name="Mở cổng nhận đơn PK")
    tg_khoa_nhan_don_pk = models.DateTimeField(null=True, blank=True, verbose_name="Khóa cổng nhận đơn PK")
    han_chot_cham_pk = models.DateTimeField(null=True, blank=True, verbose_name="Hạn chốt chấm PK")

    # Mốc thời gian bổ sung CVHT
    tg_nop_de_thi = models.DateTimeField(null=True, blank=True, verbose_name="Hạn nộp đề thi")
    tg_nhap_diem_tp = models.DateTimeField(null=True, blank=True, verbose_name="Hạn nhập điểm thành phần")
    tg_cau_hinh_trong_so = models.DateTimeField(null=True, blank=True, verbose_name="Hạn cấu hình trọng số")
    tg_chot_dieu_kien_thi = models.DateTimeField(null=True, blank=True, verbose_name="Hạn chốt điều kiện dự thi")
    tg_chot_quy_doi = models.DateTimeField(null=True, blank=True, verbose_name="Hạn chốt quy đổi")

    is_locked = models.BooleanField(default=False, db_index=True, verbose_name="Khóa chỉnh sửa")
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('nam_hoc', 'hoc_ky', 'dot_thi')
        indexes = [
            models.Index(fields=['nam_hoc', 'hoc_ky', 'dot_thi'], name='idx_cauhinh_nam_hk_dot'),
            models.Index(fields=['is_locked'], name='idx_cauhinh_locked'),
        ]
        ordering = ['-nam_hoc', 'hoc_ky', 'dot_thi']
        verbose_name = "Cấu hình Thời gian Đợt thi"
        verbose_name_plural = "Cấu hình Thời gian Đợt thi"

    def __str__(self):
        return f"{self.nam_hoc} - {self.hoc_ky} - {self.dot_thi}"
