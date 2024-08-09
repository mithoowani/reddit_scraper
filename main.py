"""
Reddit r/watchexchange scraper
v1.0
------------------------------
Scrapes r/watchexchange for new and relevant listings, saves them to a DataFrame/CSV,
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
	Retrieves relevant information from an r/watchexchange submission
	:param _submission: r/watchexchange submission
	:return: dictionary containing contents of the post
	"""
	post_date = datetime.utcfromtimestamp(_submission.created_utc)
	post_date -= timedelta(hours=4)  # TODO: Does not adjust for daylight savings

	return {'title': _submission.title,
			'date': post_date.isoformat(sep=' '),
			'ID': _submission.id,
			'author': _submission.author.name,
			'num_transact': _submission.author_flair_text,
			'price_cat': _submission.link_flair_text,
			'url': f'https://www.reddit.com{_submission.permalink}'}


def format_post(_post: dict) -> str:
	"""
	Formats the post (dictionary) as a string
	:param _post: dictionary containing relevant parts of the reddit post
	:return: string formatting of the post
	"""
	df = pd.DataFrame(_post, index=[0]).transpose()
	return df.to_html()


def send_email(contents, subject):
	"""
	Logs onto gmail account sm.reddit.scraper@gmail.com and sends an email to sirajm@gmail.com with
	the specified subject and contents
	:param contents: string
	:param subject: string
	:return: None
	"""

	yag = yagmail.SMTP(CONFIG['gmail_user'], CONFIG['gmail_pw'])
	yag.send(CONFIG['gmail_recipient'], subject, contents)


def post_is_new(_id: str, all_ids: pd.Series) -> bool:
	"""
	Checks if post has already been seen.
	:param _id: post id (string)
	:param all_ids: all post id's that have already been seen (pd.Series)
	:return: bool
	"""
	if not np.any(all_ids == _id):
		return True
	else:
		return False


def post_is_relevant(title):
	for substring in CONFIG['RELEVANT_SUBSTRINGS']:
		if substring in title:
			return True
	return False


def send_email_notification(_post: dict) -> None:
	"""
	Sends an email notifying about a new post
	:param _post: relevant post information (dict)
	:return: None
	"""
	email_body = format_post(_post)
	email_subject = _post['title']
	send_email(email_body, email_subject)


with open('config.yaml', 'r') as f:
	CONFIG = yaml.safe_load(f)


def main():
	# Initialize the dataframe of saved posts
	today_date = datetime.now().date().isoformat()
	filename = today_date + '.csv'
	file = Path(filename)
	if file.exists():
		saved_posts = pd.read_csv(file)
	else:
		saved_posts = pd.DataFrame()

	# Initialize the Reddit instance
	reddit = praw.Reddit(
		client_id=CONFIG['client_id'],
		client_secret=CONFIG['client_secret'],
		user_agent=CONFIG['user_agent']
	)

	# Scan through posts, identifying ones that are both relevant and new
	for submission in reddit.subreddit(CONFIG['subreddit']).new(limit=CONFIG['n_posts_to_search']):
		post: dict = retrieve_post_info(submission)

		if post_is_relevant(post['title']) and (saved_posts.empty or post_is_new(post['ID'], saved_posts['ID'])):
			saved_posts = saved_posts._append(post, ignore_index=True)
			send_email_notification(post)

	saved_posts.to_csv(file, index=False)


if __name__ == '__main__':
	main()
