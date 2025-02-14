import streamlit as st
import googleapiclient.discovery
import datetime

# YouTube API Key
API_KEY = "AIzaSyCuUYGZTNiXccQSobvlPlSInOAmcViDhvc"
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

# Streamlit UI
st.title("YouTube Viral Niche Finder Tool")
st.sidebar.header("Filters")

# User-defined filters
sub_range = st.sidebar.selectbox("Select Subscriber Range", [
    "1K-5K", "5K-10K", "10K-50K", "50K-100K"
])

# Setting min and max subscriber count based on selection
if sub_range == "1K-5K":
    min_subs, max_subs = 1000, 5000
elif sub_range == "5K-10K":
    min_subs, max_subs = 5000, 10000
elif sub_range == "10K-50K":
    min_subs, max_subs = 10000, 50000
else:
    min_subs, max_subs = 50000, 100000

min_views = st.sidebar.number_input("Minimum Total Views", min_value=500000, value=500000)

# Date filter (last 3 months)
date_filter = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat() + "Z"
st.sidebar.write(f"Filtering channels created after: {date_filter[:10]}")

# Function to fetch trending channels
def search_channels():
    request = youtube.search().list(
        part="snippet",
        type="channel",
        order="date",
        maxResults=50,
        publishedAfter=date_filter
    )
    response = request.execute()
    return response.get("items", [])

# Function to get channel statistics
def get_channel_stats(channel_id):
    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    response = request.execute()
    stats = response["items"][0]["statistics"]
    return {
        "subscribers": int(stats.get("subscriberCount", 0)),
        "views": int(stats.get("viewCount", 0)),
        "videos": int(stats.get("videoCount", 0))
    }

# Filter viral channels
def is_viral(stats):
    return stats["views"] / max(stats["videos"], 1) > 10000

# Search and filter channels
channels = search_channels()
filtered_channels = []

for channel in channels:
    channel_id = channel["id"]["channelId"]
    stats = get_channel_stats(channel_id)
    if min_subs <= stats["subscribers"] <= max_subs and stats["views"] >= min_views and is_viral(stats):
        filtered_channels.append({
            "Name": channel["snippet"]["title"],
            "Subscribers": stats["subscribers"],
            "Views": stats["views"],
            "Videos": stats["videos"],
            "Channel ID": channel_id
        })

# Display results
if filtered_channels:
    st.write("### Viral YouTube Channels")
    st.table(filtered_channels)
else:
    st.write("No viral channels found with the given criteria.")

