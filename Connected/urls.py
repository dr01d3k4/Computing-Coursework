from django.conf.urls import patterns, include, url;



from django.contrib import admin;
admin.autodiscover();



urlpatterns = patterns("",
	url(r"^admin/", include(admin.site.urls)),
	url(r"^/?", include("connected.urls", namespace = "connected")),
	url(r"^/?$", include("connected.urls"))
);



import settings;
if (settings.DEBUG):
	urlpatterns += patterns("django.views.static", (r"media/(?P<path>.*)", "serve", {"document_root": settings.MEDIA_ROOT}), );