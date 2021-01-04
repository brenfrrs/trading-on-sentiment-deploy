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
import datetime
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


today = date.today()
todays_date = today.strftime("%Y-%m-%d")

df = pd.read_csv(f'daily_predictions/apple/{todays_date}.csv', index_col = 0)
current_prediction = df['prediction'][0]

if current_prediction == 1:
    probability = df['probability_up'][0]
else:
    probability = df['probability_down'][0]

updated = df['updated'][0]

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/results/')
def results():
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

if __name__ == '__main__':
	app.run(debug=True)
