from django.shortcuts import render;
from django.views.generic.base import View;
from django.template import RequestContext;
from django.http import HttpResponseRedirect, HttpResponse, Http404;
from django.contrib.auth import authenticate, login, logout;
from django.utils.decorators import method_decorator;
from django.contrib.auth.decorators import login_required;
from django.contrib.auth.models import User;
from django.core.urlresolvers import reverse;
from django.db.models import Q;

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
				context["userAlreadyExists"] = (currentUser is not None);
				context["passwordsDontMatch"] = not passwordsMatch;
				context["autoOpenTo"] = "register";

				return render(request, "socialsite/index.html", context);

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

		usersRepliedToQs = viewingProfile.getUsersRepliedToQs();
		usersRepliedTo = [ ];

		for otherUser in usersRepliedToQs:
			otherUser.count = viewingProfile.getCountOfRepliesToPostsByUser(otherUser)
			usersRepliedTo.append(otherUser);

		usersRepliedTo.sort(key = lambda user: -user.count);

		context["usersRepliedTo"] = usersRepliedTo;

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
		usernameToFollow = request.POST["followUser"];
		userToFollow = None;

		try:
			userToFollow = User.objects.get(username__iexact = usernameToFollow);
		except (User.DoesNotExist):
			raise Http404;

		follows = request.user.user_profile.toggleFollows(userToFollow);

		return HttpResponse(str(follows), content_type = "text/plain");



class Search(View):
	def get(self, request, searchTerm = ""):
		userProfile = request.user.user_profile;

		userProfiles = UserProfile.objects.filter(Q(user__username__icontains = searchTerm) | Q(first_name__icontains = searchTerm) | Q(last_name__icontains = searchTerm) | Q(middle_name__icontains = searchTerm));
		context = { };
		context["userProfile"] = userProfile;
		context["userProfiles"] = userProfiles;
		context["searchTerm"] = searchTerm;

		return render(request, "socialsite/search.html", context);



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
		userProfileSettingsForm = UserProfileSettingsForm(request.POST, request.FILES, instance = userProfile);

		if (userProfileSettingsForm.is_valid()):
			userProfileSettingsForm.save();
			return HttpResponseRedirect(reverse("social:index"));

		else:
			context = { };
			context["userProfile"] = userProfile;
			context["userProfileSettingsForm"] = userProfileSettingsForm;
			return render(request, "socialsite/settings.html", context);