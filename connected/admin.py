from django.contrib import admin;
from connected.models import UserProfile, Post, Reply, Following;



class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "first_name", "middle_name", "last_name", "description", "profile_image", "website");
admin.site.register(UserProfile, UserProfileAdmin);



class PostAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "content", "date");
admin.site.register(Post, PostAdmin);



class ReplyAdmin(admin.ModelAdmin):
	list_display = ("id", "first_post", "reply_post");
admin.site.register(Reply, ReplyAdmin);



class FollowingAdmin(admin.ModelAdmin):
	list_display = ("id", "followed", "follower");
admin.site.register(Following, FollowingAdmin);