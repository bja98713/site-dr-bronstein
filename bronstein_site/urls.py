"""
URL configuration for bronstein_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse

from core import views as core_views

from django.contrib.sitemaps.views import sitemap

from bronstein_site.sitemaps import StaticViewSitemap

def robots_txt(request):
    content = """User-agent: *
Disallow: /admin/
Disallow: /i18n/
Disallow: /api/

Sitemap: https://www.docteur-bronstein-gastro.fr/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("robots.txt", robots_txt),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/chatbot/', core_views.chatbot_api, name='chatbot_api'),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    prefix_default_language=False
)

