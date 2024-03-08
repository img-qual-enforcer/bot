import logging
import os
import sys

import praw
from dotenv import load_dotenv

LIMIT = 10
SUB_NAME = "EngineeringResumes"
MIN_IMAGE_WIDTH_PX = 1700
RATELIMIT_SECONDS = 600

REMOVAL_MESSAGE = """
**Hi /u/{author}, please follow the instructions below and submit a higher quality image:**  
\n\n
---
\n\n
1. Export your resume as a [**PDF file**](https://www.adobe.com/uk/acrobat/resources/google-doc-to-pdf.html)  
\n\n
2. Convert it to a **[600 DPI](https://www.adobe.com/uk/creativecloud/photography/discover/dots-per-inch-dpi-resolution.html) PNG file** using https://www.cleverpdf.com/pdf-to-images: https://imgur.com/RxxYFQe     
\n\n
3. On **[DESKTOP (NEW.REDDIT)](https://new.reddit.com/r/{sub}/submit)**, insert the PNG into a **[text submission](https://imgur.com/8iik4YP)**  
\n\n
---
\n\n
**Please don't:**  
\n\n
* Take a picture of your resume with your phone camera  
\n\n
* Take a screenshot of your resume  
\n\n
* Crop out your margins  
\n\n
* Upload a dark mode version of your resume  
\n\n
---
"""


def setup_logger() -> None:
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%m-%d %I:%M",
        level=logging.INFO,
        handlers=[
            # logging.FileHandler("logs.log", mode="w"),
            logging.StreamHandler(),
        ],
    )


def create_reddit_instance() -> praw.Reddit:
    load_dotenv()
    reddit = praw.Reddit(
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        user_agent=os.getenv("USER_AGENT"),
        ratelimit_seconds=RATELIMIT_SECONDS,
    )

    if not reddit.user.me():
        logging.error("Failed to authenticate.")
        sys.exit()

    return reddit


def extract_width(selftext: str) -> int:
    try:
        extracted_string = selftext.split("width=")[1].split("&")[0]
        width = int(extracted_string)
        return int(width)

    except IndexError:
        return -1


def convert_to_dpi(image_width: int) -> int:
    return round(image_width / 8.5)


def remove(submission: praw.models.Submission, image_width: int) -> None:
    submission.mod.remove(spam=False)
    submission.mod.flair(text="Post Removed: Low Image Quality", css_class="remove1")
    submission.mod.lock()
    removal_message_with_author = REMOVAL_MESSAGE.format(
        author=submission.author, sub=SUB_NAME
    )
    submission.mod.send_removal_message(
        type="public", message=removal_message_with_author
    )
    submission.mod.send_removal_message(
        type="private_exposed",
        title="LOW QUALITY IMAGE",
        message=removal_message_with_author,
    )
    logging.info("REMOVED id: %s, image width: %dpx", submission.id, image_width)


def approve(submission: praw.models.Submission, image_width: int) -> None:
    submission.mod.approve()
    logging.info("APPROVED id: %s, image width: %dpx", submission.id, image_width)


def process(submission: praw.models.Submission) -> None:
    if submission.approved:
        logging.debug("skip id: %s, already approved", submission.id)
        return

    if submission.link_flair_text in {"Question", "Success Story!", "Meta"}:
        logging.debug("skip id: %s, %s", submission.id, submission.link_flair_text)
        return

    image_width = extract_width(submission.selftext)

    if image_width == -1:
        logging.error(
            "Unable to extract image width from body text: id: %s, user: /u/%s",
            submission.id,
            submission.author,
        )

    if image_width < MIN_IMAGE_WIDTH_PX:
        remove(submission, image_width)

    else:
        approve(submission, image_width)


if __name__ == "__main__":
    setup_logger()
    logging.debug("start script")
    reddit = create_reddit_instance()
    subreddit = reddit.subreddit(SUB_NAME)

    for submission in subreddit.new(limit=LIMIT):
        logging.debug("processing id: %s", submission.id)
        process(submission)
        logging.debug("processed id: %s", submission.id)
    logging.debug("script complete")
