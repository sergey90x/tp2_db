from django.db import connection
from polls.helpers import *
import pdb
import datetime


def clear():

    cursor = connection.cursor()
    cursor.execute('SET FOREIGN_KEY_CHECKS=0')
    for entity in ['follower', 'subscription', 'post', 'thread', 'forum', 'user']:
        cursor.execute('TRUNCATE %ss' % entity.capitalize())

    cursor.execute('SET FOREIGN_KEY_CHECKS=1')
    return True


def status():

    cursor = connection.cursor()
    res = {}

    for entity in ['user', 'thread', 'forum', 'post']:
        cursor.execute('SELECT COUNT(*) FROM %ss' % entity.capitalize())
        data = cursor.fetchone()
        res[entity] = data[0]

    return res


def user_create(fields):

    cursor = connection.cursor()
    cursor.execute("""INSERT INTO
                Users (username, about, name, email, isAnonymous)
                VALUES (%s, %s, %s, %s, %s)""",
                (
                    fields.get('username'),
                    fields.get('about'),
                    fields.get('name'),
                    fields.get('email'),
                    fields.get('isAnonymous', False)
                    ))

    return cursor.rowcount > 0


def user_data(email, follow_data=True, subscriptions=True):

    cursor = connection.cursor()
    cursor.execute("""SELECT id, username, about, name, email, isAnonymous
                    FROM Users
                    WHERE email = %s""",
                   (email,))

    if cursor.rowcount == 0:
        return None

    udata = cursor.fetchone()
    res = model_dict(udata, cursor.description)

    if follow_data:
        res['followers'] = user_list_followers(email)
        res['following'] = user_list_following(email)

    if subscriptions:
        cursor.execute("""SELECT thread
                        FROM Subscriptions
                        WHERE user = %s """,
                       (email,))
        threads = cursor.fetchall()
        res['subscriptions'] = [int(t[0]) for t in threads]

    return res


def user_data_short(email):
    return user_data(email, follow_data=False, subscriptions=False)


def user_exists(email):

    cursor = connection.cursor()
    cursor.execute("""SELECT 1
                    FROM Users
                    WHERE email = %s""",
                    (email, ))

    return cursor.rowcount > 0


def user_list_followers(email, limit=0, order='desc', since_id=None, full=False):

    q = """SELECT f.follower
            FROM Followers f
            INNER JOIN Users u ON u.email = f.follower
            WHERE f.followee = %s """
    qargs = [email]

    if since_id is not None:
        q += " AND u.id >= %s "
        qargs.append(since_id)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY u.name " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor = connection.cursor()
    cursor.execute(q, tuple(qargs))

    emails = [f[0] for f in cursor.fetchall()]

    if not full:
        return emails

    res = []

    print("\n\n\n" + str(res) + "\n\n\n")
    if len(emails):
        users = users_data(emails)
        print("\n\n\n" + str(users) + "\n\n\n")
        for email in emails:
            res.append(users.get(email))
            print("\n\n\n" + str(res) + "\n\n\n")

    return res


def user_list_following(email, limit=0, order='desc', since_id=None, full=False):
    q = """SELECT f.followee
            FROM Followers f
            INNER JOIN Users u ON u.email = f.follower
            WHERE f.follower = %s """
    qargs = [email]

    if since_id is not None:
        q += " AND u.id >= %s "
        qargs.append(since_id)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY u.name " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor = connection.cursor()
    cursor.execute(q, tuple(qargs))

    emails = [f[0] for f in cursor.fetchall()]

    if not full:
        return emails

    res = []
    if len(emails):
        users = users_data(emails)
        for email in emails:
            res.append(users.get(email))

    return res


