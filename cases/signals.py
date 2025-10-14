# без декораторов; просто функции-обработчики и регистратор
from django.db.models.signals import pre_save, post_save, post_delete

def _case_avatar_mark_old_for_delete(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        prev = sender.objects.only("avatar").get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old = prev.avatar
    new = instance.avatar
    if not old:
        return

    new_name = getattr(new, "name", None)
    if not new or old.name != new_name:
        instance._old_avatar_to_delete = old.name  # пометка до успешного save()

def _case_avatar_delete_old_after_save(sender, instance, **kwargs):
    name = getattr(instance, "_old_avatar_to_delete", None)
    if not name:
        return
    try:
        storage = instance.avatar.storage
        if storage.exists(name):
            storage.delete(name)
    finally:
        if hasattr(instance, "_old_avatar_to_delete"):
            delattr(instance, "_old_avatar_to_delete")

def _case_avatar_delete_on_instance_delete(sender, instance, **kwargs):
    f = instance.avatar
    fname = getattr(f, "name", None)
    if not fname:
        return
    try:
        storage = f.storage
        if storage.exists(fname):
            storage.delete(fname)
    except Exception:
        pass

def register_signal_handlers():
    from django.apps import apps
    Case = apps.get_model("cases", "Case")

    pre_save.connect(
        _case_avatar_mark_old_for_delete,
        sender=Case,
        dispatch_uid="cases.case.pre_save.avatar_mark_old",
    )
    post_save.connect(
        _case_avatar_delete_old_after_save,
        sender=Case,
        dispatch_uid="cases.case.post_save.avatar_delete_old",
    )
    post_delete.connect(
        _case_avatar_delete_on_instance_delete,
        sender=Case,
        dispatch_uid="cases.case.post_delete.avatar_delete",
    )
