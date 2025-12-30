from django.conf import settings
from django.core.mail import send_mail
from django.core import signing
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BlogPost, BlogSubscriber


def _build_post_url(post):
    base_url = getattr(settings, "SITE_URL", "").rstrip("/")
    return f"{base_url}{post.get_absolute_url()}" if base_url else post.get_absolute_url()


def _build_unsubscribe_url(email):
    base_url = getattr(settings, "SITE_URL", "").rstrip("/")
    token = signing.dumps(email, salt="blog-subscriber")
    path = f"/blog/newsletter/desabonnement/{token}/"
    return f"{base_url}{path}" if base_url else path


def _build_email_copy(language, post, email):
    title = post.title_fr
    excerpt = post.excerpt_fr
    subject = f"Nouvel article medical: {title}"
    body = (
        f"{title}\n\n"
        f"{excerpt}\n\n"
        f"Lire l'article: {_build_post_url(post)}\n\n"
        "Vous recevez cet email car vous etes inscrit au blog medical.\n"
        f"Se desabonner: {_build_unsubscribe_url(email)}"
    )
    return subject, body


@receiver(post_save, sender=BlogPost)
def notify_subscribers(sender, instance, created, **kwargs):
    if instance.status != BlogPost.Status.PUBLISHED or instance.newsletter_sent:
        return

    email_backend = getattr(settings, "EMAIL_BACKEND", "")
    if "smtp" in email_backend and not getattr(settings, "EMAIL_HOST", ""):
        return

    subscribers = BlogSubscriber.objects.filter(is_active=True)
    if not subscribers.exists():
        instance.newsletter_sent = True
        instance.save(update_fields=["newsletter_sent"])
        return

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    batch = list(subscribers.values_list("email", flat=True))
    for email in batch:
        subject, body = _build_email_copy("fr", instance, email)
        send_mail(
            subject,
            body,
            from_email,
            [email],
            fail_silently=False,
        )

    instance.newsletter_sent = True
    instance.save(update_fields=["newsletter_sent"])
