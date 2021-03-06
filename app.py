from flask import Flask, render_template, url_for,request, redirect
from newspaper import fulltext, Article
from datetime import date, timedelta
import requests
import pandas as pd
from dateutil import parser
import pandas as pd
import numpy as np
import time
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz
from selectorlib import Extractor
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException, UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from custom_scripts import *
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib


app = Flask(__name__)

#date will get the proper csv file.
tz_NY = pytz.timezone('America/New_York')
datetime_NY = datetime.now(tz_NY)
todays_date = datetime_NY.strftime("%Y-%m-%d")

@app.route('/')
def home():
	df = pd.read_csv(f'daily_predictions/apple/{todays_date}.csv', index_col = 0)
	article_count = df['total_articles'][0]
	return render_template('home.html', article_count=article_count)

@app.route('/results/')
def results():
    # #date will get the proper csv file.
	# tz_NY = pytz.timezone('America/New_York')
	# datetime_NY = datetime.now(tz_NY)
	# todays_date = datetime_NY.strftime("%Y-%m-%d")

	df = pd.read_csv(f'daily_predictions/apple/{todays_date}.csv', index_col = 0)
	current_prediction = df['prediction'][0]

	if current_prediction == 1:
		probability = df['probability_up'][0]
		arrow = "../static/green_arrow.svg"
	else:
		probability = df['probability_down'][0]
		arrow = "../static/red_arrow.svg"

	updated = df['updated'][0]

	return render_template('results.html', arrow=arrow, probability=probability, updated=updated)



if __name__ == "__main__":
    app.run()
