#!/usr/bin/env python3
"""
Slack bot using the Slack API and python SlackClient
"""

import random
import os
import time
import sys

from slackclient import SlackClient

ACCESS_TOKEN = os.environ.get("SLACK_API_TOKEN")
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM


def main():
    """
    main is the main program that will run when the script is executed.
    """
    client = SlackClient(ACCESS_TOKEN)

    if not client.rtm_connect(with_team_state=False):
        print("could not connect to slack")
        sys.exit(1)

    print("connected to network!")

    bot_id = client.api_call("auth.test")["user_id"]

    for data in tagged_messages(client, bot_id):
        if any(x in data.get("text") for x in ["lunch", "eat", "hungry"]):
            whats_for_lunch(client, data)
            continue


def tagged_messages(client: SlackClient, user_id: str):
    """
    Check the connection and parse all events. If the event is of desired type
    or content yield the message to the consumer of the iterator.
    """
    while True:
        for data in client.rtm_read():
            if data.get("type") == "message" and user_id in data.get("text"):
                yield data

        time.sleep(RTM_READ_DELAY)


def whats_for_lunch(client: SlackClient, data: dict):
    """
    Fetch a random value of what's for lunch!
    """
    restaurants = ["Textas Longhorn", "Sushi!", "I think pizza!"]
    random_restaurant = random.choice(restaurants)

    client.rtm_send_message(data.get("channel"), random_restaurant)


if __name__ == "__main__":
    main()
