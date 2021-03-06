# -*- coding: utf-8 -*-

'''
    Phoenix Add-on
    Copyright (C) 2015 Blazetamer
    Copyright (C) 2015 lambda
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Original Code by Gerrikss(structure this page only)
    Modified by  and ported for PHOENIX by VinMan_JSV 2016

'''
### Thanks to Gerikss for the structure of code
### Ported to Phoenix by VinMan_JSV 2016

import cookielib, calendar, time, json, xbmc
import re,sys,urllib,urlparse,base64,urllib2
from resources.lib.libraries import control
from resources.lib.libraries import client
from datetime import datetime, timedelta

mediaPath = control.addonInfo('path') + '/resources/media/phhuddle/'
display_status = 'true'
display_start_time = 'true'
logos ={'nba': mediaPath+'nba.png',
        'nhl': mediaPath+'nhl.png',
        'nfl': mediaPath+'nfl.png',
        'mlb': mediaPath+'mlb.png',
        'MMA': mediaPath+'mma.png'}
back = {'nba':mediaPath+'NBA-Globe.jpg',
        'nhl':mediaPath+'NHL.jpg',
        'nfl':mediaPath+'NFL.jpg',
        'MMA':mediaPath+'mma.jpg'}
def HuddleDirectory():
    addDirectoryItem('[COLOR=FF00FF00][B] NHL  [/B][/COLOR]','Huddle_Main', '0', mediaPath+'nhl.png', mediaPath+'Huddle-fanart.jpg',url='nhl')
    addDirectoryItem('[COLOR=FF00FF00][B] NBA  [/B][/COLOR]','Huddle_Main', '0', mediaPath+'nba.png', mediaPath+'Huddle-fanart.jpg',url='nba')
    addDirectoryItem('[COLOR=FF00FF00][B] NFL  [/B][/COLOR]','Huddle_Main', '0', mediaPath+'nfl.png', mediaPath+'Huddle-fanart.jpg',url='nfl')
    addDirectoryItem('[COLOR=FF00FF00][B] MLB - COMING SOON [/B][/COLOR]','Play_Main', '0', mediaPath+'icon.png', mediaPath+'Huddle-fanart.jpg',url='mlb')
    addDirectoryItem('[COLOR=FF00FF00][B] MMA  [/B][/COLOR]', 'Huddle_Sites', '0', mediaPath+'mma.png', mediaPath+'Huddle-fanart.jpg',url='MMA')
    addDirectoryItem('[COLOR=FFFFFF00][B] ARCHIVE [/COLOR][/B]', 'Archive_Main', '0', mediaPath+'archive.png', mediaPath+'Huddle-fanart.jpg','')
    endCategory()


def utc_to_local(utc_dt):
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

def GameStatus(status):
	statuses = {'pre-event':'Not started', 'mid-event':'In progress', 'post-event':'Completed'}
	if status in statuses:
		return statuses[status]
	else: return ''
	
