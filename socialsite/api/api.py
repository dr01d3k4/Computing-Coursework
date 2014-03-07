from django.http import HttpResponse, Http404;
from django.contrib.auth.models import User;
from django.contrib.auth.decorators import login_required;
from socialsite.models import UserProfile, Post, Reply, Following;
from socialsite.json_writer import writeJson;
from django.utils.html import conditional_escape;
from django.db.models import Q;



def isInteger(x):
	return isinstance(x, (int, long));



def toInteger(x):
	try:
		val = int(x);
		return val;
	except ValueError:
		return None;



def returnHttpJson(viewFunction):
	def innerFunction(*args, **kwargs):
		jsonObject = viewFunction(*args, **kwargs);

		if (isInteger(jsonObject)):
			return HttpResponseRedirect("/social/");

		jsonString = writeJson(jsonObject);
		return HttpResponse(jsonString, content_type = "application/json");

	return innerFunction;



def getUserFromUsername(username):
	user = None;
	try:
		user = User.objects.get(username__iexact = username);
	except (User.DoesNotExist):
		raise Http404;
	return user;



def requiresUserFromUsername(viewFunction):
	return lambda request, username, *args, **kwargs: viewFunction(request, getUserFromUsername(username), *args, **kwargs);



def requiresPostFromId(viewFunction):
	return lambda request, postId: viewFunction(request, Post.getPostFromId(postId));



@returnHttpJson
@requiresPostFromId
def getPost(request, post):
	return {"post": post.toDictionary(loggedInUser = request.user)};



@returnHttpJson
@requiresUserFromUsername
def getPostsBy(request, user, length = 10, startPost = 0):
	startPost = toInteger(startPost);
	length = toInteger(length);
	endPost = startPost + length;
	return {"posts": [post.toDictionary(loggedInUser = request.user) for post in user.user_profile.getPostsQs()[startPost:endPost]]};



@returnHttpJson
@requiresUserFromUsername
def getPostsByUsersFollowedBy(request, user, length = 10, startPost = 0):
	startPost = toInteger(startPost);
	length = toInteger(length);
	endPost = startPost + length;
	return {"posts": [post.toDictionary(loggedInUser = request.user) for post in user.user_profile.getPostsByUsersFollowedQs()[startPost:endPost]]};



@returnHttpJson
@requiresPostFromId
def getRepliesTo(request, post):
	return {"posts": [post.toDictionary(loggedInUser = request.user) for post in post.getReplies()]};



@login_required
@returnHttpJson
def postPost(request):
	if (request.method == "POST"):
		post = Post.postPost(request.user, request.POST["content"], toInteger(request.POST["replyToId"]));
		return {"post": post.toDictionary(loggedInUser = request.user)};
	else:
		return 500;



@login_required
@returnHttpJson
def deletePost(request):
	if (request.method == "POST"):
		post = Post.getPostFromId(request.POST["id"]);

		deleted = post.deleteBy(request.user);
		if (deleted):
			return {"response": "ok"};
		else:
			return 403;
	else:
		return 500;



@requiresUserFromUsername
def getFollowerCount(request, user):
	return HttpResponse(user.user_profile.getFollowerCount(), content_type = "text/plain");



@requiresUserFromUsername
def getFollowedCount(request, user):
	return HttpResponse(user.user_profile.getFollowedCount(), content_type = "text/plain");



@returnHttpJson
@requiresUserFromUsername
def getFollowers(request, user):
	return {"users": [following.follower.user_profile.toDictionary() for following in user.user_profile.getFollowersQs()]};




@returnHttpJson
@requiresUserFromUsername
def getUsersFollowedBy(request, user):
	return {"users": [following.followed.user_profile.toDictionary() for following in user.user_profile.getFollowedQs()]};