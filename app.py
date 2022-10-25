import streamlit as st
import pandas as pd
import tweepy
from datetime import date
from functions import *

html_temp = """
            <div style="background-color:{};padding:1px">
            
            </div>
            """

with st.sidebar:
    st.markdown("""
        ## About
        This tweets extractor aims to help retrieve online posts on the online violence incidents and the experience of women in Libya, focusing on Twitter.
        
        ## Data Collection
        The data collection process can rely on scraping tweet replies written at the timelines of several Libyan female journalists who may have possibly covered something related to the subject of the project (VAW) during a specific period. 
        The accounts of the journalists (or the profiles concerned) can be selected based on their activity on Twitter and the engagement they get from the people. 

        """)

################################### Keys ###################################

consumer_key = st.secrets["consumer_key"]
consumer_secret = st.secrets["consumer_secret"]
access_token = st.secrets["access_token"]
access_token_secret = st.secrets["access_token_secret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
if 'api' not in st.session_state:
    api = tweepy.API(auth)
    st.session_state['api'] = api

############################################################################

# st.write("___Extracting Tweets by TAGS___")


with st.expander("Tweets extraction with hashtags"):
    st.markdown("""
        Potential useful Twitter hashtags for Libyan content:
        * نسويات_ليبيا
        * ليبيا
        * المجتمع_الليبي
        
    """)
    col1, col2, col3 = st.columns(3)
    with col1:
        hashtag = st.text_input("Twitter hashtag", placeholder="Enter hashtag/word")
    with col2:
        nbTweets = st.number_input("Number of tweets", min_value=0, max_value=2000, value=100)
    with col3: 
        locations = ['None', 'Libya', 'ليبيا', 'Tripoli', 'Benghazi', 'Misrata', 'Zawiya', 'Bayda', 'Gharyan', 'Tobruk', 'Ajdabiya', 'Zliten', 'Derna', 'Sabha', 'Khoms', 'Sabratha', 'Zuwara', 'Kufra', 'Marj', 'Tocra', 'Tarhuna', 'Sirte', 'Gharyan', 'Msallata', 'Bani Walid', 'Syrte']
        location_select = st.selectbox('Location', options=locations)

    col11, col22 = st.columns(2)
    with col11:
        from_date = st.date_input("From", date(2021, 1, 1), disabled=True)
    with col22:
        to_date = st.date_input("Until", date.today(), disabled=True)

    if nbTweets and hashtag and 'api' in st.session_state:
        result = scrape(hashtag, nbTweets)
        if location_select != 'None':
            result = result[result.Location.isin([location_select])]
        st.write("__Extracted tweets__")
        st.dataframe(result)
        csv = convert_df(result)
        filename = str(hashtag)+"_tweets.csv"

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=filename,
            mime='text/csv',
        )

with st.expander("Tweets extraction with username"):
    st.markdown("""
            Some Libyan female activists on Twitter: 
            * Heba Shibani: __HebaShibani__
            * Hajer Shareif: __hajershareif__
            * Rida Al Tubuly: __RidaAltubuly__
            * Nadeen Alfarsi: __nadeen_alfarsi__
            * تَحَرَّى - Tahra: __Tahraly__
            * Huda El-Sarari: __Elsrari__ 
            * Iman Saad: __ImanSaad2__
    """)
    username = st.text_input("Twitter username", placeholder='Enter username')

    if username and 'api' in st.session_state:
        user_tweets = st.session_state['api'].user_timeline(screen_name=username, 
                            # 200 is the maximum allowed count
                            count = 200,
                            include_rts = False,
                            # Necessary to keep full_text 
                            # otherwise only the first 140 words are extracted
                            tweet_mode = 'extended'
                            )
        user_name = [] 
        user_text_tweet = []
        user_likes = []
        user_retweets = []
        followers = [] 
        retweeted = [] 
        for user_tweet in user_tweets:
            status_id = user_tweet.id
            # if user_tweet.lang != "fr" and user_tweet.lang != "en":
            user_name.append(user_tweet.user.screen_name)
            user_text_tweet.append(user_tweet.full_text)
            user_likes.append(user_tweet.favorite_count)
            user_retweets.append(user_tweet.retweet_count)
            followers.append(user_tweet.user.followers_count)
            retweeted.append(user_tweet.retweeted)

        oldest = status_id - 1
        while len(user_tweets) > 0:
            user_tweets = st.session_state['api'].user_timeline(screen_name=username,count=200,include_rts = False,tweet_mode = 'extended',max_id=oldest)
            
            #save most recent tweets
            for user_tweet in user_tweets:
                status_id = user_tweet.id
                
                user_name.append(user_tweet.user.screen_name)
                user_text_tweet.append(user_tweet.full_text)
                user_likes.append(user_tweet.favorite_count)
                user_retweets.append(user_tweet.retweet_count)
                followers.append(user_tweet.user.followers_count)
                retweeted.append(user_tweet.retweeted)
            
            #update the id of the oldest tweet less one
            oldest = status_id - 1

        df = pd.DataFrame(list(zip(user_name, user_text_tweet, user_likes, user_retweets, followers, retweeted)), columns=['username', 'tweet', 'likes', 'count retweets', 'followers', 'retweeted'])
        # ith_tweet = 
        # df.loc[len(df)] = ith_tweet
        totalFinal = len(user_text_tweet)
        to_write = str(totalFinal)+" tweets in total."
        st.info(to_write)

        st.dataframe(df)
        csv = convert_df(df)
        filename = username+"_tweets.csv"

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=filename,
            mime='text/csv',
        )

# with st.expander("Tweet replies extraction by tweet_ID"):
#     username = st.text_input("Username", placeholder='Enter username')
#     tweet_input_id = st.text_input("Tweet ID", placeholder='Enter tweet id (found in URL)')
#     max_id = None
#     replies=[]
#     if username and tweet_input_id:
#         repliers = []
#         replies = []
#         for tweet in tweepy.Cursor(st.session_state['api'].search_tweets, q='to:{}'.format(username),result_type='recent').items(100):
            
#             if hasattr(tweet, 'in_reply_to_status_id_str'):
#                 if (tweet.in_reply_to_status_id_str==tweet_input_id):
#                     # replies.append(tweet)
#                     st.write(tweet.user.screen_name)
#                     repliers.append(tweet.user.screen_name)
#                     st.write(tweet.text)
#                     replies.append(tweet.text)
#         # for tweet in replies:
#         #     st.write(tweet)
            
#         df_replies = pd.DataFrame(list(zip(repliers, replies)), columns=['Username', 'Reply tweet'])
#         st.table(df_replies)