def Huddle_Main(url, image, fanart):
    mode = url
    image = logos[mode]
    fanart = back[mode]
    try:
        murl = 'https://www.reddit.com/r/'+mode+'streams'
        today = datetime.utcnow() - timedelta(hours=8)
	today_from = str(today.strftime('%Y-%m-%d'))+'T00:00:00.000-05:00'
	today_to = str(today.strftime('%Y-%m-%d'))+'T23:59:00.000-05:00'
	result = client.request('http://www.sbnation.com/sbn_scoreboard/ajax_leagues_and_events?ranges['+mode+'][from]='+today_from+'&ranges['+mode+'][until]='+today_to)
        js = json.loads(result)
	js = js['leagues'][mode]
	if js:	
            if mode == 'nfl':
                url = murl+ '|' + 'redzone' +'vs'+ 'redzone'
                addDirectoryItem('[COLOR=FF00FF00][B]NFL Redzone[/B][/COLOR]', 'Huddle_Sites', image, image, fanart, url)
            for game in js:
                home = game['away_team']['name']
                away = game['home_team']['name']
                hs = str(game['score']['home'][game['score']['cols'].index('Total')])
                if not hs:
                        hs = '0'
                avs = str(game['score']['away'][game['score']['cols'].index('Total')])
                if not avs:
                        avs = '0'
                score = ' - '+avs+':'+hs
                start_time = game['start_time']
                try:
                        plus = False
                        st = start_time.replace('T', ' ')
                        if '+' in st:
                                plus = True
                                str_new = st.split('+')[-1]
                                st = st.replace('+'+str_new,'')
                        else:
                                str_new = st.split('-')[-1]
                                st = st.replace('-'+str_new,'')
                        str_new = str_new.split(':')[0]
                        if plus:
                                st_time_utc = datetime(*(time.strptime(st, '%Y-%m-%d %H:%M:%S')[0:6]))-timedelta(hours=int(str_new))
                        else:
                                st_time_utc = datetime(*(time.strptime(st, '%Y-%m-%d %H:%M:%S')[0:6]))+timedelta(hours=int(str_new))
                        local_game_time = utc_to_local(st_time_utc)
                        local_time_str = ' - '+local_game_time.strftime(control.region('dateshort')+' '+control.region('time').replace('%H%H','%H').replace(':%S',''))
    
                except:
                        local_time_str = ''
                status = GameStatus(game['status'])
                status = ' - '+status
                title = '[COLOR=FF00FF00][B]'+game['title'].replace(game['title'].split()[-1],'')+'[/B][/COLOR]'
                if display_start_time=='true':
                        title = title+'[COLOR=FFFFFF00]'+local_time_str+'[/COLOR]'
                if display_status=='true':
                        title = title+'[COLOR=FFFF0000]'+status+'[/COLOR]'
                if control.setting('display_score')=='true':
                        title = title+'[COLOR=FF00FFFF]'+score+'[/COLOR]'
                url = murl+ '|'+home +'vs'+away
                addDirectoryItem(title, 'Huddle_Sites', image, image, fanart, url)	
        else:
            addDirectoryItem("[COLOR=FFFF0000]No playable links...Try Later![/COLOR]", 'Play_Main', image, image, fanart)
            pass
        endDirectory()
    except:
        pass   
    

