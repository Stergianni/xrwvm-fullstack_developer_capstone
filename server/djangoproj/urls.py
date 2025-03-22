from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('djangoapp/', include('djangoapp.urls')),
    path('', TemplateView.as_view(template_name="Home.html")),
    
    # Add the About Us page URL
    path('about/', TemplateView.as_view(template_name="About.html")),
    
    # Add the Contact Us page URL
    path('contact/', TemplateView.as_view(template_name="Contact.html")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
