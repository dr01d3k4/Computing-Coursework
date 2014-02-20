from django.http import HttpResponse, Http404;
from django.contrib.auth.models import User;
from django.contrib.auth.decorators import login_required;
from socialsite.models import UserProfile, Post, Reply, Following;
from socialsite.json_writer import writeJson;
from django.utils.html import conditional_escape;


# def jsonToString(jsonObject):
# 	return json.dumps(jsonObject, indent = 4);




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



def getPostFromId(id):
	post = None;
	try:
		post = Post.objects.get(id = id);
	except (Post.DoesNotExist):
		raise Http404;
	return post;



def requiresPostFromId(viewFunction):
	return lambda request, postId: viewFunction(request, getPostFromId(postId));



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
	return {"posts": [post.toDictionary(loggedInUser = request.user) for post in user.user_profile.getPostsQS()[startPost:endPost]]};



@returnHttpJson
@requiresUserFromUsername
def getPostsByUsersFollowedBy(request, user, length = 10, startPost = 0):
	startPost = toInteger(startPost);
	length = toInteger(length);
	endPost = startPost + length;
	followedUsers = user.user_profile.getFollowed();
	postQS = Post.objects.filter(user__in = followedUsers).order_by("-date")[startPost:endPost];
	posts = [post.toDictionary(loggedInUser = request.user) for post in postQS];
	return {"posts": posts};



@returnHttpJson
@requiresPostFromId
def getRepliesTo(request, post):
	return {"posts": [post.toDictionary(loggedInUser = request.user) for post in post.getReplies()]};



@login_required
@returnHttpJson
def postPost(request):
	if (request.method == "POST"):
		content = str(conditional_escape(request.POST["content"]));
		print("Posting post", content);
		replyToId = request.POST["replyToId"];
		replyToPost = None;

		replyToIdInteger = toInteger(replyToId);
		if ((replyToIdInteger is not None) and (replyToIdInteger != -1)):
			replyToPost = getPostFromId(replyToIdInteger);

		post = Post.objects.create(user = request.user, content = content);
		if (replyToPost != None):
			reply = Reply.objects.create(first_post = replyToPost, reply_post = post);

		return {"post": post.toDictionary(loggedInUser = request.user)};
	else:
		return 500;



@login_required
@returnHttpJson
def deletePost(request):
	if (request.method == "POST"):
		post = getPostFromId(request.POST["id"]);

		if (not post.isDeletableBy(request.user)):
			return 403;

		Reply.objects.filter(first_post = post).delete();
		Reply.objects.filter(reply_post = post).delete();
		post.delete();

		return {"response": "ok"};
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
	return {"users": [following.follower.user_profile.toDictionary() for following in user.user_profile.getFollowersQS()]};




@returnHttpJson
@requiresUserFromUsername
def getUsersFollowedBy(request, user):
	return {"users": [following.followed.user_profile.toDictionary() for following in user.user_profile.getFollowedQS()]};