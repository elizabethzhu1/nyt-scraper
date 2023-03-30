from bs4 import BeautifulSoup
import requests
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from pynytimes import NYTAPI

api_key = "pkIJ8ekAwAQJvIxsr9QkUAjrMzlC3wws"

nyt = NYTAPI(api_key, parse_dates=True)

# function: cleans up words by removing special symbols
def clean_wordlist(wordlist):
    clean_list = []
    for word in wordlist:
        symbols = "!@#$%^&*()_-+={[}]|\;:\"<>?/., "
        for i in range(len(symbols)):
            word = word.replace(symbols[i], '')
        if len(word) > 0:
            clean_list.append(word)
    return clean_list


games = ["Wordle", "Today's Wordle Review", "Spelling Bee", "The Crossword", "Letter Boxed", "Tiles"]
all_words = []

url = "https://www.nytimes.com/"
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
headlines = soup.find_all('h3', class_='indicate-hover')
#summaries = soup.find_all('p', class_='summary-class')

for headline in headlines:   
    # extract most frequent words
    word_list = headline.text.split() 
    cleaned_list = clean_wordlist(word_list)
    for word in cleaned_list:
        word = word.lower()
        all_words.append(word)

#print(all_words) 
   
# create a dictionary of the most common words + their frequencies 
dict = {}
for word in all_words:
    if word not in dict:
        dict[word] = 1
    else:
        dict[word] += 1

keys = list(dict.keys())
values = list(dict.values())
sorted_value_index = np.argsort(values)
sorted_dict = {keys[i]:values[i] for i in sorted_value_index}

non_filler_words = []
filler_words = ["wordle", "how", "were", "from", "will", "been", "top", "several", "or", "out", "you", "up", "an", "over", "the", "with", "before", "was", "back", "has", "see", "ever", "now", "what", "could", "after", "on", "us", "more", "are", "have", "get", "as", "but", "be", "one", "who", "not", "by", "my", "can", "do", "that", "in", "to", "a", "is", "and", "of", "it", "for", "at", "our", "i", "about", "we", "this", "he", "she", "they"]

sorted_dict_copy = sorted_dict.copy()
for word in sorted_dict_copy:
    if sorted_dict[word] < 2:
        sorted_dict.pop(word)
    if word in filler_words and word in sorted_dict:
        sorted_dict.pop(word)

negative = 0
neutral = 0
positive = 0

for word in all_words:
    if word not in filler_words:
        non_filler_words.append(word)

for word in non_filler_words:   
    sentiment = SentimentIntensityAnalyzer()
    sent_word = sentiment.polarity_scores(word)
    if sent_word['neg'] == 1:
        negative += 1
    elif sent_word['neu'] == 1:
        neutral += 1
    elif sent_word['pos'] == 1:
        positive += 1

headline_sentiments_list = []
# analyze sentiment of each headline
headline_sentiments_dict = {}
text_headlines = []
for headline in headlines:
    if headline.text not in games:
        sentiment = SentimentIntensityAnalyzer()
        headline_sentiment = sentiment.polarity_scores(headline.text)
        headline_sentiments_dict[headline.text] = headline_sentiment
        text_headlines.append(headline.text)
        #headline_sentiment['headline'] = headline.text
        #headline_sentiments_list.append(headline_sentiment)

print(headline_sentiments_dict)

st.write("""
# What's in a NYTimes Headline? 

Welcome, visitor! This site scrapes interesting data from the headlines of The New York Times.

""")
         
# tracking word frequency
words = list(sorted_dict.keys())
frequencies = list(sorted_dict.values())
words_data = pd.DataFrame(frequencies, words) 
st.subheader("Frequent Words in the Headlines")   
st.bar_chart(words_data, width=500, height = 300, use_container_width=True)

st.subheader("Sentiment Analysis on Today's NYT Headlines")
panda_headlines = pd.Series(text_headlines)
selected_headline = st.selectbox("**Select a NYT article from today:** ", options = panda_headlines)
st.text("Selected Headline: " + str(selected_headline))
st.text("Sentiment: " + str(headline_sentiments_dict[selected_headline]))

