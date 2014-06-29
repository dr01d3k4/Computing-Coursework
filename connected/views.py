from django.shortcuts import render;
from django.views.generic.base import View;
from django.template import RequestContext;
from django.http import HttpResponseRedirect, HttpResponse, Http404;
from django.contrib.auth import authenticate, login;
from django.utils.decorators import method_decorator;
from django.contrib.auth.decorators import login_required;
from django.contrib.auth.models import User;
from django.core.urlresolvers import reverse;
from django.db.models import Q;

import random;
from connected.models import UserProfile, Following, Reply, Post;
from connected.forms import UserForm, UserProfileRegisterForm, UserProfileSettingsForm;



class Index(View):
	def get(self, request):
		if (request.user.is_authenticated()):
			return HttpResponseRedirect(reverse("connected:profile"));
		else:
			context = { };
			context["registerUserForm"] = UserForm();
			context["registerUserProfileForm"] = UserProfileRegisterForm();
			context["siteTitle"] = "Welcome";

			return render(request, "index.html", context);
			


	def post(self, request):
		submit = request.POST["submit"].lower();
		
		if (submit == "register"):
			userForm = UserForm(data = request.POST);
			userProfileRegisterForm = UserProfileRegisterForm(data = request.POST);

			currentUser = None;
			try:
				currentUser = User.objects.get(username__iexact = request.POST["username"]);
			except (User.DoesNotExist):
				pass;


			passwordsMatch = (request.POST["password"] == request.POST["confirm_password"]);


			if ((currentUser is None) and passwordsMatch and userForm.is_valid() and userProfileRegisterForm.is_valid()):
				user = userForm.save();

				user.set_password(user.password);
				user.save();

				profile = userProfileRegisterForm.save(commit = False);
				profile.user = user;
				profile.save();

				username = request.POST["username"];
				password = request.POST["password"];
				user = authenticate(username = username, password = password);

				if ((user is not None) and (user.is_active)):
					login(request, user);
					return HttpResponseRedirect(reverse("connected:profile"));
			else:
				context = { };
				context["registerUserForm"] = userForm;
				context["registerUserProfileForm"] = userProfileRegisterForm;
				context["userAlreadyExists"] = (currentUser is not None);
				context["passwordsDontMatch"] = not passwordsMatch;
				context["autoOpenTo"] = "register";
				context["siteTitle"] = "Welcome";

				return render(request, "index.html", context);

		elif (submit == "login"):
			username = request.POST["username"];

			logInUser = None;
			try:
				logInUser = User.objects.get(username__iexact = username);
			except (User.DoesNotExist):
				pass;

			if (logInUser is not None):
				username = logInUser.username;

			password = request.POST["password"];
			user = authenticate(username = username, password = password);

			context = { };

			if (user is not None):
				if (user.is_active):
					login(request, user);
					return HttpResponseRedirect(reverse("connected:profile"));
				else:
					context["diabledAccount"] = True;
			else:
				context["badDetails"] = True;

			context["registerUserForm"] = UserForm();
			context["registerUserProfileForm"] = UserProfileRegisterForm();
			context["autoOpenTo"] = "login";
			context["siteTitle"] = "Welcome";

			return render(request, "index.html", context);



class Profile(View):
	@method_decorator(login_required)
	def get(self, request, username = None):
		viewingUser = None;
		viewingProfile = None;
		userProfile = request.user.user_profile;

		if (username is None):
			viewingUser = request.user;
		else:
			try:
				viewingUser = User.objects.get(username__iexact = username);
			except (User.DoesNotExist):
				raise Http404;

		try:
			viewingProfile = viewingUser.user_profile;
		except (UserProfile.DoesNotExist):
			raise Http404;

		followerCount = viewingProfile.getFollowerCount();
		followCount = viewingProfile.getFollowedCount();

		isFollowing = userProfile.followsUser(viewingUser);

		context = { };
		context["userProfile"] = userProfile;
		context["viewingUser"] = viewingUser;
		context["viewingProfile"] = viewingProfile;
		context["isFollowing"] = isFollowing;
		context["followerCount"] = followerCount;
		context["followCount"] = followCount;
		context["headerTitle"] = viewingProfile.fullName;
		context["headerSmallTitle"] = viewingProfile.viewableUsername;
		context["siteTitle"] = "Profile";

		usersRepliedToQs = viewingProfile.getUsersRepliedToQs().exclude(id = viewingUser.id);
		usersRepliedTo = [ ];
 		for otherUser in usersRepliedToQs:
			otherUser.count = userProfile.getCountOfRepliesToPostsByUser(otherUser);
			usersRepliedTo.append(otherUser);
		usersRepliedTo.sort(key = lambda user: -user.count);

		if (userProfile == viewingProfile):
			usersRepliedTo = usersRepliedTo[0:5];

			replies = Reply.objects.filter(reply_post__user__in = usersRepliedTo);
			posts = Post.objects.filter(first_post__in = replies);
			userIds = posts.values_list("user", flat = True);

			users = User.objects.filter(id__in = userIds)
			users = users.exclude(id = request.user.id);
			users = users.exclude(followed__in = userProfile.getFollowedQs());

			usersRepliedTo = users;

			context["usersRepliedTo"] = usersRepliedTo;

		else:
			lenUsersRepliedTo = len(usersRepliedTo);
			RANDOM_USER_COUNT_MAX = 5;
			randomUserCount = lenUsersRepliedTo if lenUsersRepliedTo < RANDOM_USER_COUNT_MAX else RANDOM_USER_COUNT_MAX;
			randomUsersRepliedTo = random.sample(usersRepliedTo, randomUserCount);
			randomUsersRepliedTo.sort(key = lambda user: -user.count);
			context["usersRepliedTo"] = randomUsersRepliedTo;

		if (viewingProfile.profile_image):
			context["profileImage"] = viewingProfile.profile_image.url;

		return render(request, "profile.html", context);



