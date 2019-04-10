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
        if "lunch poll" in data.get("text"):
            create_message(client, data)
            continue

        if any(x in data.get("text") for x in ["lunch", "eat", "hungry"]):
            whats_for_lunch(client, data)
            continue

        client.rtm_send_message(
            data.get("channel"), "don't know what to say about that..."
        )


def tagged_messages(client: SlackClient, user_id: str):
    """
    Check the connection and parse all events. If the event is of desired type
    or content yield the message to the consumer of the iterator.
    """
    while True:
        for data in client.rtm_read():
            if "text" not in data:
                continue

            if data.get("type") == "message" and user_id in data.get("text"):
                yield data

        time.sleep(RTM_READ_DELAY)


def whats_for_lunch(client: SlackClient, data: dict):
    """
    Fetch a random value of what's for lunch!
    """
    restaurants = ["Textas Longhorn", "Sushi!", "I think pizza!"]

    client.rtm_send_message(data.get("channel"), random.choice(restaurants))


def create_message(client: SlackClient, data: dict):
    """
    Create a blocked message with available restaurants to vote for.
    """
    restaurants = {
        ":hamburger: Texas Longhorn": {
            "description": "Some nice burgers here!"
        },
        ":sushi: Sushi Sun": {"description": "Here we can enjoy sushi!"},
        ":seedling: Re-orient": {"description": "Meze for us!"},
    }

    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Where should we eat lunch?*"},
        },
        {"type": "divider"},
    ]

    for restaurant, info in restaurants.items():
        blocks.extend(
            [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "{}\n{}".format(
                            restaurant, info.get("description")
                        ),
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Vote",
                        },
                        "value": "click_me_123",
                    },
                },
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": "No votes"}],
                },
            ]
        )

    client.api_call(
        "chat.postMessage", channel=data.get("channel"), blocks=blocks
    )


if __name__ == "__main__":
    main()
