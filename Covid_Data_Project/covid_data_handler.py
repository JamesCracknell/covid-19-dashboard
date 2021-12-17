""" Module for handling of covid data from the Public Health England API
for the covid data dashboard.
Part of the 2021 Assessement for ECM1400 at University of Exeter
© 2021 - James Cracknell https://github.com/JamesCracknell
"""

import configparser
import time
import sched
import json
import logging
from uk_covid19 import Cov19API

data_sched = sched.scheduler(time.time, time.sleep) # create scheduler
config = configparser.ConfigParser()
config.read('config_file.ini')

def parse_csv_data(csv_filename: str) -> list[str]:
    """ Fetch covid data from CSV.

    Args:
        csv_filename: Name of the CSV file to fetch data from

    Returns:
        list_of_lines: Data from CSV in a list, each str element being a new line of csv.
    """
    list_of_lines = []
    with open(csv_filename, 'r', encoding="UTF-8") as file:
        # open the file specified by parameter "csv_filename" using read
        for line in file: # loop through file
            list_of_lines.append(line) # append data to list "list_of_lines"
    return list_of_lines

def process_covid_csv_data(covid_csv_data: list[str]) -> tuple[int, int, int]:
    """ Processes data to find 7 day rate, hospitilisations and deaths

    Args:
       covid_csv_data: list containing data from csv as string elements

    Returns:
        last7days_cases: Cumulative cases in last 7 days, excluding empty and
            incomplete cell
        current_hospital_cases: Number of cases currently in hospital
        total_deaths: Total number of deaths
    """
    current_line_count = 0 # Stores the line of the CSV file (now in an array) being searched
    last7days_cases = 0
    current_hospital_cases = 0
    counter = 10
    for item in covid_csv_data:
        current_line = item.split(",") # Splits each line of the file by comma
        if current_hospital_cases == 0 and current_line_count != 0:
            # takes data from first line with data not including the header as it is most up to date
            current_hospital_cases = int(current_line[5])
        if 2 < current_line_count < counter:
            # next 7 items, typically skipping first 2 days as they are incomplete
            if current_line[6] == "":
                #if the cell is empty, i.e, the data has not been updated for the new day yet
                counter +=1 # shifts the data selected one day in advance
            else:
                last7days_cases += int(current_line[6])
                # adds the cases for the day to the weekly sum
        elif (current_line[4] != "") and current_line_count != 0:
            # When the column is not empty (as it is for first 2 weeks) and is not the column title
            total_deaths = int(current_line[4])
            break # no more data is needed, break from for loop
        current_line_count +=1
    return last7days_cases, current_hospital_cases, total_deaths

