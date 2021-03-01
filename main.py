import os
from dataclasses import InitVar, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas
from dacite import from_dict
from matplotlib import pyplot
from typing import Any, Dict, List, Optional

import yaml
from slack_sdk import WebClient


@dataclass
class ScraperConfig():
    slack_channel_id: str
    start_date: InitVar[date]
    reaction_prefix: str
    slack_token: Optional[str] = None
    slack_token_env_variable: InitVar[str] = None

    def __post_init__(self, start_date: date, slack_token_env_variable: Optional[str]):
        self.start_datetime = datetime.fromordinal(start_date.toordinal())
        if not self.slack_token:
            assert slack_token_env_variable, "Either `slack_token` or `slack_token_env_variable` must be set"
            self.slack_token = os.getenv(slack_token_env_variable)


def get_messages(config: ScraperConfig) -> List[Dict[str, Any]]:
    slack_client = WebClient(token=config.slack_token)

    messages = []
    cursor = None
    while True:
        response = slack_client.conversations_history(channel=config.slack_channel_id, oldest=config.start_datetime.timestamp(), cursor=cursor)
        messages += response.data["messages"]
        if not response.data["has_more"]:
            break
        cursor = response.data["response_metadata"]["next_cursor"]
    return messages


def clean_messages(messages: List[Dict[str, Any]], config: ScraperConfig):
    def _message_has_reaction(message: Dict[str, Any], reaction: str) -> bool:
        return any(rc for rc in message.get("reactions", []) if rc["name"] == reaction)

    # Exclude explicitely ignored messages
    messages = [message for message in messages if not _message_has_reaction(message, f"{config.reaction_prefix}_ignore")]
    # Exclude anything that is not a direct message to the channel, e.g. "thread_broadcast", "channel_join"...
    messages = [message for message in messages if "subtype" not in message]
    # Sort messages by time stamp
    messages = sorted(messages, key=lambda message: message["ts"])
    return messages


def analyze_messages(messages: List[Dict[str, Any]], config: ScraperConfig):
    def _messages_by_week(messages: List[Dict[str, Any]], start_datetime: datetime) -> Dict[str, List[Dict[str, Any]]]:
        result = {}
        week_start = start_datetime
        while True:
            week_end = week_start + timedelta(days=7)
            week_messages = [message for message in messages if
                             week_start.timestamp() <= float(message["ts"]) < week_end.timestamp()]
            result[week_start.strftime("%y-%m-%d")] = week_messages
            week_start = week_end
            if week_start > datetime.today():
                break

        return result

    def _messages_by_label(messages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        result = {}
        for message in messages:
            for reaction in message.get("reactions", []):
                reaction_name = reaction["name"]
                if not reaction_name.startswith(f"{config.reaction_prefix}_"):
                    continue

                if reaction_name not in result:
                    result[reaction_name] = []
                result[reaction_name].append(message)

        return result

    # Display a graph of the number of support requests per week
    messages_by_week = _messages_by_week(messages, config.start_datetime)
    number_of_messages_by_week = pandas.Series({week: len(week_messages) for week, week_messages in messages_by_week.items()})
    number_of_messages_by_week.plot.bar()
    pyplot.show()

    # Display a graph of the distribution of support requests
    messages_by_label = _messages_by_label(messages)
    number_of_messages_by_label = pandas.Series({label: len(label_messages) for label, label_messages in messages_by_label.items()})
    number_of_messages_by_label = number_of_messages_by_label.sort_values()
    number_of_messages_by_label.plot.pie()
    pyplot.show()


def main():
    config_dict = yaml.safe_load(Path("scraper_config.yaml").read_text())
    config = from_dict(data_class=ScraperConfig, data=config_dict)

    messages = get_messages(config)
    messages = clean_messages(messages, config)
    analyze_messages(messages, config)


if __name__ == "__main__":
    main()