from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'db/api/clear/$', views.clear_f),
    url(r'db/api/status/$', views.status_f),

    url(r'db/api/user/create/$', views.user_create_f),
    url(r'db/api/user/details/?', views.user_details_f),
    url(r'db/api/user/follow/$', views.user_follow_f),
    url(r'db/api/user/listFollowers/?', views.user_followers_list_f),
    url(r'db/api/user/listFollowing/?', views.user_following_list_f),
    url(r'db/api/user/listPosts/?', views.user_posts_list_f),
    url(r'db/api/user/unfollow/$', views.user_unfollow_f),
    url(r'db/api/user/updateProfile/$', views.user_profile_update_f),

    url(r'db/api/forum/create/$', views.forum_create_f),
    url(r'db/api/forum/details/?', views.forum_details_f),
    url(r'db/api/forum/listPosts/?', views.forum_list_posts_f),
    url(r'db/api/forum/listThreads/?', views.forum_list_threads_f),
    url(r'db/api/forum/listUsers/?', views.forum_list_users_f),

    url(r'db/api/thread/close/$', views.thread_close_f),
    url(r'db/api/thread/create/$', views.thread_create_f),
    url(r'db/api/thread/details/?', views.thread_details_f),
    url(r'db/api/thread/listPosts/?', views.thread_list_posts_f),    # str sort type. Possible vals: ['flat', 'tree', 'parent_tree']
    url(r'db/api/thread/list/?', views.thread_list_f),  # not done
    url(r'db/api/thread/open/$', views.thread_open_f),
    url(r'db/api/thread/remove/$', views.thread_remove_f),
    url(r'db/api/thread/restore/$', views.thread_restore_f),
    url(r'db/api/thread/subscribe/$', views.thread_subscribe_f),
    url(r'db/api/thread/unsubscribe/$', views.thread_unsubscribe_f),
    url(r'db/api/thread/update/$', views.thread_update_f),
    url(r'db/api/thread/vote/$', views.thread_vote_f),

    url(r'db/api/post/create/$', views.post_create_f),             # Error !
    url(r'db/api/post/details/?', views.post_details_f),
    url(r'db/api/post/list/?', views.post_list_f),
    url(r'db/api/post/remove/$', views.post_remove_f),
    url(r'db/api/post/restore/$', views.post_restore_f),
    url(r'db/api/post/update/$', views.post_update_f),
    url(r'db/api/post/vote/$', views.post_vote_f)
]
