from django.contrib import admin, messages
from django.core.management import call_command
from django.core.mail import send_mail
from django.conf import settings
from django.template.response import TemplateResponse
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

from .models import BlogCategory, BlogTag, BlogPost, BlogSubscriber


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_fr")
    search_fields = ("slug", "name_fr")
    prepopulated_fields = {"slug": ("name_fr",)}


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_fr")
    search_fields = ("slug", "name_fr")
    prepopulated_fields = {"slug": ("name_fr",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("slug", "status", "published_at", "author")
    list_filter = ("status", "categories", "tags")
    search_fields = ("slug", "title_fr")
    filter_horizontal = ("categories", "tags")
    autocomplete_fields = ("author",)
    readonly_fields = ("published_at",)
    prepopulated_fields = {"slug": ("title_fr",)}
    actions = ("send_newsletter",)

    def send_newsletter(self, request, queryset):
        if "confirm" not in request.POST:
            context = {
                **self.admin_site.each_context(request),
                "title": "Confirmer l'envoi de la newsletter",
                "queryset": queryset,
                "action": "send_newsletter",
                "opts": self.model._meta,
                "action_checkbox_name": ACTION_CHECKBOX_NAME,
            }
            return TemplateResponse(
                request,
                "admin/core/blogpost/send_newsletter_confirmation.html",
                context,
            )
        sent_count = 0
        skipped = 0
        for post in queryset:
            if post.status != post.Status.PUBLISHED:
                skipped += 1
                continue
            if post.newsletter_sent:
                skipped += 1
                continue
            call_command("send_blog_newsletter", slug=post.slug)
            sent_count += 1
        if sent_count:
            self.message_user(request, f"Newsletter envoyee pour {sent_count} article(s).")
        if skipped:
            self.message_user(
                request,
                f"{skipped} article(s) ignores (non publies ou deja envoyes).",
                level=messages.WARNING,
            )

    send_newsletter.short_description = "Envoyer la newsletter pour ces articles"


@admin.register(BlogSubscriber)
class BlogSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "language", "is_active", "subscribed_at")
    list_filter = ("language", "is_active")
    search_fields = ("email",)
    actions = ("send_test_email",)

    def send_test_email(self, request, queryset):
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
        recipients = list(queryset.values_list("email", flat=True))
        if not recipients:
            self.message_user(request, "Aucun abonne selectionne.", level=messages.WARNING)
            return
        send_mail(
            "Test blog medical",
            "Ceci est un test d'envoi depuis l'administration.",
            from_email,
            recipients,
            fail_silently=False,
        )
        self.message_user(request, f"Email de test envoye a {len(recipients)} abonne(s).")

    send_test_email.short_description = "Envoyer un email de test"
