from django.conf.urls import patterns, include, url;
from socialsite import views;



urlpatterns = patterns("",
	url(r"^$", views.Index.as_view(), name = "index"),
	url(r"^profile/$", views.Profile.as_view(), name = "profile"),
	url(r"^profile/(?P<username>\w+)/$", views.Profile.as_view(), name = "profile"),
	url(r"^logout/$", views.logoutPage, name = "logout"),
	url(r"^follow/$", views.Follow.as_view(), name = "follow"),
	url(r"^search/$", views.Search.as_view(), name = "search"),
	url(r"^search/(?P<searchTerm>\w+)/$", views.Search.as_view(), name = "search"),
	url(r"^settings/$", views.Settings.as_view(), name = "settings"),
	url(r"^api/", include("socialsite.api.urls"))
);