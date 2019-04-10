#!/usr/bin/env python3
"""
Slack bot using the Slack API and python SlackClient
"""

import os
import time
import sys

from slackclient import SlackClient


def main():
    """
    main is the main program that will run when the script is executed.
    """
    client = SlackClient(os.environ.get("SLACK_API_TOKEN"))

    if not client.rtm_connect(with_team_state=False):
        print("could not connect to slack")
        sys.exit(1)

    print("connected to network!")

    while True:
        for data in client.rtm_read():
            print(data)

        time.sleep(1)


if __name__ == "__main__":
    main()
