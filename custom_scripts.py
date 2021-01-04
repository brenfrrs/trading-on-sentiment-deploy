import re
import tldextract
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.tokenize import regexp_tokenize
import nltk
import time
from dateutil.relativedelta import relativedelta
from nltk.corpus import stopwords

def clean_text(text):
    text.replace("\n"," ")
    text =  ' '.join(re.sub("([^A-Za-z])"," ",text).split())
    return text.lower()


def get_outlet(link):
    '''
    When a URL is passed, this function will return the company name of the entity associated with the URL.
    '''
    res = tldextract.extract(link)
    return res.domain

def get_month_day_range(year):
    '''
    When given a year, returns a list of tuples with the start and end dates for each month of the provided year.
    '''

    ranges = []

    target_year = [(pd.datetime(year,1,1)), (pd.datetime(year,2,1)), (pd.datetime(year,3,1)),
           (pd.datetime(year,4,1)), (pd.datetime(year,5,1)), (pd.datetime(year,6,1)),
           (pd.datetime(year,7,1)), (pd.datetime(year,8,1)), (pd.datetime(year,9,1)),
           (pd.datetime(year,10,1)), (pd.datetime(year,11,1)), (pd.datetime(year,12,1))]

    for date in target_year:
        last_day = date + relativedelta(day=1, months=+1, days=-1)
        first_day = date + relativedelta(day=1)
        ranges.append((first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))

    return ranges


def get_past_prices(range, ticker):
    '''
    Input: a list of date tuples in the format (%Y%m%d,%Y%m%d), and the stock ticker symbol.

    Output: a dataframe with the open/close/high/low and volume historical figures related to the provided stock ticker.

    Example: get_past_prices([('2010-12-01', '2010-12-31')], 'AAPL')
    '''

    td = TDClient(apikey="ef26202dacaf412fb157a05403f81ca3")
    times = []

    counter =1

    for start,end in range:
        #delay to prevent API limits.
        time.sleep(20)
        ts = td.time_series(
        symbol=ticker,
        interval="1day",
        start_date=start,
        end_date=end
        ).as_pandas()
        times.append(ts)
        print(str(counter) + ')', str(start) + ' to',end)
        counter +=1

    stock_prices = pd.concat(times)

    print("Final shape: {}".format(stock_prices.shape))
    return stock_prices



analyzer = SentimentIntensityAnalyzer()

def sentiment_analyzer_scores(article):
    '''
    VADER Sentiment used to tag the.
    Returns the predicted labels: positive/negative/neutral.
    Instantiate analyzer before running this function:
    analyzer = SentimentIntensityAnalyzer()
    '''
    global analyzer

    score = analyzer.polarity_scores(article)

    if score['compound'] >= .05:
        sent = 'positive'
    elif score['compound'] <= -.05:
        sent = 'negative'
    else:
        sent = 'neutral'

    return sent

def toke(text):
    '''
    Input: a string value

    Output: A list of tokens extracted from the string.
    '''
    tokens = regexp_tokenize(text, "[\w']+")
    return tokens



def unlist(x):
    return ", ".join(x)


tokenizer = nltk.tokenize.TweetTokenizer()

def tokenize(text):
    return nltk.word_tokenize(text)

lemmatizer = nltk.stem.WordNetLemmatizer()

def lemmatize_text(text):
    '''
    Input: a string value

    Output: The lemmatized words of the passed string.
    '''
    return [lemmatizer.lemmatize(word) for word in text]



#instantiate stop word list
stop_words=list(set(stopwords.words("english")))

