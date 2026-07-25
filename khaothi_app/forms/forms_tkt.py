from django import forms
from ..models import KyThi, CaThi, HocPhan, PhongThi, User, PhieuGiaoNhan

class KyThiForm(forms.ModelForm):
    class Meta:
        model = KyThi
        fields = ['ten_ky_thi', 'nam_hoc', 'hoc_ky', 'ngay_bat_dau', 'ngay_ket_thuc']
        widgets = {
            'ten_ky_thi': forms.TextInput(attrs={'class': 'form-control'}),
            'nam_hoc': forms.TextInput(attrs={'class': 'form-control'}),
            'hoc_ky': forms.Select(attrs={'class': 'form-select'}),
            'ngay_bat_dau': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ngay_ket_thuc': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class CaThiForm(forms.ModelForm):
    class Meta:
        model = CaThi
        fields = ['ky_thi', 'ten_ca', 'ngay_thi', 'gio_bat_dau', 'gio_ket_thuc']
        widgets = {
            'ky_thi': forms.Select(attrs={'class': 'form-select'}),
            'ten_ca': forms.TextInput(attrs={'class': 'form-control'}),
            'ngay_thi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gio_bat_dau': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'gio_ket_thuc': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class LapLichThiForm(forms.Form):
    ca_thi = forms.ModelChoiceField(queryset=CaThi.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    hoc_phan = forms.ModelChoiceField(queryset=HocPhan.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    phong_thi = forms.ModelChoiceField(queryset=PhongThi.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    # Giả sử User có trường is_giang_vien
    giang_vien = forms.ModelChoiceField(queryset=User.objects.filter(role='gv'), widget=forms.Select(attrs={'class': 'form-select'}))

class NhapDiemLan2SBDForm(forms.Form):
    ma_lop_thi = forms.CharField(label="Mã lớp dự thi", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Dữ liệu điểm sẽ được xử lý động, không cần định nghĩa ở đây

class NhapDiemLan2PhachForm(forms.Form):
    ma_tui_phach = forms.CharField(label="Mã túi phách", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mat_khau = forms.CharField(label="Mật khẩu túi phách", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # Dữ liệu điểm sẽ được xử lý động

class PhieuGiaoNhanForm(forms.ModelForm):
    class Meta:
        model = PhieuGiaoNhan
        fields = ['ma_phieu', 'nguoi_giao', 'nguoi_nhan', 'loai_phieu', 'bien_ban_giao_nhan', 'log_xac_nhan', 'trang_thai']
