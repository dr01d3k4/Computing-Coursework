from django.shortcuts import render;
from django.views.generic.base import View;
from django.template import RequestContext;
from django.http import HttpResponseRedirect, HttpResponse, Http404;
from django.contrib.auth import authenticate, login, logout;
from django.utils.decorators import method_decorator;
from django.contrib.auth.decorators import login_required;
from django.contrib.auth.models import User;
from django.core.urlresolvers import reverse;

from socialsite.models import UserProfile, Following;
from socialsite.forms import UserForm, UserProfileRegisterForm, UserProfileSettingsForm;



class Index(View):
	def get(self, request):
		if (request.user.is_authenticated()):
			return HttpResponseRedirect(reverse("social:profile"));
		else:
			context = { };
			context["registerUserForm"] = UserForm();
			context["registerUserProfileForm"] = UserProfileRegisterForm(); 

			return render(request, "socialsite/index.html", context);
			


	def post(self, request):
		submit = request.POST["submit"].lower();
		if (submit == "register"):
			userForm = UserForm(data = request.POST);
			userProfileRegisterForm = UserProfileRegisterForm(data = request.POST);

			if (userForm.is_valid() and userProfileRegisterForm.is_valid()):
				user = userForm.save();

				user.set_password(user.password);
				user.save();

				profile = userProfileRegisterForm.save(commit = False);
				profile.user = user;
				profile.save();

				Following.objects.get_or_create(followed = user, follower = user);

				username = request.POST["username"];
				password = request.POST["password"];
				user = authenticate(username = username, password = password);

				if ((user is not None) and (user.is_active)):
					login(request, user);
					return HttpResponseRedirect(reverse("social:profile"));
			else:
				context = { };
				context["registerUserForm"] = userForm;
				context["registerUserProfileForm"] = userProfileRegisterForm;
				context["autoOpenTo"] = "register";

				return render(request, "socialsite/index.html", context);

		elif (submit == "login"):
			username = request.POST["username"];
			password = request.POST["password"];
			user = authenticate(username = username, password = password);

			context = { };

			if (user is not None):
				if (user.is_active):
					login(request, user);
					return HttpResponseRedirect(reverse("social:profile"));
				else:
					context["diabledAccount"] = True;
			else:
				context["badDetails"] = True;

			context["registerUserForm"] = UserForm();
			context["registerUserProfileForm"] = UserProfileRegisterForm();
			context["autoOpenTo"] = "login";

			return render(request, "socialsite/index.html", context);



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

		if (viewingProfile.profile_image):
			context["profileImage"] = viewingProfile.profile_image.url;

		return render(request, "socialsite/profile.html", context);



@login_required
def logoutPage(request):
	logout(request);
	return HttpResponseRedirect("/social/");



class Follow(View):
	@method_decorator(login_required)
	def post(self, request):
		followUsername = request.POST["followUser"]
		followedUser = None;
		try:
			followedUser = User.objects.get(username = followUsername);
		except (User.DoesNotExist):
			raise Http404;

		isAlreadyFollowing = False;
		try:
			Following.objects.get(followed = followedUser, follower = request.user);
			isAlreadyFollowing = True;
		except (Following.DoesNotExist):
			pass;

		if (isAlreadyFollowing):
			Following.objects.get(followed = followedUser, follower = request.user).delete();
		else:
			Following.objects.get_or_create(followed = followedUser, follower = request.user);

		return HttpResponse(str(not isAlreadyFollowing), content_type = "text/plain");



class Search(View):
	def get(self, request, searchTerm = ""):
		return render_to_response("socialsite/search.html", { }, RequestContext(request));



class Settings(View):
	def get(self, request):
		userProfile = request.user.user_profile;

		userProfileSettingsForm = UserProfileSettingsForm(instance = userProfile);

		context = { };
		context["userProfile"] = userProfile;
		context["userProfileSettingsForm"] = userProfileSettingsForm;

		return render(request, "socialsite/settings.html", context);



	def post(self, request):
		userProfile = request.user.user_profile;
		userProfileSettingsForm = UserProfileSettingsForm(data = request.POST, instance = userProfile);

		if (userProfileSettingsForm.is_valid()):
			newUserProfile = userProfileSettingsForm.save(commit = False);

			if ("profile_image" in request.FILES):
				if (request.FILES["profile_image"]._size > 0.2 * 1024 * 1024):
					context = { };
					context["userProfile"] = userProfile;
					context["userProfileSettingsForm"] = userProfileSettingsForm;
					context["profileImageTooLarge"] = True;
					return render(request, "socialsite/settings.html", context);

				newUserProfile.profile_image = request.FILES["profile_image"];

			newUserProfile.save();

			return HttpResponseRedirect(reverse("social:index"));

		else:
			context = { };
			context["userProfile"] = userProfile;
			context["userProfileSettingsForm"] = userProfileSettingsForm;
			return render(request, "socialsite/settings.html", context);