# Generated by Django 4.2.5 on 2024-06-02 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.ImageField(blank=True, default='defaults/user.png', null=True, upload_to='profiles/', verbose_name='پروفایل'),
        ),
    ]