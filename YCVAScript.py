import os
import pytube
from pytube.exceptions import VideoUnavailable
import scrapetube
import sys
import re
import requests

#Funciton to get the unique Channel ID from the HTML/Inspect Soruce Data of the pasted url
def get_Url(channel_url):
    # Send a GET request to the channel URL
    response = requests.get(channel_url)

    # Get the HTML content from the response
    html_content = response.text

    # Find the URL using regular expressions, this gets the string beginning with UC
    #The UC string ends at the end of the HTML content tag
    url_pattern = r'(?<=content="vnd.youtube://www.youtube.com/channel/)[^">]+'
    match = re.search(url_pattern, html_content)

    if match:
        url = match.group(0)
        print("Parsed Channel URL:", url)
        return url
    else:
        print("URL not found. Please try a different URL")
        channel_url = input("Please paste the correct URL here:")
        get_Url(channel_url)


# Function to display videos and get the number of videos to download
def get_num_videos_to_download():
    print("Below is the list of available videos from Channel URL:")
    videosInChannel = 0
    for i, video in enumerate(videos, 1):
        video_url = "https://www.youtube.com/watch?v=" + str(video['videoId'])
        currVideo = pytube.YouTube(video_url)
        videosInChannel += 1
        videoDownloadList.append(video_url)
        print(f"{i}. {currVideo.title}")
        

    while True:
        num_videos = input(f"Enter the number of videos to download (0 to {videosInChannel}): ")
        if not num_videos.isdigit():
            print("Invalid input. Please enter a positive integer or 0.")
        else:
            num_videos = int(num_videos)
            if num_videos < 0 or num_videos > videosInChannel:
                print(f"Invalid input. Please enter a value between 0 and {videosInChannel}.")
            else:
                break

    return num_videos

channel_id_input = input("Paste Channel URL Here: ")
#channel_id = channel_id_input.strip("https://www.youtube.com/channel/")
channel_id = get_Url(channel_id_input)
#get the actual Channel name by removing everything before the @
channel_name = channel_id_input[24:]
# Remove invalid characters from the channel ID
channel_folder_name = re.sub(r"[<>:\"/\\|?*]", "", channel_name)

videos = scrapetube.get_channel(channel_id)
print(videos)
videoDownloadList = []
# Create a folder with the name of the YouTube channel in the "Videos" directory
videos_folder = os.path.join(os.path.expanduser("~/Videos"), channel_folder_name)
os.makedirs(videos_folder, exist_ok=True)

path = os.path.join(videos_folder, 'Console_Logs.txt')

print("The result will be saved in '_list.txt' file.")

# Prints the output in the console and into the '_list.txt' file.
class Logger:
    def __init__(self, filename):
        self.console = sys.stdout
        self.file = open(filename, 'w', encoding='utf-8')

    def write(self, message):
        message = str(message)
        self.console.write(message)
        self.file.write(message)

    def flush(self):
        self.console.flush()
        self.file.flush()

sys.stdout = Logger(path)
####
num_videos_to_download = get_num_videos_to_download()
print("Commencing downloads..")
for i, video in enumerate(videoDownloadList[:num_videos_to_download], 1):
    video_url = str(video)
    try:
        video = pytube.YouTube(video_url)
        video_title = re.sub(r"[<>:\"/\\|?*]", "", video.title)  # Remove invalid characters from the video title
        file_path = os.path.join(videos_folder, video_title + ".mp4")
        print(f"Downloading: {video.title} ...")
        try:
            stream = video.streams.get_highest_resolution()
            stream.download(output_path=file_path)
            print(f"Downloaded: {video.title} !")
        except Exception as e:
            print(f"Unable to Download: {video.title}")
            print("Encoutnered Error",e)
        
    except VideoUnavailable:
        print(f"Video at URL {video_url} is unavailable")
    except KeyError as e:
        print(f"Error: {str(e)}")


print("Video download completed. Videos have been stored in",videos_folder)
