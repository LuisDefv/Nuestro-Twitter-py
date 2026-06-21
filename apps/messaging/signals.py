import threading

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message


@receiver(post_save, sender=Message)
def trigger_ai_bot_dm_reply(sender, instance, created, **kwargs):
    """Si le escriben al bot de IA por DM, generar su respuesta en un thread."""
    if not created:
        return

    from apps.posts.ai import get_bot_user, reply_to_dm

    bot = get_bot_user()
    # El bot no se responde a sí mismo.
    if instance.sender_id == bot.id:
        return
    # Solo si el bot participa de la conversación.
    if not instance.conversation.participants.filter(id=bot.id).exists():
        return

    threading.Thread(
        target=reply_to_dm,
        args=(instance.conversation_id,),
        daemon=True,
    ).start()
