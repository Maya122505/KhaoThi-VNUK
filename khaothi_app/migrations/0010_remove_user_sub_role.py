# Được tạo tự động bởi Django 6.0.4 on 2026-07-15 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('khaothi_app', '0009_remove_dotinsao_de_thi_remove_dotinsao_thoi_gian_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='sub_role',
        ),
    ]
