#!/usr/bin/python3.6

import boto3
import json
from slackclient import SlackClient
from datetime import date, datetime, timezone


slack_token = '<your_slack_token>'
sc = SlackClient(slack_token)
current_date = date.today()
today = current_date.strftime("%Y/%m/%d")

def _slackNotification(message):
    sc.api_call(
    "chat.postMessage",
        channel = "#your_channel",
        text = "*" + today + " - Upcoming events of " + aws_env + ": *\n" + str(message),
        user = "AWS Health Event"
    )

def _checkResponse(response):
    if response:
        pass
    else:
        msg = ">There is no upcoming event today"
        _slackNotification(msg)


def _getUpcomingEvents(aws_environment, aws_profile):
    global aws_env
    global event_description
    aws_env = aws_environment
    noir_monitor = boto3.session.Session(profile_name=aws_profile)
    health_check = noir_monitor.client('health', region_name='us-east-1')
    
    # Get all upcoming AWS events
    json_resps = health_check.describe_events(
        filter={
            'eventStatusCodes': [
                "upcoming",
            ]
        }
    ) 

    # Check response is null or not
    _checkResponse(json_resps["events"])

    # Parse JSON response
    for json_resp in json_resps["events"]:
        detail_rsps = health_check.describe_event_details(
            eventArns=[
                json_resp['arn'],
            ],
            locale='en'
        )

        # Get event description
        for detail_rsp in detail_rsps['successfulSet']:
            event_description = detail_rsp['eventDescription']['latestDescription']

        # Message content
        event_message = ">Service: " + json_resp['service'] + "\n"\
            + ">Event Type: " + json_resp['eventTypeCode'] + "\n"\
            + ">Start time: " + str(json_resp['startTime'].date()) + "\n"\
            + ">Region: " + json_resp['region']  + "\n"\
            + ">Description: " + "```" + str(event_description) + "```"

        _slackNotification(event_message)


# Declare main execution
def main():
    _getUpcomingEvents("<your_env>", "your_aws_profile")
main()