# Generated manually for BonusSpin model

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0008_add_parent_spin_to_spin'),
    ]

    operations = [
        migrations.CreateModel(
            name='BonusSpin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('actual_amount_usd', models.DecimalField(decimal_places=2, default=0.01, max_digits=14, verbose_name='Сумма выигрыша')),
                ('server_seed_hash', models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='Server Seed Hash')),
                ('server_seed', models.TextField(blank=True, null=True, verbose_name='Server Seed')),
                ('client_seed', models.CharField(blank=True, max_length=64, null=True, verbose_name='Client Seed')),
                ('nonce', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Nonce')),
                ('roll_digest', models.CharField(blank=True, max_length=64, null=True, verbose_name='Roll Digest')),
                ('rng_value', models.DecimalField(blank=True, decimal_places=18, max_digits=20, null=True, verbose_name='RNG Value')),
                ('weights_snapshot', models.JSONField(blank=True, null=True, verbose_name='Снимок весов')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cases.case', verbose_name='Кейс')),
                ('case_prize', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cases.caseprize', verbose_name='Приз кейса')),
                ('parent_spin', models.ForeignKey(help_text='Основной спин, к которому относится это дополнительное открытие', on_delete=django.db.models.deletion.CASCADE, related_name='bonus_spin_records', to='cases.spin', verbose_name='Основной спин')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Дополнительное открытие',
                'verbose_name_plural': 'Дополнительные открытия',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='bonusspin',
            index=models.Index(fields=['parent_spin', '-created_at'], name='cases_bonus_parent__idx'),
        ),
        migrations.AddIndex(
            model_name='bonusspin',
            index=models.Index(fields=['user', '-created_at'], name='cases_bonus_user_id_idx'),
        ),
    ]

