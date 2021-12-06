""" Module for handling of news articles from the News API
for the covid data dashboard.
Part of the 2021 Assessement for ECM1400 at University of Exeter
- James Cracknell
"""

import requests

def news_api_request(covid_terms = "Covid COVID-19 coronavirus"):
    base_url = "https://newsapi.org/v2/top-headlines?" # should it be top headlines or evrything?
    api_key = "bac7f5dd24084f8bb8a13fddd24a7bac"
    for i in covid_terms.split(' '):
        news_return = requests.get(base_url+'q='+i+"&apiKey="+api_key)
        return news_return.json()

def get_source_language(language = 'en'):
    """ Function to filter news sources collected from the news api based on their language
    Uses the parameter "language" with a default value of "en" for english.
    Returns a list with the names of all news sources matching the specified language
    """
    base_url = "https://newsapi.org/v2/top-headlines/sources?language="
    api_key = "bac7f5dd24084f8bb8a13fddd24a7bac"
    filtered_source_list = []
    sources_return = requests.get(base_url+language+"&apiKey="+api_key)
    sources_return = sources_return.json()
    sources = sources_return['sources']
    for source in sources:
        filtered_source_list.append(source['name'])
    return filtered_source_list

def process_news_articles():
    """ Function to process news sources collected from the news api
    to be displayed onto the dashboard"""
    news_source_list = get_source_language()
    news_dict = news_api_request()
    list_of_articles = []
    articles = news_dict['articles']
    for article in articles:
        if article['source']['name'] in news_source_list: # if the news article is in english
            list_of_articles.append({'title': article['title'], 'content': 'Publisher: '  + str(article['source']['name']) + "  |  " + article['description'] + "  |  " + article['url']})
    return list_of_articles
process_news_articles()
# title + author + company + description + link
# make sure english, top or what
# how many articles
# delete articles


# merge dictionaries
# look for duplicated news
# scheduler
# remove data
