from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from core.views import EXAMS


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
 
