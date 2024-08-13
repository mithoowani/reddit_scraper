## reddit_scraper (v1.0)

- [X] Scrapes subreddit(s) for new submissions with titles containing user-specified keywords
- [X] Saves new submissions to CSV
- [X] Sends email notifications about new submissions

### Example
`Get email alerts for new submissions on r/watchexchange with a specific make/model`

### Requirements
1. `Python 3.10`
2. `pip install -r requirements.txt`

### Usage
1. `Edit config/config_example.yaml and save as config.yaml`
2. `Edit secrets/secrets_example.yaml and save as secrets.yaml`
3. `Set up crontab to run the script on a schedule`
4. `CSV files containing new submissions are stored in /data, with date as filename`

### Docker
```
docker run --rm \ 
--mount type=bind,source=/folder/containing/config,target=/config \
--mount type=bind,source=/folder/containing/secrets,target=/secrets \
--mount type=bind,source=/folder/containing/data,target=/data \
reddit_scraper
```