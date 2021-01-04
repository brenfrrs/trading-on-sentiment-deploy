#!/bin/zsh

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
import os
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
import sys

today = date.today()
todays_date = today.strftime("%Y-%m-%d")

co = ['apple']

counter = 0
while True:

    if counter >= 1:
        counter += 1
        print('sleeping for 30 minutes before scraping again.')
        time.sleep(1800) #sleep for 30 minutes after getting data for all companies in `co` list.
    else:
        counter += 1
        pass

    for comp in co:
        class Collect:
            '''
            This class handles all of the scraping and data collection activities.

            To instantiate: call `Collect('apple',time_period=<time_period>)`

            Possible time periods are: 12 and 2 (hrs)
            time_period=2 -- will scrape every article published in the last two hours.
            time_period=12 -- will scrape evert article published in the last 12 hours.

            By default, the time period defaults to 24 hours.

            '''

            def __init__(self, company, ticker='#', time_period='#tp_24'):
                self.company = company
                self.time_period = time_period
                self.ticker = ticker

                if time_period == 12:
                    self.time_period = '#tp_12'
                elif time_period == 2:
                    self.time_period = '#tp_2'
                elif time_period == 1:
                    self.time_period = '#tp_1'
                else:
                    pass

                #some logic so the user does not need to enter exact company names or know the ticker.
                formed_query = self.company.lower()
                stocks = {
                "the walt disney company":"DIS",
                "walmart inc.":"WMT",
                "dow inc.":"DOW",
                "salesforce, inc.":"CRM",
                "nike, inc.":"NKE",
                "the home depot, inc.":"HD",
                "visa, inc.":"V",
                "microsoft corporation":"MSFT",
                "3m company":"MMM",
                "cisco systems, inc.":"CSCO",
                "coke":"KO",
                "the coca-cola company":"KO",
                "apple inc.":"AAPL",
                "honeywell international inc.":"HON",
                "j&j":"JNJ",
                "johnson and johnson":"JNJ",
                "the travelers companies, inc.":"TRV",
                "the proctor and gamble company":"PG",
                "chevron corporation":"CVX",
                "verizon communications inc.":"VZ",
                "caterpillar inc.":"CAT",
                "the boeing company":"BA",
                "amgen inc.":"AMGN",
                "ibm":"IBM",
                "international business machines corporation":"IBM",
                "american express company":"AXP",
                "jpmorgan chase & co.":"JPM",
                "walgreens boots alliance, inc.":"WBA",
                "mcdonalds corporation":"MCD",
                "merck & co., inc.": "MRK",
                "the goldman sachs group, inc.":"GS",
                "unitedhealth group incorporated":"UNH",
                "intel corporation":"INTC"
                }

                try:
                    result = {key:value for (key,value) in stocks.items() if formed_query in key}
                    self.ticker = str(list(result.values())[0])
                except IndexError as e:
                    raise type(e)('That is not a valid name for a stock in the DOW!')



            def fetch_articles(self):
                '''
                Scrapes newslookup.com for a given stock and time interval.

                Company name and time interval declared during class instantiation, by default it will
                scrape all articles published in the last 24 hours.

                '''
                now = datetime.now()
                todays_dt = now.strftime("%Y-%m-%d@%I:%M:%S%p") #used for file naming.
                chrome_options = webdriver.ChromeOptions()
                chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--remote-debugging-port=9222')
                driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
                time.sleep(2)
                print('navigating to newslookup..')
                news_look = "https://www.newslookup.com"
                time.sleep(1)
                driver.get(news_look)
                time.sleep(3)

                driver.find_element_by_css_selector('#lookup').send_keys(self.company)

                #search button
                driver.find_element_by_css_selector('#form-group > div > span > button').click()

                #time period
                driver.find_element_by_css_selector('#timeperiod').click()

                #past 24 hours--------------------------------------------------
                driver.find_element_by_css_selector(self.time_period).click()

                #scroll down
                for loaded_page in range(10000):
                    try:
                        print(f'{loaded_page}')
                        time.sleep(1.50)
                        driver.find_element_by_tag_name('body').send_keys(Keys.END)
                        time.sleep(1.50)
                        driver.find_element_by_css_selector('#more-btn').click()
                    except ElementNotInteractableException:
                        print('no more pages')
                        break
                    except (TimeoutException, ElementClickInterceptedException) as e: #extraneous errors usually fixed after retry.
                        continue
                    except NoSuchElementException:
                        break

                results_list = [] #list of all the links and associated publish dates.

                raw_html = driver.page_source
                extracted_text = Extractor.from_yaml_string("""
                card:
                    css: 'div#results'
                    xpath: null
                    type: Text
                    children:
                        title:
                            css: 'a.title:nth-of-type(n+4)'
                            xpath: null
                            multiple: true
                            type: Link
                        date:
                            css: span.stime
                            xpath: null
                            multiple: true
                            type: Text

                 """)
                raw_data = extracted_text.extract(raw_html)

                #combines the links with their appropriate publish dates (dates in UTC format at this point.)
                results = list(zip(raw_data['card']['title'],raw_data['card']['date'][1:]))
                for entry in results:
                    results_list.append(entry)

                final_df = pd.DataFrame(columns= ['update', 'date', 'source', 'author', 'fulltext', 'summary'])


                counter = 0
                for link, date in results_list:
                    try:
                        article= Article(link)
                        article.download()
                        article.parse()
                        text = article.text
                        published = article.publish_date
                        auth = article.authors
                        source = link
                        summ = article.summary
                        titl = article.title
                        final_df = final_df.append({'update':published, 'date':date, 'source':link, 'author':auth, 'fulltext':text, 'summary':summ, 'title':titl}, ignore_index=True)
                        counter += 1
                        final_df = final_df.drop_duplicates(subset='fulltext')
                        print(f"{final_df.shape[0]} unique articles, {counter - final_df.shape[0]} duplicates removed.")
                    except:
                        continue
                final_df = final_df.drop_duplicates(subset='fulltext')
                final_df.drop(columns=['summary', 'author', 'update'], inplace=True)
                final_df.dropna(subset=['fulltext'], inplace=True)
                driver.close()

                #save to results to csv (but there are duplicate entries that need removal)
                filepath = 'daily_data/{}/full_results.csv'.format(self.company)
                with open(filepath, 'a') as f:
                    final_df.to_csv(f, header=False) #If ran for the first time, needs to be set to true on the first run then back to false for all subsequent loops.
                print(f"{final_df.shape[0]} results added to {filepath}")

                #remove duplicates from the file.
                drop_repeats = pd.read_csv(filepath, index_col=0)
                num_repeats = drop_repeats.fulltext.duplicated().sum()
                drop_repeats.drop_duplicates(subset=['fulltext'], inplace=True)
                drop_repeats.to_csv(filepath)
                print(f"{final_df.shape[0] - num_repeats} new articles added.")


                return final_df


            def current_info(self):
                '''
                Grabs the current stock information from yahoo finance.
                '''
                import yahoo_fin.stock_info as si
                from datetime import date

                tick = self.ticker
                table = si.get_quote_table(tick)
                today = date.today()

                open_price = table['Open']
                current_volume = table['Volume']
                current_high = table["Day's Range"].split('-')[1].lstrip()
                current_low = table["Day's Range"].split('-')[0].rstrip()
                today_date = today.strftime('%Y-%m-%d')

                row_data = {'open':open_price,
                    'volume': current_volume,
                    'high': current_high,
                    'low':current_low,
                    'date':today_date}

                df = pd.DataFrame.from_dict(row_data, orient='index').T

                #convert date column to datetime series
                datetime_series = pd.to_datetime(df.date)

                #convert the series to a DateTime index.
                datetime_index = pd.DatetimeIndex(datetime_series.values)

                #set as the index of the df.
                df = df.set_index(datetime_index)

                #drop original date column
                df.drop(columns=['date'], inplace=True)
                return df

        #company name provided as arguments when ran from CLI
        company = comp.lower()

        query = Collect(company)
        results = query.fetch_articles()

        def vader_sent(company_name):
            filepath = 'daily_data/{}/full_results.csv'.format(company_name)
            results = pd.read_csv(filepath, index_col=0)
            results.dropna(inplace=True)

            results['sentiment'] = results['fulltext'].apply(sentiment_analyzer_scores) #predict the sentiment of each article
            sentiment_dummies = pd.get_dummies(results['sentiment'], prefix='sent') #dummy the sentiment values
            results = pd.concat([results, sentiment_dummies], axis=1)
            results.drop(columns='sentiment', inplace=True) #drop original categorical value

            res = process_frame(results) #manage the conversions of the datetimes from UTC to Eastern. Can be found in custom_scripts.py.

            res.fulltext = res.fulltext.apply(clean_text)
            res['tokens'] = res['fulltext'].apply(toke)

            pre_process = [remove_stopwords, lemmatize_text, unlist]

            for action in pre_process:
                res.tokens = res.tokens.apply(action)
                print('Completed: {}'.format(str(action)))

            return res


        cleaned = vader_sent(company)

        def aggregate(df):
            df.reset_index(inplace=True)
            df['date'] = pd.to_datetime(df['date'])

            #aggregate all of the articles and associated sentiment into one column for the day.
            sentiment = df.groupby('date')['sent_negative', 'sent_positive'].agg(np.sum)
            text = df.groupby('date')['tokens'].agg(''.join)

            df = pd.merge(text, sentiment, how='inner', left_index=True, right_index=True)

            today = date.today()
            todays_date = today.strftime("%Y-%m-%d")

            df = pd.DataFrame(df.loc[todays_date]).T

            return df

        aggregated_row = aggregate(cleaned)

        print(aggregated_row)

        #merge todays price
        todays_data = query.current_info()
        aggregated_row=pd.merge(aggregated_row,todays_data, how='outer', left_index=True, right_index=True)
        aggregated_row[['sent_negative', 'sent_positive', 'open', 'volume', 'high', 'low']] = aggregated_row[['sent_negative', 'sent_positive', 'open', 'volume', 'high', 'low']].apply(pd.to_numeric)

        def tfidf(company, daily_row):
            tfidf = joblib.load(f'pickles/{company}/tfidf')
            selector = joblib.load(f'pickles/{company}/kbest')
            rf_feats = daily_row.tokens.values

            X = tfidf.transform(rf_feats).toarray()
            X_2 = selector.transform(X)

            tfidf_train = pd.DataFrame(X_2)

            X_test = daily_row.reset_index(drop=True)
            frames = [X_test, tfidf_train]
            X_test = pd.concat(frames, axis=1)

            X_test.drop(columns=['tokens'], inplace=True) #tokens not needed after TFIDF

            return X_test


        prediction_row = tfidf(query.company, aggregated_row)


        model = joblib.load(f'pickles/{query.company}/gausfinalmodel')
        final_result = model.predict(prediction_row)

        final_proba = model.predict_proba(prediction_row)
        prob_up = "{:.3%}".format(final_proba[:,1][0])
        prob_down = "{:.3%}".format(final_proba[0][0:1][0])

        prediction_row['prediction'] = int(final_result[0])
        prediction_row['probability_up'] = prob_up
        prediction_row['probability_down'] = prob_down
        prediction_row['ticker'] = query.ticker

        time_ = datetime.now() #underscore so we don't overwrite the time module.
        pred_time = time_.strftime("%I:%M:%S %p")
        prediction_row['updated'] = pred_time


        prediction_row.to_csv(f"daily_predictions/{query.company}/{todays_date}.csv")
        print(f'Scrape loop count: {counter}')
