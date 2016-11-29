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

_url = sys.argv[0]

_handle = int(sys.argv[1])

PLUGIN_ID = 'plugin.video.mediaklikk'
LOGO_URL = 'special://home/addons/{0}/resources/logo/'.format(PLUGIN_ID)

BASEURL = 'http://player.mediaklikk.hu/player/player-inside-full3.php?userid=mtva&streamid='
BASEURL_END = '&flashmajor=22&flashminor=0'
CHANNELS = [
    {
        'key': 'mtv1live',
        'name': 'M1',
        'icon': 'm1.png'
    },
    {
        'key': 'mtv2live',
        'name': 'M2',
        'icon': 'm2.png'
    },
    {
        'key': 'mtv4live',
        'name': 'M4',
        'icon': 'm4.png'
    },
    {
        'key': 'mtv5live',
        'name': 'M5',
        'icon': 'm5.png'
    },
    {
        'key': 'dunalive',
        'name': 'Duna',
        'icon': 'duna.png'
    },
    {
        'key': 'dunaworldlive',
        'name': 'Duna World',
        'icon': 'duna_world.png'
    }

]

RESOLUTIONS = [
	'720p', '480p', '360p', '270p', '180p'
]

#M3U = [
#	'VID_1280x720_HUN', 'VID_854x480_HUN', 'VID_640x360_HUN', 'VID_480x270_HUN', 'VID_320x180_HUN'
#]

M3U = [
	'01', '02', '03', '04', '05'
]

RESULTS = []


def generate_urls():
    for channel in CHANNELS:
        response = urllib2.urlopen(BASEURL + channel['key'] + BASEURL_END)
        html = response.read()
        begin = html.index('http://c')
        end = html.index('index.m3u8')
        url = html[begin:end]

        RESULTS.append(url)


def list_channels():
    listing = []

    i = 0
    for channel in CHANNELS:
        list_item = xbmcgui.ListItem(label=channel['name'])

        list_item.setInfo('video', {'title': channel['name'], 'genre': 'none'})

        list_item.setArt(
            {'thumb': LOGO_URL + channel['icon'], 'icon': LOGO_URL + channel['icon'], 'fanart': ''})

        list_item.setProperty('IsPlayable', 'true')

        url = '{0}?action=play&video={1}'.format(_url, RESULTS[i])

        is_folder = False

        listing.append((url, list_item, is_folder))

        i = i + 1

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def get_path(path):
    dialog = xbmcgui.Dialog()
    selected = dialog.select('Select resolution', RESOLUTIONS)
    realPath = path + M3U[selected] + '.m3u8'

    return realPath


def router(paramstring):
    params = dict(parse_qsl(paramstring))

    if params:
        if params['action'] == 'play':
            play_video(get_path(params['video']))
    else:
        list_channels()


if __name__ == '__main__':
    generate_urls()
    router(sys.argv[2][1:])
