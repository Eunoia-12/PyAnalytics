from flask import Flask, request, jsonify
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, max, min, stddev_pop, col
import isodate
from flask_cors import CORS

# Load environment variables
load_dotenv()
DEVELOPER_KEY = os.getenv("YOUTUBE_API")

app = Flask(__name__)
CORS(app)
spark = SparkSession.builder.appName("YouTubeChannelAnalytics").getOrCreate()

def get_youtube_service():
    return build('youtube', 'v3', developerKey=DEVELOPER_KEY)

def get_channel_data(youtube, channel_id):
    response = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    ).execute()
    item = response.get('items', [None])[0]
    if item:
        return {
            "title": item["snippet"]["title"],
            "subscriber_count": int(item["statistics"]["subscriberCount"]),
            "video_count": int(item["statistics"]["videoCount"]),
            "playlist_id": item['contentDetails']['relatedPlaylists']['uploads']
        }
    return None

def get_videos(youtube, playlist_id):
    videos = []
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        videos.extend([item['contentDetails']['videoId'] for item in res.get('items', [])])
        next_page_token = res.get('nextPageToken')

        if not next_page_token:
            break

    return videos

def get_video_categories(youtube,category_ids=None):
    params = {
        'part' : 'snippet'
    }
    if category_ids:
        params['id'] = ','.join(category_ids)
    else:
        params['regionCode'] = 'US'
    request = youtube.videoCategories().list(**params)
    response = request.execute()
    categories = {item['id']: item['snippet']['title'] for item in response.get('items', [])}
    return categories

def get_video_details(youtube, video_ids, categories):
    video_details = []
    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids[i:i+50])
        ).execute()

        for item in response.get('items', []):
            duration_iso = item["contentDetails"]["duration"]
            duration_seconds = isodate.parse_duration(duration_iso).total_seconds()
            category_name = categories.get(item["snippet"]["categoryId"], "Unknown Category")
            video_details.append({
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "duratioin": duration_seconds,
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "comments": int(item["statistics"].get("commentCount", 0)),
                "category_name": category_name
            })
    return video_details

def analyze_videos(data):
    df = spark.createDataFrame(data)
    stats = {
        "average_views": df.select(avg("views")).collect()[0][0],
        "max_likes": df.select(max("likes")).collect()[0][0],
        "max_comments": df.select(max("comments")).collect()[0][0],
        "stddev_views": df.select(stddev_pop("views")).collect()[0][0]
    }
    # Like-to-view ratio
    df = df.withColumn("like_to_view_ratio", col("likes") / col("views"))
    stats["average_like_to_view_ratio"] = df.select(avg("like_to_view_ratio")).collect()[0][0]

    # Comment-to-view ratio
    df = df.withColumn("comment_to_view_ratio", col("comments") / col("views"))
    stats["average_comment_to_view_ratio"] = df.select(avg("comment_to_view_ratio")).collect()[0][0]

    return stats

def top_10_videos(data,video_details):
    # Top 10 videos by views
    df = spark.createDataFrame(data)
    stats = {
        "average_views": df.select(avg("views")).collect()[0][0],
        "max_likes": df.select(max("likes")).collect()[0][0],
        "max_comments": df.select(max("comments")).collect()[0][0],
        "stddev_views": df.select(stddev_pop("views")).collect()[0][0]
    }
    top_videos = df.orderBy(col("views").desc()).limit(10)
    top_videos_list = top_videos.collect()
    stats["top_videos_by_views"] = [{"title": row.title, "views": row.views} for row in top_videos_list]
    # Sort and slice the list to get the top 10 videos by views
    top_videos = sorted(video_details,key=lambda x: x['views'], reverse=True)[:10]



@app.route('/analyze', methods=['POST'])
def analyze_channel():
    if not request.is_json:
        return jsonify({"error": "Invalid content type"}), 415
    data = request.get_json()
    channel_id = data.get('channel_id')
    if not channel_id:
        return jsonify({"error": "Channel ID is required"}), 400

    youtube = get_youtube_service()
    channel_data = get_channel_data(youtube, channel_id)
    if not channel_data:
        return jsonify({"error": "Channel not found"}), 404

    playlist_id = channel_data['playlist_id']
    video_ids = get_videos(youtube, playlist_id)
    categories =get_video_categories(youtube)
    video_details = get_video_details(youtube, video_ids, categories)
    top_videos = sorted(video_details, key=lambda x: x['views'], reverse=True)[:10]
    analysis_results = analyze_videos(video_details)

    return jsonify({
        "status" : "success",
        "channel_info": {
            "title" : channel_data['title'],
            "subscribers" : channel_data['subscriber_count'],
            "total_videos" : channel_data['video_count']
        },
        "top_videos": top_videos,
        "analysis": analysis_results
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)