def users_data(emails, follow_data=True, subscriptions=True):
    cursor = connection.cursor()
    cursor.execute("""SELECT id, username, about, name, email, isAnonymous
                    FROM Users
                    WHERE email IN (%s)""" % sql_in(emails))

    res = {}
    udata = cursor.fetchone()

    print("\n\n1\n" + str(udata) + "\n udata = cursor.fetchone \n\n\n")

    while udata is not None:
        ures = model_dict(udata, cursor.description)
        print("\n\n1.5\n" + str(ures) + "\n res[ures['email']] = ures \n\n\n")
        res[ures['email']] = ures
        print("\n\n2\n" + str(res) + "\n res[ures['email']] = ures \n\n\n")
        udata = cursor.fetchone()
        print("\n\n3\n" + str(udata) + "\n udata = cursor.fetchone() \n\n\n")

    print("\n\n4\n" + str(len(res)) + "\n len(res) \n\n\n")
    if not len(res):
        return res

    if follow_data:
        following = {}
        cursor = connection.cursor()
        cursor.execute("""SELECT follower, GROUP_CONCAT(followee, ',')
                        FROM Followers
                        WHERE follower IN (%s)
                        GROUP BY follower""" % sql_in(emails))

        follow_row = cursor.fetchone()
        print("\n\n5\n" + str(follow_row) + "\n follow_row = cursor.fetchone() \n\n\n")
        while follow_row is not None:
            follower = follow_row[0]
            followees = follow_row[1]
            print("\n\n5.5\n" + str(follower) + "  " + str(followees) + "\n follower and followees \n\n\n")
            str1 = followees
            num = str1.find(',')
            followees = str1[0:num]
            following[follower] = [followees]
            # following[follower] = filter(None, followees.split(','))
            print("\n\n6\n" + str(following) + "\n following[follower] = filter(None, followees.split(',')) \n\n\n")
            follow_row = cursor.fetchone()
            print("\n\n7\n" + str(follow_row) + "\n follow_row = cursor.fetchone() \n\n\n")

        followers = {}
        cursor.execute("""SELECT followee, GROUP_CONCAT(follower, ',')
                        FROM Followers
                        WHERE followee IN (%s)
                        GROUP BY followee""" % sql_in(emails))


        follow_row = cursor.fetchone()
        print("\n\n8\n" + str(follow_row) + "\n follow_row = cursor.fetchone() \n\n\n")
        while follow_row is not None:
            followee = follow_row[0]
            ufollowers = follow_row[1]
            str1 = ufollowers
            num = str1.find(',')
            ufollowers = str1[0:num]
            followers[followee] = [ufollowers]
            # followers[followee] = filter(None, ufollowers.split(','))
            print("\n\n9\n" + str(followers) + "\n followers[follower] = filter(None, followers.split(',')) \n\n\n")
            follow_row = cursor.fetchone()

    if subscriptions:
        threads = {}
        cursor.execute("""SELECT user, GROUP_CONCAT(thread, ',')
                        FROM Subscriptions
                        WHERE user IN (%s)
                        GROUP BY user""" % sql_in(emails))

        thread_row = cursor.fetchone()
        print("\n\n10\n" + str(thread_row) + "\n  thread_row = cursor.fetchone() \n\n\n")
        while thread_row is not None:
            user = thread_row[0]
            uthreads = thread_row[1]
            print("\n\n10.5\n" + str(user) + "  " + str(uthreads) + str(len(uthreads)) + "\n user and uthreads \n\n\n")
            num = len(uthreads)
            nthreads = []
            if uthreads[num-1] == ',':
                str1 = uthreads[0:num-1]
            else:
                str1 = uthreads
            str2 = str1.split(',')
            for el in str2:
                if(el == ''):
                    pp = 0
                    #nthreads.append(el)
                else:
                    nthreads.append(int(el))
            print("\n\n11\n" + str(nthreads) + "\n\n\n\n")
            # threads[user] = map(int, filter(None, uthreads.split(',')))
            threads[user] = nthreads
            print("\n\n11\n" + str(threads) + "\n   threads[user] = map(int, filter(None, uthreads.split(','))) \n\n\n")
            thread_row = cursor.fetchone()

    if follow_data or subscriptions:
        for key in res:
            if follow_data:
                res[key]['followers'] = followers.get(key, [])
                res[key]['following'] = following.get(key, [])
                print("\n\n12\n" + str(thread_row) + "\n  thread_row = cursor.fetchone() \n\n\n")
            if subscriptions:
                res[key]['subscriptions'] = threads.get(key, [])
                print("\n\n13\n" + str(res) + "\n  res[key]['subscriptions'] = threads.get(key, [])\n\n\n")
    return res


def split_num(values):
    a = values.split(',')
    for tmp in a:
        if(len(tmp)>1):
            if(tmp == ' '):
                vv = tmp[1]
        else:
            vv = tmp[0]

