"""
Subreddit scraper and email notifications
v1.0
------------------------------
Scrapes a subreddit for new and relevant submissions, saves them to a DataFrame/CSV,
and sends e-mail notifications.

Python 3.10
New users pip install -r requirements.txt
------------------------------
"""


from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import praw
import yagmail
import yaml


def retrieve_post_info(_submission: praw.reddit.Submission) -> dict:
	"""
	Retrieves relevant information from a new submission
	:param _submission: subreddit submission
	:return: dictionary containing contents of the post
	"""
	post_date = datetime.utcfromtimestamp(_submission.created_utc)
	post_date -= timedelta(hours=4)  # TODO: Does not adjust for daylight savings

	return {'subreddit': _submission.subreddit.display_name,
			'title': _submission.title,
			'post date': post_date.isoformat(sep=' '),
			'ID': _submission.id,
			'author': _submission.author.name,
			'num_transact': _submission.author_flair_text,
			'price_cat': _submission.link_flair_text,
			'url': f'https://www.reddit.com{_submission.permalink}'}


def format_post(_post: dict) -> str:
	"""
	Formats the post (dictionary) as an HTML table
	:param _post: dictionary containing relevant parts of the reddit post
	:return: string formatting of the post
	"""
	df = pd.DataFrame(_post, index=[0]).transpose()
	return df.to_html()


def send_email(contents, subject):
	"""
	Logs onto a gmail account, sends email to recipient with subject/contents
	:param contents: string
	:param subject: string
	:return: None
	"""

	yag = yagmail.SMTP(SECRETS['gmail_user'], SECRETS['gmail_pw'])
	yag.send(SECRETS['gmail_recipient'], subject, contents)


def post_is_new(_id: str, all_ids: pd.Series) -> bool:
	"""
	Checks if post has already been seen.
	:param _id: post id (string)
	:param all_ids: all post id's that have already been seen (pd.Series)
	:return: bool
	"""
	if np.any(all_ids == _id):
		return False
	else:
		return True


def post_is_relevant(title):
	"""
	Checks if post contains the relevant substring
	:param title: title of the post (string)
	:return: bool
	"""
	for substring in CONFIG['RELEVANT_SUBSTRINGS']:
		if substring in title:
			return True
	return False


def send_email_notification(_post: dict) -> None:
	"""
	Sends email notification about new post
	:param _post: relevant post information (dict)
	:return: None
	"""
	email_body = format_post(_post)
	email_subject = _post['title']
	send_email(email_body, email_subject)


def process_post(_submission: praw.Reddit.submission, _saved_posts: pd.DataFrame):
	"""
	Processes redidit submission, determines if it's relevant and previously unseen - if both conditions
	are met, then saves relevant info to the dataframe and sends an email to user, if desired.
	:param _submission: A praw.Reddit.submission
	:param _saved_posts: A pd.DataFrame containing all previously seen posts
	:return: None
	"""
	post: dict = retrieve_post_info(_submission)
	post_df = pd.DataFrame(post, index=[0])

	if post_is_relevant(post['title']) and (_saved_posts.empty or post_is_new(post['ID'], _saved_posts['ID'])):
		print(post['title'])  # TODO: Remove
		if CONFIG['email_notifications']:
			send_email_notification(post)
		return pd.concat([_saved_posts, post_df])

	else:
		return _saved_posts


def main():
	# Initialize the dataframe of saved posts
	today_date = datetime.now().date().isoformat()
	filename = today_date + '.csv'
	file = Path('data/' + filename)
	if file.exists():
		saved_posts = pd.read_csv(file)
	else:
		saved_posts = pd.DataFrame()

	# Initialize the Reddit instance
	reddit = praw.Reddit(
		client_id=SECRETS['client_id'],
		client_secret=SECRETS['client_secret'],
		user_agent=SECRETS['user_agent']
	)

	# Scan through posts in all user-defined subreddits
	subreddits = CONFIG['subreddits']
	for subreddit_name in subreddits:
		for submission in reddit.subreddit(subreddit_name).new(limit=CONFIG['n_posts_to_search']):
			saved_posts = process_post(submission, saved_posts)

	saved_posts.to_csv(file, index=False)


if __name__ == '__main__':

	with open('config/config.yaml') as f:
		CONFIG = yaml.safe_load(f)

	with open('secrets/secrets.yaml') as f:
		SECRETS = yaml.safe_load(f)

	main()
