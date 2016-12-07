import json

from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from polls.addtional_funcs import *
from polls.helpers import *
import pdb


def index(request):
    return HttpResponse("Here's the text of the Web page.")


@csrf_exempt
def clear_f(request):
    res = clear()

    if res:
        return result("OK")
    else:
        return result_unknown("Couldn't clear data")


def status_f(request):
    response = status()
    return result(response)

@csrf_exempt
def user_create_f(request):
    json_str = request.body.decode('utf-8')
    udata = json.loads(json_str)

    if user_exists(udata.get('email')):
        return result_user_exists("User %s already exists" % udata.get('email'))

    res = user_create(udata)

    if res:
        udata = user_data_short(udata.get('email'))
        return result(udata)
    # else:
    #     return result_user_exists("User %s already exists" % udata.get('email'))


def user_details_f(request):

    email = request.GET.get('user')

    res = user_data(email)
    if res is None:
        return result_not_found("User %s doesn't exist" % email)

    return result(res)

@csrf_exempt
def user_follow_f(request):

    json_str = ((request.body).decode('utf-8'))
    data = json.loads(json_str)

    follower = data.get('follower')
    followee = data.get('followee')

    if not user_exists(follower):
        return result_not_found("User %s doesn't exist" % follower)

    if follower == followee:
        return result_invalid_semantic("User %s cannot follow himself" % follower)

    if not user_exists(followee):
        return result_not_found("User %s doesn't exist" % followee)

    if not user_follows(follower, followee):
        res = user_follow(follower, followee)

        if res:
            udata = user_data(follower)
            return result(udata)
        else:
            return result_unknown("Couldn't follow %s by %s" % (followee, follower))

    else:
        return result_unknown("User %s already follows %s" % (follower, followee))


def user_followers_list_f(request):

    email = request.GET.get('user')
    order = request.GET.get('order', 'desc')
    since_id = request.GET.get('since_id')
    limit= request.GET.get('limit', 0)

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    res = user_list_followers(email, limit=limit, order=order, since_id=since_id, full=True)

    return result(res)


def user_following_list_f(request):
    email = request.GET.get('user')
    order = request.GET.get('order', 'desc')
    since_id = request.GET.get('since_id')
    limit = request.GET.get('limit', 0)

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    res = user_list_following(email, limit=limit, order=order, since_id=since_id, full=True)
    return result(res)


