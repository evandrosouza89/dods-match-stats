import logging
import re
from base64 import b64encode

import requests

from dods_match_stats import config


class TopicWriter:
    __EXTERNAL_URL = config.get("HTMLPageOutputSection", "external.url")
    __API_URL = config.get("ForumTopicOutputSection", "ipb.apiurl")
    __API_KEY = config.get("ForumTopicOutputSection", "ipb.apikey")
    __FORUM_ID = config.get("ForumTopicOutputSection", "ipb.forumid")
    __AUTHOR_ID = config.get("ForumTopicOutputSection", "ipb.authorid")
    __TOPIC_SUFFIX = config.get("ForumTopicOutputSection", "ipb.topicsuffix")
    __POST_PREFIX = config.get("ForumTopicOutputSection", "ipb.postprefix")
    __LINK_TEXT = config.get("ForumTopicOutputSection", "ipb.linktext")

    def write(self, file_name, topic_name):
        encoded_bytes = b64encode((TopicWriter.__API_KEY + ":").encode("utf-8"))
        api_key = str(encoded_bytes, "utf-8")
        headers = {'Authorization': 'Basic %s' % api_key}

        url = re.sub(r"/$", "", TopicWriter.__EXTERNAL_URL)

        if not url.startswith("http://"):
            url = "http://" + url
        url += "/" + file_name

        post = "<p>" + TopicWriter.__POST_PREFIX + " " + "<a href=\"" + url + ".html\">" + TopicWriter.__LINK_TEXT + "</a></p>"

        data = {"forum": TopicWriter.__FORUM_ID,
                "title": TopicWriter.__TOPIC_SUFFIX + " " + topic_name,
                "post": post,
                "author": TopicWriter.__AUTHOR_ID}

        response = None
        retry = 0

        while (response is None or (200 != response.status_code and 201 != response.status_code)) and retry <= 3:
            logging.info(
                "[TopicWriter] - Trying to create topic " + TopicWriter.__TOPIC_SUFFIX + topic_name
                + " in forum: " + TopicWriter.__FORUM_ID + " ...")

            url = re.sub(r"/$", "", TopicWriter.__API_URL) + "/forums/topics"

            response = requests.post(url, data=data, headers=headers)
            retry += 1

        if response is not None and (200 == response.status_code or 201 == response.status_code):
            logging.info(
                "[TopicWriter] - Topic " + TopicWriter.__TOPIC_SUFFIX + topic_name
                + " created with success in forum: " + TopicWriter.__FORUM_ID)
        else:
            logging.info(
                "[TopicWriter] - Failed to create topic " + TopicWriter.__TOPIC_SUFFIX + topic_name
                + " in forum: " + TopicWriter.__FORUM_ID)

            if response is not None:
                logging.info(
                    "[TopicWriter] - Response status is: " + str(response.status_code))
                logging.info(
                    "[TopicWriter] - Response data is: " + response.text)
