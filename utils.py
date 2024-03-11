import logging
import os
import sys

import praw

SUB_NAME = os.environ["SUB_NAME"]

MIN_IMAGE_WIDTH_PX = int(os.environ["MIN_IMAGE_WIDTH_PX"])

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


def setup_logger():
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        datefmt="%m-%d %I:%M",
        level=logging.INFO,
        handlers=[
            logging.FileHandler("logs.txt", mode="a"),
            logging.StreamHandler(),
        ],
    )


def create_reddit_instance():
    reddit = praw.Reddit(
        username=os.environ["USERNAME"],
        password=os.environ["PASSWORD"],
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        user_agent=os.environ["USER_AGENT"],
        ratelimit_seconds=os.environ["RATELIMIT_SECONDS"],
    )
    if reddit.user.me():
        return reddit
    else:
        logging.error("Failed to authenticate.")
        sys.exit()
