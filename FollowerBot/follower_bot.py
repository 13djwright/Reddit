#!/usr/bin/python
import praw, time, sys, sqlite3, re, smtplib

#------Bot Configuration------#
BOTNAME     = 'FollowerBot'
USERAGENT   = 'send comments and submission info via email from subscribed users. Author: /u/13djwright'
USERS_TO_FOLLOW = []
MESSAGE     = ""
CHANGES     = 0
server      = smtplib.SMTP("smtp.gmail.com",587)
server.starttls()
#------SQL Database------#
print('\nSetting up database...')
sql = sqlite3.connect('/home/devin/code/side_projects/reddit/FollowerBot/posts.db')
cur = sql.cursor()
cur.execute('create table if not exists oldposts(id TEXT)')

sql.commit()
print('DONE')

#------Reddit Login------#
print('Logging in to Reddit...')
r = praw.Reddit(user_agent=USERAGENT)
r.login("13djwright","tiger0082")
print('DONE')
for row in cur.execute('select name from users where name is not "13djwright"'):
    USERS_TO_FOLLOW.append(str(row[0]))

EMAIL    = str(cur.execute('select email from users where name is "13djwright"').fetchone()[0])
PASSWORD = str(cur.execute('select password from users where name is "13djwright"').fetchone()[0])

server.login(EMAIL,PASSWORD)

#---------HELPER FUNCTIONS---------#

#------This function should be able to handle submissions and comments, checking whether it has been seen, if not adding it to the database table------#
def is_new_post(post_id, post_author):
    cur.execute('select * from oldposts where id=?',(post_id,))
    if not cur.fetchone() and post_author.lower() != BOTNAME.lower():
        cur.execute('insert into oldposts values(?)', (post_id,))
        sql.commit()
        return True
    else:
        return False

#------This function is used to process new submissions. Pass in a block of code for posts------#
def process_submissions(posts, is_comment, user_name):
    global MESSAGE
    global CHANGES
    if is_comment:
        MESSAGE += "Recent comments for " + user_name + "\n\n"
    else:
        MESSAGE += "Recent submissions for " + user_name + "\n\n"
    for p in posts:
        pID = p.id
        try:
            pAuth = p.author.name
        except:
            pAuth = '[DELETED]'
        if is_new_post(pID, pAuth):
            #This is a new post we havent seen, we can now process it.
            #by this point, it has already been added to the database
            if not is_comment:  #submission
                MESSAGE += p.subreddit.display_name + " | " + p.title + " | " + p.short_link + "\n\n"
            else:   #comment
               MESSAGE += p.submission.subreddit.display_name + " | " + p.submission.title + " | " + p.permalink + "\n\n" + p.body + "\n\n"
            CHANGES += 1

def main():
    for u in USERS_TO_FOLLOW:
       print("Getting submissions from " + u)
       user = r.get_redditor(u)
       sub_posts = user.get_submitted(sort='new',limit=10)
       com_posts = user.get_comments(sort='new',limit=10)
       process_submissions(sub_posts, False, u)
       process_submissions(com_posts, True, u)
    if CHANGES > 0:
        print("New changes found, emailing now")
        emailMessage = "\r\n".join(["From: follower_bot@reddit.com", "To: 13djwright@gmail.com", "Subject: Updated Subs and Comments from stalker_bot", "", MESSAGE])
        server.sendmail('follower_bot@reddit.com', '13djwright@gmail.com', emailMessage) 
       
main()  
