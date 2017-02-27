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


def get_duration(element):
    for e in element.find_all('div'):
        if 'duration' in e.get('class'):
            return e.string
    return None


def get_uploader(element):
    for e in element.find_all('a'):
        if 'username' in e.get('class'):
            return e.string
    return None


def get_title(element):
    return element.input.get('value')


def get_thumb(element):
    for e in element.find_all('div'):
        if 'myvideos_tmb' in e.get('class'):
            temp = e.get("style")
            begin_index = temp.find('(')
            end_index = temp.find(')')
            return temp[begin_index + 1: end_index]
    return None


def get_browse_token():
    response = urllib2.urlopen(BROWSE_TOKEN_URL)
    temp = response.geturl()
    begin_index = temp.find('=')
    end_index = len(temp)
    return temp[begin_index + 1: end_index]


def get_last_page(element):
    for e in element.find_all('div'):
        if e.get('class') != None:
            if 'btn_last' in e.get('class'):
                temp = e.div.get("onclick")
                begin_index = temp.find("','")
                end_index = temp.find("');")
                return temp[begin_index + 3: end_index]
    return None


def get_video_hash(video_name):
    response = urllib2.urlopen(BASE_HASH_URL + video_name)
    html = response.read()
    element = BeautifulSoup(html, 'html.parser')
    temp = element.iframe.get("src")
    begin_index = temp.find("/new/")
    end_index = temp.find("?autostart")
    return temp[begin_index + 5: end_index]


def get_video_item_list(video_hash, video_name):
    response = urllib2.urlopen(
        BASE_VIDEO_URL + video_hash + COMMON_PART + video_name)
    resp = json.loads(response.read())

    video_item_list = []

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

    obj_360p = VideoItem('360p', url_360 + "&token=" + token_360)
    video_item_list.append(obj_360p)

    if token_720 != None and url_720 != None:
        obj_720p = VideoItem('720p', url_720 + '&token=' + token_720)
        video_item_list.append(obj_720p)

    return video_item_list


def get_list_item(title, thumb, is_folder):
    list_item = xbmcgui.ListItem(label=title)
    if is_folder == False:
        list_item.setInfo('video', {'title': title, 'genre': 'none'})
    list_item.setArt({'thumb': thumb, 'icon': '', 'fanart': ''})
    list_item.setProperty('IsPlayable', 'false')
    return list_item

def play_video(video_name):
    video_item_list = get_video_item_list(get_video_hash(video_name), video_name)
    names = []
    for video_item in video_item_list:
        names.append(video_item.resolution)

    if (names.__len__ > 1):
        dialog = xbmcgui.Dialog()
        selected = dialog.select('Resolution', names)
        xbmc.Player().play(video_item_list[selected].link)
    else:
        xbmc.Player().play(video_item_list[0].link)


def list_videos(current_url, current_category, current_page):
    url = None
    navParam = None
    listing = []
    if current_category == 'browse':
        navParam = '#p_date=' + current_page + '&isAJAXrequest=1&tabToShow=TAB_0&'
    elif current_category == 'search':
        navParam = '#p_uni=' + current_page
        url = '{0}?action=open&categoryName={1}'.format(_url, 'search')
        is_folder = True
        listing.append((url, get_list_item('Search', 'none', is_folder), is_folder))

    if int(current_page) != 1:
        url = current_url + navParam
    else:
        url = current_url

    xbmc.log(msg='url=' + url, level=xbmc.LOGNOTICE)

    response = urllib2.urlopen(url)
    html = response.read()
    parsed = BeautifulSoup(html, 'html.parser')
    current_last_page = get_last_page(parsed)
    menu_item_list = []

    for link in parsed.find_all('div'):
        if (link.get('class') != None):
            if ("item_inner" in link.get('class')):
                obj = MenuItem(get_title(link), get_thumb(link),
                               get_duration(link), get_uploader(link))
                menu_item_list.append(obj)

    url = '{0}'.format(_url)
    is_folder = True
    listing.append((url, get_list_item('Back to main menu', 'none', is_folder), is_folder))

    if current_last_page != None:
        if current_last_page > 1 and int(current_page) != current_last_page:
            label = 'Next page ' + \
                str(int(current_page) + 1) + '/' + str(current_last_page)
            url = '{0}?action=nav&url={1}&category={2}&page={3}'.format(
                _url, current_url, current_category, str(int(current_page) + 1))
            is_folder = True
            listing.append((url, get_list_item(label, 'none', is_folder), is_folder))
        if current_last_page > 1 and int(current_page) > 1:
            label = 'Prev page ' + \
                str(int(current_page) - 1) + '/' + str(current_last_page)
            url = '{0}?action=nav&url={1}&category={2}&page={3}'.format(
                _url, current_url, current_category, str(int(current_page) - 1))
            is_folder = True
            listing.append((url, get_list_item(label, 'none', is_folder), is_folder))

    for menu_item in menu_item_list:
        url = '{0}?action=play&videoName={1}'.format(_url, menu_item.title)
        is_folder = False
        listing.append((url, get_list_item(menu_item.title, 'http:' + menu_item.thumb, is_folder), is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_handle)


def list_categories():
    listing = []

    for category in CATEGORIES:
        url = '{0}?action=open&categoryName={1}'.format(
            _url, category['value'])
        is_folder = True
        listing.append((url, get_list_item(category['name'], 'none', is_folder), is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def browse():
    current_url = BASE_URL + 'browse?token=' + get_browse_token()
    current_category = 'browse'
    current_page = '1'
    list_videos(current_url, current_category, current_page)


def search():
    currentSearchText = get_keyboard(heading="Enter the query")
    # if ( not currentSearchText ): return False, 0
    current_url= BASE_URL + 'search/text/' + currentSearchText.encode("utf-8") + '?channel_constraint=undefined'
    current_category = 'search'
    current_page = '1'
    list_videos(current_url, current_category, current_page)


def get_keyboard( default="", heading="", hidden=False ):
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
