from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/api/courses/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include("lms.urls")),
    path("api/", include("courses.urls")),
    path("api/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
