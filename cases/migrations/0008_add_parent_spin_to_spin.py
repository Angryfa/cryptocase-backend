# Generated manually for parent_spin field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0007_add_bonus_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='spin',
            name='parent_spin',
            field=models.ForeignKey(
                blank=True,
                help_text='Если это дополнительное открытие, указывает на основной спин',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='extra_spins',
                to='cases.spin',
                verbose_name='Основной спин'
            ),
        ),
    ]