headlines = list(headline_sentiments_dict.keys())
sentiments = list(headline_sentiments_dict.values())
sentiments.reverse()
headlines_data = pd.DataFrame(sentiments, headlines)
st.bar_chart(headlines_data, width=300, height=400)

# color_scale = alt.Scale(
#     domain=[
#         "pos",
#         "neu",
#         "neg",
#         "compound"
#     ],
#     range=["#c30d24", "#f3a583", "#cccccc", "#94c6da"]
# )

# y_axis = alt.Axis(
#     title='Sentiment',
#     offset=5,
#     ticks=False,
#     minExtent=60,
#     domain=False
# )

# print(headline_sentiments_list)
# data = alt.pd.DataFrame(headline_sentiments_list)
# print(data)
# chart = alt.Chart(data).mark_bar().encode(
#     x='compound',
#     y=alt.Y('headline:N', axis=y_axis),
#     color=alt.Color(
#         'type:N',
#         legend=alt.Legend( title='sentiments'),
#         scale=color_scale,
#     )
# )

# chart = chart.configure_view(
#     width=500,
#     height=300
# )

# st.altair_chart(chart, use_container_width=True)


#chart = alt.Chart(headlines_data).mark_bar().encode(
    #x='headline', y='sentiment')
#st.altair_chart(chart, use_container_width=True)

neg_total = 0
pos_total = 0
neu_total = 0
compound_total = 0
for sentiment in sentiments:
    neg_total += sentiment['neg']
    pos_total += sentiment['pos']
    neu_total += sentiment['neu']
    compound_total += sentiment['compound']

average_sentiment = ['neg: ' + str(round(neg_total/len(text_headlines), 3)),'pos: ' + str(round(pos_total/len(text_headlines), 3)), 'neu: ' + str(round(neu_total/len(text_headlines), 3)), 'compound: ' + str(round(compound_total/len(text_headlines), 3))]

st.subheader("Average Sentiment of a NYT Headline: ")
st.text(str(average_sentiment))

st.subheader("Sad News or Happy News?")
st.markdown("Let's find out whether there are more positive words or negative words in the headlines.")
st.text("Positive Word Count: " + str(negative))
st.text("Negative Word Count: " + str(positive))
st.text("Neutral Word Count: " + str(neutral))

if negative > positive:
    st.markdown("Overall, there are " + str(negative - positive) + " more **:red[negative]** words featured in the headlines.")
elif positive > negative:
    st.text("Overall, there are " + str(positive - negative) + " more positive words featured in the headlines.")
else:
    st.text("Overall, there are an equal number of positive and negative words featured in the headlines. Eh.")

# mapping where headlines are occuring
url = "https://api.nytimes.com/svc/topstories/v2/home.json"
params = {
    "api-key": "pkIJ8ekAwAQJvIxsr9QkUAjrMzlC3wws"
}

response = requests.get(url, params=params)
data = response.json()

geolocator = Nominatim(user_agent="nyt-map")
geolocator.timeout = 5
latitudes = []
longitudes = []
for result in data["results"]:
    if "geo_facet" in result:
        location = result["geo_facet"]
        loc = geolocator.geocode(location)
        if loc:
            latitudes.append(loc.latitude)
            longitudes.append(loc.longitude)

location_data = {'lat': latitudes, "lon": longitudes}
loc_data = pd.DataFrame(location_data)
st.subheader("Where Are Today's Headlines Happening?")
st.map(loc_data, zoom=1, use_container_width=True)

# recommend the user an article based on a search query
st.subheader("Now, let's recommend an article for you.")
input = st.text_input("**What topic are you interested in?**")
articles = nyt.article_search(query = input, results = 5)

for article in articles.copy():
    to_remove = ["snippet", "lead_paragraph", "source", "multimedia", "headline", "keywords", "pub_date", "document_type", "news_desk", "uri", "byline", "subsection_name", "type_of_material", "_id", "print_section", "print_page"]
    for key in to_remove:
        if key in article:
            del article[key]

if input != "":
    st.success("Here are some articles that might pique your curiosity!")
    table = pd.DataFrame(articles)
    st.dataframe(table, width = 2000, height = 400, use_container_width=False)
