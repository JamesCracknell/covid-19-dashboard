""" Module for handling of covid data from the Public Health England API
for the covid data dashboard.
Part of the 2021 Assessement for ECM1400 at University of Exeter
- James Cracknell
"""

from uk_covid19 import Cov19API
import sched
import time

def parse_csv_data(csv_filename: str) -> list:
    """ Function that takes file name in argument 'csv_filename' and returns
    a list of string for the lines in the file of that name.
    """
    list_of_lines = []
    with open(csv_filename, 'r', encoding="UTF-8") as file:
        # open the file specified by parameter "csv_filename" using read
        for line in file: # loop through file
            list_of_lines.append(line) # append data to list "list_of_lines"
    return list_of_lines

def process_covid_csv_data(covid_csv_data: list) -> int:
    """ Function that takes a list of data from the argument "covid_csv_data".
    It returns: number of cases in last 7 days, current hospital cases and
    cumulative number of deaths"""
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

def covid_api_request(location = "Exeter", location_type = "ltla") -> dict:
    """ Function to interact with the UK government covid data api
    (https://coronavirus.data.gov.uk/details/developers-guide) and
    return the required data for the dashboard: regional 7 day rate,
    national 7 day rate, hospital cases and total deaths."""
    api_request = [ # the data filter. Takes parameters passed up.
    'areaType='+location_type,
    'areaName='+location
    ]

    desired_data_region = {
    "date": "date",
    "areaName": "areaName",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    }

    desired_data_nation = {
    "date": "date",
    "areaName": "areaName",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    "hospitalCases": "hospitalCases",
    "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate",
    }
    if location_type == "ltla": # if region data is needed
        api = Cov19API(filters=api_request, structure=desired_data_region)
    elif location_type == "nation": # if national data is needed
        api = Cov19API(filters=api_request, structure=desired_data_nation)
    else:
        return None
        # raise calling error here
    api = api.get_json()
    return api

def process_region_request(region = 'Exeter'):
    """ Function to process regional data from the UK government API
    in order to be sent through flask to the front end website"""
    covid_data = covid_api_request() # request data from api
    seven_day_rate = process_covid_api_data(covid_data, 'region')[0]
    return region, seven_day_rate


def process_nation_request(nation = 'England'):
    """ Function to process national data from the UK government API
    in order to be sent through flask to the front end website"""
    covid_data = covid_api_request(nation, 'nation') # request data from api
    seven_day_rate, hospitalisations, deaths = process_covid_api_data(covid_data, 'nation')
    return nation, seven_day_rate, hospitalisations, deaths

def process_covid_api_data(covid_data: dict, area_type) -> int:
    """ Function to calculate 7 day infection rate based on api data in the
    "covid_data" parameter."""
    seven_day_rate = 0
    no_of_days_ignore = 1 # the number of days of data skipped due to being incomplete
    no_of_days_counted = 0
    hospital_cases = None
    deaths = None
    covid_data_entries = covid_data['data']
    for daily_data in covid_data_entries:
        if daily_data['newCasesBySpecimenDate'] == 0: # if the data column is empty
            no_of_days_ignore +=1
            # adds an extra day to skip over to find complete data for 7 day rate
        no_of_days_ignore -= 1
        if area_type == 'nation':
            if deaths is None:
                deaths = daily_data['cumDeaths28DaysByDeathDate']
            if daily_data['hospitalCases'] is not None and hospital_cases is None:
                hospital_cases = daily_data['hospitalCases']
        if no_of_days_ignore <= 0 and no_of_days_counted <= 7:
            seven_day_rate += daily_data['newCasesBySpecimenDate']
            no_of_days_counted +=1
    return seven_day_rate, hospital_cases, deaths

# def schedule_covid_updates(update_interval, update_name):
#     s = sched.scheduler(time.time, time.sleep)
#     e1 = s.enter(update_interval, ?, )

    
