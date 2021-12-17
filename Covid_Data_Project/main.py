""" Module for integrating a flask web sever with the back end python code.

Part of the 2021 Assessement for ECM1400 at University of Exeter
© 2021 - James Cracknell https://github.com/JamesCracknell """

import sched
import time
import logging
from datetime import datetime

from flask import Flask
from flask import request
from flask import render_template

from covid_data_handler import process_covid_api_data, delete_scheduled_data_event,\
    data_sched, schedule_covid_updates, process_nation_request, process_region_request
from covid_news_handling import create_filtered_list, news_API_request,\
    news_sched, update_news, delete_scheduled_news_event
import time_conversions as convert_time

s = sched.scheduler(time.time, time.sleep) # create scheduler
logging.basicConfig(filename='sys.log', encoding='utf-8', level=logging.DEBUG,\
    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('\n \n \n==== New Instance Started ====')
removed_articles = []
updates = []

app = Flask(__name__)

@app.route('/index')
def index():
    """ Function in charge of loading the flask template and processing the data needed for it

    Uses functions in modules 'covid_data_handler' and 'covid_news_handling' to fetch data for
    flask webpage - passed up in return statement.
    Handles events that occur through request.args.get:
        'notif': news article removal (x clicked)
        'two' and 'update': scheduling data updates
        'update_item': removing scheduled updates
    """
    logging.info('Data called')
    region_data = process_covid_api_data('region')
    nation_data = process_covid_api_data('nation')
    logging.info('News called')
    news_articles_list = create_filtered_list(removed_articles)
    notif = request.args.get('notif') # if x is pressed on news article

    if notif: # processes news article removal
        logging.info('News article with name: %s removed', notif)
        removed_articles.append(notif)
        news_API_request()
        news_articles_list = create_filtered_list(removed_articles)

    if request.args.get('two') and request.args.get('update'):
        # if there is a name and update time
        logging.info('Scheduled update requested')
        schedule_update()

    if request.args.get('update_item'):
        # deletes a scheduled update event, when the x is pressed
        update_name = request.args.get('update_item')
        logging.info('Scheduled update with name %s deleted', update_name)
        delete_scheduled_data_event(update_name) # delete data sched
        delete_scheduled_news_event(update_name) # delete news sched
        remove_item(update_name) # delete front end display

    news_sched.run(blocking=False)
    data_sched.run(blocking=False)
    s.run(blocking=False)

    logging.info('Return statement executed')
    return render_template('index.html',
    title='Covid-19 Dashboard',
    image='covid_icon.png',
    favicon ='static/images/covid_icon.png',
    location=region_data[0],
    local_7day_infections=region_data[1],
    nation_location = nation_data[0],
    national_7day_infections = nation_data[1],
    hospital_cases = nation_data[2],
    deaths_total = nation_data[3],
    news_articles = news_articles_list,
    updates = updates
    )

def schedule_update() -> None:
    """ Schedules updates for data and news.

    Schedules news and data if the user has ticked the box for this.
    Handles repeats if the user has specified this"""
    update_name = request.args.get('two')
    if request.args.get('covid-data'): # if user ticked covid updates box
        update_covid_data = True
    else:
        update_covid_data = False
    if request.args.get('news'): # if user ticked news updates box
        update_news_articles = True
    else:
        update_news_articles = False
    if request.args.get('repeat'): # if user ticked repeat box
        repeat = True
    else:
        repeat = False
    if update_covid_data or update_news_articles:
        # if the update affects either covid data or news
        name_unique = True
        for update in updates:
            if update['title'] == update_name:
                # update name is not unique
                name_unique = False
        if name_unique is True:
            # if update name is already in list of updates it is invalid
            time_of_update = request.args.get('update') # gets update time
            current_time = datetime.now().strftime("%H:%M:%S") # gets current time
            # append to updates, an array storing how updates are displayed on dashboard
            # format message
            update_message = ('Update scheduled for: ' + time_of_update+'.')
            if update_news_articles:
                update_message = update_message + " News articles will update."
            if update_covid_data:
                update_message = update_message + " Covid data will update."
            if repeat:
                update_message = update_message + " Update will repeat."
            else:
                update_message = update_message + " Update will not repeat."
            updates.append({'title': update_name,
            'content': update_message})
            # convert both times to seconds
            time_of_update = convert_time.hhmm_to_seconds(time_of_update)
            current_time = convert_time.hhmmss_to_seconds(current_time)
            if time_of_update > current_time: # if update is in the future
                time_till_update = time_of_update - current_time
            else: # update time is in the 'past' (so is scheduled for tomorrow)
                time_till_update = (86400 - current_time) + time_of_update
            if update_news_articles:
                # schedule news updates through update_news function
                update_news(update_name, time_till_update)
            if update_covid_data:
                # schedule covid updates through schedule_covid_updates function
                schedule_covid_updates(update_name, time_till_update)
            # 'overarching scheduler' controls deleting of update, or creating repeat
            s.enter(time_till_update, 1, update_occured, (update_name, repeat,
            update_news_articles, update_covid_data, ((86400 - current_time) + time_of_update)))
        else:
            logging.warning('Warning: Name is not unique. There is already an \
            update with name: %s', update_name)
    else:
        logging.warning('Warning: Neither data or news will be updated. Update request ignored.')

def remove_item(update_name: str) -> None:
    """ Removes update from updates, so it is no longer displayed on front end

    Arguments:
        update_name: name of update to be removed
        """
    for update in updates:
        if update['title'] == update_name:
            updates.remove(update)
            logging.info('Update removed from front end')

def update_occured(update_name: str, repeat: bool, update_news_articles:
    bool, update_covid_data: bool, future_update_time: int) -> None:
    """ Deletes front end update display, or repeats scheduler.

    Arguments:
        update_name: Identifier for the update, specified by the user
        repeat: True if scheduled update is to be repeated
        update_news_articles: True if news articles are to be updated
        update_covid_data: True if data is to updates
        future_update_time: Time next update occurs
    """
    for update in updates:
        if update['title'] == update_name:
            # item is that which was scheduled
            if repeat is False: # remove the item
                remove_item(update_name)
                logging.info('Non repeating update %s removed', update_name)
            else: # recreate schedules to allow for repeat
                logging.info('Update %s is repeating', update_name)
                s.enter(future_update_time, 1, update_occured, (update_name, repeat,
                    update_news_articles, update_covid_data, future_update_time))
                if update_news_articles:
                    # schedule news updates through update_news function
                    logging.info('News update rescheduled')
                    update_news(update_name, future_update_time)
                if update_covid_data:
                    # schedule covid updates through schedule_covid_updates function
                    logging.info('Data update rescheduled')
                    schedule_covid_updates(update_name, future_update_time)

if __name__ == '__main__':
    # run program and fetch initial data
    news_API_request()
    process_region_request()
    process_nation_request()
    app.run()