def user_follow(follower, followee):

    cursor = connection.cursor()
    cursor.execute("""INSERT INTO
                Followers (followee, follower)
                VALUES (%s, %s)""",
                (
                    followee,
                    follower
                    ))

    return cursor.rowcount > 0

def user_unfollow(follower, followee):

    cursor = connection.cursor()
    cursor.execute("""DELETE
                FROM Followers
                WHERE followee = %s AND follower = %s""",
                (
                    followee,
                    follower
                    ))

    return cursor.rowcount > 0

def user_follows(follower, followee):

    cursor = connection.cursor()
    cursor.execute(""" SELECT 1
                    FROM Followers
                    WHERE follower = %s AND followee = %s """,
                    (follower, followee))

    return cursor.rowcount > 0

def forum_create(fdata):

    cursor = connection.cursor()
    cursor.execute("""INSERT INTO
                Forums (name, short_name, user)
                VALUES (%s, %s, %s)""",
                (
                    fdata.get('name'),
                    fdata.get('short_name'),
                    fdata.get('user')
                    ))

    return cursor.rowcount > 0

def forum_data(forum, related=[]):

    cursor = connection.cursor()
    cursor.execute("""SELECT id, name, short_name, user
                    FROM Forums
                    WHERE short_name = %s""",
                    (forum, ))

    if cursor.rowcount == 0:
        return None

    fdata = cursor.fetchone()
    res = model_dict(fdata, cursor.description)

    if 'user' in related:
        res['user'] = user_data(res['user'])

    return res


def forums_data(forums):

    cursor = connection.cursor()
    cursor.execute("""SELECT id, name, short_name, user
                    FROM Forums
                    WHERE short_name IN (%s)"""
                    % sql_in(forums))

    res = {}
    fdata = cursor.fetchone()

    while fdata is not None:
        fres = model_dict(fdata, cursor.description)
        res[fres['short_name']] = fres

        fdata = cursor.fetchone()

    return res

def forum_exists(forum):

    cursor = connection.cursor()
    cursor.execute("""SELECT 1
                    FROM Forums
                    WHERE short_name = %s""",
                   forum)

    return cursor.rowcount > 0


def forum_posts(forum, limit=0, order='desc', since_date=None, related=[]):
    return posts_list({ 'forum' : forum }, limit, order, since_date, related)


def thread_create(fields):

    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO
        Threads (title, slug, message, date, isClosed, isDeleted, forum, user)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                fields.get('title'),
                fields.get('slug'),
                fields.get('message'),
                fields.get('date'),
                fields.get('isClosed', False),
                fields.get('isDeleted', False),
                fields.get('forum'),
                fields.get('user')
                ))

    return cursor.lastrowid


def forum_threads(forum, limit=0, order='desc', since_date=None, related=[]):
    return threads_list({ 'forum' : forum }, limit, order, since_date, related)


def forum_users(forum, limit=0, order='desc', since_id=None, full=False):

    cursor = connection.cursor()
    q = """SELECT DISTINCT p.user
            FROM Posts p """

    # if since_id is not None:
    q += """ INNER JOIN Users u ON u.email = p.user """

    q += """ WHERE p.forum = %s """
    qargs = [forum]

    if since_id is not None:
        q += " AND u.id >= %s "
        qargs.append(since_id)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY u.name " + order           #user_name    i changed to   user

    if limit:
        q += " LIMIT " + str(limit)

    print("\n\n\n\n" + q + "\n q before\n\n\n")

    cursor.execute(q, tuple(qargs))

    emails = [f[0] for f in cursor.fetchall()]
    print("\npuff\n\n\n" + str(cursor.fetchall()) + "\n q before\n\n\n")
    print("\npuff\n\n\n" + str(emails) + "\n q before\n\n\n")

    if not full:
        return emails

    res = []
    if emails:
        users = users_data(emails)
        for email in emails:
            res.append(users.get(email))

    return res


def thread_posts(thread, limit=0, order='desc', since_date=None, related=[], sort='flat'):
    print("step 5")
    return posts_list({ 'thread' : thread }, limit, order, since_date, related, sort)

def thread_open(thread):
    return thread_set_closed(thread, False)

def thread_remove(thread):
    return thread_set_deleted(thread, True)

def thread_restore(thread):
    return thread_set_deleted(thread, False)


