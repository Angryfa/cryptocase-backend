# Generated manually for bonus system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0006_alter_caseprize_unique_together'),
    ]

    operations = [
        # Добавляем поля в модель Case
        migrations.AddField(
            model_name='case',
            name='bonus_chance',
            field=models.DecimalField(decimal_places=4, default=0.0, help_text='Вероятность выпадения бонуса после открытия кейса', max_digits=5, verbose_name='Шанс выпадения бонуса (0-1)'),
        ),
        migrations.AddField(
            model_name='case',
            name='bonus_type_chance_multiplier',
            field=models.DecimalField(decimal_places=4, default=0.5, help_text='Если бонус выпал, вероятность что это будет множитель (иначе - доп. открытие)', max_digits=5, verbose_name='Шанс множителя vs доп. открытия (0-1)'),
        ),
        migrations.AddField(
            model_name='case',
            name='bonus_multipliers',
            field=models.JSONField(blank=True, default=list, help_text='Список множителей с весами: [{"multiplier": 2, "weight": 10}, {"multiplier": 3, "weight": 5}]', null=True, verbose_name='Множители бонуса'),
        ),
        migrations.AddField(
            model_name='case',
            name='max_bonus_opens',
            field=models.PositiveIntegerField(default=1, help_text='Максимальное количество дополнительных открытий за один спин', verbose_name='Максимум доп. открытий'),
        ),
        # Добавляем поля в модель Spin
        migrations.AddField(
            model_name='spin',
            name='has_bonus',
            field=models.BooleanField(default=False, verbose_name='Есть бонус'),
        ),
        migrations.AddField(
            model_name='spin',
            name='bonus_type',
            field=models.CharField(blank=True, choices=[('multiplier', 'Множитель'), ('extra_open', 'Дополнительное открытие')], max_length=20, null=True, verbose_name='Тип бонуса'),
        ),
        migrations.AddField(
            model_name='spin',
            name='bonus_multiplier',
            field=models.PositiveIntegerField(blank=True, help_text='Множитель выигрыша (x2, x3 и т.д.)', null=True, verbose_name='Множитель бонуса'),
        ),
        migrations.AddField(
            model_name='spin',
            name='base_amount_usd',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Сумма выигрыша до применения бонуса', max_digits=14, null=True, verbose_name='Начальная сумма выигрыша'),
        ),
        migrations.AddField(
            model_name='spin',
            name='bonus_spins',
            field=models.JSONField(blank=True, help_text='Массив дополнительных спинов: [{"spin_id": ..., "amount": ..., "bonus_type": ...}]', null=True, verbose_name='Дополнительные спины'),
        ),
    ]

