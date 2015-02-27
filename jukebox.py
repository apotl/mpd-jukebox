import unicodedata
from mpd import MPDClient
from flask import Flask
app = Flask(__name__)

mpd_root = '/music'
mpd_db_loc = mpd_root + '/db' # where users can browse files
mpd_q_loc = mpd_root + '/queue' # where queueing post requests go

def connect_to_mpd():
	jukebox = MPDClient()
	jukebox.timeout = 10
	jukebox.idletimeout = None
	jukebox.connect( "localhost", 6600)
	return jukebox

def grab_mpd_info( directory):
	directory = unicodedata.normalize( 'NFKD', directory).encode( 'utf-8', 'ignore')
	jukebox = connect_to_mpd()
	mem = ''
	for listing in jukebox.lsinfo( directory):
		if 'directory' in listing:
			mem += 'DIR: '
			mem += '<a href="' + mpd_db_loc + '/' + listing['directory'] + '">'
			mem += listing['directory'] + '</a>'
		else:
			mem += 'SNG: '
			mem += '<a href="' + mpd_q_loc + '?song=' + get_listing_info( listing, 'file') + '">'
			mem += get_listing_info( listing, 'artist') + ' - ' + get_listing_info( listing, 'title') + '</a>'
		mem += '<br>'
	return mem

def get_listing_info( listing, tag):
	if tag in listing:
		return listing[tag]
	return '(no ' + tag + ')'

@app.route( mpd_db_loc + '/<path:directory>')
def route_music_directory( directory):
	return grab_mpd_info( directory)

@app.route( mpd_db_loc + '/<path:directory>/')
def route_music_directory( directory):
	return grab_mpd_info( directory)

@app.route( mpd_db_loc)
def route_music():
	return grab_mpd_info( u'/')

@app.route( mpd_db_loc + '/')
def route_music():
	return grab_mpd_info( u'/')

if __name__ == '__main__':
	app.run( host = '0.0.0.0')