def user_subscribed(email, thread):

    cursor = connection.cursor()
    cursor.execute(""" SELECT 1
                    FROM Subscriptions
                    WHERE user = %s AND thread = %s """,
                    (email, thread))

    return cursor.rowcount > 0


def thread_subscribe(user, thread):

    cursor = connection.cursor()
    cursor.execute("""INSERT INTO
                Subscriptions (thread, user)
                VALUES (%s, %s)""",
                (
                    thread,
                    user
                    ))

    return cursor.rowcount > 0

def thread_update(thread, fields):

    cursor = connection.cursor()
    cursor.execute("""UPDATE Threads
                    SET message = %s,
                    slug = %s
                    WHERE id = %s """,
                    (
                        fields.get('message'),
                        fields.get('slug'),
                        thread,
                        ))

    return True


def thread_unsubscribe(user, thread):

    cursor = connection.cursor()
    cursor.execute("""DELETE
                FROM Subscriptions
                WHERE thread = %s AND user = %s""",
                (
                    thread,
                    user
                    ))

    return cursor.rowcount > 0


def thread_vote(thread, like=True):
    field = 'likes'
    if not like:
        field = 'dis' + field

    cursor = connection.cursor()
    cursor.execute("""UPDATE Threads
                    SET %s = %s + 1
                    WHERE id = %s """ % (field, field, '%s'),
                    (
                        thread,
                        ))

    return True

def thread_exists(thread):

    cursor = connection.cursor()
    cursor.execute("""SELECT 1
                    FROM Threads
                    WHERE id = %s""",
                    (thread, ))

    return cursor.rowcount > 0


def thread_data(thread, related=[], counters=True):
    cursor = connection.cursor()
    cursor.execute("""SELECT id, title, slug, message, date, likes, dislikes, (likes - dislikes)
                      AS points, isClosed, isDeleted, posts, forum, user
                    FROM Threads
                    WHERE id = %s""" % thread)

    if cursor.rowcount == 0:
        return None

    tdata = cursor.fetchone()
    remove = []
    if not counters:
        remove = ['likes', 'dislikes', 'points']
    res = model_dict(tdata, cursor.description, remove=remove)

    if 'user' in related:
        res['user'] = user_data(res['user'])

    if 'forum' in related:
        res['forum'] = forum_data(res['forum'])

    return res


def sql_in(values):
    return ','.join(map(lambda x: '"' + str(x) + '"', values))


def threads_data(threads):
    cursor = connection.cursor()

    cursor.execute("""SELECT id, title, slug, message, date, likes, dislikes, (likes - dislikes) AS points, isClosed, isDeleted, posts, forum, user
                    FROM Threads
                    WHERE id IN (%s)"""
                    % sql_in(threads))

    res = {}
    tdata = cursor.fetchone()

    while tdata is not None:
        tres = model_dict(tdata, cursor.description)
        res[tres['id']] = tres

        tdata = cursor.fetchone()

    return res


def threads_list(search_fields, limit=0, order='desc', since_date=None, related=[]):
    print("\n1\n\n\n" + str(related) + "\n\nbefor q\n\n")
    cursor = connection.cursor()
    q = """SELECT *, (likes - dislikes) AS points
            FROM Threads
            WHERE 1=1 """
    qargs = []

    for k in search_fields:
        q += "AND %s = " % k
        q += " %s "
        qargs.append(search_fields.get(k))

    if since_date is not None:
        q += " AND `date` >= %s "
        qargs.append(since_date)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY `date` " + order

    if limit:
        q += " LIMIT " + str(limit)


    print("\n1\n\n\n" + q + "\n\nbefor q\n\n")
    print("\n2\n\n\n" + str(qargs) + "\n\nbefor qargs\n\n")
    cursor.execute(q, tuple(qargs))

    res = []
    row = cursor.fetchone()

    forums = []
    users = []

    while row is not None:
        rowres = model_dict(row, cursor.description)

        if 'forum' in related:
            forums.append(rowres['forum'])
        if 'user' in related:
            users.append(rowres['user'])
        res.append(rowres)
        print("\n3\n\n\n" + str(res) + "\n\nres.append(rowres)\n\n")
        row = cursor.fetchone()
        print("\n4\n\n\n" + str(row) + "\n\n row = cursor.fetchone()\n\n")

    if 'forum' in related and forums:
        forums = forums_data(forums)
        print("\n5\n\n\n" + str(forums) + "\n\n forums = forums_data(forums)\n\n")
        for keyn, val in enumerate(res):
            res[keyn]['forum'] = forums.get(val['forum'])

    if 'user' in related and users:
        users = users_data(users)
        print("\n6\n\n\n" + str(users) + "\n\n users  users_data\n\n")
        for keyn, val in enumerate(res):
            res[keyn]['user'] = users.get(val['user'])

    return res


