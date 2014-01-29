from django.conf.urls import patterns, url;
from socialsite.api import api;



urlpatterns = patterns("",
	url(r"^get-posts-by/(?P<username>\w+)/$", api.getPostedBy),
	url(r"^get-replies-to/(?P<postId>\w+)/$", api.getRepliesTo),
	url(r"^get-post/(?P<postId>\w+)/$", api.getPost),
	url(r"^get-posts-by-users-followed-by/(?P<username>\w+)/$", api.getPostsByUsersFollowedBy),
	url(r"^post-post/$", api.postPost),
	url(r"^delete-post/$", api.deletePost),
	url(r"^get-follower-count/(?P<username>\w+)/$", api.getFollowerCount),
	url(r"^get-followed-count/(?P<username>\w+)/$", api.getFollowedCount),
	url(r"^get-followers/(?P<username>\w+)/$", api.getFollowers),
	url(r"^get-users-followed-by/(?P<username>\w+)/$", api.getUsersFollowedBy)
);