def user_posts_list_f(request):
    email = request.GET.get('user')
    limit = request.GET.get('limit', 0)
    since_date = request.GET.get('since')
    order = request.GET.get('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order: %s" % order)

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    posts = user_posts(email, limit=limit, order=order, since_date=since_date)
    return result(posts)

@csrf_exempt
def user_unfollow_f(request):
    json_str = ((request.body).decode('utf-8'))
    data = json.loads(json_str)

    follower = data.get('follower')
    followee = data.get('followee')

    if not user_exists(follower):
        return result_not_found("User %s doesn't exist" % follower)

    if not user_exists(followee):
        return result_not_found("User %s doesn't exist" % followee)

    if user_follows(follower, followee):
        res = user_unfollow(follower, followee)

        if res:
            udata = user_data(follower)
            return result(udata)
        else:
            return result_unknown("Couldn't unfollow %s by %s" % (followee, follower))
    else:
        return result_unknown("User %s doesn't follow %s" % (follower, followee))


@csrf_exempt
def user_profile_update_f(request):
    json_str = ((request.body).decode('utf-8'))
    data = json.loads(json_str)

    email = data.get('user')
    name = data.get('name')
    about = data.get('about')

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    res = user_update(email, data)

    if res:
        udata = user_data(email)
        return result(udata)
    else:
        return result_unknown("Couldn't update user profile for %s" % (email))

#############################################   Forum  #################################################################

@csrf_exempt
def forum_create_f(request):
    json_str = ((request.body).decode('utf-8'))
    fdata = json.loads(json_str)

    email = fdata.get('user')

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    forum = fdata.get('short_name')
    res = forum_create(fdata)
    fdata = forum_data(forum)

    if fdata:
        return result(fdata)
    else:
        return result_not_found("Couldn't create forum %s" % forum)


def forum_details_f(request):
    forum = request.GET.get('forum')
    related = request.GET.getlist('related')

    if not check_enum(related, ['user']):                            # if not   i changed to if   now it works   check
        return result_invalid_semantic("Wrong value for related")

    fdata = forum_data(forum, related=related)
    if fdata:
        return result(fdata)
    else:
        return result_not_found("Forum %s doesn't exist" % forum)


def forum_list_posts_f(request):                            #Error     to use near '['forumfirstuser1'])' at line 3

    forum = request.GET.getlist('forum')

    if not forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    limit = request.GET.get('limit', 0)
    since_date = request.GET.get('since')
    order = request.GET.get('order', 'desc')
    related = request.GET.getlist('related')

    if not check_enum(related, ['user', 'forum', 'thread']):                       #if not check_enum
        return result_invalid_semantic("Wrong value for related")

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    posts = forum_posts(forum, limit=limit, order=order, since_date=since_date, related=related)
    return result(posts)


def forum_list_threads_f(request):                           #Error     to use near '['forumfirstuser1'])' at line 3
    forum = request.GET.get('forum')

    if not forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    limit = request.GET.get('limit', 2)
    since_date = request.GET.get('since')
    order = request.GET.get('order', 'desc')
    related = request.GET.getlist('related')

    if not check_enum(related, ['user', 'forum']):
        return result_invalid_semantic("Wrong value for related")

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    threads = forum_threads(forum, limit=limit, order=order, since_date=since_date, related=related)
    return result(threads)


def forum_list_users_f(request):                           #Need to check   response []
    forum = request.GET.get('forum')
    if not forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    limit = request.GET.get('limit', 0)
    since_id = request.GET.get('since_id')
    order = request.GET.get('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    users = forum_users(forum, limit=limit, order=order, since_id=since_id, full=True)
    return result(users)


#############################################   Threads   #################################################################

@csrf_exempt
def thread_close_f(request):

    json_str = request.body.decode('utf-8')
    tdata = json.loads(json_str)

    thread = tdata.get('thread')

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    res = thread_close(thread)
    return result({ 'thread': thread })

@csrf_exempt
def thread_create_f(request):
    json_str = request.body.decode('utf-8')
    tdata = json.loads(json_str)

    email = tdata.get('user')

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    forum = tdata.get('forum')

    if not forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)
    thread_id = thread_create(tdata)
    tdata = thread_data(thread_id, counters=False)
    if tdata:
        return result(tdata)
    else:
        return result_not_found("Couldn't create thread %s" % tdata.get('title'))


def thread_details_f(request):

    thread = request.GET.get('thread')
    related = request.GET.getlist('related')

    if not check_enum(related, ['user', 'forum']):
        return result_invalid_semantic("Wrong value for related")

    tdata = thread_data(thread, related=related)
    if tdata:
        return result(tdata)
    else:
        return result_not_found("Thread %s doesn't exist" % thread)


def thread_list_f(request):

    limit = request.GET.get('limit', 0)
    since_date = request.GET.get('since')
    order = request.GET.get('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    forum = request.GET.get('forum')

    if forum is not None:
        if not forum_exists(forum):
            return result_not_found("Forum %s doesn't exist" % forum)

        threads = forum_threads(forum, limit=limit, order=order, since_date=since_date)
        return result(threads)

    email = request.GET.get('user')
    if email is not None:
        if not user_exists(email):
            return result_not_found("User %s doesn't exist" % email)

        threads = user_threads(email, limit=limit, order=order, since_date=since_date)
        return result(threads)

    return result_invalid_semantic("User and forum are not set")


def thread_list_posts_f(request):
    thread = request.GET.get('thread')

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    limit = request.GET.get('limit', 0)
    since_date = request.GET.get('since')
    order = request.GET.get('order', 'desc')
    sort = request.GET.get('sort', 'flat')
    if not check_arg(sort, ['flat', 'tree', 'parent_tree']):
        return result_invalid_semantic("Wrong value for sort")
    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")
    postres = thread_posts(thread, limit=limit, order=order, since_date=since_date, sort=sort)

    return result(postres)
    #return HttpResponse("fuke")



@csrf_exempt
def thread_open_f(request):

    json_str = request.body.decode('utf-8')
    tdata = json.loads(json_str)
    thread = tdata.get('thread')

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    res = thread_open(thread)
    return result({ 'thread': thread })


@csrf_exempt
def thread_remove_f(request):

    json_str = request.body.decode('utf-8')
    tdata = json.loads(json_str)
    thread = tdata.get('thread')

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    res = thread_remove(thread)
    return result({ 'thread': thread })


@csrf_exempt
def thread_restore_f(request):

    json_str = request.body.decode('utf-8')
    tdata = json.loads(json_str)
    thread = tdata.get('thread')

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    res = thread_restore(thread)
    return result({ 'thread': thread })


@csrf_exempt
def thread_subscribe_f(request):

    json_str = request.body.decode('utf-8')
    data = json.loads(json_str)

    email = data.get('user')
    thread = data.get('thread')

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    if not user_subscribed(email, thread):
        res = thread_subscribe(email, thread)

        if res:
            return result({
                'user': email,
                'thread': thread
                })
        else:
            return result_unknown("Couldn't subscribe %s by %s" % (thread, email))
    else:
        return result_unknown("User %s already is subscribed to %s" % (email, thread))


@csrf_exempt
def thread_unsubscribe_f(request):

    json_str = request.body.decode('utf-8')
    data = json.loads(json_str)

    email = data.get('user')
    thread = data.get('thread')

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    if user_subscribed(email, thread):
        res = thread_unsubscribe(email, thread)

        if res:
            return result({
                'user': email,
                'thread': thread
            })
        else:
            return result_unknown("Couldn't unsubscribe %s by %s" % (thread, email))
    else:
        return result_unknown("User %s is not subscribed to %s" % (email, thread))

@csrf_exempt
def thread_update_f(request):

    json_str = request.body.decode('utf-8')
    tdata = json.loads(json_str)
    thread = tdata.get('thread')

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    res = thread_update(thread, tdata)
    tdata = thread_data(thread)
    if tdata:
        return result(tdata)
    else:
        return result_unknown("Couldn't update thread %s" % thread)


@csrf_exempt
def thread_vote_f(request):

    json_str = request.body.decode('utf-8')
    tdata = json.loads(json_str)
    thread = tdata.get('thread')
    vote = int(tdata.get('vote') or 0)

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    if not check_arg(vote, [-1, 1]):
        return result_invalid_semantic("Wrong value for vote")

    res = thread_vote(thread, vote > 0)
    tdata = thread_data(thread)
    if tdata:
        return result(tdata)
    else:
        return result_unknown("Couldn't vote for thread %s" % thread)


#############################################   Post   #################################################################


@csrf_exempt
def post_create_f(request):

    json_str = request.body.decode('utf-8')
    pdata = json.loads(json_str)

    #return HttpResponse(pdata.get('parent'))
    email = pdata.get('user')

    if not user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    forum = pdata.get('forum')

    if not forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    thread = pdata.get('thread')

    if not thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    post_id = post_create(pdata)
    pdata = post_data(post_id, counters=False)

    if pdata:
        return result(pdata)
    else:
        return result_not_found("Couldn't create post")


def post_details_f(request):                           #Error    'NoneType' object is not iterable
    post = request.GET.get('post')
    related = request.GET.getlist('related')


    if not check_enum(related, ['user', 'forum', 'thread']):               #if not  user  ***
        return result_invalid_semantic("Wrong value for related")

    pdata = post_data(post, related=related)
    if pdata:
        return result(pdata)
    else:
        return result_not_found("Post %s doesn't exist" % post)


def post_list_f(request):
    limit = request.GET.get('limit', 0)
    since_date = request.GET.get('since')
    order = request.GET.get('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    forum = request.GET.get('forum')
    if forum is not None:
        if not forum_exists(forum):
            return result_not_found("Forum %s doesn't exist" % forum)

        posts = forum_posts(forum, limit=limit, order=order, since_date=since_date)
        return result(posts)

    thread = request.GET.get('thread')
    if thread is not None:
        if not thread_exists(thread):
            return result_not_found("Thread %s doesn't exist" % thread)

        posts = thread_posts(thread, limit=limit, order=order, since_date=since_date)
        return result(posts)

    return result_invalid_semantic("Thread and forum are not set")

@csrf_exempt
def post_remove_f(request):

    json_str = request.body.decode('utf-8')
    pdata = json.loads(json_str)
    post = pdata.get('post')

    if not post_exists(post):
        return result_not_found("Post %s doesn't exist" % post)

    res = post_remove(post)
    return result({'post': post})


@csrf_exempt
def post_restore_f(request):

    json_str = request.body.decode('utf-8')
    pdata = json.loads(json_str)
    post = pdata.get('post')

    if not post_exists(post):
        return result_not_found("Post %s doesn't exist" % post)

    res = post_restore(post)
    return result({'post': post})


@csrf_exempt                                #Error          massage = NULL    but need   my massage 1
def post_update_f(request):

    json_str = request.body.decode('utf-8')
    pdata = json.loads(json_str)
    post = pdata.get('post')

    if not post_exists(post):
        return result_not_found("Post %s doesn't exist" % post)

    res = post_update(post, pdata)
    pdata = post_data(post)
    if pdata:
        return result(pdata)
    else:
        return result_unknown("Couldn't update post %s" % post)


@csrf_exempt
def post_vote_f(request):

    json_str = request.body.decode('utf-8')
    pdata = json.loads(json_str)
    post = pdata.get('post')
    vote = int(pdata.get('vote') or 0)

    if not post_exists(post):
        return result_not_found("Post %s doesn't exist" % post)

    if not check_arg(vote, [-1, 1]):
        return result_invalid_semantic("Wrong value for vote")

    res = post_vote(post, vote > 0)
    pdata = post_data(post)
    if pdata:
        return result(pdata)
    else:
        return result_unknown("Couldn't vote for post %s" % post)



            # def thread_close(request):
#
#     json_str = request.body.decode('utf-8')
#     tdata = json.loads(json_str)
#
#     thread = tdata.get('thread')IID
#
#     if not model.thread_exists(thread):
#         return result_not_found("Thread %s doesn't exist" % thread)
#
#     res = model.thread_close(thread)
#     return result({ 'thread': thread })