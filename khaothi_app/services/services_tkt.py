from ..models import TuiPhach, PhongThi, MaPhach, PhieuGiaoNhan, User
from django.db import transaction

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
