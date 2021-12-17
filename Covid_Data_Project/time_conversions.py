""" Module to convert time into other formats

From ECM1400 Alarm Clock - Matt Collison"""
import logging

def minutes_to_seconds(minutes: str) -> int:
    """ Function to convert minutes to seconds"""
    return int(minutes)*60

def hours_to_minutes(hours: str) -> int:
    """ Function to convert hours to minutes"""
    return int(hours)*60

def hhmm_to_seconds(hhmm: str) -> int:
    """ Function to convert hh:mmformat into seconds"""
    if len(hhmm.split(':')) != 2:
        logging.warning('Incorrect format. Argument must be formatted as HH:MM')
        return None
    return minutes_to_seconds(hours_to_minutes(hhmm.split(':')[0])) + \
        minutes_to_seconds(hhmm.split(':')[1])

def hhmmss_to_seconds(hhmmss: str) -> int:
    """ Converts hh:mm:ss format into seconds"""
    if len(hhmmss.split(':')) != 3:
        logging.warning('Incorrect format. Argument must be formatted as HH:MM:SS')
        return None
    return minutes_to_seconds(hours_to_minutes(hhmmss.split(':')[0])) + \
        minutes_to_seconds(hhmmss.split(':')[1]) + int(hhmmss.split(':')[2])
