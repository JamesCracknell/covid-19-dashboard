""" Module for handling of covid data from the Public Health England API.
Part of the 2021 Assessement for ECM1400 at University of Exeter
- James Cracknell
"""

from uk_covid19 import Cov19API

def parse_csv_data(csv_filename: str) -> list:
    """ Function that takes file name in argument 'csv_filename' and returns a list of string for the lines in the file of that name.
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
    for item in covid_csv_data:
        current_line = item.split(",") # Splits each line of the file by comma
        if current_line_count == 1: # takes data from first line, most up to date
            current_hospital_cases = int(current_line[5])
        elif 2 < current_line_count < 10:
            # next 7 items, skipping first 2 days as they are incomplete
            last7days_cases += int(current_line[6])
        elif (current_line[4] != "") and current_line_count != 0:
            # When the column is not empty (as it is for first 2 weeks) and is not the column title
            total_deaths = int(current_line[4])
            break # no more data is needed, break from for
        current_line_count +=1
    return last7days_cases, current_hospital_cases, total_deaths

def covid_api_request(location = "Exeter", location_type = "ltla") -> dict:

    return
