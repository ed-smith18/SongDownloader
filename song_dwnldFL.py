# Edward Smith
# -*- coding: utf-8 -*-
# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python
# https://developers.google.com/youtube/v3/docs/playlistItems/list



from __future__ import unicode_literals
import os
from os import path
import requests
import json 
import youtube_dl
from sys import argv

import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import googleapiclient.discovery
import googleapiclient.errors

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

import config

youtube = build('youtube','v3',developerKey=config.api_key)
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


#LOOKS THROUGH JSON FILE AND WRITES SONGS & YOUTUBELINKS TO TXT FILE
def songList(response, parent_dir):
    os.chdir(parent_dir)
    if not path.exists("SongListNew.txt"):
        songsnewTxt = open("SongListNew.txt","x")
    youB = ['https://www.youtube.com/watch?v=','&list=']
    songsnewTxt = open("SongListNew.txt","a")
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
    #ONLY NEED CLIENT SECRET FILE IF TRYING TO ACCESS PRIVATE DATA (i.e private Youtube playlist)
    client_secrets_file = r'C:\Coding Workspace\SongDownloader\client_secret_440876599079-lotmaj2kiqssjodtf8k31f98uee6gl7f.apps.googleusercontent.com.json'

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


def main(playlistId):

    #Creating Directories
    directory = 'Music'
    parent_dir = os.path.join('C:/', directory)
    songFolder = os.path.join(parent_dir, 'Songs') 

    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)
          
    if not os.path.exists(songFolder):
        os.mkdir(songFolder)

    os.chdir(parent_dir)
    if not os.path.exists("SongList.txt"):
        open("SongList.txt","w")

    youtube = api_response()
    # playlistId = "PLaCftlCWzVXTbo0r2nHEGvIHTMsK7LZDF" #uncomment to manually enter playlist Id
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId=playlistId
    )
    response = request.execute()
    songList(response, parent_dir)
    
    try: 
        nxtPgTokn = response['nextPageToken']
    
        #Going through all the differenent pages of results
        if nxtPgTokn:
            print("Next page token outer:",nxtPgTokn)
            while nxtPgTokn:
                request = youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    maxResults=50,
                    pageToken = nxtPgTokn,
                    playlistId=playlistId
                )
                response = request.execute()
                songList(response, parent_dir)
                try:
                    nxtPgTokn = response['nextPageToken']
                    print("Next page token inner:",nxtPgTokn)
                except KeyError:
                    print("No next page token")
                    break

    except KeyError:    
            print("No next page token")

    #SEEING DIFFERENCE BETWEEN TXT FILES
    with open('SongList.txt') as f:
        t1 = f.read().splitlines()
        t1s = set(t1)
    with open('SongListNew.txt') as f:
        t2 = f.read().splitlines()
        t2s = set(t2)
    
    
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

 #COPY SONGS FROM NEW SONGSTXT TO SONGS TXT
    os.chdir(parent_dir)
    sN=open('SongListNew.txt',"r")  
    s=open('SongList.txt','w')
    for x in sN.readlines():
        s.write(x)
    sN.close()
    s.close() 
    open('SongListNew.txt', "w").close()

    os.chdir(songFolder)

    for diff in t2s-t1s:
        with youtube_dl.YoutubeDL(download_options) as dl:
            print (t2.index(diff)+1, diff)
            # dl.download([diff]) 

class MainWindow(Screen):
    name = ObjectProperty(None)
    playlistID = ObjectProperty(None)
    # current = ""

    def downloadBtn(self):
        # sm.current = "download"
        if self.playlistID.text != "":
            playlistId = self.playlistID.text
            main(playlistId)
        else:
            print('Playlist ID cannot be empty')


class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("UI.kv")
sm = WindowManager()
sm.add_widget(MainWindow())

class MainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MainApp().run()