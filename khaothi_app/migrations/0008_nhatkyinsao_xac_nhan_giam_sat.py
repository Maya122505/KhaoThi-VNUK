# Được tạo tự động bởi Django 6.0.4 on 2026-07-15 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khaothi_app', '0007_user_sub_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='nhatkyinsao',
            name='xac_nhan_giam_sat',
            field=models.BooleanField(default=False),
        ),
    ]