def covid_API_request(location = "Exeter", location_type = "LTLA") -> None:
    # note this name is necessary to pass tests - ignore Pylint
    """ Interacts with the UK government covid data api to return live data.

    Interacts with https://coronavirus.data.gov.uk/details/developers-guide) to
    fetch the required data for the dashboard: regional 7 day rate,
    national 7 day rate, hospital cases and total deaths. The data
    is then stored in two JSON files -> 'region_covid_data.json' and
    'nation_covid_data.json' to be accessed later.

    Arguments:
        type: the type of area the data is for
    """
    covid_api_data = {}
    if location_type == 'LTLA':
        location = config['covid_defaults']['region']
    elif location_type == 'nation':
        location = config['covid_defaults']['nation']
    api_request = [ # the data filter. Takes parameters passed up.
    'areaType='+location_type,
    'areaName='+location
    ]

    desired_data_region = { # data required for region
    "date": "date",
    "areaName": "areaName",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    }

    desired_data_nation = { # data required for nation
    "date": "date",
    "areaName": "areaName",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    "hospitalCases": "hospitalCases",
    "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    }
    if location_type == 'LTLA': # if region data is needed
        covid_api_data = Cov19API(filters=api_request, structure=desired_data_region)
        covid_api_data = covid_api_data.get_json()
        logging.info('API data called for %s', location)
        with open('region_covid_data.json', 'w', encoding = 'UTF-8') as write_file:
            # open json in write
            json.dump(covid_api_data, write_file)
            logging.info('%s data added to JSON', location_type)
    elif location_type == 'nation': # if national data is needed
        covid_api_data = Cov19API(filters=api_request, structure=desired_data_nation)
        covid_api_data = covid_api_data.get_json()
        logging.info('API data called for %s', location)
        with open("nation_covid_data.json", "w", encoding="UTF-8") as write_file:
            # open json in writeyes
            json.dump(covid_api_data, write_file)
            logging.info('%s data added to JSON', location_type)
    else:
        logging.warning('Warning: No data request occured for location: %s', location_type)
    return covid_api_data

def process_region_request(region = 'Exeter') -> None:
    """ Process regional data from API for frontend

    Arguments:
        region: location of which data is fetched for
    """
    logging.info('Region request processing for %s', region)
    covid_API_request('', 'LTLA') # request data from api
    process_covid_api_data('region')

def process_nation_request(nation = 'England') -> None:
    """ Process national data from API for frontend

    Arguments:
        nation: location of which data is fetched for
    """
    logging.info('Nation request processing for %s', nation)
    covid_API_request('', 'nation') # request data from api
    process_covid_api_data('nation')

def process_covid_api_data(area_type: str) -> tuple:
    """ Function to process data from the covid API.

    Loads data from json files - 'region_covid_data.json' and
    'nation_covid_data.json'. Calculates 7 day infection rate
    based on api data.

    Arguments:
        area_type: the area that the data is being fetched for, determines how data is processed

    Returns:
        seven_day_rate: Cumulative cases in last 7 days, excluding empty and
            incomplete cell
        hospital_cases: current number of hospitalisations
        deaths: total number of deaths in desired region
    """
    seven_day_rate = 0
    no_of_days_ignore = 2 # the number of days of data skipped due to no data uploaded
    no_of_days_counted = 0
    hospital_cases = None
    deaths = None
    # load covid data from json
    if area_type == 'region':
        with open('region_covid_data.json', 'r', encoding='UTF-8') as covid_json:
            covid_data = json.load(covid_json)
    else:
        with open('nation_covid_data.json', 'r', encoding='UTF-8') as covid_json:
            covid_data = json.load(covid_json)

    covid_data_entries = covid_data['data']
    for daily_data in covid_data_entries:
        if daily_data['newCasesBySpecimenDate'] is None: # if the data column is empty
            no_of_days_ignore +=1
            logging.warning("Warning: More case data than expected empty.\
 Data for %s missing. API may not be up to date.", str(daily_data['date']))
            # adds an extra day to skip over to find complete data for 7 day rate
        no_of_days_ignore -= 1
        if area_type == 'nation': # if data is for nation, more is processed
            if deaths is None and daily_data['cumDailyNsoDeathsByDeathDate'] is not None:
                deaths = daily_data['cumDailyNsoDeathsByDeathDate']
            if daily_data['hospitalCases'] is not None and hospital_cases is None:
                hospital_cases = daily_data['hospitalCases']
        if no_of_days_ignore <= 0 and no_of_days_counted <= 6:
            seven_day_rate += daily_data['newCasesBySpecimenDate']
            no_of_days_counted +=1
    if area_type == 'nation': # returns data
        logging.info('Returning API data for: %s', area_type)
        return 'England', seven_day_rate, hospital_cases, deaths
    else:
        logging.info('Returning API data for: %s', area_type)
        return 'Exeter', seven_day_rate

def schedule_covid_updates (update_name: str, update_interval: int) -> None:
    """ Creates scheduler for covid data that calls execute_update

    Create scheduler to update covid data based on user specified time,
    in order to update the covid data that is shown to the user.

    Arguments:
        update_name: the name of the update, specified by user, used as an identifier
        update_interval: the time until the update is requested to occur
    """
    data_sched.enter(update_interval, 1, execute_update, (update_name,))
    logging.info('Schedule created for: %s', update_name)

def execute_update(update_name: str) -> None:
    """ Function executed by scheduler to update covid data on the frontend.

    Refreshes the data in the json files, by querying the api again.

    Arguments:
        update_name: the name of the update, specified by user, used as an identifier
    """
    logging.info('Schedule execure for: %s', update_name)
    process_region_request() # refresh data in region json
    process_nation_request() # refresh data in nation json

def delete_scheduled_data_event(item_name: str) -> None: # needs reworking
    """ Function to delete a scheduled update for data if requested by the user (x is pressed)

    Arguments:
        update_name: the name of the update, specified by user, used as an identifier
    """
    for event in data_sched.queue:
        if event.argument == item_name:
            data_sched.cancel(event)
            logging.info('Schedule deleted for: %s', item_name)