def Huddle_Sites(url, image, fanart):
    try:
        
        
        
            if url != "MMA":
            
                murl = url.split('|')
                home = murl[1].split('vs')[0]
                away = murl[1].split('vs')[1]
                url = murl[0]
                html = client.request(url)
                block_content = client.parseDOM(html, "a", attrs={"class": "comments may-blank"}, ret="href") 
                orig_title = '[COLOR=FF00FF00][B]'+away+' at '+home+'[/B][/COLOR]'
                home_f = home.lower().split()[0]
                away_f = away.lower().split()[0]
                home_l = home.lower().split()[-1]
                away_l = away.lower().split()[-1]
                link = None	
                for element in block_content:
                        if (home_f in element and (away_l in element or away_f in element)) or (home_l in element and (away_l in element or away_f in element)) or (home_f in element and home_l in element) or (away_f in element and away_l in element):
                                link = element
                                break
                        else:
                                continue
                            
            if url =="MMA":
                    fanart = back['MMA']
                    link = 'https://www.reddit.com/r/MMAStreams/'
                    html = client.request(link)
                    result = client.parseDOM(html, 'p', attrs={'class': 'title'})
                    channel = client.parseDOM(result, 'a', ret='href')
                    for item in channel:
                            if ('fight') in item:
                                link = 'https://www.reddit.com/'+item
                                break
                            else:
                                continue
                    if not ('fight') in link:addDirectoryItem("[COLOR=FFFF0000]No live event right now...Try Later![/COLOR]", 'Play_Main', image, image, fanart)
            if link:   
                html = client.request(link)
                content = client.parseDOM(html, "a", ret="href")
                cont = client.parseDOM(html, "p")
                ct = client.parseDOM(html, "code")
                urls = []
                for el in content:
                           
                        if 'blabseal.com' in el:
                                url = Blabseal(el)
                                if url and url not in urls:
                                        addDirectoryItem('Blabseal.com', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif '1apps.com' in el:
                                url = Oneapp(el)
                                if url and url not in urls:
                                        addDirectoryItem('Oneapp', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'youtu' in el and 'channel' not in el and 'list' not in el:
                                url = GetYoutube(el)
                                if url and url not in urls:
                                        addDirectoryItem('Youtube.com', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'freecast.in' in el:
                                url = Freecastin(el)
                                if url and url not in urls:
                                        addDirectoryItem('Freecast.in', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'streamboat.tv' in el:
                                url = Streambot(el)
                                if url and url not in urls:
                                        addDirectoryItem('Streamboat.tv', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'nbastream.net' in el:
                                url = Nbanhlstreams(el)
                                if url and url not in urls:
                                        addDirectoryItem('Nbastream.net', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'nhlstream.net' in el:
                                url = Nbanhlstreams(el)
                                if url and url not in urls:
                                        addDirectoryItem('Nhlstream.net', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'livenflstream.net' in el:
                                url = Nbanhlstreams(el)
                                if url and url not in urls:
                                        addDirectoryItem('Livenflstream.net', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'fs.anvato.net' in el:
                                url = Getanvato(el)
                                if url and url not in urls:
                                        addDirectoryItem('Fox ToGo (US IP Only)', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'streamsarena.eu' in el:
                                url = Streamarena(el)
                                if url and url not in urls:
                                        addDirectoryItem('Streamsarena.eu', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'streamup.com' in el and 'm3u8' not in el:
                                url = GetStreamup(el.split('/')[3])
                                if url and url not in urls:
                                        addDirectoryItem('Streamup.com', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'torula' in el:
                                url = Torula(el)
                                if url and url not in urls:
                                        addDirectoryItem('Torula.us', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'gstreams.tv' in el:
                                url = Gstreams(el)
                                if url and url not in urls:
                                        addDirectoryItem('Gstreams.tv', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'nfl-watch.com/live/watch' in el or 'nfl-watch.com/live/-watch' in el or 'nfl-watch.com/live/nfl-network' in el:
                                url = Nflwatch(el)
                                if url and url not in urls:
                                        addDirectoryItem('Nfl-watch.com', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'ducking.xyz' in el:
                                url = Ducking(el)
                                if url and url not in urls:
                                        addDirectoryItem('Ducking.xyz', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'streamandme' in el:
                                url = Streamandme(el)
                                if url and url not in urls:
                                        addDirectoryItem('Streamandme', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'mursol.moonfruit.com' in el:
                                url = Moonfruit(el)
                                if url and url not in urls:
                                        addDirectoryItem('Moonfruit', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'room' in el and 'm3u8' in el:
                                url = Getroom(el)
                                if url and url not in urls:
                                        addDirectoryItem('Room HD', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                        elif 'm3u8' in el and 'room' not in el and 'anvato' not in el and 'turner.com' not in el:
                                url = el
                                if url and url not in urls:
                                        addDirectoryItem('M3U8 stream', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)            
                for el in cont:
                        if '101livesportsvideos.com' in el and 'SD' not in el and 'ace' not in el:
                                url = Livesports101(el)
                                if url and url not in urls:
                                        addDirectoryItem('101livesportsvideos.com', 'Play_Main',image, image,fanart, url)
                                        urls.append(url)
                for el in ct:
                        if 'turner.com' in el and el not in urls:
                                try:
                                        timest = el.split("exp=")[-1].split("~acl")[0]
                                        time_exp = datetime.fromtimestamp(int(timest)).strftime(control.region('time').replace('%H%H','%H').replace(':%S',''))
                                except:
                                        time_exp = ''
                                addDirectLink('Turner HD (external player) link expires '+time_exp, {'Title': orig_title}, el)
                                urls.append(el)		
                                    
            else:
            
                addDirectoryItem("[COLOR=FFFF0000]Could not find playable link[/COLOR]", 'Play_Main', image, image, fanart)
            endDirectory()
    except:
        pass
    
def GetStreamup(channel):
	try:
		req = client.request('https://api.streamup.com/v1/channels/'+channel)
		chan = json.loads(req)
		if chan['channel']['live']:
			return 'https://video-cdn.streamup.com/app/'+chan['channel']['capitalized_slug'].lower()+'/playlist.m3u8'
	except:
		return None	

def GetYoutube(url):
	try:
		regex = (r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
		youtube_regex_match = re.match(regex, url)
		videoId = youtube_regex_match.group(6)
		link = 'plugin://plugin.video.youtube/?action=play_video&videoid=' + videoId
		return link
	except:
		return None
		
def Getanvato(url):
	try:
		if 'master' in url:
			return url
		else:	 
			lst = url.split('/')
			link = url.replace(lst[len(lst)-2],'4028k')
			return link
	except:
		return None
		
def Getroom(url):
	try:
		if 'master' in url:
			return url
		else:	 
			lst = url.split('/')
			link = url.replace(lst[len(lst)-2],'4028k')
			return link
	except:
		return url
		
def Blabseal(url):
	try:
		html = client.request(url)
		block_content = client.parseDOM(html, "iframe", attrs={"name": "thebox"}, ret="src")[0]
		link = GetYoutube(block_content)
		return link
	except:
		return None
		
def Rawstreams(url):
	try:
		html = client.request(url)
		block_content = client.parseDOM(html, "input", ret="value")
		return block_content
	except:
		return None
		
def Oneapp(url):
	try:
		html = client.request(url)
		block_content = client.parseDOM(html, "iframe", ret="src")[0]
		link = GetYoutube(block_content)
		return link
	except:
		return None
		
def Torula(url):
	try:
		html = client.request(url)
		block_content = client.parseDOM(html, "input", attrs={"id": "vlc"}, ret="value")[0]
		link = block_content
		return link
	except:
		return None

def Freecastin(url):
	try:
		html = client.request(url)
		block_content = client.parseDOM(html, "iframe", attrs={"width": "100%"}, ret="src")[0]
		link = GetYoutube(block_content)
		return link
	except:
		return None
		
def Streambot(url):
	try:
		cookieJar = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar), urllib2.HTTPHandler())
		conn = urllib2.Request('https://streamboat.tv/signin')
		connection = opener.open(conn)
		for cookie in cookieJar:
			token = cookie.value
		headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Cookie":"_gat=1; csrftoken="+token+"; _ga=GA1.2.943051497.1450922237",
            "Origin":"https://streamboat.tv",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8,bg;q=0.6,it;q=0.4,ru;q=0.2,uk;q=0.2",
            "Accept-Encoding" : "windows-1251,utf-8;q=0.7,*;q=0.7",
            "Referer": "https://streamboat.tv/signin"
		}
		reqData = {'csrfmiddlewaretoken':token,'username' : 'test_user', 'password' : 'password'}
		conn = urllib2.Request('https://streamboat.tv/signin', urllib.urlencode(reqData), headers)
		connection = opener.open(conn)
		conn = urllib2.Request(url)
		connection = opener.open(conn)
		html = connection.read()
		connection.close()
		block_content = client.parseDOM(html, "source", attrs={"type": "application/x-mpegURL"}, ret="src")[0]
		link = block_content
		return link
	except:
		return None

def Nbanhlstreams(url):
	try:
		if 'nba' in url:
			URL = 'http://www.nbastream.net/'
		elif 'nhl' in url:
			URL = 'http://www.nhlstream.net/'
		elif 'nfl' in url:
			URL = 'http://www.livenflstream.net/'
		html = client.request(url)
		link = client.parseDOM(html, "iframe",  ret="src")[0]
		html  = client.request(URL+link)
		link = client.parseDOM(html, "iframe",  ret="src")[0]
		if 'streamup' in link:
			channel = link.split('/')[3]
			link = GetStreamup(channel)
			return link
	except:
		return None
		
def Streamandme(url):
	try:
		html = client.request(url)
		link = client.parseDOM(html, "iframe",  ret="src")[0]
		channel = link.split('/')[3]
		link = GetStreamup(channel)
		return link
	except:
		return None

def Gstreams(url):
	try:
		html = client.request(url)
		link = client.parseDOM(html, "iframe",  ret="src")[0]
		if 'gstreams.tv' in link:
			html  = client.request(link)
			link = html.split('https://')[1]
			link = link.split("'")[0]
			link = 'https://' + link 
			return link
		elif 'streamup.com' in link:
			channel = link.split('/')[3]
			link = GetStreamup(channel)
			return link
		elif 'youtu' in link:
			link = GetYoutube(link)
			return link
	except:
		return None
		
def Moonfruit(url):
	try:
		cookieJar = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar), urllib2.HTTPHandler())
		conn = urllib2.Request(url+'/htown3')
		connection = opener.open(conn)
		for cookie in cookieJar:
			token = cookie.value
		headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Cookie":"markc="+token,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8,bg;q=0.6,it;q=0.4,ru;q=0.2,uk;q=0.2",
		}
		html = connection.read()
		link = client.parseDOM(html, "iframe",  ret="src")
		link = url+link[-1]
		conn = urllib2.Request(link, headers=headers)
		connection = opener.open(conn)
		html = connection.read()
		link = client.parseDOM(html, "iframe",  ret="src")[0]
		if 'streamup.com' in link:
			channel = link.split('/')[4]
			link = GetStreamup(channel)
			return link
	except:
		return None

def Nflwatch(url):
	try:
		html = client.request(url)
		links = client.parseDOM(html, "iframe",  ret="src")
		for link in links:
			if 'streamup' in link:
				channel = link.split('/')[3]
				link = GetStreamup(channel)
				return link
			else:
				continue
		if 'p2pcast.tv' in html:
			agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
			id = html.split("'text/javascript'>id='")[-1]
			id = id.split("';")[0]
			url = 'http://p2pcast.tv/stream.php?id='+id+'&live=0&p2p=0&stretching=uniform'
			request = urllib2.Request(url)
			request.add_header('User-Agent', agent)
			request.add_header('Referer', url)
			response = urllib2.urlopen(request)
			html = response.read()
			token = html.split('murl = "')[1].split('";')[0]
			link = base64.b64decode(token)
			request = urllib2.Request('http://p2pcast.tv/getTok.php')
			request.add_header('User-Agent', agent)
			request.add_header('Referer', url)
			request.add_header('X-Requested-With', 'XMLHttpRequest')
			response = urllib2.urlopen(request)
			html = response.read()
			js = json.loads(html)
			tkn = js['token']
			link = link+tkn
			link = link + '|User-Agent='+agent+'&Referer='+url
			return link
	except:
		return None

def Ducking(url):
	try:
		request = urllib2.Request('http://www.ducking.xyz/kvaak/stream/basu.php')
		request.add_header('Referer', 'www.ducking.xyz/kvaak/')
		request.add_header('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36')
		response = urllib2.urlopen(request)
		html = response.read()
		link = client.parseDOM(html, "iframe", ret="src")[0]
		channel = link.split('/')[3]
		link = GetStreamup(channel)
		return link
	except:
		return None
		
def Streamarena(url):
	try:
		html = client.request(url)
		link = client.parseDOM(html, "iframe",  ret="src")[1]
		link = link.replace('..','http://www.streamsarena.eu/')
		html  = client.request(link)
		link = client.parseDOM(html, "iframe",  ret="src")[0]
		channel = link.split('/')[3]
		link = GetStreamup(channel)
		return link
	except:
		return None
		
def Livesports101(url):
	try:
		url = url.split('</strong>')[0]
		url = 'http://101'+url.split('101')[1]
		html = client.request(url)
		block_content = client.parseDOM(html, "meta", attrs={"property": "og:description"}, ret="content")
		for el in block_content:
			if 'youtube.com' in el:
				link = GetYoutube(block_content)
				return link
			elif 'streamboat.tv' in el:
				link = el
				link = link.split('http://')[1]
				link = link.split("'")[0]
				link = 'http://' + link 
				return link
			elif 'streamup' in el:
				link = el
				link = link.split('https://')[1]
				link = link.split("'")[0]
				link = 'https://' + link 
				return link
		block_content = client.parseDOM(html, "embed", attrs={"id": "vlcp"}, ret="target")[0]
		if 'streamboat' in block_content or 'streamup' in block_content:
			link = block_content
			return link
	except:
		return None
      

def Archive_Main(url, image, fanart):
    addDirectoryItem('[COLOR=FFFFFF00][B] NHL Archive [/B][/COLOR]','NHL_ARC', '0', mediaPath+'nhl.png', mediaPath+'Huddle-fanart.jpg', url="nhlarch")
    addDirectoryItem('[COLOR=FFFFFF00][B] NBA Archive [/B][/COLOR]','NBANFL_ARC', '0', mediaPath+'nba.png', mediaPath+'Huddle-fanart.jpg', url="nbaarch")
    addDirectoryItem('[COLOR=FFFFFF00][B] NFL Archive [/B][/COLOR]','NBANFL_ARC', '0', mediaPath+'nfl.png', mediaPath+'Huddle-fanart.jpg', url="nflarch")
    addDirectoryItem('[COLOR=FFFFFF00][B] MLB Archive - COMING SOON [/B][/COLOR]','Play_Main', '0', mediaPath+'icon.png', mediaPath+'Huddle-fanart.jpg', url="mlbarch")
    
    endCategory()

def NBANFL_ARC(url, image, fanart):
    try:
        if 'nbaarch' in url or 'nflarch' in url:
            page = '1'
        else:
            url = url.split('/')
            page = url[1]
            url = url[0]
        if url == 'nbaarch' or url == 'nba':
            fanart = back['nba']
            image = logos['nba']
            url = 'http://www.life2sport.com/category/basketbol/nba/page/'+str(page)
        elif url == 'nflarch' or url == 'nfl':
            fanart = back['nfl']
            image = logos['nfl']
            url = 'http://www.life2sport.com/category/american-football/page/'+str(page)
        html = client.request(url)
        links = client.parseDOM(html, "a", attrs={"rel": "bookmark"}, ret="href")
        titles = client.parseDOM(html, "a", attrs={"rel": "bookmark"}, ret="title")
        del links[1::2]
        for i, el in enumerate(links):
                if '-nba-' in el or '-nfl-' in el:
                        title = client.parseDOM(html, "a", attrs={"href": el}, ret="title")[0]
                        title = title.split('/')[-1]+' - '+title.split('/')[len(title.split('/'))-2]
                        addDirectoryItem(title, 'NBANFL_Stream', image, image, fanart,url=el)
        page =  str(int(page)+1)
        if re.search ('-nba-',str(links)):addDirectoryItem("next page...",'NBANFL_ARC',image,image,fanart,url='nba'+'/'+page)
        if re.search ('-nfl-',str(links)):addDirectoryItem("next page...",'NBANFL_ARC',image,image,fanart,url='nfl'+'/'+page)
        
        endDirectory()
    except:
        pass
    
def NHL_ARC(url,image,fanart):
    fanart = back['nhl']
    image = logos['nhl']
    try:
        if re.search('/',str(url)):
            url = url.split('/')
            page = url[1]
            url = url[0]
        else:
            page ='1'
        url = 'http://rutube.ru/api/video/person/979571/?page='+str(page)+'&format=json'
        html = client.request(url)
        js = json.loads(str(html))
        js = js['results']
        for el in js:
            title = el['title']
            id = el['id']
            img = el['thumbnail_url']
            
            addDirectoryItem(title, 'NHL_Stream', image, image, fanart,url=id)
        page =  str(int(page)+1)
        addDirectoryItem("next page...", 'NHL_ARC', image,image,fanart,url='nhl'+'/'+page)
        endDirectory()
    except:
        pass

def NBANFL_Stream(url,image,fanart):
    try:
        title = control.infoLabel('ListItem.Label')
        html = client.request(url)
        html = html.split('>english<')[-1]
        link = client.parseDOM(html, "iframe", ret="src")[0]
        link = link.replace('https://videoapi.my.mail.ru/videos/embed/mail/','http://videoapi.my.mail.ru/videos/mail/')
        link = link.replace('html','json')
        cookieJar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar), urllib2.HTTPHandler())
        conn = urllib2.Request(link)
        connection = opener.open(conn)
        f = connection.read()
        connection.close()
        js = json.loads(f)
        for cookie in cookieJar:
                token = cookie.value
        js = js['videos']
        for el in js:
                addDirectoryItem(title, 'Play_Main',image,image,fanart,url=el['url']+'|Cookie=video_key='+token)
        endDirectory()    
    except:
        pass
    
def NHL_Stream(url):
    try:
        url = 'http://rutube.ru/api/play/options/'+url+'?format=json'
        html = client.request(url)
        js = json.loads(html)
        url = js['video_balancer']['m3u8']
        player().run(url)
    except:
        pass
    
def Play_Main(url):
    print url
    try:
        control.idle()
        
        player().run(url)
    except:
        return



def addDirectoryItem(name, action, thumb, image, fanart, url='0'):
    if thumb == '0': thumb = image
    u = '%s?action=%s&url=%s&image=%s&fanart=%s' % (sys.argv[0], str(action), urllib.quote_plus(url), urllib.quote_plus(thumb), urllib.quote_plus(fanart))
    item = control.item(name, iconImage=thumb, thumbnailImage=thumb)
    item.addContextMenuItems([], replaceItems=False)
    item.setProperty('Fanart_Image', fanart)
    control.addItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True)


def endDirectory():
    control.directory(int(sys.argv[1]), cacheToDisc=True)


def endCategory():
    if control.skin == 'skin.confluence': control.execute('Container.SetViewMode(500)')
    control.directory(int(sys.argv[1]), cacheToDisc=True)


def movieCategory():
    control.content(int(sys.argv[1]), 'movies')
    if control.skin == 'skin.confluence': control.execute('Container.SetViewMode(500)')
    control.directory(int(sys.argv[1]), cacheToDisc=True)


def episodeCategory():
    control.content(int(sys.argv[1]), 'episodes')
    control.directory(int(sys.argv[1]), cacheToDisc=True)


def addDirectLink(title, infoLabels, url, iconImg="DefaultVideo.png"):
    item = control.item(title, iconImage=iconImg, thumbnailImage=iconImg)
    item.setInfo(type='Video', infoLabels=infoLabels)
    control.addItem(handle=int(sys.argv[1]), url=url, listitem=item)
                                
class player(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)

    def run(self, url):
        title = control.infoLabel('ListItem.Label')
        image = control.infoLabel('ListItem.Icon')
        item = control.item(path=url, iconImage=image, thumbnailImage=image)
        item.setInfo(type='Video', infoLabels = {'title': title})
        control.player.play(url, item)

        for i in range(0, 240):
            if self.isPlayingVideo(): break
            control.sleep(1000)

    def onPlayBackStarted(self):
        control.sleep(200)
        control.idle()


