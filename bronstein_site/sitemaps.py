from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from core.views import EXAMS
from core.models import BlogPost


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "home",
            "exam_list",
            "consultations",
            "appointment",
            "pathologies",
            "guides",
            "symptomes",
            "faq",
            "blog_list",
            "actualites",
            "contact",
        ]

    def location(self, item):
        return reverse(item)


class ExamSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return EXAMS

    def location(self, obj):
        return reverse("exam_detail", kwargs={"slug": obj["slug"]})


class BlogPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BlogPost.objects.published()

    def lastmod(self, obj):
        return obj.published_at or obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
 
