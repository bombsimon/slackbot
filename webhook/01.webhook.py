#!/usr/bin/env python3
"""
This is a webhook integration for Slack bots. The interactive component
configuration points to this server.
"""

import os
import json

from flask import Flask, request
from slackclient import SlackClient

app = Flask(__name__)
client = SlackClient(os.environ.get("SLACK_API_TOKEN"))


@app.route("/slackbot", methods=["POST"])
def slackbot():
    """
    HTTP endpoint handling slack integrations
    """
    payload = json.loads(request.form["payload"])

    try:
        button_clicked = payload["actions"][0]["block_id"]
        message_ts = payload["container"]["message_ts"]
        channel_id = payload["channel"]["id"]
        blocks = payload["message"]["blocks"]
    except (KeyError, IndexError):
        # We're missing either a key or index in list.
        return "Bad request", 400

    for i, block in enumerate(blocks):
        if block.get("block_id") != button_clicked:
            continue

        try:
            next_block = blocks[i + 1]
            next_block_text = next_block["elements"][0].get("text")
        except (KeyError, IndexError):
            return "Bad request", 400

        # If there's not thumbsup yet, this is the first vote.
        if ":thumbsup:" not in next_block_text:
            next_block_text = ""

        next_block_text += ":thumbsup:"
        next_block["elements"][0]["text"] = next_block_text

        break

    client.api_call(
        "chat.update",
        channel=channel_id,
        ts=message_ts,
        blocks=payload.get("message").get("blocks"),
    )

    return "OK", 200
