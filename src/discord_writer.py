import logging
import os
import re

import discord


class DiscordWriter:

    def __init__(self):
        self.__enabled = os.getenv("DMS_DISCORD_ENABLED")
        self.__token = os.getenv("DMS_DISCORD_TOKEN")
        self.__channel_id = os.getenv("DMS_DISCORD_CHANNEL_ID")
        self.__external_url = os.getenv("DMS_EXTERNAL_URL")
        self.__intents = discord.Intents.default()
        self.__discord_client = discord.Client(intents=self.__intents)

    async def write(self, file_name):

        if self.__enabled:

            logging.info(
                "[DiscordWriter] - Attempting to send war report to discord channel " + self.__channel_id + "...")

            await self.__discord_client.wait_until_ready()  # Ensure bot is ready

            channel = self.__discord_client.get_channel(int(self.__channel_id))  # Get the channel

            if channel:

                link = self.__build_link_url(file_name, self.__external_url)

                await channel.send("🎖 War Report - " + file_name + "🎖")
                await channel.send(link)

            else:
                logging.error("[DiscordWriter] - Channel with id: " + self.__channel_id + "not found.")

        else:
            logging.info("[DiscordWriter] - Discord writing is disabled and will be skipped")

    @staticmethod
    def __build_link_url(file_name, external_url):

        url = re.sub(r"/$", "", external_url)

        if not url.startswith("http://"):
            url = "http://" + url

        url += "/" + file_name

        return url
