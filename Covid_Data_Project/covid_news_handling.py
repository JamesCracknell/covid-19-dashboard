""" Module for handling of news articles from the News API
for the covid data dashboard.
Part of the 2021 Assessement for ECM1400 at University of Exeter
© 2021 - James Cracknell https://github.com/JamesCracknell
"""

import configparser
import time
import sched
import json
import logging
import requests
from flask import Markup

config = configparser.ConfigParser()
config.read('config_file.ini')

news_sched = sched.scheduler(time.time, time.sleep) # create scheduler

def news_API_request(covid_terms = 'Covid COVID-19 coronavirus') -> None:
    """ Queries news api to fetch news articles to display.

    Queries https://newsapi.org/
    """
    logging.info('News API called')
    base_url = "https://newsapi.org/v2/top-headlines?"
    api_key = config['news_api']['API_key']
    language = config['news_api']['language']
    covid_terms = config['news_api']['search_terms']
    news_return_list = []
    for i in covid_terms.split(' '): # queries api with "Covid", then "COVID-19", then "coronavirus"
        # combined to form an API request
        # api request
        news_return = requests.get(base_url+'q='+i+"&apiKey="+api_key+'&language='+language)
        # only gets english articles
        news_return = news_return.json()
        if not news_return_list: # if it is the first query
            news_return_list = news_return
        else:
            for item in news_return:
                if item not in news_return_list: # if the news article is not a duplicate
                    news_return_list.append(item)
    process_news_articles(news_return_list)
    return news_return_list

def process_news_articles(news_return) -> json:
    """ Function to process data into a json file 'news_articles.json'

    Loads data into a json to be stored or used later"

    Arguments:
        news_return: List of news articles as dictionaries
    """
    articles = news_return['articles']
    with open("news_articles.json", "w", encoding="UTF-8") as write_file:
        json.dump(articles, write_file)
    logging.info('News data added to JSON')

def create_filtered_list(removed_articles: list[dict]) -> list[dict]:
    """ Formats news articles to be displayed on dashboard

    Processes JSON data into the correct format to be presented on the
    news tab of the dashboard
    Selects first four articles to be displayed on front end dashboard.
    Ensures articles to display have not already been removed by displaying it against
    the 'removed_articles' list.

    Arguments:
        removed_articles: list of articles that have been removed by the user,
            so should not be displayed again

    Returns:
        filtered_list: list of dictionaries storing formatted articles
    """
    filtered_list = []
    current_location = 0
    with open('news_articles.json', 'r', encoding='UTF-8') as news_json:
        # open the json file
        news_return = json.load(news_json)
        list_of_articles = []
        for article in news_return:
            # format article for front end display including html markup to embed urls
            list_of_articles.append({'title': Markup('<a href='+article["url"]+'>'
            +article["title"]+'</a>'), 'content': article['description']})
    # filter articles into list of four
    while len(filtered_list) <= int(config['news_api']['number_of_articles']) and list_of_articles:
        try:
            if list_of_articles[current_location]['title'] not in removed_articles:
                filtered_list.append(list_of_articles[current_location])
            else:
                logging.info('News Article %s not added as removed by user',\
                list_of_articles[current_location]['title'])
        except IndexError:
            # less than specified articles in list
            logging.warning('Warning: Insufficient articles available to display')
            break
        current_location+=1
    return filtered_list

def update_news(update_name: str, update_interval:int = 86399) -> None:
    """ Function to schedule news updates.

    Uses the sched module to schedule updates using the interval provided by the user.

    Arguments:
        update_interval: time until update occurs
        update_name: the name of the update, specified by user, used as an identifier"""
    logging.info("News scheduler: %s, called", update_name)
    news_sched.enter(update_interval, 1, update_news_process, (update_name,))

def update_news_process(update_name: str) -> None:
    """ Runs when the scheduled update executes, re-queries the API to update JSON files.
    Removes item from the dictionary of updates.

    Arguments:
        update_name: the name of the update, specified by user, used as an identifier
    """
    logging.info("News scheduler: %s, running", update_name)
    news_API_request()


def delete_scheduled_news_event(item_name: str) -> None: # needs reworking
    """ Deletes scheduled update for news if requested by the user (x is pressed)

    Arguments:
        item_name: the name of the sched to delete
    """
    logging.info('News scheduler delete called for: %s', item_name)
    for event in news_sched.queue:
        if event.argument == item_name:
            news_sched.cancel(event)
