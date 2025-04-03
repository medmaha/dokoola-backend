import threading
from typing import Union

from bs4 import BeautifulSoup, Tag


class Logging:

    def error(self, *args, **kwargs):
        print(*args, **kwargs)

    def info(self, *args, **kwargs):
        print(*args, **kwargs)


logger = Logging()


def kill_zombie_threads():
    """Clean up any zombie threads"""

    current = threading.current_thread()
    for thread in threading.enumerate():
        if thread != current and not thread.daemon:
            try:
                thread.join(timeout=1.0)
            except Exception:
                pass


def get_job_type_or_other(job_type: str) -> Union[str, str | None]:
    job_type = (job_type or "").lower()

    if "full" in job_type:
        return ["full-time", None]
    elif "part" in job_type:
        return ["part-time", None]
    elif "freelance" in job_type:
        return ["freelance", None]
    elif "contract" in job_type:
        return ["contract", None]
    elif "intern" in job_type:
        return ["internship", None]
    else:
        return ["other", job_type]


def clean_html_content(
    soup: BeautifulSoup, elems=None, classes=None, attrs=None, remove_comments=None
) -> None:
    """
    Clean HTML content by removing unnecessary elements and attributes.

    Args:
        soup: BeautifulSoup object containing the HTML
        classes: List of class names to target specific elements
        attrs: Dictionary of attributes to target specific elements
        remove_comments: List of comments to remove from the HTML
    """
    # Remove unnecessary tags from the HTML
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("soup must be a BeautifulSoup object")

    elements = [soup]

    try:
        if attrs:
            elements.extend(soup.find_all(attrs=attrs))
        if classes:
            elements.extend(soup.find_all(class_=classes))

        # Unwanted_tags to remove
        unwanted_tags = [
            "script",
            "style",
            "link",
            "form",
            "input",
            "button",
            "head",
            "nav",
            "aside",
            "meta",
            "iframe",
            "embed",
            "object",
            "noscript",
            "img",
            "footer",
            "select",
            # "a",
        ]

        if elems:
            unwanted_tags += elems

        for element in elements:
            # Remove unwanted tags
            for tag in unwanted_tags:
                for elem in element.find_all(tag):
                    elem.decompose()

            # Remove comments if specified
            if remove_comments:
                for comment in remove_comments:
                    for com_elem in element.find_all(
                        text=lambda text: isinstance(text, comment)
                    ):
                        com_elem.extract()

            # Remove head section
            head = element.find("head")
            if head:
                head.decompose()

            # Remove empty tags
            for tag in element.find_all():
                if len(tag.get_text(strip=True)) == 0 and len(tag.find_all()) == 0:
                    tag.decompose()

            # Remove specific attributes that might contain unwanted content
            for tag in element.find_all(True):
                for attr in ["onclick", "onload", "onmouseover", "onmouseout", "style"]:
                    if attr in tag.attrs:
                        del tag.attrs[attr]

    except Exception as e:
        logger.error(f"Error cleaning HTML content: {str(e)}")
        raise
