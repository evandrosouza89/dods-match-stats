import logging
import os
import re
import sys

import requests


class DiscordWriter:
    __API_BASE_URL = "https://discord.com/api/v10"

    def __init__(self):

        enabled_value = os.getenv("DMS_DISCORD_ENABLED")

        if enabled_value is not None:
            self.__enabled = "true" == enabled_value.lower()
        else:
            self.__enabled = False

        self.__token = os.getenv("DMS_DISCORD_TOKEN")
        self.__channel_id = os.getenv("DMS_DISCORD_CHANNEL_ID")
        self.__external_url = os.getenv("DMS_EXTERNAL_URL")

        if self.__enabled:

            # Headers
            self.__headers = {
                "Authorization": "Bot " + self.__token,
                "Content-Type": "application/json"
            }

            self.test_bot_permissions(self.__headers, str(self.__channel_id))

    @staticmethod
    def test_bot_permissions(headers, channel_id):

        logging.info(
            "[DiscordWriter] - Testing discord bot setup...")

        # Step 1: Check if the channel exists

        DiscordWriter._check_if_channel_exists(channel_id, headers)

        logging.info(
            "[DiscordWriter] - Channel " + channel_id + " exists. Proceeding to test writing permissions...")

        # Step 2: Send the message

        test_message_id = DiscordWriter._send_test_message(channel_id, headers)

        # Step 3: Delete the message

        DiscordWriter._delete_message(channel_id, headers, test_message_id)

        logging.info(
            "[DiscordWriter] - Discord bot setup looks alright!")

    @staticmethod
    def _delete_message(channel_id, headers, test_message_id):

        logging.info("[DiscordWriter] - Proceeding to delete message " + test_message_id + "...")

        delete_url = DiscordWriter.__API_BASE_URL + "/channels/" + channel_id + "/messages/" + test_message_id

        delete_response = requests.delete(delete_url.format(message_id=test_message_id), headers=headers)

        if delete_response.status_code != 200 and delete_response.status_code != 204:
            logging.error(
                "[DiscordWriter] - Failed to delete test message " + test_message_id + ". Check bot permissions on channel " + channel_id + ". Response code is " + str(
                    delete_response.status_code))
            sys.exit(2)

        logging.info("[DiscordWriter] - Message " + test_message_id + " successfully deleted!")

    @staticmethod
    def _send_test_message(channel_id, headers):

        payload = {
            "content": "Greetings from dods-match-stats bot!"
        }

        send_url = DiscordWriter.__API_BASE_URL + "/channels/" + channel_id + "/messages"

        response = requests.post(send_url, json=payload, headers=headers)

        if response.status_code != 200:
            logging.error(
                "[DiscordWriter] - Failed to send test message. Check bot permissions on channel " + channel_id + ". Response code is " + str(
                    response.status_code))
            sys.exit(2)

        logging.info("[DiscordWriter] - Test message sent successfully!")

        message_data = response.json()

        return str(message_data["id"])

    @staticmethod
    def _check_if_channel_exists(channel_id, headers):

        channel_check_url = DiscordWriter.__API_BASE_URL + "/channels/" + channel_id

        response = requests.get(channel_check_url, headers=headers)

        if response.status_code != 200:
            logging.info(
                "[DiscordWriter] - Channel " + channel_id + " not found!")

    async def write(self, file_name):

        if self.__enabled:

            channel_id = str(self.__channel_id)

            logging.info(
                "[DiscordWriter] - Attempting to send war report to discord channel " + channel_id + "...")

            send_url = DiscordWriter.__API_BASE_URL + "/channels/" + channel_id + "/messages"

            report_title = "🎖 War Report - " + file_name + "🎖"

            payload = {
                "content": report_title
            }

            response = requests.post(send_url, json=payload, headers=self.__headers)

            if response.status_code != 200:
                logging.error(
                    "[DiscordWriter] - Failed to send report title message. Response code is " + str(
                        response.status_code))

            report_link = self.__build_link_url(file_name, self.__external_url)

            payload = {
                "content": report_link
            }

            response = requests.post(send_url, json=payload, headers=self.__headers)

            if response.status_code != 200:
                logging.error(
                    "[DiscordWriter] - Failed to send report link message. Response code is " + str(
                        response.status_code))

    @staticmethod
    def __build_link_url(file_name, external_url):

        url = re.sub(r"/$", "", external_url)

        url += "/" + file_name + ".html"

        return  "[Click to view](" + url + ")"