def thread_close(thread):
    return thread_set_closed(thread, True)


def thread_set_closed(thread, closed= True):

    cursor = connection.cursor()
    cursor.execute("""UPDATE Threads
                    SET isClosed = %s
                    WHERE id = %s """,
                    (closed, thread,))

    return True


def thread_set_deleted(thread, deleted=True):

    cursor = connection.cursor()

    cursor.execute("""UPDATE Threads
                    SET isDeleted = %s
                    WHERE id = %s """,
                    (deleted, thread,))

    cursor.execute("""UPDATE Posts
                    SET isDeleted = %s
                    WHERE thread = %s""",
                    (-int(deleted), thread, ))
    cursor.execute("""UPDATE Threads
                    SET posts = (SELECT COUNT(*) FROM Posts WHERE thread = %s AND isDeleted = 0)
                    WHERE id = %s """,
                    (thread, thread,))

    return True


def user_update(email, data):

    cursor = connection.cursor()
    cursor.execute("""UPDATE Users
                    SET about = %s, name = %s
                    WHERE email = %s """,
                (
                    data.get('about'),
                    data.get('name'),
                    email
                    ))

    ##########################  user_name  -  unknown column ##########################
    # cursor.execute("""UPDATE Posts
    #                 SET user = %s
    #                 WHERE user = %s """,
    #             (
    #                 data.get('name'),
    #                 email
    #                 ))

    return True


def user_threads(email, limit=0, order='desc', since_date=None, related=[]):
    return threads_list({ 'user' : email }, limit, order, since_date, related)


def user_posts(email, limit=0, order='desc', since_date=None, related=[]):
    return posts_list({ 'user' : email }, limit, order, since_date, related)


def post_create(fields):
    sorter = sorter_date = str(fields.get('thread'))

    if fields.get('parent') is not None:
        parent_data = post_data(fields.get('parent'))
        sorter = parent_data.get('sorter')
        sorter_date = parent_data.get('sorter_date')

    cursor = connection.cursor()                                  # I deleted user_name    why it was ?
    cursor.execute("""INSERT INTO
                Posts (message, date, isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent, user, thread, forum)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s)""",
                (
                    fields.get('message'),
                    fields.get('date'),
                    fields.get('isApproved', False),
                    fields.get('isHighlighted', False),
                    fields.get('isEdited', False),
                    fields.get('isSpam', False),
                    fields.get('isDeleted', False),
                    fields.get('parent', None),
                    fields.get('user'),
                    #fields.get('user'), for user_name
                    fields.get('thread'),
                    fields.get('forum')
                    ))

    id = cursor.lastrowid

    sorter_date_part = fields.get('date').replace('-', '').replace(':', '').replace(' ', '')[2:]
    cursor.execute("""UPDATE Posts
                        SET sorter = %s,
                        sorter_date = %s
                        WHERE id = %s""",
                        (
                            str(sorter) + "." + str(id),
                            str(sorter_date) + "-" + sorter_date_part + "-" + str(id),
                            id,
                        ))

    cursor.execute("""UPDATE Threads
                        SET posts = posts + 1
                        WHERE id = %s""",
                        (
                            fields.get('thread'),
                        ))

    return id


def post_data(post, related=[], counters=True):

    cursor = connection.cursor()
    cursor.execute("""SELECT id, message, date, likes, dislikes, (likes - dislikes)
                    AS points, isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent, user, thread, forum, sorter, sorter_date
                    FROM Posts
                    WHERE id = %s""",
                    (post,))

    if cursor.rowcount == 0:
        return None

    pdata = cursor.fetchone()
    remove = []
    if not counters:
        remove = ['likes', 'dislikes', 'points']
    res = model_dict(pdata, cursor.description, remove=remove)

    if 'user' in related:
        res['user'] = user_data(res['user'])

    if 'forum' in related:
        res['forum'] = forum_data(res['forum'])

    if 'thread' in related:
        res['thread'] = thread_data(res['thread'])

    return res


