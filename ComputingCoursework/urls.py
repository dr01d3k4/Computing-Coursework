from django.conf.urls import patterns, include, url;


from django.contrib import admin;
admin.autodiscover();



from django.http import HttpResponseRedirect;
def socialRedirect(request):
	return HttpResponseRedirect("/social/");



urlpatterns = patterns("",
	url(r"^admin/", include(admin.site.urls)),
	url(r"^social/", include("socialsite.urls", namespace = "social")),
	url(r"^/?$", socialRedirect)
);



import settings;
if (settings.DEBUG):
	urlpatterns += patterns("django.views.static", (r"media/(?P<path>.*)", "serve", {"document_root": settings.MEDIA_ROOT}), );