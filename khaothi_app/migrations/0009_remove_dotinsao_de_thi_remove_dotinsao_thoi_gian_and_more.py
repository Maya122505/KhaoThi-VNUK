# Được tạo tự động bởi Django 6.0.4 on 2026-07-15 09:54

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khaothi_app', '0008_nhatkyinsao_xac_nhan_giam_sat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dotinsao',
            name='de_thi',
        ),
        migrations.RemoveField(
            model_name='dotinsao',
            name='thoi_gian',
        ),
        migrations.RemoveField(
            model_name='nhatkyinsao',
            name='bien_ban_file',
        ),
        migrations.RemoveField(
            model_name='nhatkyinsao',
            name='so_ban_in',
        ),
        migrations.RemoveField(
            model_name='nhatkyinsao',
            name='thoi_gian',
        ),
        migrations.RemoveField(
            model_name='nhatkyinsao',
            name='xac_nhan_giam_sat',
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='ca_thi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dot_in_sao', to='khaothi_app.cathi'),
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='can_bo_giam_sat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dot_in_sao_duoc_giam_sat', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='ghi_chu',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='hoc_phan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dot_in_sao', to='khaothi_app.hocphan'),
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='ky_thi',
            field=models.ForeignKey(default='KT-HK3-2026', on_delete=django.db.models.deletion.PROTECT, related_name='dot_in_sao', to='khaothi_app.kythi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='ngay_tao',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='nguoi_tao',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='dot_in_sao_da_tao', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='noi_in_sao',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='phong_thi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dot_in_sao', to='khaothi_app.phongthi'),
        ),
        migrations.AddField(
            model_name='dotinsao',
            name='thoi_gian_in_sao',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Thời gian in sao dự kiến'),
        ),
        migrations.AddField(
            model_name='nhatkyinsao',
            name='ngay_cap_nhat',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nhatkyinsao',
            name='so_luong_in_thuc_te',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='nhatkyinsao',
            name='so_luong_niem_phong',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='nhatkyinsao',
            name='thoi_gian_thuc_hien',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Thời gian thực hiện in sao'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dotinsao',
            name='trang_thai',
            field=models.CharField(choices=[('ChoCapNhat', 'Chờ cập nhật nhật ký'), ('DaCapNhat', 'Đã cập nhật nhật ký (Chờ xác nhận)'), ('HoanTat', 'Hoàn tất'), ('TuChoi', 'Từ chối xác nhận')], default='ChoCapNhat', max_length=50),
        ),
        migrations.AlterField(
            model_name='nhatkyinsao',
            name='dot_in_sao',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='nhat_ky', to='khaothi_app.dotinsao'),
        ),
        migrations.AlterField(
            model_name='nhatkyinsao',
            name='nguoi_giam_sat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='nhat_ky_in_sao_da_giam_sat', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='nhatkyinsao',
            name='nguoi_thuc_hien',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='nhat_ky_in_sao_da_lam', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BienBanGiamSatInSao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trang_thai', models.CharField(choices=[('ChoXacNhan', 'Chờ xác nhận'), ('DaXacNhan', 'Đã xác nhận'), ('TuChoi', 'Từ chối xác nhận')], default='ChoXacNhan', max_length=50)),
                ('nhan_xet_giam_sat', models.TextField(blank=True, null=True, verbose_name='Ý kiến nhận xét giám sát')),
                ('chu_ky_so', models.TextField(blank=True, null=True, verbose_name='Chuỗi chữ ký số xác nhận')),
                ('ngay_xac_nhan', models.DateTimeField(blank=True, null=True)),
                ('ghi_chu', models.TextField(blank=True, null=True)),
                ('dot_in_sao', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bien_ban_giam_sat', to='khaothi_app.dotinsao')),
                ('nguoi_xac_nhan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bien_ban_giam_sat_da_ky', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
