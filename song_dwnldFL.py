 #Edward Smith
 #December 2019
  # -*- coding: utf-8 -*-
# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python


from __future__ import unicode_literals
import os
import os.path
import requests
from os import path
import json 
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
import googleapiclient.errors
from googleapiclient.discovery import build
import youtube_dl
import os
import difflib,sys
from sys import argv

api_key = "AIzaSyCHupu7nmZci--NuPdLYQyYnguiNUUbUbU"
youtube = build('youtube','v3',developerKey=api_key)
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

#LOOKS THROUGH JSON FILE AND WRITES SONGS & YOUTUBELINKS TO TXT FILE
def songList(response):
    os.chdir(r"C:\\Music")
    if not path.exists("SongsNew.txt"):
        songsnewTxt = open("SongsNew.txt","x")
    youB = ['https://www.youtube.com/watch?v=','&list=']
    songsnewTxt = open("SongsNew.txt","a")
    for item in response['items']:
        print(item['snippet']['title'] + " video_id = "+ item['snippet']['resourceId']['videoId'])
        vidId = item['snippet']['resourceId']['videoId']
        nyouB = vidId.join(youB)
        playId = (item['snippet']['playlistId'])
        #for testing
        pos = int(item['snippet']['position'])
        print(pos)
        nyouB += playId
        songsnewTxt.write(nyouB)
        songsnewTxt.write('\n')
        print(nyouB)
    songsnewTxt.close()
    return pos
#REFRESHING ACCESS TOKEN
def refreshToken(client_id, client_secret, refresh_token):
        params = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
        }
        authorization_url = "https://www.googleapis.com/oauth2/v4/token"
        r = requests.post(authorization_url, data=params)
        if r.ok:
                return r.json()['access_token']
        else:
                return None

def api_response():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = r'C:\Users\edams\AppData\Roaming\Code\User\VSC_Workspace\.vscode\python\.vscode\client_secret_440876599079-lotmaj2kiqssjodtf8k31f98uee6gl7f.apps.googleusercontent.com.json'

    #USING TEXT FILE TO RETREIVE CREDENTIALS
    if os.path.isfile("credentials.json"):
        with open("credentials.json","r") as f:
            creds_data = json.load(f)
            client_id = creds_data['client_id']
            client_secret = creds_data['client_secret']
            refresh_token = creds_data['refresh_token']
        access_token = refreshToken(client_id, client_secret, refresh_token)
        creds = Credentials(access_token)
    else:
    # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
        creds = flow.run_console()
        creds_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
            }
        with open("credentials.json", 'w') as outfile: #WRITING CREDENTIALS TO FILE 
            json.dump(creds_data, outfile)
    return build(api_service_name, api_version, credentials = creds)

def main():
    #Creating Directories
    if not os.path.exists(r'C:\Music\Songs'):
        os.chdir(r"C:\\Music")
        os.mkdir(r'C:\\Music\Songs')
    else: 
        os.chdir(r"C:\Music\Songs")
    os.chdir(r"C:\Music")
    if not path.exists("Songs.txt"):
        songsTxt = open("Songs.txt","w")
    youtube = api_response()
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId="PLaCftlCWzVXT6grOrFK-nUyQSyDCOLEdX"
    )
    response = request.execute()
    songList(response)
    nxtPgTokn = response['nextPageToken']
    #Going through all the differenent pages of results
    if nxtPgTokn:
        print("Next page token outer:",nxtPgTokn)
        while nxtPgTokn:
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                maxResults=50,
                pageToken = nxtPgTokn,
                playlistId="PLaCftlCWzVXT6grOrFK-nUyQSyDCOLEdX"
            )
            response = request.execute()
            songList(response)
            try:
                nxtPgTokn = response['nextPageToken']
                print("Next page token inner:",nxtPgTokn)
            except KeyError:
                print("No next pg token")
                break
    #SEEING DIFFERENCE BETWEEN TXT FILES
    with open('Songs.txt') as f:
        t1 = f.read().splitlines()
        t1s = set(t1)
    with open('SongsNew.txt') as f:
        t2 = f.read().splitlines()
        t2s = set(t2)
    os.chdir(r"C:\Music\Songs")
    #in file2 but not file1
    print ("Only in file2")
    #DOWNLOAD FILES THAT ARE ONLY IN NEW SONGS TXT
    download_options = {
    'format':'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'nocheckcertificate':True,
    'postprocessors':[{ 
        'key': 'FFmpegExtractAudio',
        'preferredcodec':'mp3',
        'preferredquality': '192',
    }],
    }
    for diff in t2s-t1s:
        with youtube_dl.YoutubeDL(download_options) as dl:
            print (t2.index(diff)+1, diff)    
            dl.download([diff])
            
    #COPY SONGS FROM NEW SONGSTXT TO SONGS TXT
    os.chdir(r"C:\Music")
    sN=open('SongsNew.txt',"r")  
    s=open('Songs.txt','w')
    for x in sN.readlines():
        s.write(x)
    sN.close()
    s.close()
    open('SongsNew.txt', "w").close()

if __name__ == "__main__":
    main()