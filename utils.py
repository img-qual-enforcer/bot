import os
import sys
import logging
import praw

RATELIMIT_SECONDS = 600

SUB_NAME = os.environ["SUBREDDIT_NAME"]

MIN_IMAGE_WIDTH_PX = 849

REMOVAL_MESSAGE = """
# Hi /u/{author}, your post was removed because a low quality image was detected.
\n\n
# Please follow the instructions below and [submit a higher quality image.](https://new.reddit.com/r/{sub}/submit)
\n\n
---
\n\n
1. Export your resume as a [**PDF file**](https://www.adobe.com/uk/acrobat/resources/google-doc-to-pdf.html)  
\n\n
2. Convert the PDF to a **PNG file ([600 DPI](https://www.adobe.com/uk/creativecloud/photography/discover/dots-per-inch-dpi-resolution.html))** using https://www.cleverpdf.com/pdf-to-images  
\n\n
    • https://imgur.com/RxxYFQe   
\n\n
3. On **[Desktop (New Reddit)](https://new.reddit.com/r/{sub}/submit)**, insert the PNG file into a **[text submission](https://imgur.com/8iik4YP)**  
\n\n
    • https://imgur.com/8iik4YP  
\n\n
---
\n\n
# Please don't:  
\n\n
* Use your phone camera to take a picture of your resume  
\n\n
* Take a screenshot of your resume  
\n\n
* Crop out your margins  
\n\n
* Upload a dark mode version of your resume  
\n\n
---
\n\n
*beep boop. I am a bot, and this action was performed automatically. Please [contact the mod team](/message/compose/?to=/r/{sub}) if you have any questions or concerns.*
\n\n
---
"""


def setup_logger():
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%m-%d %I:%M",
        level=logging.INFO,
        handlers=[
            logging.FileHandler("status.log", mode="a"),
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
        ratelimit_seconds=RATELIMIT_SECONDS,
    )
    if reddit.user.me():
        logging.info("Authenticated.")
        return reddit
    else:
        logging.error("Failed to authenticate.")
        sys.exit()