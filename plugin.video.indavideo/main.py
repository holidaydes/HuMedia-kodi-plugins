# -*- coding: utf-8 -*-
# Module: default
# Author: holiday
# Created on: 14.08.2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urlparse import parse_qsl
import json
import xbmc
import xbmcgui
import xbmcplugin
import urllib2
from bs4 import BeautifulSoup

_url = sys.argv[0]

_handle = int(sys.argv[1])

PLUGIN_ID = 'plugin.video.mediaklikk'
LOGO_URL = 'special://home/addons/{0}/resources/logo/'.format(PLUGIN_ID)
# constans
BASE_URL = 'http://indavideo.hu/'
BASE_HASH_URL = 'http://indavideo.hu/videobox_request?url_title='
BASE_VIDEO_URL = 'http://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData/'
BROWSE_TOKEN_URL = 'https://daemon.indapass.hu/http/session_request?redirect_to=http%3A%2F%2Findavideo.hu%2Fbrowse&partner_id=indavideo'
COMMON_PART = '/12////?http%3A%2F%2Findavideo.hu%2Fvideo%2F'
CATEGORIES = [{'name': 'Browse', 'value': 'browse'}, {
    'name': 'Search', 'value': 'search'}, {'name': 'User', 'value': 'user'}]


class MenuItem:

    def __init__(self, title, thumb, duration, uploader):
        self.title = title
        self.thumb = thumb
        self.duration = duration
        self.uploader = uploader


class VideoItem:

    def __init__(self, resolution, link):
        self.resolution = resolution
        self.link = link


def getDuration(element):
    for e in element.find_all('div'):
        if 'duration' in e.get('class'):
            return e.string
    return None


def getUploader(element):
    for e in element.find_all('a'):
        if 'username' in e.get('class'):
            return e.string
    return None


def getTitle(element):
    return element.input.get('value')


def getThumb(element):
    for e in element.find_all('div'):
        if 'myvideos_tmb' in e.get('class'):
            temp = e.get("style")
            beginIndex = temp.find('(')
            endIndex = temp.find(')')
            return temp[beginIndex + 1: endIndex]
    return None


def getBrowseToken():
    response = urllib2.urlopen(BROWSE_TOKEN_URL)
    temp = response.geturl()
    beginIndex = temp.find('=')
    endIndex = len(temp)
    return temp[beginIndex + 1: endIndex]


def getLastPage(element):
    for e in element.find_all('div'):
        if e.get('class') != None:
            if 'btn_last' in e.get('class'):
                temp = e.div.get("onclick")
                beginIndex = temp.find("','")
                endIndex = temp.find("');")
                return temp[beginIndex + 3: endIndex]
    return None


def getVideoHash(videoName):
    response = urllib2.urlopen(BASE_HASH_URL + videoName)
    html = response.read()
    element = BeautifulSoup(html, 'html.parser')
    temp = element.iframe.get("src")
    beginIndex = temp.find("/new/")
    endIndex = temp.find("?autostart")
    return temp[beginIndex + 5: endIndex]


def getVideoItemList(videoHash, videoName):
    response = urllib2.urlopen(
        BASE_VIDEO_URL + videoHash + COMMON_PART + videoName)
    resp = json.loads(response.read())

    videoItemList = []

    token_360 = resp["data"]["filesh"]["360"]
    token_720 = None
    try:
        token_720 = resp["data"]["filesh"]["720"]
    except KeyError:
        print "There is no 720 token"

    url_360 = resp["data"]["video_files"][0]
    url_720 = None
    try:
        url_720 = resp["data"]["video_files"][1]
        if '.360.' in url_720:
            url_720 = None
    except IndexError:
        print "There is no 720 url"

    obj360p = VideoItem('360p', url_360 + "&token=" + token_360)
    videoItemList.append(obj360p)

    if token_720 != None and url_720 != None:
        obj720p = VideoItem('720p', url_720 + '&token=' + token_720)
        videoItemList.append(obj720p)

    return videoItemList


def play_video(videoName):
    videoItemList = getVideoItemList(getVideoHash(videoName), videoName)
    names = []
    for videoItem in videoItemList:
        names.append(videoItem.resolution)

    if (names.__len__ > 1):
        dialog = xbmcgui.Dialog()
        selected = dialog.select('Resolution', names)
        xbmc.Player().play(videoItemList[selected].link)
    else:
        xbmc.Player().play(videoItemList[0].link)


