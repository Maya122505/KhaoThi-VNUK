from rest_framework import serializers
from .models import KyThi, CaThi, HocPhan, TuiPhach, MaPhach, PhieuGiaoNhan, DonPhucKhao, User

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

class TuiPhachSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuiPhach
        fields = '__all__'

class MaPhachSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaPhach
        fields = '__all__'

class PhieuGiaoNhanSerializer(serializers.ModelSerializer):
    nguoi_giao = UserSerializer(read_only=True)
    nguoi_nhan = UserSerializer(read_only=True)

    class Meta:
        model = PhieuGiaoNhan
        fields = '__all__'

class DonPhucKhaoSerializer(serializers.ModelSerializer):
    ma_phach = MaPhachSerializer(read_only=True)

    class Meta:
        model = DonPhucKhao
        fields = '__all__'
