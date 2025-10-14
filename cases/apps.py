from django.apps import AppConfig

class CasesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cases"
    verbose_name = "Кейсы"

    def ready(self):
        # Подключаем обработчики сигналов
        from .signals import register_signal_handlers
        register_signal_handlers()