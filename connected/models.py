from django.contrib.auth.models import User;
from django.db import models;
from django.core.urlresolvers import reverse;
from django.core.exceptions import ValidationError;
from django.utils.html import conditional_escape;
from django.db.models import Q;

from Connected import settings;
from connected.url_matcher import urlPattern;

import re;
import os;



profileImageMegabyteLimit = 2;



class UserProfile(models.Model):
	user = models.OneToOneField(User, db_index = True, related_name = "user_profile");
	first_name = models.CharField(max_length = 256);
	middle_name = models.CharField(max_length = 256, blank = True);
	last_name = models.CharField(max_length = 256, blank = True);
	description = models.CharField(max_length = 1000, blank = True);



	def validateWebsite(urlObject):
		if (not re.match(urlPattern, urlObject)):
			raise ValidationError("Invalid address");



	website = models.CharField(blank = True, max_length = 256, validators = [validateWebsite]);



	def validateProfileImage(fieldFileObject):
		fileSize = fieldFileObject.file.size;
		if (fileSize > profileImageMegabyteLimit * 1024 * 1024):
			raise ValidationError("This file is too large.  Max size is %(size)Mb", params = {size: str(profileImageMegabyteLimit)}, code = "large");



	def generateNewFilenameForProfileImage(instance, filename):
		file, extension = os.path.splitext(filename);
		newFileName = "/".join(("profile-images", "%s-profile-image%s" % (instance.user.username, extension)));

		existingFile = "/".join((settings.MEDIA_ROOT, newFileName));
		if (os.path.exists(existingFile)):
			os.remove(existingFile);

		return newFileName;



	profile_image = models.ImageField(upload_to = generateNewFilenameForProfileImage, blank = True, validators = [validateProfileImage]);



	def getFullName(self):
		name = self.first_name;
		if (len(self.middle_name) > 0):
			name += " " + self.middle_name;
		name += " " + self.last_name;
		return name;

	fullName = property(getFullName);



	def getFollowersQs(self):
		return Following.objects.filter(followed = self.user);



	def getFollowedQs(self):
		return Following.objects.filter(follower = self.user);



	def getFollowerCount(self):
		return self.getFollowersQs().count();



	def getFollowedCount(self):
		return self.getFollowedQs().count();



	def getFollowers(self):
		return self.getFollowersQs().values_list("follower", flat = True);



	def getFollowed(self):
		return self.getFollowedQs().values_list("followed", flat = True);



	def followsUser(self, otherUser):
		follows = False;
		if (self.user != otherUser):
			try:
				Following.objects.get(followed = otherUser, follower = self.user);
				follows = True;
			except (Following.DoesNotExist):
				pass;
		return follows;



	def isFollowedBy(self, otherUser):
		follows = False;
		if (self.user != otherUser):
			try:
				Following.objects.get(follower = otherUser, followed = self.user);
				follows = True;
			except (Following.DoesNotExist):
				pass;
		return follows;



	def getPostsQs(self):
		return Post.objects.filter(user = self.user).order_by("-date");



	def getPostsByUsersFollowedQs(self):
		return Post.objects.filter(Q(user__in = self.getFollowed()) | Q(user = self.user)).order_by("-date");
		


	def getPostsRepliedToQs(self):
		postsByUser = Post.objects.filter(user = self.user);
		firstPostList = Reply.objects.filter(reply_post = postsByUser).values("first_post");
		firstPosts = Post.objects.filter(id__in = firstPostList);
		return firstPosts;



	def getUsersRepliedToQs(self):
		firstPosts = self.getPostsRepliedToQs();
		firstPostPosters = firstPosts.values("user").distinct();
		users = User.objects.filter(id__in = firstPostPosters).select_related("user_profile");
		return users;



	def getPostsRepliedToPostsByUserQS(self, otherUser):
		return self.getPostsRepliedToQs().filter(user = otherUser);



	def getPostsThatAreRepliesToPostsByUserQs(self, otherUser):
		allRepliesToOtherUser = Reply.objects.filter(first_post__user = otherUser);
		replyPostsToOtherUser = allRepliesToOtherUser.values_list("reply_post", flat = True)
		postsBySelf = Post.objects.filter(user = self.user)
		postsBySelfToOtherUser = postsBySelf.filter(id__in = replyPostsToOtherUser);
		return postsBySelfToOtherUser;



	def getCountOfRepliesToPostsByUser(self, otherUser):
		return self.getPostsThatAreRepliesToPostsByUserQs(otherUser).count();



	def toggleFollows(self, otherUser):
		follows = False;

		try:
			Following.objects.get(follower = self.user, followed = otherUser).delete();
			follows = False;

		except (Following.DoesNotExist):
			Following.objects.get_or_create(follower = self.user, followed = otherUser);
			follows = True;

		return follows;



	def toDictionary(self):
		dictionary = {
			"id": self.user.id,
			"username": self.viewableUsername,
			"firstName": self.first_name,
			"middleName": self.middle_name,
			"lastName": self.last_name,
			"fullName": self.fullName,
			"absoluteUrl": self.absoluteUrl,
			"description": self.description,
			"website": self.website
		};

		if (self.profile_image):
			dictionary["profileImage"] = self.profile_image.url;
		else:
			dictionary["profileImage"] = "";

		return dictionary;



	def __unicode__(self):
		return self.fullName;



	def getViewableUsername(self):
		return "@%s" % self.user.username;


	viewableUsername = property(getViewableUsername);



	def get_absolute_url(self):
		return reverse("connected:profile", args = [self.user.username]);

	absoluteUrl = property(get_absolute_url);



