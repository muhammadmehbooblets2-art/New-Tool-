import streamlit as st
import requests
from datetime import datetime, timedelta, timezone

# YouTube API Key
API_KEY = "Enter your API Key here"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool - Yonggi Cho Niche")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=15)
max_subs = st.number_input("Max Subscribers of Channel:", min_value=100, max_value=1000000, value=10000, step=1000)
max_results = st.slider("Videos to check per keyword:", min_value=5, max_value=50, value=15)

# List of specific keywords (Yonggi Cho niche)
keywords = [
    "Yonggi Cho Sermon", "Yonggi Cho Fourth Dimension", "Yonggi Cho Prayer",
    "Yonggi Cho Faith Message", "David Yonggi Cho Full Sermon",
    "Yonggi Cho Holy Spirit Sermon", "Yonggi Cho Healing Sermon",
    "Yonggi Cho Miracle Story", "Yonggi Cho Powerful Message",
    "Yonggi Cho Sermon English", "Yonggi Cho Sermon Hindi",
    "Yonggi Cho Sermon Urdu", "Yonggi Cho Sermon Tamil",
    "Yonggi Cho Sermon Telugu", "Yonggi Cho Sermon Malayalam",
    "Yonggi Cho Sermon Spanish", "Yonggi Cho Life Story",
    "Yonggi Cho Testimony", "Yonggi Cho Sermon Shorts",
    "Yoido Full Gospel Church Sermon", "Cho Yonggi Preaching"
]

st.caption(f"Estimated API quota per click: {len(keywords) * 100} units (daily free limit: 10,000)")

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.now(timezone.utc) - timedelta(days=int(days))).strftime("%Y-%m-%dT%H:%M:%SZ")
        all_results = []
        seen_videos = set()

        # Iterate over the list of keywords
        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")

            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": int(max_results),
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            # Show API errors clearly (quota, invalid key, etc.)
            if "error" in data:
                st.error(f"API error: {data['error'].get('message', 'Unknown error')}")
                break

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = [v for v in data["items"] if "videoId" in v.get("id", {})]
            video_ids = [v["id"]["videoId"] for v in videos]
            channel_ids = list({v["snippet"]["channelId"] for v in videos if "channelId" in v.get("snippet", {})})

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing video/channel data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_data = requests.get(YOUTUBE_VIDEO_URL, params=stats_params).json()

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_data = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params).json()

            if "items" not in stats_data or "items" not in channel_data:
                st.warning(f"Failed to fetch statistics for keyword: {keyword}")
                continue

            # Map by ID so videos and channels always match correctly
            video_stats = {s["id"]: s["statistics"] for s in stats_data["items"]}
            channel_stats = {c["id"]: c["statistics"] for c in channel_data["items"]}

            # Collect results
            for video in videos:
                vid = video["id"]["videoId"]
                if vid in seen_videos:
                    continue

                ch_id = video["snippet"].get("channelId")
                if vid not in video_stats or ch_id not in channel_stats:
                    continue

                views = int(video_stats[vid].get("viewCount", 0))
                subs = int(channel_stats[ch_id].get("subscriberCount", 0))

                if subs < int(max_subs):
                    seen_videos.add(vid)
                    all_results.append({
                        "Title": video["snippet"].get("title", "N/A"),
                        "Description": video["snippet"].get("description", "")[:200],
                        "URL": f"https://www.youtube.com/watch?v={vid}",
                        "Views": views,
                        "Subscribers": subs,
                        "Keyword": keyword,
                    })

        # Display results (highest views first)
        if all_results:
            all_results.sort(key=lambda x: x["Views"], reverse=True)
            st.success(f"Found {len(all_results)} results across all keywords!")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']:,}  \n"
                    f"**Subscribers:** {result['Subscribers']:,}  \n"
                    f"**Keyword:** {result['Keyword']}"
                )
                st.write("---")
        else:
            st.warning(f"No results found for channels with fewer than {int(max_subs):,} subscribers.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