class Search(View):
	def get(self, request, searchTerm = ""):
		userProfile = request.user.user_profile;

		userProfiles = UserProfile.objects.filter(
			Q(user__username__icontains = searchTerm) |
			Q(first_name__icontains = searchTerm) |
			Q(last_name__icontains = searchTerm) |
			Q(middle_name__icontains = searchTerm)
		);
		context = { };
		context["userProfile"] = userProfile;
		context["userProfiles"] = userProfiles;
		context["headerTitle"] = "Search";
		context["headerSmallTitle"] = "Search for your friends";
		context["siteTitle"] = "Search";
		length = len(userProfiles);
		context["userListTitle"] = "%d result%s for '%s'" % (length, "s" if length != 1 else "", searchTerm);

		return render(request, "user_list.html", context);



class Settings(View):
	def get(self, request):
		userProfile = request.user.user_profile;

		userProfileSettingsForm = UserProfileSettingsForm(instance = userProfile);

		context = { };
		context["userProfile"] = userProfile;
		context["userProfileSettingsForm"] = userProfileSettingsForm;
		context["headerTitle"] = "Settings";
		context["headerSmallTitle"] = "Configure your profile";
		context["siteTitle"] = "Settings";

		return render(request, "settings.html", context);



	def post(self, request):
		userProfile = request.user.user_profile;
		userProfileSettingsForm = UserProfileSettingsForm(request.POST, request.FILES, instance = userProfile);

		if (userProfileSettingsForm.is_valid()):
			userProfileSettingsForm.save();
			return HttpResponseRedirect(reverse("connected:index"));

		else:
			context = { };
			context["userProfile"] = userProfile;
			context["userProfileSettingsForm"] = userProfileSettingsForm;
			return render(request, "connected/settings.html", context);



class ViewFollowersOrFollowed(View):
	def getUsers(self, viewingProfile, viewingUser):
		pass;



	def getTitle(self):
		pass;



	def getMessage(self, name):
		pass;



	def get(self, request, username = None):
		viewingUser = None;
		viewingProfile = None;
		userProfile = request.user.user_profile;

		if (username is None):
			viewingUser = request.user;
		else:
			try:
				viewingUser = User.objects.get(username__iexact = username);
			except (User.DoesNotExist):
				raise Http404;

		try:
			viewingProfile = viewingUser.user_profile;
		except (UserProfile.DoesNotExist):
			raise Http404;

		userProfiles = self.getUsers(viewingProfile, viewingUser);
		name = viewingProfile.first_name;

		context = { };
		context["userProfile"] = userProfile;
		context["userProfiles"] = userProfiles;
		followersMessage = self.getMessage(name);
		title = self.getTitle();
		context["siteTitle"] = title;
		context["userListTitle"] = followersMessage;
		context["headerTitle"] = title;
		context["headerSmallTitle"] = viewingProfile.viewableUsername;

		return render(request, "user_list.html", context);



class ViewFollowers(ViewFollowersOrFollowed):
	def getUsers(self, viewingProfile, viewingUser):
		return UserProfile.objects.filter(user = viewingProfile.getFollowers());


	def getTitle(self):
		return "Followers";


	def getMessage(self, name):
		return "%s'%s followers" % (name, "s" if name[-1] != "s" else "");



class ViewFollowed(ViewFollowersOrFollowed):
	def getUsers(self, viewingProfile, viewingUser):
		return UserProfile.objects.filter(user = viewingProfile.getFollowed());


	def getTitle(self):
		return "Followed";


	def getMessage(self, name):
		return "Who %s follows" % name;