def post_exists(post):

    cursor = connection.cursor()
    cursor.execute("""SELECT 1
                    FROM Posts
                    WHERE id = %s""",
                    (post, ))

    return cursor.rowcount > 0


def post_remove(post):
    return post_set_deleted(post, True)

def post_restore(post):
    return post_set_deleted(post, False)


def post_set_deleted(post, deleted=True):

    cursor = connection.cursor()
    cursor.execute("""UPDATE Posts
                    SET isDeleted = %s
                    WHERE id = %s """,
                    (deleted, post,))

    pdata = post_data(post)

    sign = '-'
    if not deleted:
        sign = '+'

    cursor.execute("""UPDATE Threads
                        SET posts = posts %s 1
                        WHERE id = %s""" % (sign, '%s'),
                        (
                            pdata.get('thread'),
                        ))

    return True


def post_update(post, fields):

    cursor = connection.cursor()
    cursor.execute("""UPDATE Posts
                    SET message = %s
                    WHERE id = %s """,
                    (
                        fields.get('message'),
                        post,
                        ))

    return True




def posts_list(search_fields, limit=0, order='desc', since_date=None, related=[], sort='flat'):
    print("step 6")
    cursor = connection.cursor()

    print("\n1\n\n" + str(related) + "\n before cursor.execute(q, tuple(qargs))\n\n ")
    if sort == 'tree':
        return posts_list_tree(search_fields, limit, order, since_date, related)
    if sort == 'parent_tree':
        return posts_list_parent_tree(search_fields, limit, order, since_date, related)

    q = """SELECT *, (likes - dislikes) AS points
            FROM Posts
            WHERE 1=1 """
    qargs = []

    for k in search_fields:
        q += "AND %s = " % k
        q += " %s "
        qargs.append(search_fields.get(k))

    if since_date is not None:
        q += " AND `date` >= %s "
        qargs.append(since_date)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY `date` " + order + ", id"

    if limit:
        q += " LIMIT " + str(limit)

    print("\n1\n\n" + q + "\n before cursor.execute(q, tuple(qargs))\n\n ")
    print("\n1\n\n" + str(qargs) + "\n before cursor.execute(q, tuple(qargs))\n\n ")
    cursor.execute(q, tuple(qargs))

    res = []
    row = cursor.fetchone()
    print("\n2\n\n" + str(row) + "\n     row = cursor.fetchone()\n\n ")

    forums = []
    threads = []
    users = []

    ti = ui = fi = 0

    while row is not None:
        rowres = model_dict(row, cursor.description)
        print("\n3\n\n" + str(rowres) + "\n     row = cursor.fetchone()\n\n ")

        if 'forum' in related:
            forums.append(rowres['forum'])
            print("\n4\n\n" + str(forums) + "\n     forums.append(rowres['forum'])\n\n ")
        if 'thread' in related:
            threads.append(rowres['thread'])
            print("\n5\n\n" + str(threads) + "\n     threads.append(rowres['thread'])\n\n ")
        if 'user' in related:
            users.append(rowres['user'])
            print("\n6\n\n" + str(users) + "\n     users.append(rowres['user'])\n\n ")
        res.append(rowres)
        row = cursor.fetchone()
        #row = None   # Dangerous!!!

    if 'forum' in related and forums:
        print('forums')
        forums = forums_data(forums)
        print("\n7\n\n" + str(forums) + "\n     forums = forums_data(forums)\n\n ")
        for keyn, val in enumerate(res):
            res[keyn]['forum'] = forums.get(val['forum'])
            print("\n8\n\n" + str(res) + "\n      res[keyn]['forum'] = forums.get(val['forum'])\n\n ")

    if 'thread' in related and threads:
        print('threads')
        threads = threads_data(threads)
        print("\n9\n\n" + str(threads) + "\n      threads = threads_data(threads)\n\n ")
        for keyn, val in enumerate(res):
            res[keyn]['thread'] = threads.get(val['thread'])
            print("\n10\n\n" + str(res) + "\n     res[keyn]['thread'] = threads.get(val['thread'])\n\n ")

    if 'user' in related and users:
        print("users")
        users = users_data(users)
        print("\n11\n\n" + str(users) + "\n     forums = forums_data(forums)\n\n ")
        for keyn, val in enumerate(res):
            res[keyn]['user'] = users.get(val['user'])
            print("\n12\n\n" + str(res) + "\n     res[keyn]['user'] = users.get(val['user'])\n\n ")

    return res


