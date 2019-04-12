#!/usr/bin/env python3
"""
This is a webhook integration for Slack bots. The interactive component
configuration points to this server.
"""

import os
import json

from flask import Flask, request
from pprint import pprint
from slackclient import SlackClient

app = Flask(__name__)
client = SlackClient(os.environ.get("SLACK_API_TOKEN"))
votes = {}


@app.route("/slackbot", methods=["POST"])
def slackbot():
    """
    HTTP endpoint handling slack integrations
    """
    payload = json.loads(request.form["payload"])

    try:
        user_id = payload["user"]["id"]
        button_clicked = payload["actions"][0]["block_id"]
        message_ts = payload["container"]["message_ts"]
        channel_id = payload["channel"]["id"]
        blocks = payload["message"]["blocks"]
    except (KeyError, IndexError):
        # We're missing either a key or index in list.
        return "Bad request", 400

    # User has already voted! By returning a 4xx status code the user will se a
    # ⚠ in their Slack client.
    if votes.get(message_ts, {}).get(user_id, False):
        client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text="Hey all! <@{}> is cheating and tried to vote more than once!".format(
                user_id
            ),
        )

        return "Forbidden", 403

    user_data = client.api_call("users.info", user=user_id)
    user_info = construct_user_info(user_data)

    for i, block in enumerate(blocks):
        if block.get("block_id") != button_clicked:
            continue

        try:
            next_block = blocks[i + 1]
        except (KeyError, IndexError):
            return "Bad request", 400

        # Insert the user who voted.
        next_block["elements"].insert(0, user_info)

        # Update the number of votes.
        vote_word = "vote"
        if len(next_block["elements"]) - 1 > 1:
            vote_word += "s"

        next_block["elements"][-1]["text"] = "{} {}".format(
            len(next_block["elements"]) - 1, vote_word
        )

        break

    blocks = clean_blocks(blocks)

    # Store that the user has voted on this specific message.
    if message_ts not in votes:
        votes[message_ts] = {}

    votes[message_ts][user_id] = True

    result = client.api_call(
        "chat.update", channel=channel_id, ts=message_ts, blocks=blocks
    )

    if not result["ok"]:
        pprint(result)

        return "Internal error", 500

    return "OK", 200


def construct_user_info(user_data):
    """
    Based on all the user data returned from the API for a user, create a
    context block and add appropreate alt tag.
    """
    user_info = {
        "type": "image",
        "image_url": user_data["user"]["profile"]["image_48"],
    }

    profile_fields = ["real_name", "display_name", "first_name"]
    user_fields = ["real_name", "name"]

    # Search relevant profile fields
    for field in profile_fields:
        if user_data["user"]["profile"][field]:
            user_info["alt_text"] = user_data["user"]["profile"][field]

            return user_info

    # Serach relevant user fields
    for field in user_fields:
        if user_data["user"][field]:
            user_info["alt_text"] = user_data["user"][field]

            return user_info

    # We couldn't figure it out...
    user_info["alt_text"] = "Unknown"

    return user_info


def clean_blocks(blocks):
    """
    The message that comes from the action button from Slack has added
    additional information for the context blocks which does not conform with
    the API documentation. To be able to post the message back to Slack we must
    clean all fields that's not allowed.
    """
    for block in blocks:
        for i, element in enumerate(block.get("elements", [])):
            if element["type"] != "image":
                continue

            block["elements"][i] = {
                "type": element["type"],
                "image_url": element["image_url"],
                "alt_text": element["alt_text"],
            }

    return blocks


if __name__ == "__main__":
    app.run()
