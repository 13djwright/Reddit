#!/usr/bin/python3
import praw, configparser, pprint, sqlite3, re, smtplib

#-----Setting Up Configuration-----#
ini_file = "config.ini"
users_to_follow = []
MESSAGE = ""
CHANGES = 0

config = configparser.ConfigParser(allow_no_value=True)
config.read(ini_file)

user_name = config['User']['name']
password = config['User']['password']
email = config['User']['email']
posts_file = config['SQL']['posts_file']
smtp_email = config['SMTP']['email']
smtp_password = config['SMTP']['password']

user_agent = "Follower script by " + user_name

server = smtplib.SMTP("smtp.gmail.com",587)
server.ehlo()
server.starttls()
server.login(smtp_email,smtp_password)
r = praw.Reddit(user_agent=user_agent)

#------SQL Database------#
print('\nSetting up database...')
sql = sqlite3.connect(posts_file)
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(id TEXT)')

sql.commit()
print('DONE')

for user in config['To Follow']:
    users_to_follow.append(str(user))

#---------HELPER FUNCTIONS---------#

#------This function should be able to handle submissions and comments, checking whether it has been seen, if not adding it to the database table------#
def is_new_post(post_id, post_author):
    cur.execute('SELECT * FROM oldposts WHERE id=?',(post_id,))
    if not cur.fetchone():
        cur.execute('INSERT INTO oldposts VALUES(?)', (post_id,))
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
    for u in users_to_follow:
       print("Getting submissions from " + u + "\n")
       user = r.get_redditor(u)
       sub_posts = user.get_submitted(sort='new',limit=10)
       com_posts = user.get_comments(sort='new',limit=10)
       process_submissions(sub_posts, False, u)
       process_submissions(com_posts, True, u)
    if CHANGES > 0:
        from_e = "From: follower_bot"
        to_e = "To: " + email
        print("New changes found, emailing now\n")
        emailMessage = "\r\n".join([from_e, to_e, "Subject: Updated Submissions and Comments from FollowerBot", "", MESSAGE])
        server.sendmail('follower_bot@reddit.com', email, emailMessage) 
       
main()  
