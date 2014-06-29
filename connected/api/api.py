from django.http import HttpResponse, Http404, HttpResponseRedirect;
from django.contrib.auth.models import User;
from django.contrib.auth.decorators import login_required;
from django.shortcuts import render;
from connected.models import UserProfile, Post, Reply, Following;
from connected.json_writer import writeJson;
from django.utils.html import conditional_escape;
from django.db.models import Q;
from django.contrib.auth import logout;
from django.core.urlresolvers import reverse;



METHOD_GET = "GET";
METHOD_POST = "POST";
TYPE_HTML = "text/html";
TYPE_JSON = "application/json";
TYPE_PLAIN_TYPE = "text/plain";
TYPE_STRING = "String";
TYPE_INTEGER = "Integer";



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
			return HttpResponseRedirect("/");

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
	def getPost(request, postId):
		post = Post.getPostFromId(postId);
		if (post is not None):
			return viewFunction(request, post);
		else:
			raise Http404;

	return getPost;


apiMethods = [ ];

class apiMethodDescription(object):
	def __init__(self, method = "", url = "", parameters = { }, returnContentType = "", description = "", returnValue = ""):
		apiMethods.append({
			"method": method,
			"url": url,
			"parameters": parameters,
			"returnContentType": returnContentType,
			"description": description,
			"returnValue": returnValue
		});



	def __call__(self, originalFunction):
		return lambda *args, **kwargs: originalFunction(*args, **kwargs);



@apiMethodDescription(
	method = METHOD_GET, 
	url = "/", 
	returnContentType = TYPE_HTML, 
	description = "Views this page"
)
def viewApi(request):
	context = { };
	context["apiMethods"] = apiMethods;
	return render(request, "api.html", context);



@apiMethodDescription(
	method = METHOD_GET, 
	url = "/get-post/", 
	parameters = {
		"post_id": {
			"type": TYPE_INTEGER,
			"description": "ID of the post to get"
		}
	},
	returnContentType = TYPE_JSON, 
	description = "Gets the post from post_id and returns it as JSON",
	returnValue = "The post as JSON or 404"
)
@returnHttpJson
@requiresPostFromId
def getPost(request, post):
	return {"post": post.toDictionary(loggedInUser = request.user)};





@apiMethodDescription(
	method = METHOD_GET, 
	url = "/get-posts-by/", 
	parameters = {
		"username": {
			"type": TYPE_STRING,
			"description": "username",
		},
		"length": {
			"type": TYPE_INTEGER,
			"description": "length",
			"default": "10"
		},
		"start_post": {
			"type": TYPE_INTEGER,
			"description": "start post",
			"default": "0"
		}
	},
	returnContentType = TYPE_JSON, 
	description = "Gets posts by USERNAME. Starts from index START_POST (default 0), length of LENGTH (default 10)",
	returnValue = "List of posts in JSON"
)
@returnHttpJson
@requiresUserFromUsername
def getPostsBy(request, user, length = 10, startPost = 0):
	startPost = toInteger(startPost);
	length = toInteger(length);
	endPost = startPost + length;
	return {"posts": [post.toDictionary(loggedInUser = request.user) for post in user.user_profile.getPostsQs()[startPost:endPost]]};




@apiMethodDescription(
	method = METHOD_GET, 
	url = "/get-posts-by-users-followed-by/", 
	parameters = {
		"username": {
			"type": TYPE_STRING,
			"description": "username",
		},
		"length": {
			"type": TYPE_INTEGER,
			"description": "length",
			"default": "10"
		},
		"start_post": {
			"type": TYPE_INTEGER,
			"description": "start post",
			"default": "0"
		}
	},
	returnContentType = TYPE_JSON, 
	description = "Gets posts by the users who are followed by USERNAME. Starts from index START_POST (default 0), length of LENGTH (default 10)",
	returnValue = "List of posts in JSON"
)
@returnHttpJson
@requiresUserFromUsername
def getPostsByUsersFollowedBy(request, user, length = 10, startPost = 0):
	startPost = toInteger(startPost);
	length = toInteger(length);
	endPost = startPost + length;
	return {"posts": [post.toDictionary(loggedInUser = request.user) for post in user.user_profile.getPostsByUsersFollowedQs()[startPost:endPost]]};



@apiMethodDescription(
	method = METHOD_GET, 
	url = "/get-replies-to/", 
	parameters = {
		"post-id": {
			"type": TYPE_INTEGER,
			"description": "ID of the post to get",
		},
	},
	returnContentType = TYPE_JSON, 
	description = "Gets a list of posts that are a reply to post POST_ID",
	returnValue = "List of posts in JSON"
)
@returnHttpJson
@requiresPostFromId
def getRepliesTo(request, post):
	return {"posts": [post.toDictionary(loggedInUser = request.user) for post in post.getReplies()]};



