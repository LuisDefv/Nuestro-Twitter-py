"""Bot de IA estilo Grok usando la API de Gemini (vía REST con requests).

Cuando un usuario arroba al bot (@lekaja) en un post o comentario, se genera
una respuesta con Gemini y se publica como reply al post que lo mencionó.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GEMINI_URL = (
    'https://generativelanguage.googleapis.com/v1beta/models/'
    '{model}:generateContent'
)

# Personalidad del bot: ingenioso y sarcástico (estilo Grok) pero hablando como
# paraguayo cheto asunceno, con jopara/slang ("che olou", "nde", "luego", "ko").
SYSTEM_PROMPT = (
    'Sos {name}, un bot de IA en una red social tipo Twitter. Sos paraguayo, '
    'cheto asunceno: hablás canchero con jopara y slang paraguayo (ej: "che '
    'olou", "nde", "luego", "ko", "pio", "na", "guapo/a"), sin exagerar tanto '
    'que no se entienda. Respondés con ingenio, humor y un toque sarcástico '
    'estilo Grok, pero siempre útil y sin ser ofensivo. Breve y al grano. '
    'Tu respuesta es un comentario público, así que máximo {max_chars} '
    'caracteres. No uses hashtags ni te presentes, andá directo a responder.'
)

# Personalidad para chat privado (DM): igual onda pero conversacional.
CHAT_SYSTEM_PROMPT = (
    'Sos {name}, un bot de IA en una red social tipo Twitter, chateando por '
    'mensaje privado (DM) con un usuario. Sos paraguayo, cheto asunceno: '
    'hablás canchero con jopara y slang paraguayo (ej: "che olou", "nde", '
    '"luego", "ko", "pio", "na", "guapo/a"), sin exagerar tanto que no se '
    'entienda. Respondés con ingenio, humor y un toque sarcástico estilo Grok, '
    'pero siempre útil y sin ser ofensivo. Conversá natural; podés extenderte '
    'un poco más que en un comentario pero sin escribir testamentos. No uses '
    'hashtags ni te presentes en cada mensaje.'
)


def get_bot_user():
    """Devuelve (creando si hace falta) el usuario del bot de IA."""
    from apps.accounts.models import User

    username = settings.AI_BOT_USERNAME
    bot, created = User.objects.get_or_create(
        username=username,
        defaults={
            'bio': '🤖 Bot de IA paraguayo. Arrobame en un comentario y te respondo, che olou.',
            'is_active': True,
        },
    )
    if created:
        bot.set_unusable_password()
        bot.save(update_fields=['password'])
    return bot


def _max_chars():
    try:
        from constance import config as cconfig
        return int(cconfig.POST_MAX_CHARS)
    except Exception:
        return 280


def _gemini_request(system, contents, max_output_tokens=300):
    """Llama a Gemini con un system prompt y una lista de `contents`.

    Devuelve el texto generado, o None si la key falta, la API falla o la
    respuesta vino vacía/bloqueada (mejor silencio que postear un error).
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.warning('GEMINI_API_KEY no configurada; el bot no puede responder.')
        return None

    url = GEMINI_URL.format(model=settings.GEMINI_MODEL)
    payload = {
        'system_instruction': {'parts': [{'text': system}]},
        'contents': contents,
        'generationConfig': {
            'maxOutputTokens': max_output_tokens,
            'temperature': 0.9,
        },
    }

    try:
        resp = requests.post(
            url,
            headers={'X-goog-api-key': api_key},
            json=payload,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        logger.error('Error llamando a Gemini: %s', exc)
        return None

    candidates = data.get('candidates') or []
    if not candidates:
        logger.warning('Gemini sin candidates (posible bloqueo): %s', data.get('promptFeedback'))
        return None
    try:
        text = candidates[0]['content']['parts'][0]['text'].strip()
    except (KeyError, IndexError, TypeError):
        logger.warning('Gemini sin texto usable en la respuesta.')
        return None
    return text or None


def generate_reply(user_text, context_text=''):
    """Llama a Gemini y devuelve el texto de la respuesta, o None si falla."""
    max_chars = _max_chars()
    system = SYSTEM_PROMPT.format(name=settings.AI_BOT_USERNAME, max_chars=max_chars)

    prompt = user_text.strip()
    if context_text:
        prompt = (
            f'Contexto del post original: "{context_text.strip()}"\n\n'
            f'El usuario te dijo: "{user_text.strip()}"'
        )

    text = _gemini_request(system, [{'parts': [{'text': prompt}]}], max_output_tokens=300)
    if not text:
        return None

    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + '…'
    return text


def generate_chat_reply(history):
    """Respuesta conversacional para DM.

    `history` es una lista cronológica de dicts {'is_bot': bool, 'content': str}.
    """
    system = CHAT_SYSTEM_PROMPT.format(name=settings.AI_BOT_USERNAME)
    contents = [
        {
            'role': 'model' if msg['is_bot'] else 'user',
            'parts': [{'text': msg['content']}],
        }
        for msg in history
        if msg['content'].strip()
    ]
    if not contents:
        return None

    text = _gemini_request(system, contents, max_output_tokens=500)
    if not text:
        return None

    max_len = 800
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + '…'
    return text


def reply_to_mention(post_id):
    """Genera y publica la respuesta del bot al post que lo mencionó.

    Pensado para correr en un thread aparte; abre y cierra su propia conexión.
    """
    from django.db import connection

    from .models import Post

    try:
        post = Post.objects.select_related('author', 'parent').get(pk=post_id)
        bot = get_bot_user()

        # Evitar loops: el bot no se responde a sí mismo.
        if post.author_id == bot.id:
            return
        # Evitar responder dos veces al mismo post.
        if Post.objects.filter(parent=post, author=bot).exists():
            return

        context = post.parent.content if post.parent_id else ''
        text = generate_reply(post.content, context_text=context)
        if not text:
            return

        # Arrobamos a quien nos llamó para que le llegue la notificación.
        mention = f'@{post.author.username} '
        content = mention + text
        max_chars = _max_chars()
        if len(content) > max_chars:
            content = content[:max_chars]

        Post.objects.create(author=bot, content=content, parent=post)
    except Exception as exc:  # noqa: BLE001 - thread, no queremos que reviente
        logger.error('Fallo generando respuesta del bot: %s', exc)
    finally:
        connection.close()


def reply_to_dm(conversation_id, history_limit=12):
    """Genera y publica la respuesta del bot en una conversación de DM.

    Pensado para correr en un thread aparte; abre y cierra su propia conexión.
    Además emite el mensaje por el channel layer para que los clientes con el
    WebSocket abierto lo reciban en vivo.
    """
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from django.db import connection

    from apps.messaging.models import Conversation, Message

    try:
        bot = get_bot_user()
        conv = Conversation.objects.filter(
            id=conversation_id, participants=bot
        ).first()
        if not conv:
            return

        recent = list(
            conv.messages.select_related('sender').order_by('-created_at')[:history_limit]
        )
        recent.reverse()
        if not recent:
            return
        # Si el último mensaje ya es del bot, no respondemos (evita loops).
        if recent[-1].sender_id == bot.id:
            return

        history = [
            {'is_bot': m.sender_id == bot.id, 'content': m.content}
            for m in recent
        ]
        text = generate_chat_reply(history)
        if not text:
            return

        message = Message.objects.create(
            conversation=conv, sender=bot, content=text
        )

        channel_layer = get_channel_layer()
        if channel_layer is not None:
            async_to_sync(channel_layer.group_send)(
                f'chat_{conv.id}',
                {
                    'type': 'chat_message',
                    'id': message.id,
                    'sender_id': bot.id,
                    'sender_username': bot.username,
                    'sender_avatar': bot.avatar_url,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                },
            )
    except Exception as exc:  # noqa: BLE001 - thread, no queremos que reviente
        logger.error('Fallo generando respuesta DM del bot: %s', exc)
    finally:
        connection.close()