def posts_list_tree(search_fields, limit=0, order='desc', since_date=None, related=[]):
    res = posts_list_parent_tree(search_fields, limit, order, since_date, related, True)

    return res


def posts_list_parent_tree(search_fields, limit=0, order='desc', since_date=None, related=[], limit_total=False):
    cursor = connection.cursor()

    q = """SELECT p.*, (p.likes - p.dislikes) AS points
            FROM Posts p
            WHERE 1=1 """
    qargs = []

    for k in search_fields:
        q += "AND p.%s = " % k
        q += " %s "
        qargs.append(search_fields.get(k))

    if since_date is not None:
        q += " AND p.`date` >= %s "
        qargs.append(since_date)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " AND (LENGTH(sorter) - LENGTH(REPLACE(sorter, '.', ''))) = 1"
    q += " ORDER BY sorter_date " + order

    if limit:
        q += " LIMIT " + str(limit)

    print("\np1\n\n" + str(q) + "\n     q\n\n ")
    cursor.execute(q, tuple(qargs))

    res = []
    ids = []
    row = cursor.fetchone()
    print("\np2\n\n" + str(row) + "\n         row = cursor.fetchone()\n\n ")

    while row is not None:
        rowres = model_dict(row, cursor.description)
        print("\np3\n\n" + str(rowres) + "\n          rowres = model_dict(row, cursor.description)\n\n ")
        ids.append(rowres['sorter'])
        print("\np4\n\n" + str(ids) + "\n     q\n\n ")
        res.append(rowres)
        print("\np5\n\n" + str(res) + "\n     q\n\n ")
        row = cursor.fetchone()
        print("\np6\n\n" + str(row) + "\n     q\n\n ")

    if not ids:
        return res

    ids = ' OR '.join(["sorter LIKE '" + id  + ".%'" for id in ids])
    cursor.execute("""SELECT *, (likes - dislikes) AS points
                FROM Posts
                WHERE 0=1 OR %s""" % ids)

    childs = {}

    row = cursor.fetchone()
    print("\np7\n\n" + str(row) + "\n     q\n\n ")

    while row is not None:
        rowres = model_dict(row, cursor.description)
        print("\np8\n\n" + str(rowres) + "\n     q\n\n ")
        row = cursor.fetchone()
        if rowres['parent'] in childs:
        # if childs.has_key(rowres['parent']):
        # if childs[(rowres('parent'))] is not None:
            childs.get(rowres['parent']).append(rowres)
        else:
            childs[rowres['parent']] = [rowres]

    def find_childs(cur):
        # if childs.has_key(cur.get('id')):
        # if childs[(cur.get('id'))] is not None:
        if cur.get('id') in childs:
            for keyn, val in enumerate(childs[cur.get('id')]):
                child_childs = find_childs(val)
                if child_childs:
                    val['childs'] = child_childs
            return childs[cur.get('id')]
        return []

    for keyn, val in enumerate(res):
        cur_childs = find_childs(val)

        if cur_childs:
            val['childs'] = cur_childs

    def _flatten_tree(tree, arr, order, reverse_childs=False):
        get_datetime = lambda obj: datetime.datetime.strptime(obj.get('date'), '%Y-%m-%d %H:%M:%S')
        order = True if order in['desc', True] else False
        for node in tree:
            arr.append(node)
            _childs = node.get('childs', [])
            _childs.sort(key=get_datetime, reverse=reverse_childs)
            _flatten_tree(_childs, arr, order, reverse_childs)
            # if node.has_key('childs'):
            # if node[('childs')] is not None:
            if 'childs' in node:
                del node['childs']
        return arr

    res = _flatten_tree(res, [], order, False)

    if limit_total and limit:
        return res[:int(limit)]

    print("\npend\n\n" + str(res) + "\n     end of \n\n ")

    return res


def post_vote(post, like=True):

    cursor = connection.cursor()
    field = 'likes'
    if not like:
        field = 'dis' + field

    cursor.execute("""UPDATE Posts
                    SET %s = %s + 1
                    WHERE id = %s """ % (field, field, '%s'),
                    (
                        post,
                        ))

    return True