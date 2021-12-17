# Covid Data Dashboard

## Introduction

A covid data dashboard hosted locally to provide information and news about the pandemic.

Displays local and nation data: 7 day infection rates, national current hospitalisations and national total deaths. By default the local region is Exeter and nation is England.

Also displays news articles (by defualt four at a time) that contain search terms 'Covid', 'Covid-19' or 'coronavirus'. These can be removed (pressing x) to load more and URLs can be followd to find out more.

Users can schedule updates to the program, they can choose a time to update and if it updates news articles, data or both. They can also set it to repeat and name the update.
---

## Installation

Download the repo from github: https://github.com/JamesCracknell/covid-19-dashboard

Requirements:
python 3.9.7
```python
pip install uk_covid19
pip install configparser
pip install sched
pip install logging
pip install requests
pip install flask
```
For testing: 
```pip install pytest
```


## Usage

Run main.py from python terminal

Navigate via a web browser to http://127.0.0.1:5000/index to enter the dashboard.

### How to Interact With the Dashboard
The program is entirely interacted with via the dashboard. No other input is necessary.

#### Schedule Updates

Enter the time the update should occur in the correct time box. Note events can be scheduled for earlier times in the next day.
Select the 'repeat update' box if the update should repeat every 24 hours.
Select the 'Update Covid data' box if covid data should be updated.
Select the 'Update news articles' box if news stories should be updated.

Once you are happy with your selections, press submit and the scheduled update will be shown. Note, you must choose to update at least one of the datas and must choose a name that is unique to other existing scheduled updates.

#### Remove Updates

Updates can be removed so they are not executed by pressing the x on them.

#### Remove News Articles

News articles can be removed by pressing the x on them. This allows a new article to take its place.

### Config file
Values in the config file can be changed to create a more personalised dashboard, such as changing the region in which data is displayed. Ensure cahnges are valid as this may otherwise cause errors.

## Testing

Tests are included to ensure project functionality. To test:

Navigate to the folder containing this project using a terminal
Run pytest (enter command: pytest)
## Developer Details
James Cracknell
ECM1400 University of Exeter
Github: https://github.com/JamesCracknell

Flask Template and Project Specification:
Matt Collison - Lecturer University of Exeter

With thanks to Hugo Barbosa - Lecturer University of Exeter

## License
[MIT](https://choosealicense.com/licenses/mit/)
