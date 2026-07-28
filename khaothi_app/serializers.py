from rest_framework import serializers
from .models import (
    KyThi, CaThi, HocPhan, TuiPhach, MaPhach, PhieuGiaoNhan, DonPhucKhao, User,
    LichThi, ChiTietGiaoNhan, TuiBaiThi, GiangVien, PhienBanCotDiem, CauHinhPhucKhao,
    PhanCongCoiThi, QuyetToanThuLao, CauHinhHeThong
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role']

class KyThiSerializer(serializers.ModelSerializer):
    class Meta:
        model = KyThi
        fields = '__all__'

class CaThiSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaThi
        fields = '__all__'

class HocPhanSerializer(serializers.ModelSerializer):
    class Meta:
        model = HocPhan
        fields = '__all__'

class LichThiSerializer(serializers.ModelSerializer):
    lop_hp = serializers.StringRelatedField()
    ten_hoc_phan = serializers.CharField(source='lop_hp.hoc_phan.ten_hoc_phan', read_only=True, default='')
    ca_thi = serializers.StringRelatedField()
    phong_thi = serializers.StringRelatedField()

    class Meta:
        model = LichThi
        fields = ['ma_lich_thi', 'lop_hp', 'ten_hoc_phan', 'ca_thi', 'phong_thi', 'ngay_thi', 'so_luong_sv']

class TuiBaiThiSerializer(serializers.ModelSerializer):
    lich_thi = LichThiSerializer(read_only=True)

    class Meta:
        model = TuiBaiThi
        fields = ['ma_tui_bai', 'lich_thi', 'so_luong_bai', 'trang_thai']

class TuiPhachSerializer(serializers.ModelSerializer):
    hoc_phan = serializers.StringRelatedField()
    trang_thai = serializers.CharField(source='get_trang_thai_display')

    class Meta:
        model = TuiPhach
        fields = ['ma_tui', 'hoc_phan', 'so_luong_bai', 'trang_thai']

class GiangVienSerializer(serializers.ModelSerializer):
    khoa = serializers.StringRelatedField()

    class Meta:
        model = GiangVien
        fields = ['ma_giang_vien', 'ho_ten', 'khoa']

class PhanCongCoiThiSerializer(serializers.ModelSerializer):
    can_bo = GiangVienSerializer(read_only=True)
    lich_thi = LichThiSerializer(read_only=True)

    class Meta:
        model = PhanCongCoiThi
        fields = '__all__'

class MaPhachSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaPhach
        fields = '__all__'

class ChiTietGiaoNhanSerializer(serializers.ModelSerializer):
    tui_phach = TuiPhachSerializer(read_only=True)
    lich_thi = LichThiSerializer(read_only=True)

    class Meta:
        model = ChiTietGiaoNhan
        fields = ['tui_phach', 'lich_thi', 'tinh_trang']

class PhieuGiaoNhanSerializer(serializers.ModelSerializer):
    nguoi_giao = UserSerializer(read_only=True)
    nguoi_nhan = UserSerializer(read_only=True)
    chi_tiet = ChiTietGiaoNhanSerializer(many=True, read_only=True)
    loai_phieu = serializers.CharField(source='get_loai_phieu_display')
    trang_thai = serializers.CharField(source='get_trang_thai_display')

    class Meta:
        model = PhieuGiaoNhan
        fields = [
            'ma_phieu', 'nguoi_giao', 'nguoi_nhan', 'ngay_giao', 'loai_phieu',
            'bien_ban_giao_nhan', 'log_xac_nhan', 'trang_thai', 'chi_tiet'
        ]

class DonPhucKhaoSerializer(serializers.ModelSerializer):
    ma_phach = MaPhachSerializer(read_only=True)
    hoc_phan = serializers.StringRelatedField()
    sinh_vien = serializers.StringRelatedField()

    class Meta:
        model = DonPhucKhao
        fields = '__all__'

class PhienBanCotDiemSerializer(serializers.ModelSerializer):
    ma_hoc_phan = serializers.StringRelatedField()

    class Meta:
        model = PhienBanCotDiem
        fields = '__all__'

class CauHinhPhucKhaoSerializer(serializers.ModelSerializer):
    ma_hoc_phan = serializers.StringRelatedField()

    class Meta:
        model = CauHinhPhucKhao
        fields = '__all__'


class QuyetToanThuLaoSerializer(serializers.ModelSerializer):
    ky_thi = serializers.StringRelatedField()
    nguoi_duyet = serializers.StringRelatedField()
    class Meta:
        model = QuyetToanThuLao
        fields = '__all__'


class CauHinhHeThongSerializer(serializers.ModelSerializer):
    nguoi_cap_nhat = serializers.StringRelatedField()
    class Meta:
        model = CauHinhHeThong
        fields = '__all__'
