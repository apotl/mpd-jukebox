import unicodedata
from mpd import MPDClient
from flask import Flask, request
app = Flask(__name__)

mpd_root = '/music'
mpd_db_loc = mpd_root + '/db' # where users can browse files
mpd_q_loc = mpd_root + '/queue' # where queueing post requests go
mpd_skip_loc = mpd_root + '/skip' # where skip requests go


def connect_to_mpd():
	jukebox = MPDClient()
	jukebox.timeout = 10
	jukebox.idletimeout = None
	jukebox.connect( "localhost", 6600)
	return jukebox

setup = connect_to_mpd()
setup.consume( 1)
setup.random( 0)
setup.repeat( 0)
setup.setvol( 100)
setup.close()

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
	jukebox.close()
	return mem

def get_listing_info( listing, tag):
	if tag in listing:
		return listing[tag]
	return '(no ' + tag + ')'

def get_current_song():
	jukebox = connect_to_mpd()
	if len( jukebox.currentsong()) == 0:
		jukebox.close()
		return "No song is playing."
	song = jukebox.currentsong()['artist'] + ' - ' + jukebox.currentsong()['title']
	jukebox.close()
	return song

@app.route( mpd_db_loc + '/<path:directory>')
def route_music_directory( directory):
	page = 'Now playing: ' + get_current_song() + '<br>'
	page += 'ACTION: <a href="' + mpd_skip_loc + '">Skip current song</a><br><br>'
	return page + grab_mpd_info( directory)

@app.route( mpd_db_loc + '/<path:directory>/')
def route_music_directory_s( directory):
	page = 'Now playing: ' + get_current_song() + '<br>'
	page += 'ACTION: <a href="' + mpd_skip_loc + '">Skip current song</a><br><br>'
	return page + grab_mpd_info( directory)

@app.route( mpd_db_loc)
def route_music():
	page = 'Now playing: ' + get_current_song() + '<br>'
	page += 'ACTION: <a href="' + mpd_skip_loc + '">Skip current song</a><br><br>'
	return page + grab_mpd_info( u'/')

@app.route( mpd_db_loc + '/')
def route_music_s():
	page = 'Now playing: ' + get_current_song() + '<br>'
	page += 'ACTION: <a href="' + mpd_skip_loc + '">Skip current song</a><br><br>'
	return page + grab_mpd_info( u'/')

@app.route( mpd_q_loc)
def route_music_queue():
	jukebox = connect_to_mpd()
	song = request.args.get( 'song')
	jukebox.add( song)
	if jukebox.status()['state'] != 'play':
		jukebox.play( 0)
	jukebox.close()
	return '"' + song + '" successfully queued.  <a href="' + mpd_db_loc + '">Return to the song listings.</a>'

@app.route( mpd_q_loc + '/')
def route_music_queue_s():
	jukebox = connect_to_mpd()
	song = request.args.get( 'song')
	jukebox.add( song)
	if jukebox.status()['state'] != 'play':
		jukebox.play( 0)
	jukebox.close()
	return '"' + song + '" successfully queued.  <a href="' + mpd_db_loc + '">Return to the song listings.</a>'

@app.route( mpd_skip_loc)
def route_music_skip():
	jukebox = connect_to_mpd()
	if jukebox.status()['playlistlength'] == '0':
		jukebox.close()
		return 'ERROR: no songs in the playlist to skip.  <a href="' + mpd_db_loc + '">Return to the song listings.</a>'
	jukebox.delete( 0)
	jukebox.close()
	return 'Current song successfully skipped.  <a href="' + mpd_db_loc + '">Return to the song listings.</a>'

@app.route( mpd_skip_loc + '/')
def route_music_skip_s():
	jukebox = connect_to_mpd()
	if jukebox.status()['playlistlength'] == '0':
		jukebox.close()
		return 'ERROR: no songs in the playlist to skip.  <a href="' + mpd_db_loc + '">Return to the song listings.</a>'
	jukebox.delete( 0)
	jukebox.close()
	return 'Current song successfully skipped.  <a href="' + mpd_db_loc + '">Return to the song listings.</a>'

if __name__ == '__main__':
	app.run( host = '0.0.0.0')