class Post(models.Model):
	user = models.ForeignKey(User, db_index = True, related_name = "post");
	content = models.CharField(max_length = 256);
	date = models.DateTimeField(db_index = True, auto_now_add = True);



	def getFirstPost(self):
		try:
			return Reply.objects.get(reply_post = self).first_post;
		except (Reply.DoesNotExist):
			return None;



	def getReplies(self):
		replyPosts = Post.objects.filter(id__in = Reply.objects.filter(first_post = self).values_list("reply_post", flat = True)).order_by("-date");

		firstPosters = [ ];
		firstPost = self;

		while (firstPost is not None):
			firstPosters.append(firstPost.user);
			firstPost = firstPost.getFirstPost();

		postsByFirstPosters = [ ];
		otherPosts = [ ];

		for replyPost in replyPosts:
			if (replyPost.user in firstPosters):
				postsByFirstPosters.append(replyPost);
			else:
				otherPosts.append(replyPost);

		return postsByFirstPosters + otherPosts;



	def isDeletableBy(self, user = None):
		return ((user is not None) and (self.user == user));


	
	@staticmethod
	def getPostFromId(id):
		post = None;
		try:
			post = Post.objects.get(id = id);
		except (Post.DoesNotExist):
			pass;
		return post;



	@staticmethod
	def postPost(user, content, replyToId = None):
		content = str(conditional_escape(content));
		replyToPost = None;

		if ((replyToId is not None) and (replyToId >= 0)):
			replyToPost = Post.getPostFromId(replyToId);

		post = Post.objects.create(user = user, content = content);
		if (replyToPost != None):
			reply = Reply.objects.create(first_post = replyToPost, reply_post = post);

		return post;



	def deleteBy(self, user):
		isDeletable = self.isDeletableBy(user);
	
		if (isDeletable):
			self.delete();
		
		return isDeletable;



	def getFormattedDate(self):
		return self.date.strftime("%A, %d %B %Y %H:%M %p");



	def toDictionary(self, secondLevel = False, loggedInUser = None):
		postDictionary = {
			"id": self.id,
			"content": self.content,
			"date": self.getFormattedDate(),
			"poster": UserProfile.objects.get(user = self.user).toDictionary(),
			"isDeletableByLoggedInUser": self.isDeletableBy(loggedInUser)
		};

		firstPost = self.getFirstPost();
		if ((firstPost is not None) and (not secondLevel)):
			postDictionary["isReplyTo"] = firstPost.toDictionary(secondLevel = True, loggedInUser = loggedInUser);

		return postDictionary;



	def __unicode__(self):
		return "%s %s: %s" % (self.getFormattedDate(), self.user.username, self.content);



class Reply(models.Model):
	first_post = models.ForeignKey(Post, db_index = True, related_name = "first_post");
	reply_post = models.ForeignKey(Post, db_index = True, related_name = "reply_post");

	def __unicode__(self):
		return "%s replied to %s" % (self.reply_post.user.username, self.first_post.user.username);

	class Meta:
		verbose_name_plural = "Replies";



class Following(models.Model):
	followed = models.ForeignKey(User, db_index = True, related_name = "followed");
	follower = models.ForeignKey(User, db_index = True, related_name = "follower");

	def __unicode__(self):
		return "%s follows %s" % (self.follower.username, self.followed.username);