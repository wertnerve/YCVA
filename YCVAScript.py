import os
import pytube
from pytube.exceptions import VideoUnavailable
import scrapetube
import sys
import re
import requests

# Function to get the unique Channel ID from the HTML/Inspect Source Data of the pasted URL
def get_channel_id(channel_url):
    """
    Retrieves the unique Channel ID from the HTML/Inspect Source Data of the given URL.
    """
    response = requests.get(channel_url)  # Send a GET request to the channel URL
    html_content = response.text  # Get the HTML content from the response

    # Find the URL using regular expressions, this gets the string beginning with UC
    # The UC string ends at the end of the HTML content tag
    url_pattern = r'(?<=content="vnd.youtube://www.youtube.com/channel/)[^">]+'
    match = re.search(url_pattern, html_content)

    if match:
        channel_id = match.group(0)
        print("Parsed Channel ID:", channel_id)
        return channel_id
    else:
        print("URL not found. Please try a different URL")
        channel_url = input("Please paste the correct URL here:")
        return get_channel_id(channel_url)


def display_videos(videos):
    """
    Displays the available videos from the channel URL and prompts the user to enter the number of videos to download.
    """
    print("Below is the list of available videos from the Channel URL:")
    videos_in_channel = 0
    video_download_list = []

    for i, video in enumerate(videos, 1):
        video_url = "https://www.youtube.com/watch?v=" + str(video['videoId'])
        curr_video = pytube.YouTube(video_url)
        videos_in_channel += 1
        video_download_list.append(video_url)
        print(f"{i}. {curr_video.title}")

    while True:
        num_videos = input(f"Enter the number of videos to download (0 to {videos_in_channel}): ")
        if not num_videos.isdigit():
            print("Invalid input. Please enter a positive integer or 0.")
        else:
            num_videos = int(num_videos)
            if num_videos < 0 or num_videos > videos_in_channel:
                print(f"Invalid input. Please enter a value between 0 and {videos_in_channel}.")
            else:
                break

    return num_videos, video_download_list


def main():
    channel_url_input = input("Please paste Channel URL here: ")
    channel_id = get_channel_id(channel_url_input)
    channel_name = channel_url_input[24:]  # Get the actual Channel name by removing everything before the '@'
    channel_folder_name = re.sub(r"[<>:\"/\\|?*]", "", channel_name)  # Remove invalid characters from the channel ID

    videos = scrapetube.get_channel(channel_id)

    video_download_list = []
    videos_folder = os.path.join(os.path.expanduser("~/Videos"), channel_folder_name)
    os.makedirs(videos_folder, exist_ok=True)

    log_path = os.path.join(videos_folder, 'Console_Logs.txt')

    print(f"Console logs will be saved in 'Console_Logs.txt' file, located here:")
    print(str(videos_folder))


    sys.stdout = Logger(log_path)

    num_videos_to_download, video_download_list = display_videos(videos)

    print("Commencing downloads...")
    for i, video_url in enumerate(video_download_list[:num_videos_to_download], 1):
        try:
            video = pytube.YouTube(video_url)
            video_title = re.sub(r"[<>:\"/\\|?*]", "", video.title)  # Remove invalid characters from the video title
            file_path = os.path.join(videos_folder, video_title + ".mp4")
            
            print(f"Downloading: '{video.title}'")
            
            try:
                stream = video.streams.get_highest_resolution()
                stream.download(output_path=file_path)
                print(f"Downloaded: {video.title}")
                print('='*len(f"Downloaded: '{video_title}'"))
            except Exception as e:
                print(f"Unable to download: {video.title}")
                print("Encountered Error:", e)

        except VideoUnavailable:
            print(f"Video at URL {video_url} is unavailable")
        except KeyError as e:
            print(f"Error: {str(e)}")

    print("Video download completed. Videos have been stored in", videos_folder)

    #Have the user decide to continue or exit the program
    choice = input("Please enter :3c to run the program again, or any other key to exit: ")
    if str(choice) != ":3c":
        exit()
    print("Thank you! Let's continue onto the next channel:")
    main()


class Logger:
    """
    Custom logger class to redirect console output to a file.
    """

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


if __name__ == "__main__":
    main()