def list_videos(currentUrl, currentCategory, currentPage):
    url = None
    navParam = None
    if currentCategory == 'browse':
        navParam = '#p_date=' + currentPage + '&isAJAXrequest=1&tabToShow=TAB_0&'
    elif currentCategory == 'search':
        navParam = '#p_uni='
        list_item = xbmcgui.ListItem(label='Search')
        list_item.setArt({'thumb': 'none', 'icon': '', 'fanart': ''})
        list_item.setProperty('IsPlayable', 'false')
        url = '{0}?action=open&categoryName={1}'.format(_url, 'search')
        is_folder = True
        listing.append((url, list_item, is_folder))

    if int(currentPage) != 1:
        url = currentUrl + navParam
    else:
        url = currentUrl

    #xbmc.log(msg='url is null', level=xbmc.LOGNOTICE)

    response = urllib2.urlopen(url)
    html = response.read()
    parsed = BeautifulSoup(html, 'html.parser')
    currentLastPage = getLastPage(parsed)
    menuItemList = []

    for link in parsed.find_all('div'):
        if (link.get('class') != None):
            if ("item_inner" in link.get('class')):
                obj = MenuItem(getTitle(link), getThumb(link),
                               getDuration(link), getUploader(link))
                menuItemList.append(obj)

    listing = []

    list_item = xbmcgui.ListItem(label='Back to main menu')
    list_item.setArt({'thumb': 'none', 'icon': '', 'fanart': ''})
    list_item.setProperty('IsPlayable', 'false')
    url = '{0}'.format(_url)
    is_folder = True
    listing.append((url, list_item, is_folder))

    if currentLastPage != None:
        if currentLastPage > 1 and int(currentPage) != currentLastPage:
            label = 'Next page ' + \
                str(int(currentPage) + 1) + '/' + str(currentLastPage)
            list_item = xbmcgui.ListItem(label=label)
            list_item.setArt({'thumb': 'none', 'icon': '', 'fanart': ''})
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=nav&url={1}&category={2}&page={3}'.format(
                _url, currentUrl, currentCategory, str(int(currentPage) + 1))
            is_folder = True
            listing.append((url, list_item, is_folder))
        if currentLastPage > 1 and int(currentPage) > 1:
            label = 'Prev page ' + \
                str(int(currentPage) - 1) + '/' + str(currentLastPage)
            list_item = xbmcgui.ListItem(label=label)
            list_item.setArt({'thumb': 'none', 'icon': '', 'fanart': ''})
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=nav&url={1}&category={2}&page={3}'.format(
                _url, currentUrl, currentCategory, str(int(currentPage) - 1))
            is_folder = True
            listing.append((url, list_item, is_folder))

    for menuItem in menuItemList:
        list_item = xbmcgui.ListItem(label=menuItem.title)
        list_item.setInfo('video', {'title': menuItem.title, 'genre': 'none'})
        list_item.setArt(
            {'thumb': "http:" + menuItem.thumb, 'icon': '', 'fanart': ''})
        list_item.setProperty('IsPlayable', 'false')
        url = '{0}?action=play&videoName={1}'.format(_url, menuItem.title)
        is_folder = False
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_handle)


def list_categories():
    listing = []

    for category in CATEGORIES:
        list_item = xbmcgui.ListItem(label=category['name'])
        list_item.setArt({'thumb': '', 'icon': '', 'fanart': ''})
        list_item.setProperty('IsPlayable', 'false')
        url = '{0}?action=open&categoryName={1}'.format(
            _url, category['value'])
        is_folder = True
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def browse():
    currentUrl = BASE_URL + 'browse?token=' + getBrowseToken()
    currentCategory = 'browse'
    currentPage = '1'
    list_videos(currentUrl, currentCategory, currentPage)


def search():
    currentSearchText = _get_keyboard(heading="Enter the query")
    # if ( not currentSearchText ): return False, 0
    currentUrl= BASE_URL + 'search/text/' + currentSearchText.encode("utf-8") + '?channel_constraint=undefined'
    currentCategory = 'search'
    currentPage = '1'
    list_videos(currentUrl, currentCategory, currentPage)


def _get_keyboard( default="", heading="", hidden=False ):
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return unicode( keyboard.getText(), "utf-8" )
    return default


def router(paramstring):
    params = dict(parse_qsl(paramstring))

    if params:
        if params['action'] == 'play':
            play_video(params['videoName'])
        if params['action'] == 'open':
            if params['categoryName'] == 'browse':
                browse()
            elif params['categoryName'] == 'search':
                search()
        if params['action'] == 'nav':
            list_videos(params['url'], params['category'], params['page'])
    else:
        list_categories()


if __name__ == '__main__':
    router(sys.argv[2][1:])
