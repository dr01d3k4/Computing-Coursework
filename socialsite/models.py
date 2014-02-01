from django.contrib.auth.models import User;
from django.db import models;
from django.core.urlresolvers import reverse;
from django.core.exceptions import ValidationError;
from ComputingCoursework import settings;
import re;
import os;



profileImageMegabyteLimit = 2;



def buildUrlPattern():
	protocol = "https?://";

	validLetter = "[\w\-_]";

	ipDigit = "(" \
		+ "(0|1)?\d?\d" \
		+ "|" \
		+ "(" \
			+ "2[0-4]\d"\
			+ "|" \
			+ "25[0-5]" \
		+ ")" \
		+ ")";
	ip = "(" + ipDigit + "\.){3}" + ipDigit;
	port = "(:\d{4})?"

	domain = "(" + validLetter + "+\.)*";
	lastDomain = "(" + validLetter + "+)";

	folder = "(/" + validLetter + "+)*";

	parameter = validLetter + "+=" + validLetter + "+";

	parameterList = "\?" + parameter + "(&" + parameter + ")*";

	parameters = "(/" + validLetter + "*" + parameterList + ")?"

	urlPattern = r"^" \
		+ protocol \
		+ "(" \
			+ ip \
			+ port \
		+ "|" \
			+ domain \
			+ lastDomain \
		+ ")" \
		+ folder \
		+ parameters \
		+ "/?" \
		+ "$";

	return urlPattern;

urlPattern = re.compile(buildUrlPattern());



class UserProfile(models.Model):
	user = models.OneToOneField(User, db_index = True, related_name = "user_profile");
	first_name = models.CharField(max_length = 256);
	middle_name = models.CharField(max_length = 256, blank = True);
	last_name = models.CharField(max_length = 256, blank = True);
	description = models.CharField(max_length = 256, blank = True);



	def validateWebsite(urlObject):
		print("Validating model");
		print("Url object %s" % urlObject);
		if (not re.match(urlPattern, urlObject)):
			raise ValidationError("Invalid address");



	website = models.CharField(blank = True, max_length = 256, validators = [validateWebsite]);



	def validateProfileImage(fieldFileObject):
		fileSize = fieldFileObject.file.size;
		if (fileSize > profileImageMegabyteLimit * 1024 * 1024):
			raise ValidationError("This file is too large.  Max size is %(size)Mb", params = {size: str(profileImageMegabyteLimit)}, code = "large");



	def generateNewFilename(instance, filename):
		file, extension = os.path.splitext(filename);
		newFileName = "/".join(("profile-images", "%s-profile-image%s" % (instance.user.username, extension)));

		existingFile = "/".join((settings.MEDIA_ROOT, newFileName));
		if (os.path.exists(existingFile)):
			os.remove(existingFile);

		return newFileName;



	profile_image = models.ImageField(upload_to = generateNewFilename, blank = True, validators = [validateProfileImage]);



	def getFullName(self):
		name = self.first_name;
		if (len(self.middle_name) > 0):
			name += " " + self.middle_name;
		name += " " + self.last_name;
		return name;

	fullName = property(getFullName);



	def getFollowersQS(self):
		return Following.objects.filter(followed = self.user);



	def getFollowedQS(self):
		return Following.objects.filter(follower = self.user);



	def getFollowerCount(self):
		return self.getFollowersQS().count() - 1;



	def getFollowedCount(self):
		return self.getFollowedQS().count() - 1;



	def getFollowers(self):
		return self.getFollowersQS().values_list("follower", flat = True);



	def getFollowed(self):
		return self.getFollowedQS().values_list("followed", flat = True);



	def followsUser(self, otherUser):
		follows = False;
		if (self.user != otherUser):
			try:
				Following.objects.get(followed = otherUser, follower = self.user);
				follows = True;
			except (Following.DoesNotExist):
				pass;
		return follows;



	def followedByUser(self, otherUser):
		follows = False;
		if (self.user != otherUser):
			try:
				Following.objects.get(follower = otherUser, followed = self.user);
				follows = True;
			except (Following.DoesNotExist):
				pass;
		return follows;



	def getPostsQS(self):
		return Post.objects.filter(user = self.user).order_by("-date");



	def toDictionary(self):
		dictionary = {
			"id": self.user.id,
			"username": self.user.username,
			"firstName": self.first_name,
			"middleName": self.middle_name,
			"lastName": self.last_name,
			"fullName": self.fullName,
			"absoluteUrl": self.get_absolute_url(),
		};

		if (self.profile_image):
			dictionary["profileImage"] = self.profile_image.url;
		else:
			dictionary["profileImage"] = "";

		return dictionary;



	def __unicode__(self):
		return self.fullName;



	# @permalink
	def get_absolute_url(self):
		return reverse("social:profile", args = [self.user.username]);



class Post(models.Model):
	content = models.CharField(max_length = 256);
	user = models.ForeignKey(User, db_index = True, related_name = "post");
	date = models.DateTimeField(db_index = True, auto_now_add = True);



	def getFirstPost(self):
		try:
			return Reply.objects.get(reply_post = self).first_post;
		except (Reply.DoesNotExist):
			return None;



	def getReplies(self):
		replies = Reply.objects.filter(first_post = self).order_by("-reply_post__date");

		firstPosters = [ ];
		firstPost = self;

		while (firstPost is not None):
			firstPosters.append(firstPost.user);
			firstPost = firstPost.getFirstPost();

		postsByFirstPosters = [ ];
		otherPosts = [ ];

		for reply in replies:
			replyPost = reply.reply_post;

			if (replyPost.user in firstPosters):
				postsByFirstPosters.append(replyPost);
			else:
				otherPosts.append(replyPost);

		return postsByFirstPosters + otherPosts;



	def isDeletableBy(self, user):
		return (self.user == user);



	def toDictionary(self, secondLevel = False, loggedInUser = None):
		postDictionary = {
			"id": self.id,
			"content": self.content,
			"date": self.date.strftime("%A, %d %B %Y %H:%M %p"),
			"poster": UserProfile.objects.get(user = self.user).toDictionary()
		};

		if (loggedInUser is not None):
			postDictionary["isDeletableByLoggedInUser"] = self.isDeletableBy(loggedInUser);
		else:
			postDictionary["isDeletableByLoggedInUser"] = False;

		firstPost = self.getFirstPost();
		if ((firstPost is not None) and (not secondLevel)):
			postDictionary["isReplyTo"] = firstPost.toDictionary(secondLevel = True, loggedInUser = loggedInUser);

		return postDictionary;



	def __unicode__(self):
		return "%s: %s" % (self.user.username, self.content);



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