@apiMethodDescription(
	method = METHOD_POST, 
	url = "/post-post/", 
	parameters = {
		"content": {
			"type": TYPE_STRING,
			"description": "Message content",
		},
		"replyToId": {
			"type": TYPE_INTEGER,
			"description": "ID of post to reply to, if applicable, else null"
		}
		
	},
	returnContentType = TYPE_JSON, 
	description = "Posts the new post to the database and maybe adds reply links",
	returnValue = "New post as JSON or 500"
)
@login_required
@returnHttpJson
def postPost(request):
	if (request.method == "POST"):
		post = Post.postPost(request.user, request.POST["content"], toInteger(request.POST["replyToId"]));
		return {"post": post.toDictionary(loggedInUser = request.user)};
	else:
		return 500;



@apiMethodDescription(
	method = METHOD_POST, 
	url = "/delete-post/", 
	parameters = {
		"post_id": {
			"type": TYPE_INTEGER,
			"description": "ID of the post to delete",
		},
	},
	returnContentType = TYPE_JSON, 
	description = "Deletes the post if user is authenticated",
	returnValue = "Ok if post delete, else 403 or 500"
)
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



# @apiMethodDescription(METHOD_GET, "/get-follower-count/USERNAME/", TYPE_JSON, "Deletes a post as long as the logged in user is allowed to delete it. Takes parameter \"id\"")
@apiMethodDescription(
	method = METHOD_GET, 
	url = "/get-follower-count/", 
	parameters = {
		"username": {
			"type": TYPE_STRING,
			"description": "username",
		},
	},
	returnContentType = TYPE_PLAIN_TYPE, 
	description = "Returns the amount of followers this user has",
	returnValue = "Integer follower count"
)
@requiresUserFromUsername
def getFollowerCount(request, user):
	return HttpResponse(user.user_profile.getFollowerCount(), content_type = "text/plain");



@requiresUserFromUsername
@apiMethodDescription(
	method = METHOD_GET, 
	url = "/get-followed-count/", 
	parameters = {
		"username": {
			"type": TYPE_STRING,
			"description": "username",
		},
	},
	returnContentType = TYPE_PLAIN_TYPE, 
	description = "Returns the amount of users this user follows",
	returnValue = "Integer followed count"
)
def getFollowedCount(request, user):
	return HttpResponse(user.user_profile.getFollowedCount(), content_type = "text/plain");



@apiMethodDescription(
	method = METHOD_GET, 
	url = "/get-follower-count/", 
	parameters = {
		"username": {
			"type": TYPE_STRING,
			"description": "username",
		},
	},
	returnContentType = TYPE_JSON, 
	description = "Returns the users who follow this username",
	returnValue = "JSON list of users"
)
@returnHttpJson
@requiresUserFromUsername
def getFollowers(request, user):
	return {"users": [following.follower.user_profile.toDictionary() for following in user.user_profile.getFollowersQs()]};




@apiMethodDescription(
	method = METHOD_GET, 
	url = "/get-follower-count/", 
	parameters = {
		"username": {
			"type": TYPE_STRING,
			"description": "username",
		}
	},
	returnContentType = TYPE_JSON, 
	description = "Returns the users who are followed by this user",
	returnValue = "JSON list of users"
)
@returnHttpJson
@requiresUserFromUsername
def getUsersFollowedBy(request, user):
	return {"users": [following.followed.user_profile.toDictionary() for following in user.user_profile.getFollowedQs()]};



@apiMethodDescription(
	method = METHOD_POST, 
	url = "/toggle_follows/", 
	parameters = {
		"username": {
			"type": TYPE_STRING,
			"description": "username",
		}
	},
	returnContentType = TYPE_PLAIN_TYPE, 
	description = "Toggles whether the logged in user follows the user in the parameter",
	returnValue = "True or false as string to say whether the user now follows this user or not"
)
@login_required
def toggleFollows(request):
	if (request.method == "POST"):
		usernameToFollow = request.POST["followUser"];
		userToFollow = None;

		try:
			userToFollow = User.objects.get(username__iexact = usernameToFollow);
		except (User.DoesNotExist):
			raise Http404;

		follows = request.user.user_profile.toggleFollows(userToFollow);

		return HttpResponse(str(follows), content_type = "text/plain");
	else:
		return HttpResponse("false", content_type = "text/plain");



@apiMethodDescription(
	method = METHOD_POST, 
	url = "/logout/", 
	parameters = { },
	returnContentType = TYPE_PLAIN_TYPE, 
	description = "Logs out the current user",
	returnValue = "Ok if the user was logged out, else redirect to profile page"
)
@login_required
def logoutUser(request):
	if (request.method == "POST"):
		logout(request);
		return HttpResponse("ok", content_type = "text/plain");
	else:
		return HttpResponseRedirect(reverse("connected:profile"));