#add additional stop words discovered through manually browsing the corpus.
eda_stopwords = [
    'x', 'u', "'", 'e', 'a', 'i', 'n', 'u', 'd', 'c', 'p', 's', 'i',
    'o', 'r', 't', 'journalism', 'support', 'u', 'editor', 'fair', 'informed',
    'cookie', 'miamiaccording', 'article', 'expired', 'no', 'longer', 'want',
    'search', 'google', 'every', 'term', 'newswire', 'subscribe', 'button', 'close',
    'accept', 'goal', 'achieve', 'u', 'subscribed', 'many', 'continue', 'offer',
    'hard', 'provide', 'dear', 'reader', 'standard', 'always', 'strived', 'miamiinterested',
    'adopting', 'pet', 'gazing', 'lovable', 'pup', 'adoption', 'dog', 'animal', 'shelter',
    'ziprecruiter', 'miami', 'policy', 'clicking', 'explicit', 'consent',
    'please', 'see', 'even', 'better', 'relevant', 'goal', 'le', 'u,', 'philip', 'schiller',
    'believe', 'getty', 'josh', 'edelson', 'topical', 'issue', 'relevance',
    'seen', 'man', 'forward', 'dunkin', 'late', 'wife', 'bagelsee', 'rental', 'site', 'zumper',
    'quarantinefind', 'irvine', 'using', 'yelp', 'find', 'devon', 'horse', 'show',
    'urge', 'turn', 'ad', 'blocker', 'telegraph', 'barbecue', 'stop', 'crunched',
    'porch', 'ebay', 'amazon', 'curry', 'weeknightsset', 'easy', 'dinner', 'matter', 'partner',
    'find', 'detailed', 'description', 'apartment', 'got', 'news', 'mission', 'day', 'impersonal',
    'get', 'tip', 'top', 'mirror', 'newsletter', 'sign', 'thank', 'subscribing',
    'newsletter', 'invalid', 'full', 'swing', 'keen', 'get', 'hand', 'high', 'street',
    'john', 'lewis', 'curry', 'ton', 'currently', 'available', 'actual', 'check', 'back', 'also', 'honor',
    'writer', 'try', 'put', 'apartment', 'rent', 'via', 'go', 'rounded', 'dog', 'shelter', 'pup',
    'dozen', 'donut', 'south', 'targeted', 'practise', 'floridado', 'love', 'florida', 'doggy',
    'cancer', 'hide', 'caption', 'cooky', 'browser', 'sauce', 'pandemicthe',
    'something', 'penguina', 'eagle', 'email', 'notification', 'irvinein', 'hoodline',
    'recipe', 'perfect', 'meal', 'googlethe', 'v', 'doggy', 'delightful',
    'place', 'live', 'retire', 'takeout', 'youtubethe', 'barnes', 'museum',
    'cooking', 'nonstick', 'cookware', 'pretzelslearn', 'homemade', 'soft',
    'collectionsmany', 'franklin', 'u', 'gotten', 'tour', 'familiesthis',
    'best', 'spot', 'noticed', 'adblocking', 'help', 'fund', 'award', 'winning',
    'image', 'curry', 'ton', 'miamimiami', 'new', 'jersey', 'photographer',
    'authoritative', 'apartment', 'cheapest', 'downtown', 'bedroom', 'adventure',
    'aquarium', 'artwork', 'pretzel', 'click', 'play', 'tap', 'play',
    'aught', 'newsletter', 'pear', 'david', 'nield', 'gizmodo', 'pic', 'twitter',
    'com', 'thimbleweed', 'monument', 'pas', 'afp', 'u', 'prepear'
]


#extend the original stop word list to include eda stopwords.
stop_words.extend(eda_stopwords)


def remove_stopwords(text):
    '''input a string and output that string with the stop words removed'''
    return [word for word in text if word not in stop_words]




#classification target threshold can be changed easily if needed.
def thresh(change):
    targ = None
    if change >= .055: #only predict if price increase is at or above .20 cents
        targ = 1
    else:
        targ = 0
    return targ


def process_frame(df):
    """
    Manages the Datetime information for the results(main) dataframe.
    """
    #make date index
    df.set_index('date', inplace=True)

    #Change to Datetime
    df.index = pd.to_datetime(df.index).tz_convert('utc')

    #convert DateTime index to eastern time.
    df.index = df.index.tz_convert('US/Eastern')
    #put into year/month/day format
    df.index = df.index.strftime('%Y-%m-%d')

    #rename to date
    df.index.names = ["date"]

    df.dropna(inplace=True)
    df.fulltext = df.fulltext.apply(clean_text)
    return df
