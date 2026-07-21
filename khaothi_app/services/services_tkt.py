from ..models import TuiPhach, PhongThi, MaPhach, PhieuGiaoNhan, User, DonPhucKhao, SinhVien, LichThi, HocPhan, DanhSachThiSinh
from django.db import transaction, models
from django.utils import timezone


class PhucKhaoService:
    """
    Service layer xử lý các nghiệp vụ Quản lý Phúc khảo trực tiếp với CSDL.
    """

    @staticmethod
    def lay_danh_sach_don(trang_thai=None, search=None):
        queryset = DonPhucKhao.objects.select_related(
            'sinh_vien', 'ma_phach', 'lich_thi__lop_hp__hoc_phan', 'hoc_phan', 'nguoi_duyet'
        ).all()
        if trang_thai:
            queryset = queryset.filter(trang_thai=trang_thai)
        if search:
            queryset = queryset.filter(
                models.Q(ma_don__icontains=search) |
                models.Q(sinh_vien__ho_ten__icontains=search) |
                models.Q(sinh_vien__ma_sinh_vien__icontains=search) |
                models.Q(ma_phach__ma_phach__icontains=search)
            )
        return queryset

    @staticmethod
    @transaction.atomic
    def tao_don_phuc_khao(ma_don, ma_sinh_vien, ma_phach_str=None, ma_lich_thi=None, ly_do="", diem_goc=None):
        sv_obj, _ = SinhVien.objects.get_or_create(ma_sinh_vien=ma_sinh_vien)
        mp_obj = MaPhach.objects.filter(ma_phach=ma_phach_str).first() if ma_phach_str else None
        lt_obj = LichThi.objects.filter(ma_lich_thi=ma_lich_thi).first() if ma_lich_thi else None
        hp_obj = lt_obj.lop_hp.hoc_phan if (lt_obj and lt_obj.lop_hp and lt_obj.lop_hp.hoc_phan) else None

        don, created = DonPhucKhao.objects.update_or_create(
            ma_don=ma_don,
            defaults={
                "sinh_vien": sv_obj,
                "ma_phach": mp_obj,
                "lich_thi": lt_obj,
                "hoc_phan": hp_obj,
                "diem_goc": diem_goc,
                "ly_do": ly_do,
                "trang_thai": "ChoXuLy"
            }
        )
        return don

    @staticmethod
    @transaction.atomic
    def luu_diem_phuc_khao(ma_don, diem_1=None, diem_2=None, diem_cuoi=None, file_bien_ban=None, trang_thai="DaXuLy"):
        don = DonPhucKhao.objects.get(ma_don=ma_don)
        if diem_1 is not None:
            don.diem_phuc_khao_1 = diem_1
        if diem_2 is not None:
            don.diem_phuc_khao_2 = diem_2
        if diem_cuoi is not None:
            don.diem_phuc_khao_cuoi = diem_cuoi
        if file_bien_ban is not None:
            don.file_bien_ban = file_bien_ban
        don.trang_thai = trang_thai
        don.save()
        return don

    @staticmethod
    @transaction.atomic
    def phe_duyet_phuc_khao(ma_don, nguoi_duyet_user=None):
        don = DonPhucKhao.objects.get(ma_don=ma_don)
        don.trang_thai = "DaPheDuyet"
        if nguoi_duyet_user:
            don.nguoi_duyet = nguoi_duyet_user
        don.ngay_duyet = timezone.now()
        don.save()

        # Đồng bộ điểm phúc khảo cuối vào thí sinh nếu có
        if don.ma_phach and don.diem_phuc_khao_cuoi is not None:
            ts = getattr(don.ma_phach, 'thi_sinh', None)
            if ts:
                ts.diem_thi = don.diem_phuc_khao_cuoi
                ts.save()

        return don

class TuiPhachTKTService:
    """
    Service layer để xử lý các nghiệp vụ phức tạp liên quan đến Túi phách
    do Tổ Khảo thí thực hiện.
    """

    @staticmethod
    @transaction.atomic
    def ghep_phong_thanh_tui_phach(danh_sach_ma_phong: list[str]) -> list[TuiPhach]:
        """
        Nghiệp vụ gom các phòng thi thành các túi phách.
        """
        # TODO: Implement logic
        pass

    @staticmethod
    def huy_tui_phach(ma_tui_phach: str):
        """
        Hủy một túi phách, hoàn trả các phòng thi về trạng thái ban đầu.
        """
        # TODO: Implement logic
        pass

class DoiSoatTKTService:
    """
    Service layer cho các nghiệp vụ đối soát, so khớp của TKT.
    """

    @staticmethod
    def doi_soat_diem_lan_2(ma_lop_thi: str, du_lieu_diem: dict) -> dict:
        """
        Đối soát điểm nhập lần 2 theo SBD.
        """
        # TODO: Implement logic
        pass

    @staticmethod
    def khop_phach_tu_dong(ma_tui_phach: str) -> bool:
        """
        Thực hiện giải mã, khớp mã phách với thông tin sinh viên.
        """
        # TODO: Implement logic
        pass

class GiaoNhanTKTService:
    """
    Service layer cho quy trình giao nhận của TKT.
    """

    @staticmethod
    @transaction.atomic
    def tao_phieu_giao_nhan(nguoi_giao, nguoi_nhan, list_ma_tui_phach, list_ma_phong_thi, ghi_chu) -> PhieuGiaoNhan:
        """
        Tạo một phiếu giao nhận mới từ TKT.
        """
        # TODO: Implement logic
        pass

    @staticmethod
    def xac_nhan_nhan_phieu(ma_phieu: str, nguoi_xac_nhan: User) -> PhieuGiaoNhan:
        """
        TKT xác nhận đã nhận lại phiếu.
        """
        # TODO: Implement logic
        pass

