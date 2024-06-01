# Generated by Django 4.2.5 on 2024-06-01 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='dessert',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dessert_meals', to='api.food', verbose_name='دسر'),
        ),
        migrations.AlterField(
            model_name='drink',
            name='meal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drinks', to='api.meal', verbose_name='وعده'),
        ),
        migrations.AlterField(
            model_name='drink',
            name='name',
            field=models.CharField(max_length=100, verbose_name='نام'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='diet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diet_meals', to='api.food', verbose_name='غذای رژیمی'),
        ),
    ]
