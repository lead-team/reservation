# Generated by Django 4.2.5 on 2024-05-31 20:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_meal_options_alter_shift_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='food',
            field=models.CharField(max_length=500, verbose_name='نام غذا'),
        ),
        migrations.AlterField(
            model_name='shiftmeal',
            name='shift',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_meals', to='api.shift', verbose_name='شیفت'),
        ),
    ]