from django.utils import timezone

from .models import BlogPost


def blog_context(request):
    latest_post = BlogPost.objects.published().first()
    is_new = False
    if latest_post and latest_post.published_at:
        is_new = latest_post.published_at >= timezone.now() - timezone.timedelta(days=14)
    return {
        "latest_blog_post": latest_post,
        "latest_blog_is_new": is_new,
    }
