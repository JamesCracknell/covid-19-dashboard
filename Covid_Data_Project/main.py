import covid_data_handler as data_handler
import covid_news_handling as news_hander

from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

@app.route('/index')

def index():
    region_data = data_handler.process_region_request()
    nation_data = data_handler.process_nation_request()
    news_articles_dict = news_hander.process_news_articles()
    return render_template('index.html',
    title='Covid-19 Dashboard',
    image='covid_icon.png',
    location=region_data[0],
    local_7day_infections=region_data[1],
    nation_location = nation_data[0],
    national_7day_infections = nation_data[1],
    hospital_cases = nation_data[2],
    deaths_total = nation_data[3],
    news_articles = news_articles_dict
    )

if __name__ == '__main__':
    app.run()

