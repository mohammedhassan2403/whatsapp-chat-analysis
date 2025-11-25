import pandas as pd
from collections import Counter
from urlextract import URLExtract
from wordcloud import WordCloud
import emoji

extract = URLExtract()


# ---------------------------------------------------
# BASIC STATS
# ---------------------------------------------------
def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_messages = df.shape[0]
    
    # Efficiently calculate total words
    words = sum(len(str(message).split()) for message in df["message"])
    
    num_media_messages = df[df["message"] == "<Media omitted>\n"].shape[0]
    
    # Efficiently fetch links
    links = sum(len(extract.find_urls(str(message))) for message in df["message"])

    return num_messages, words, num_media_messages, links


# ---------------------------------------------------
# BUSIEST USERS
# ---------------------------------------------------
def most_busy_users(df):
    top_users = df["user"].value_counts().head()
    percent_df = (
        df["user"].value_counts(normalize=True) * 100
    ).round(2).reset_index()
    
    percent_df.columns = ["name", "percent"] 
    return top_users, percent_df


# ---------------------------------------------------
# WORDCLOUD WITH EMOJI SUPPORT
# ---------------------------------------------------
def create_wordcloud(selected_user, df, stop_words_file="stop_hinglish.txt"):
    try:
        f = open(stop_words_file, 'r', encoding="utf-8")
        stop_words = set(f.read().split())
    except FileNotFoundError:
        stop_words = set()

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[
        (df["user"] != "group_notification") & (df["message"] != "<Media omitted>\n")
    ].copy()
    
    # Check for empty DataFrame
    if temp.empty:
        return None

    def clean_message(message):
        if not isinstance(message, str):
            return ""
            
        words = []
        for token in message.lower().split():
            # Check for stop words OR if the token is an emoji (to keep emojis)
            if token not in stop_words or any(char in emoji.EMOJI_DATA for char in token):
                words.append(token)
        return " ".join(words)

    temp.loc[:, "cleaned"] = temp["message"].apply(clean_message)

    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color="white",
        collocations=False,
        regexp=r"\S+",
    )
    
    wordcloud_text = " ".join(temp["cleaned"].astype(str))
    
    # If text is empty, return None to avoid ValueError
    if not wordcloud_text.strip():
        return None

    return wc.generate(wordcloud_text)


# ---------------------------------------------------
# MOST COMMON WORDS
# ---------------------------------------------------
def most_common_words(selected_user, df, stop_words_file="stop_hinglish.txt"):
    try:
        f = open(stop_words_file, 'r', encoding="utf-8")
        stop_words = set(f.read().split())
    except FileNotFoundError:
        stop_words = set()

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[
        (df["user"] != "group_notification") & (df["message"] != "<Media omitted>\n")
    ]
    
    if temp.empty:
        return pd.DataFrame(columns=[0, 1])

    words = []

    for message in temp['message']:
        if isinstance(message, str):
            for word in message.lower().split():
                if word not in stop_words or any(char in emoji.EMOJI_DATA for char in word):
                    words.append(word)
    
    if not words:
        return pd.DataFrame(columns=[0, 1])

    return pd.DataFrame(Counter(words).most_common(20))


# ---------------------------------------------------
# EMOJI ANALYSIS
# ---------------------------------------------------
def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    emojis_list = []
    for message in df['message']:
        if isinstance(message, str):
            emojis_list.extend([c for c in message if c in emoji.EMOJI_DATA])

    return pd.DataFrame(Counter(emojis_list).most_common())


# ---------------------------------------------------
# TIMELINE & ACTIVITY FUNCTIONS
# ---------------------------------------------------
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month'])['message'].count().reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.groupby('only_date')['message'].count().reset_index()


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if "period" not in df.columns:
        return None

    user_heatmap = df.pivot_table(
        index='day_name', 
        columns='period', 
        values='message', 
        aggfunc='count'
    ).fillna(0)

    return user_heatmap