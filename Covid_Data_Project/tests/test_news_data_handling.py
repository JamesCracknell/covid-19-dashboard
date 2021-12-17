from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import create_filtered_list

def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news('test')

def test_create_filtered_list():
    news_API_request()
    data = create_filtered_list({})
    assert isinstance(data, list)
    assert data != []

