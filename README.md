<h1>reddit</h1>

Reddit bots written in Python to do various functions. (Currently only 1 finished more in Dev).


<h5>Follower Bot</h5>

A bot used to follow certain users and have their posts and comments emailed to you. Best run as a cron job every few minutes. 
Relies on a config.ini file that looks like the following:

[User]
name=username
password=password
email=email_to_recieve@email.com

[SMTP]
email=email_to_send@email.com
password=password

[To Follow]
user1
user2
user3

[SQL]
posts_file=/path/to/posts/database/posts.db


