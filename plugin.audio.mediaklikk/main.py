# -*- coding: utf-8 -*-
# Module: default
# Author: holiday
# Created on: 15.08.2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
import sys
import urllib
import urlparse
import xbmcaddon
import xbmcgui
import xbmcplugin

PLUGIN_ID = 'plugin.audio.mediaklikk'
LOGO_URL = 'special://home/addons/{0}/resources/logo/'.format(PLUGIN_ID)

BASEURL = 'http://stream002.radio.hu:80/'
CHANNELS = [
    {
        'key': 'mr1',
        'name': 'Kossuth',
        'icon': 'kossuth.png'
    },
    {
        'key': 'mr2',
        'name': 'Petőfi',
        'icon': 'petofi.png'
    },
    {
        'key': 'mr3hq',
        'name': 'Bartok',
        'icon': 'bartok.png'
    },
    {
        'key': 'mr7',
        'name': 'Danko',
        'icon': 'danko.png'
    },
    {
        'key': 'mr8',
        'name': 'Duna World',
        'icon': 'duna_world.png'
    },
    {
        'key': 'mr4',
        'name': 'Nemzetiségi',
        'icon': 'nemzetisegi.png'
    },
    {
        'key': 'mr5',
        'name': 'Parlamenti',
        'icon': 'parlamenti.png'
    }

]

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)

def list_channels():
    song_list = []
    # iterate over the contents of the dictionary songs to build the list
    for channel in CHANNELS:
        # create a list item using the song filename for the label
        li = xbmcgui.ListItem(
            label=channel['name'], thumbnailImage=LOGO_URL + channel['icon'])
        # set the fanart to the albumc cover
        li.setProperty('fanart_image', '')
        # set the list item to playable
        li.setProperty('IsPlayable', 'true')
        # build the plugin url for Kodi
        # Example:
        # plugin://plugin.audio.example/?url=http%3A%2F%2Fwww.theaudiodb.com%2Ftestfiles%2F01-pablo_perez-your_ad_here.mp3&mode=stream&title=01-pablo_perez-your_ad_here.mp3
        url = build_url({'mode': 'stream', 'url': BASEURL +
                         channel['key'] + '.mp3', 'title': ''})
        # add the current list item to a list
        song_list.append((url, li, False))
    # add list to Kodi per Martijn
    # http://forum.kodi.tv/showthread.php?tid=209948&pid=2094170#pid2094170
    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    # set the content of the directory
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)


def play_radio(url):
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)


def main():
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)

    if mode is None:
        list_channels()
    elif mode[0] == 'stream':
        play_radio(args['url'][0])


if __name__ == '__main__':
    addon_handle = int(sys.argv[1])
    main()
