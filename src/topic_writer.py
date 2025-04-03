import logging
import os
import re
from base64 import b64encode

import requests


class TopicWriter:

    def __init__(self):

        enabled_value = os.getenv("DMS_IPB_ENABLED")

        if enabled_value is not None:
            self.__enabled = "true" == enabled_value.lower()
        else:
            self.__enabled = False

        self.__api_url = os.getenv("DMS_IPB_API_URL")
        self.__api_key = os.getenv("DMS_IPB_API_KEY")
        self.__forum_id = os.getenv("DMS_IPB_FORUM_ID")
        self.__author_id = os.getenv("DMS_IPB_AUTHOR_ID")
        self.__topic_suffix = os.getenv("DMS_IPB_TOPIC_SUFFIX")
        self.__post_prefix = os.getenv("DMS_IPB_POST_PREFIX")
        self.__link_text = os.getenv("DMS_IPB_LINK_TEXT")
        self.__external_url = os.getenv("DMS_EXTERNAL_URL")

    async def write(self, file_name, topic_name):

        if self.__enabled:

            logging.info(
                "[TopicWriter] - Attempting to create topic '" + topic_name + "' for war report '" + file_name + "' on IPB forum...")

            encoded_bytes = b64encode((self.__api_key + ":").encode("utf-8"))
            api_key = str(encoded_bytes, "utf-8")
            headers = {'Authorization': 'Basic %s' % api_key}

            url = re.sub(r"/$", "", self.__external_url)

            if not url.startswith("http://"):
                url = "http://" + url
            url += "/" + file_name

            post = "<p>" + self.__post_prefix + " " + "<a href=\"" + url + ".html\">" + self.__link_text + "</a></p>"

            data = {"forum": self.__forum_id,
                    "title": self.__topic_suffix + " " + topic_name,
                    "post": post,
                    "author": self.__author_id}

            response = None
            retry = 0

            while (response is None or (200 != response.status_code and 201 != response.status_code)) and retry <= 3:
                logging.info(
                    "[TopicWriter] - Trying to create topic " + self.__topic_suffix + topic_name
                    + " in forum: " + self.__forum_id + " ...")

                url = re.sub(r"/$", "", self.__api_url) + "/forums/topics"

                response = requests.post(url, data=data, headers=headers)
                retry += 1

            if response is not None and (200 == response.status_code or 201 == response.status_code):
                logging.info(
                    "[TopicWriter] - Topic " + self.__topic_suffix + topic_name
                    + " created with success in forum: " + self.__forum_id)
            else:
                logging.info(
                    "[TopicWriter] - Failed to create topic " + self.__topic_suffix + topic_name
                    + " in forum: " + self.__forum_id)

                if response is not None:
                    logging.info(
                        "[TopicWriter] - Response status is: " + str(response.status_code))
                    logging.info(
                        "[TopicWriter] - Response data is: " + response.text)
        else:
            logging.info(
                "[TopicWriter] - Topic writing is disabled and will be skipped")
