import praw
from concurrent.futures import ThreadPoolExecutor

reddit = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
                    client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
def get_comments(url):
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=None)
    comments = []
    for comment in submission.comments.list():
        comments.append(comment.body)
    return comments

urls = ['https://www.reddit.com/r/Python/comments/psrskf/python_3100a2_is_now_available/', 
        'https://www.reddit.com/r/datascience/comments/psjhd7/how_to_learn_data_science_a_comprehensive/', 
        'https://www.reddit.com/r/MachineLearning/comments/pqo3m3/d_learning_rate_and_batch_size_in_the_deep_learning/']

with ThreadPoolExecutor() as executor:
    results = list(executor.map(get_comments, urls))

for url, comments in zip(urls, results):
    print(f"Comments from {url}:")
    for comment in comments:
        print(f"- {comment}")