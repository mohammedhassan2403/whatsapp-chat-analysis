import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import preprocessor
import helper

# Use Seaborn theme for prettier plots
sns.set_style("whitegrid")

# Emoji-support font (Ensures emojis render correctly in plots on many systems)
matplotlib.rcParams['font.family'] = 'Segoe UI Emoji'

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    # Decode the uploaded file data
    data = uploaded_file.getvalue().decode("utf-8")
    
    # Preprocess the raw data into a DataFrame
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    
    # Check if 'group_notification' exists before attempting to remove it
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
        
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # -------------------------
        # TOP STATISTICS
        # -------------------------
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # -------------------------
        # MONTHLY TIMELINE
        # -------------------------
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(timeline['time'], timeline['message'], color='green', marker='o')
            ax.set_title("Messages Over Months")
            ax.set_xlabel("Time")
            ax.set_ylabel("Number of Messages")
            ax.set_xticks(range(len(timeline['time'])))
            ax.set_xticklabels(timeline['time'], rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

        # -------------------------
        # DAILY TIMELINE (FIXED)
        # -------------------------
        st.title("Daily Timeline")
        daily = helper.daily_timeline(selected_user, df)
        if not daily.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(daily['only_date'], daily['message'], color='black', marker='o')
            ax.set_title("Messages Over Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of Messages")
            # FIX: Removed manual tick calculation that was breaking the chart.
            # Using simple rotation works best for dates.
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # -------------------------
        # ACTIVITY MAPS
        # -------------------------
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            if not busy_day.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                ax.set_xticks(range(len(busy_day.index)))
                ax.set_xticklabels(busy_day.index, rotation=45, ha='right')
                ax.set_title("Messages by Day of Week")
                st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            if not busy_month.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                ax.set_xticks(range(len(busy_month.index)))
                ax.set_xticklabels(busy_month.index, rotation=45, ha='right')
                ax.set_title("Messages by Month")
                st.pyplot(fig)

        # -------------------------
        # WEEKLY HEATMAP
        # -------------------------
        st.title("Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        if user_heatmap is not None and not user_heatmap.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(user_heatmap, ax=ax, cmap="YlGnBu", annot=True, fmt="g", linewidths=0.5, linecolor='white')
            ax.set_title("Weekly Activity Heatmap")
            ax.set_ylabel("Day of Week")
            ax.set_xlabel("Time Period")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.write("No data available to display the heatmap for this selection.")

        # -------------------------
        # MOST BUSY USERS
        # -------------------------
        if selected_user == "Overall":
            st.title("Most Busy Users")
            top_users, percent_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                ax.bar(top_users.index, top_users.values, color='red')
                ax.set_xticks(range(len(top_users.index)))
                ax.set_xticklabels(top_users.index, rotation=45, ha='right')
                ax.set_title("Top 5 Busiest Users")
                st.pyplot(fig)

            with col2:
                st.header("User Contribution Percentage")
                st.dataframe(percent_df)

        # -------------------------
        # WORDCLOUD
        # -------------------------
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        
        # Check if WordCloud data was returned (not None) before plotting
        if df_wc is not None: 
            fig, ax = plt.subplots()
            ax.imshow(df_wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.write("No suitable words found for the Wordcloud after filtering messages and stop words.")


        # -------------------------
        # MOST COMMON WORDS
        # -------------------------
        st.title("Most Common Words")
        common_df = helper.most_common_words(selected_user, df)
        if not common_df.empty:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(common_df[0], common_df[1], color='blue')
            ax.invert_yaxis()
            ax.set_title("Top 20 Most Common Words/Emojis")
            ax.set_xlabel("Count")
            ax.set_ylabel("Word/Emoji")
            plt.tight_layout()
            st.pyplot(fig)

        # -------------------------
        # EMOJI ANALYSIS
        # -------------------------
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)
        with col1:
            st.header("Emoji Counts")
            st.dataframe(emoji_df)
        with col2:
            if not emoji_df.empty:
                st.header("Top 5 Emojis")
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f%%", startangle=90)
                ax.axis('equal')
                st.pyplot(fig)