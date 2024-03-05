import logging

from utils import (
    MIN_IMAGE_WIDTH_PX,
    REMOVAL_MESSAGE,
    SUB_NAME,
    create_reddit_instance,
    setup_logger,
)


def extract_width(selftext: str) -> int:
    try:
        extracted_string = selftext.split("width=")[1].split("&")[0]
        width = int(extracted_string)
        return int(width)

    except IndexError:
        return -1


def convert_to_dpi(image_width: int) -> int:
    return round(image_width / 8.5)


def remove(submission, image_width: int) -> None:
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
    logging.info(f"REMOVED {submission.id}, {image_width}, {submission.author}")


def approve(submission, image_width: int) -> None:
    submission.mod.approve()
    logging.debug(f"APPROVED {submission.id}, {image_width}, {submission.author}")


def process(submission) -> None:
    if submission.approved:
        return

    if submission.link_flair_text in {"Question", "Success Story!", "Meta"}:
        return

    image_width = extract_width(submission.selftext)

    if image_width == -1:
        logging.error(
            f"Unable to extract image width from body text, {submission.id}, {submission.author}"
        )
        return

    elif image_width < MIN_IMAGE_WIDTH_PX:
        remove(submission, image_width)

    else:
        approve(submission, image_width)


if __name__ == "__main__":
    setup_logger()
    reddit = create_reddit_instance()
    subreddit = reddit.subreddit(SUB_NAME)

    for submission in subreddit.new(limit=20):
        process(submission)
