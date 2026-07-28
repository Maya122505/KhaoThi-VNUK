# Được tạo tự động bởi Django 6.0.3 on 2026-07-14 02:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khaothi_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaPhach',
            fields=[
                ('ma_phach', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('sbd', models.CharField(blank=True, max_length=50, null=True)),
                ('trang_thai', models.CharField(default='MoiTao', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='LopHanhChinh',
            fields=[
                ('ma_lop', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('ten_lop', models.CharField(max_length=255)),
                ('nganh', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhongThi',
            fields=[
                ('ma_phong', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('ten_phong', models.CharField(max_length=255)),
                ('loai_phong', models.CharField(blank=True, max_length=50, null=True)),
                ('suc_chua', models.PositiveIntegerField(default=0)),
                ('vi_tri', models.CharField(blank=True, max_length=255, null=True)),
                ('trang_thai', models.CharField(default='KhaDung', max_length=50)),
                ('ghi_chu', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='donphuckhao',
            name='bai_thi',
        ),
        migrations.RemoveField(
            model_name='phongthigoc',
            name='ca_thi',
        ),
        migrations.RemoveField(
            model_name='phongthigoc',
            name='hoc_phan',
        ),
        migrations.RemoveField(
            model_name='phieugiaonhan',
            name='phong_thi_dinh_kem',
        ),
        migrations.RemoveField(
            model_name='tuiphach',
            name='phong_thi_goc',
        ),
        migrations.RenameField(
            model_name='cathi',
            old_name='ten_ca_thi',
            new_name='ten_ca',
        ),
        migrations.RenameField(
            model_name='phieugiaonhan',
            old_name='ghi_chu',
            new_name='log_xac_nhan',
        ),
        migrations.RenameField(
            model_name='phieugiaonhan',
            old_name='thoi_gian_giao',
            new_name='ngay_giao',
        ),
        migrations.RenameField(
            model_name='tuiphach',
            old_name='so_luong_bai_thi',
            new_name='so_luong_bai',
        ),
        migrations.RemoveField(
            model_name='cathi',
            name='id',
        ),
        migrations.RemoveField(
            model_name='donphuckhao',
            name='ngay_tao',
        ),
        migrations.RemoveField(
            model_name='donphuckhao',
            name='nguoi_tao',
        ),
        migrations.RemoveField(
            model_name='kythi',
            name='id',
        ),
        migrations.RemoveField(
            model_name='phieugiaonhan',
            name='thoi_gian_nhan',
        ),
        migrations.RemoveField(
            model_name='phieugiaonhan',
            name='tui_phach_dinh_kem',
        ),
        migrations.RemoveField(
            model_name='tuiphach',
            name='giang_vien_cham_1',
        ),
        migrations.RemoveField(
            model_name='tuiphach',
            name='giang_vien_cham_2',
        ),
        migrations.RemoveField(
            model_name='tuiphach',
            name='hoc_phan',
        ),
        migrations.RemoveField(
            model_name='tuiphach',
            name='ma_tui_phach',
        ),
        migrations.RemoveField(
            model_name='tuiphach',
            name='mat_khau',
        ),
        migrations.AddField(
            model_name='cathi',
            name='ma_ca_thi',
            field=models.CharField(default='CT-001', max_length=50, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cathi',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='donphuckhao',
            name='diem_goc',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='donphuckhao',
            name='diem_phuc_khao_1',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='donphuckhao',
            name='diem_phuc_khao_2',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='donphuckhao',
            name='diem_phuc_khao_cuoi',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='donphuckhao',
            name='file_bien_ban',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='hocphan',
            name='ma_hp',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='hocphan',
            name='so_tin_chi',
            field=models.PositiveIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='kythi',
            name='dot_thi',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='kythi',
            name='ma_ky_thi',
            field=models.CharField(default='KT-HK3-2026', max_length=50, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='kythi',
            name='mo_ta',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='kythi',
            name='trang_thai',
            field=models.CharField(default='DangDienRa', max_length=50),
        ),
        migrations.AddField(
            model_name='phieugiaonhan',
            name='chu_ky_so',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='phieugiaonhan',
            name='loai_phieu',
            field=models.CharField(default='Ban giao', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='phieugiaonhan',
            name='tep_dinh_kem',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tuiphach',
            name='ca_thi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tui_phach', to='khaothi_app.cathi'),
        ),
        migrations.AddField(
            model_name='tuiphach',
            name='ma_tui',
            field=models.CharField(default='TP-001', max_length=50, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tuiphach',
            name='mat_khau_khoa',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='cathi',
            name='ky_thi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ca_thi', to='khaothi_app.kythi'),
        ),
        migrations.AlterField(
            model_name='cathi',
            name='ngay_thi',
            field=models.DateField(blank=True, null=True, verbose_name='Ngày thi'),
        ),
        migrations.AlterField(
            model_name='donphuckhao',
            name='ma_don',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='donphuckhao',
            name='trang_thai',
            field=models.CharField(default='ChoXuLy', max_length=50),
        ),
        migrations.AlterField(
            model_name='hocphan',
            name='ma_hoc_phan',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='kythi',
            name='ngay_bat_dau',
            field=models.DateField(blank=True, null=True, verbose_name='Ngày bắt đầu'),
        ),
        migrations.AlterField(
            model_name='kythi',
            name='ngay_ket_thuc',
            field=models.DateField(blank=True, null=True, verbose_name='Ngày kết thúc'),
        ),
        migrations.AlterField(
            model_name='phieugiaonhan',
            name='ma_phieu',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='phieugiaonhan',
            name='nguoi_giao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='phieu_giao_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='phieugiaonhan',
            name='nguoi_nhan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='phieu_nhan_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='phieugiaonhan',
            name='trang_thai',
            field=models.CharField(default='ChoXacNhan', max_length=50),
        ),
        migrations.AlterField(
            model_name='tuiphach',
            name='trang_thai',
            field=models.CharField(default='MoiTao', max_length=50),
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action', models.TextField()),
                ('ip_address', models.CharField(blank=True, max_length=50, null=True)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CauHinhDiemHocPhan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ten_cot_diem', models.CharField(max_length=255)),
                ('trong_so', models.DecimalField(decimal_places=2, max_digits=5)),
                ('thoi_gian_mo_cong', models.DateTimeField(blank=True, null=True)),
                ('thoi_gian_khoa_cong', models.DateTimeField(blank=True, null=True)),
                ('hoc_phan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cau_hinh_diem', to='khaothi_app.hocphan')),
            ],
            options={
                'unique_together': {('hoc_phan', 'ten_cot_diem')},
            },
        ),
        migrations.CreateModel(
            name='DeThi',
            fields=[
                ('ma_de_thi', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('trang_thai', models.CharField(default='MoiTao', max_length=50)),
                ('hoc_phan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='de_thi', to='khaothi_app.hocphan')),
            ],
        ),
        migrations.CreateModel(
            name='DoiSoatDiem',
            fields=[
                ('ma_phach', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='doi_soat', serialize=False, to='khaothi_app.maphach')),
                ('diem_lan_1', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('diem_lan_2', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('chenh_lech', models.DecimalField(decimal_places=2, default=0.0, max_digits=4)),
                ('trang_thai', models.CharField(default='ChuaDoiSoat', max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='maphach',
            name='tui_phach',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='danh_sach_phach', to='khaothi_app.tuiphach'),
        ),
        migrations.AddField(
            model_name='donphuckhao',
            name='ma_phach',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='don_phuc_khao', to='khaothi_app.maphach'),
        ),
        migrations.CreateModel(
            name='DotInSao',
            fields=[
                ('ma_dot_in_sao', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('thoi_gian', models.DateTimeField()),
                ('so_luong_ban_in', models.PositiveIntegerField(default=0)),
                ('trang_thai', models.CharField(default='ChuaIn', max_length=50)),
                ('de_thi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dot_in_sao', to='khaothi_app.dethi')),
            ],
        ),
        migrations.CreateModel(
            name='GiangVien',
            fields=[
                ('ma_giang_vien', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('ho_ten', models.CharField(max_length=255)),
                ('don_vi', models.CharField(blank=True, max_length=255, null=True)),
                ('sdt', models.CharField(blank=True, max_length=20, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='giang_vien_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DiemThi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lan_cham', models.PositiveIntegerField()),
                ('diem', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('ma_phach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diem_thi', to='khaothi_app.maphach')),
                ('can_bo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='diem_thi_da_cham', to='khaothi_app.giangvien')),
            ],
            options={
                'unique_together': {('ma_phach', 'lan_cham')},
            },
        ),
        migrations.CreateModel(
            name='LichThi',
            fields=[
                ('ma_lich_thi', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('ngay_thi', models.DateField()),
                ('so_luong_sv', models.PositiveIntegerField(default=0)),
                ('ca_thi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lich_thi', to='khaothi_app.cathi')),
                ('ky_thi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lich_thi', to='khaothi_app.kythi')),
            ],
        ),
        migrations.CreateModel(
            name='ChiTietGiaoNhan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tinh_trang', models.CharField(blank=True, max_length=255, null=True)),
                ('phieu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chi_tiet', to='khaothi_app.phieugiaonhan')),
                ('tui_phach', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='giao_nhan_chi_tiet', to='khaothi_app.tuiphach')),
                ('lich_thi', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='giao_nhan_chi_tiet', to='khaothi_app.lichthi')),
            ],
        ),
        migrations.AddField(
            model_name='donphuckhao',
            name='lich_thi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='don_phuc_khao', to='khaothi_app.lichthi'),
        ),
        migrations.AddField(
            model_name='tuiphach',
            name='lich_thi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tui_phach_phong', to='khaothi_app.lichthi'),
        ),
        migrations.CreateModel(
            name='LopHocPhan',
            fields=[
                ('ma_lop_hp', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('hoc_ky', models.CharField(max_length=20)),
                ('nam_hoc', models.CharField(max_length=20)),
                ('giang_vien', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lop_hoc_phan', to='khaothi_app.giangvien')),
                ('hoc_phan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lop_hoc_phan', to='khaothi_app.hocphan')),
            ],
        ),
        migrations.AddField(
            model_name='lichthi',
            name='lop_hp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lich_thi', to='khaothi_app.lophocphan'),
        ),
        migrations.CreateModel(
            name='NhatKyInSao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thoi_gian', models.DateTimeField(auto_now_add=True)),
                ('so_ban_in', models.PositiveIntegerField(default=0)),
                ('ghi_chu', models.TextField(blank=True, null=True)),
                ('bien_ban_file', models.CharField(blank=True, max_length=255, null=True)),
                ('dot_in_sao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nhat_ky', to='khaothi_app.dotinsao')),
                ('nguoi_giam_sat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='nhat_ky_in_sao_giam_sat', to=settings.AUTH_USER_MODEL)),
                ('nguoi_thuc_hien', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='nhat_ky_in_sao_thuc_hien', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NopDeThi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thoi_gian_nop', models.DateTimeField(auto_now_add=True)),
                ('tep_dinh_kem', models.CharField(blank=True, max_length=255, null=True)),
                ('de_thi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nop_de_thi', to='khaothi_app.dethi')),
                ('nguoi_nop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='de_thi_da_nop', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PhanCongChamThi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vai_tro', models.CharField(max_length=50)),
                ('trang_thai', models.CharField(default='ChuaCham', max_length=50)),
                ('giang_vien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phan_cong_cham', to='khaothi_app.giangvien')),
                ('tui_phach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phan_cong_cham', to='khaothi_app.tuiphach')),
            ],
            options={
                'unique_together': {('tui_phach', 'giang_vien', 'vai_tro')},
            },
        ),
        migrations.CreateModel(
            name='PhanCongCoiThi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vai_tro', models.CharField(max_length=100)),
                ('actual_hours', models.DecimalField(decimal_places=2, default=2.0, max_digits=4)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('can_bo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phan_cong_coi_thi', to='khaothi_app.giangvien')),
                ('lich_thi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phan_cong_coi_thi', to='khaothi_app.lichthi')),
            ],
            options={
                'unique_together': {('lich_thi', 'can_bo')},
            },
        ),
        migrations.AddField(
            model_name='lichthi',
            name='phong_thi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lich_thi', to='khaothi_app.phongthi'),
        ),
        migrations.CreateModel(
            name='RaSoatDeThi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ket_qua', models.TextField()),
                ('ghi_chu', models.TextField(blank=True, null=True)),
                ('de_thi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ra_soat_de_thi', to='khaothi_app.dethi')),
                ('nguoi_rao_soat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='de_thi_da_rao_soat', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SinhVien',
            fields=[
                ('ma_sinh_vien', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('ho_ten', models.CharField(max_length=255)),
                ('debt', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('is_eligible', models.BooleanField(default=True)),
                ('lop_hanh_chinh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sinh_vien', to='khaothi_app.lophanhchinh')),
            ],
        ),
        migrations.AddField(
            model_name='maphach',
            name='sinh_vien',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='danh_sach_phach', to='khaothi_app.sinhvien'),
        ),
        migrations.CreateModel(
            name='LopHocPhanSinhVien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_eligible', models.BooleanField(default=True)),
                ('lop_hp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sinh_vien_lien_ket', to='khaothi_app.lophocphan')),
                ('sinh_vien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lop_hp_lien_ket', to='khaothi_app.sinhvien')),
            ],
            options={
                'unique_together': {('lop_hp', 'sinh_vien')},
            },
        ),
        migrations.CreateModel(
            name='DiemThanhPhan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diem', models.DecimalField(decimal_places=2, max_digits=4)),
                ('cau_hinh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diem_thanh_phan', to='khaothi_app.cauhinhdiemhocphan')),
                ('lop_hp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diem_thanh_phan', to='khaothi_app.lophocphan')),
                ('sinh_vien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diem_thanh_phan', to='khaothi_app.sinhvien')),
            ],
            options={
                'unique_together': {('sinh_vien', 'lop_hp', 'cau_hinh')},
            },
        ),
        migrations.CreateModel(
            name='DanhSachThiSinh',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sbd', models.CharField(max_length=50)),
                ('trang_thai_diem_danh', models.CharField(default='CoMat', max_length=50)),
                ('sbd_ma_phach', models.CharField(blank=True, max_length=50, null=True)),
                ('lich_thi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='danh_sach_thi_sinh', to='khaothi_app.lichthi')),
                ('sinh_vien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lich_thi_tham_gia', to='khaothi_app.sinhvien')),
            ],
            options={
                'unique_together': {('lich_thi', 'sinh_vien')},
            },
        ),
        migrations.CreateModel(
            name='BienBanViPham',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noi_dung', models.TextField()),
                ('hinh_thuc_xu_ly', models.CharField(max_length=100)),
                ('nguoi_lap', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bien_ban_da_lap', to=settings.AUTH_USER_MODEL)),
                ('lich_thi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bien_ban_vi_pham', to='khaothi_app.lichthi')),
                ('sinh_vien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bien_ban_vi_pham', to='khaothi_app.sinhvien')),
            ],
            options={
                'unique_together': {('lich_thi', 'sinh_vien')},
            },
        ),
        migrations.AddField(
            model_name='donphuckhao',
            name='sinh_vien',
            field=models.ForeignKey(default='SV001', on_delete=django.db.models.deletion.CASCADE, related_name='don_phuc_khao', to='khaothi_app.sinhvien'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='BaiThi',
        ),
        migrations.DeleteModel(
            name='PhongThiGoc',
        ),
    ]
