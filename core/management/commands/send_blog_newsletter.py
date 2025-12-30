from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.core import signing

from core.models import BlogPost, BlogSubscriber


def build_post_url(post):
    base_url = getattr(settings, "SITE_URL", "").rstrip("/")
    return f"{base_url}{post.get_absolute_url()}" if base_url else post.get_absolute_url()


def build_unsubscribe_url(email):
    base_url = getattr(settings, "SITE_URL", "").rstrip("/")
    token = signing.dumps(email, salt="blog-subscriber")
    path = f"/blog/newsletter/desabonnement/{token}/"
    return f"{base_url}{path}" if base_url else path


def build_email(language, post, email):
    title = post.title_fr
    excerpt = post.excerpt_fr
    subject = f"Nouvel article medical: {title}"
    body = (
        f"{title}\n\n"
        f"{excerpt}\n\n"
        f"Lire l'article: {build_post_url(post)}\n\n"
        "Vous recevez cet email car vous etes inscrit au blog medical.\n"
        f"Se desabonner: {build_unsubscribe_url(email)}"
    )
    return subject, body


class Command(BaseCommand):
    help = "Send the newsletter for a published blog post."

    def add_arguments(self, parser):
        parser.add_argument("--slug", help="Blog post slug to send")
        parser.add_argument("--force", action="store_true", help="Send even if already sent")

    def handle(self, *args, **options):
        slug = options.get("slug")
        force = options.get("force")

        if slug:
            try:
                post = BlogPost.objects.get(slug=slug, status=BlogPost.Status.PUBLISHED)
            except BlogPost.DoesNotExist as exc:
                raise CommandError("Article introuvable ou non publie.") from exc
        else:
            post = BlogPost.objects.published().first()
            if not post:
                raise CommandError("Aucun article publie.")

        if post.newsletter_sent and not force:
            self.stdout.write(self.style.WARNING("Newsletter deja envoyee (utilise --force pour renvoyer)."))
            return

        subscribers = BlogSubscriber.objects.filter(is_active=True)
        if not subscribers.exists():
            self.stdout.write(self.style.WARNING("Aucun abonne actif."))
            return

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
        total_sent = 0
        batch = list(subscribers.values_list("email", flat=True))
        for email in batch:
            subject, body = build_email("fr", post, email)
            send_mail(
                subject,
                body,
                from_email,
                [email],
                fail_silently=False,
            )
            total_sent += 1

        post.newsletter_sent = True
        post.save(update_fields=["newsletter_sent"])
        self.stdout.write(self.style.SUCCESS(f"Newsletter envoyee a {total_sent} abonne(s)."))
