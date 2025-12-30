from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import get_language


User = get_user_model()


class LocalizedFieldMixin:
    def _localized_field(self, base_name):
        lang = (get_language() or "fr")[:2]
        for code in (lang, "fr"):
            value = getattr(self, f"{base_name}_{code}", "")
            if value:
                return value
        return ""


class BlogCategory(LocalizedFieldMixin, models.Model):
    slug = models.SlugField(unique=True)
    name_fr = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Blog category"
        verbose_name_plural = "Blog categories"

    def __str__(self):
        return self.name_fr

    @property
    def name_display(self):
        return self._localized_field("name")


class BlogTag(LocalizedFieldMixin, models.Model):
    slug = models.SlugField(unique=True)
    name_fr = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Blog tag"
        verbose_name_plural = "Blog tags"

    def __str__(self):
        return self.name_fr

    @property
    def name_display(self):
        return self._localized_field("name")


class BlogPostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=BlogPost.Status.PUBLISHED, published_at__isnull=False)


class BlogPost(LocalizedFieldMixin, models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    title_fr = models.CharField(max_length=250)
    excerpt_fr = models.TextField(blank=True)
    content_fr = models.TextField()

    image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)

    categories = models.ManyToManyField(BlogCategory, blank=True, related_name="posts")
    tags = models.ManyToManyField(BlogTag, blank=True, related_name="posts")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    newsletter_sent = models.BooleanField(default=False)

    objects = BlogPostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title_fr

    def save(self, *args, **kwargs):
        is_new_publish = self.status == self.Status.PUBLISHED and self.published_at is None
        if is_new_publish:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def title_display(self):
        return self._localized_field("title")

    @property
    def excerpt_display(self):
        return self._localized_field("excerpt")

    @property
    def content_display(self):
        return self._localized_field("content")

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("blog_detail", kwargs={"slug": self.slug})

    @property
    def author_display(self):
        if not self.author:
            return ""
        full_name = self.author.get_full_name()
        return full_name or self.author.get_username()


class BlogSubscriber(models.Model):
    email = models.EmailField(unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.CharField(max_length=2, default="fr")
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Blog subscriber"
        verbose_name_plural = "Blog subscribers"

    def __str__(self):
        return self.email
