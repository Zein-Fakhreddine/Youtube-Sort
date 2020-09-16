import sys
import os
from apiclient.discovery import build

api_key = os.environ.get('YOUTUBE-API')
youtube = build('youtube', 'v3', developerKey=api_key)
def get_channel_videos(channel_id):
    
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    videos = []
    next_page_token = None
    
    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id, 
                                           part='snippet', 
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    
    return videos

videos = get_channel_videos(sys.argv[1])

def get_videos_stats(videos):
    stats = []
    video_ids = list(map(lambda x:x['snippet']['resourceId']['videoId'], videos))
    for i in range(0, len(video_ids), 50):
        res = youtube.videos().list(id=','.join(video_ids[i:i+50]),
                                   part='statistics,snippet').execute()
        stats += res['items']
        
    return stats

stats = get_videos_stats(videos)

def customSort(video):
    likeCount = int(video['statistics']['likeCount']) if 'likeCount' in video['statistics'] else 0
    dislikeCount = int(video['statistics']['dislikeCount']) if 'dislikeCount' in video['statistics'] else 0
    ratio = dislikeCount / likeCount if likeCount !=0 else 0
    sortKey = sys.argv[2] if len(sys.argv) == 3 else 'ratio'

    if sortKey == 'like':
        return likeCount
    if sortKey == 'dislike':
        return dislikeCount

    return ratio

sortedVideos = sorted(stats, key=customSort, reverse=True)
maxLength = 0
for video in sortedVideos:
    titleLength = len(video['snippet']['title'].encode('ascii', 'ignore').decode('ascii'))
    if titleLength > maxLength:
        maxLength = titleLength

for video in sortedVideos:
    title = video['snippet']['title'].encode('ascii', 'ignore').decode('ascii')
    likeCount = int(video['statistics']['likeCount']) if 'likeCount' in video['statistics'] else 0
    dislikeCount = int(video['statistics']['dislikeCount']) if 'dislikeCount' in video['statistics'] else 0
    ratio = dislikeCount / likeCount if likeCount !=0 else 0
    print('{:{width}} {:<10} {:<10} {:<10}'.format(title, likeCount, dislikeCount, ratio, width=maxLength + 5))