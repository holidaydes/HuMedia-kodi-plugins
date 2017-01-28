# -*- coding: utf-8 -*-
# Module: default
# Author: holiday
# Created on: 14.08.2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import urllib2
from bs4 import BeautifulSoup

_url = sys.argv[0]

_handle = int(sys.argv[1])

PLUGIN_ID = 'plugin.video.mediaklikk'
LOGO_URL = 'special://home/addons/{0}/resources/logo/'.format(PLUGIN_ID)

BASE_URL = 'http://indavideo.hu/'
searchText = 'vándorló palota'
channelConstrait = 'undefined'
url = BASE_URL + 'search/text/' + searchText + '?channel_constraint=' + channelConstrait

class MenuItem:
    def __init__(self, title, thumb, duration, uploader):
        self.title = title
        self.thumb = thumb
        self.duration = duration
        self.uploader = uploader

def getDuration( element ):
    for e in element.find_all('div'):
        if 'duration' in e.get('class'):
            return e.string
    return "None"

def getUploader( element ):
    for e in element.find_all('a'):
        if 'username' in e.get('class'):
            return e.string
    return "None"

def getTitle( element ):
    return element.input.get('value')

def getThumb( element ):
    for e in element.find_all('div'):
        if 'myvideos_tmb' in e.get('class'):
            temp = e.get("style")
            beginIndex = temp.find('(')
            endIndex = temp.find(')')
            return temp[beginIndex + 1 : endIndex]
    return "None"


def list_videos():
	response = urllib2.urlopen(url)
	html = response.read()
	parsed = BeautifulSoup(html, 'html.parser')

	menuItemList = []

	for link in parsed.find_all('div'):
        if (link.get('class') != None):
            if ("item_inner" in link.get('class')):
                obj = MenuItem(getTitle(link), getThumb(link), getDuration(link), getUploader(link))
                menuItemList.append(obj)

    listing = []
	i = 0
	for o in menuItemList:
		list_item = xbmcgui.ListItem(label=o.title)
		list_item.setInfo('video', {'title': o.title, 'genre': 'none'})
		list_item.setArt({'thumb': "http://indavideo.hu" + o.thumb, 'icon': '', 'fanart': ''})
		list_item.setProperty('IsPlayable', 'false')
		url = '{0}?action=play&video={1}'.format(_url, o.title)
		is_folder = False
		listing.append((url, list_item, is_folder))
		i = i + 1

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def router(paramstring):
    params = dict(parse_qsl(paramstring))

    if params:
        if params['action'] == 'play':
            play_video(get_path(params['video']))
    else:
        list_channels()


if __name__ == '__main__':
    list_videos()
    router(sys.argv[2][1:])
