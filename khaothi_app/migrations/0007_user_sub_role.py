# Được tạo tự động bởi Django 6.0.4 on 2026-07-15 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khaothi_app', '0006_alter_lichthi_phong_thi'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sub_role',
            field=models.CharField(blank=True, choices=[('admin', 'Quản lý chung TKT'), ('in_sao', 'Cán bộ In sao'), ('giam_sat', 'Cán bộ Giám sát')], default='admin', max_length=20, null=True),
        ),
    ]
