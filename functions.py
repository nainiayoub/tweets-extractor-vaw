import streamlit as st
import tweepy
import pandas as pd

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def scrape(words, numtweet):
    # Create dataframe
    df = pd.DataFrame(columns=['Tweet ID', 'Username', 'Location', 'Tweet', 'Likes', 'Total retweets', 'Date', 'Followers', 'TotalTweets'])
    # Tweets search limited by numtweet
    tweets = tweepy.Cursor(st.session_state['api'].search_tweets, words+ " -filter:retweets", lang="ar", tweet_mode='extended').items(numtweet)
    # get info about each tweet
    list_tweets = [tweet for tweet in tweets]

    # tweet count
    i = 0
    for tweet in list_tweets:
        username = tweet.user.screen_name
        location = tweet.user.location
        id_tweet = tweet.id
        text = tweet.full_text
        likes = tweet.favorite_count
        nb_retweets = tweet.retweet_count
        date = tweet.created_at
        followers = tweet.user.followers_count
        totaltweets = tweet.user.statuses_count

        ith_tweet = [id_tweet, username, location, text, likes, nb_retweets, date, followers, totaltweets]
        df.loc[len(df)] = ith_tweet

    return df
