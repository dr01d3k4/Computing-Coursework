from django.conf.urls import patterns, include, url;
from connected import views;



urlpatterns = patterns("",
	url(r"^$", views.Index.as_view(), name = "index"),
	url(r"^profile/$", views.Profile.as_view(), name = "profile"),
	url(r"^profile/(?P<username>.+)/$", views.Profile.as_view(), name = "profile"),
	url(r"^search/$", views.Search.as_view(), name = "search"),
	url(r"^search/(?P<searchTerm>.+)/$", views.Search.as_view(), name = "search"),
	url(r"^settings/$", views.Settings.as_view(), name = "settings"),
	url(r"^view-followers/(?P<username>.+)/$", views.ViewFollowers.as_view(), name = "view-followers"),
	url(r"^view-followed/(?P<username>.+)/$", views.ViewFollowed.as_view(), name = "view-followed"),
	url(r"^api/", include("connected.api.urls", namespace = "api"))
);