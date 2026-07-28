# Được tạo tự động bởi Django 6.0.4 on 2026-07-15 09:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khaothi_app', '0005_remove_maphach_sbd_remove_maphach_sinh_vien_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lichthi',
            name='phong_thi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lich_thi', to='khaothi_app.phongthi'),
        ),
    ]
