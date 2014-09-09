import praw, time, sys, sqlite3, re
from datetime import datetime
from getpass import getpass


print '''
============ REDDITBOTWRAPPER ============
Version: 1.0'''

#------Bot Configuration------#
BOTNAME     = raw_input('Username: ')
PASSWORD    = getpass('Password: ')
USERAGENT   = 'Author: /u/13djwright'
SUBREDDIT   = 'all'


#------SQL Database------#
print '\nSetting up database...'
sql = sqlite3.connect('posts.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')

sql.commit()
print 'DONE'


#------Reddit Login------#
print 'Logging in to Reddit...'
r = praw.Reddit(USERAGENT)
r.login(BOTNAME, PASSWORD)
print 'DONE'

#---------HELPER FUNCTIONS---------#

#------This function should be able to handle submissions and comments, checking whether it has been seen, if not adding it to the database table------#
def is_new_post(post_id, post_author):
    cur.execute('SELECT * FROM oldposts WHERE ID=?',(post_id,))
    if not cur.fetchone() and post_author.lower() != BOTNAME.lower():
        cur.execute('INSERT INTO oldposts VALUES(?)', (post_id,))
        sql.commit()
        return True
    else:
        return False

#------This function is used to process new submissions. Pass in a block of code for posts------#
def process_submissions(posts):
    for p in posts:
        pID = p.id
        try:
            pAuth = p.author.name
        except:
            pAuth = '[DELETED]'
        if is_new_post(pID, pAuth):
            #This is a new post we havent seen, we can now process it.
            #by this point, it has already been added to the database


#---------Wrapping function for processing---------#
def parsing():
    sub = r.get_subreddit(SUBREDDIT)
    posts = sub.get_comments(SUBREDDIT)
    process_submissions(posts)


