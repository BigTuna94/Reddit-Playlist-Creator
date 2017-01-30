#!/ussr/bin/python

import gmusicapi, praw, time, sys

"""
A supporting function to avoid more complicated logic.
"""
def dumbIndexOf(passed_str, passed_char):
	try: # attempt to get the actual index of the char
		return passed_str.index(passed_char)
	except ValueError: # just return length of string 
		return len(passed_str)


# configurable portion
subreddit = 'metalcore'
gpm_email = ''
gpm_passwd= ''
debug = False


# some init stuff
gpm_api = gmusicapi.Mobileclient()
gpm_api.login(gpm_email, gpm_passwd, gpm_api.FROM_MAC_ADDRESS, locale='en_US')
if not gpm_api.is_authenticated():
	print('ERROR! Count not authenticate with Google Play Music')
new_playlist_name = 'Metalcore Subreddit '+time.strftime("%d/%m/%y")
# delete eisting playlist if exists
playlist_dict = gpm_api.get_all_playlists()
for playlist in playlist_dict:
	if playlist['name'].strip() in new_playlist_name.strip():
		gpm_api.delete_playlist(playlist['id'])
# create the new platlist		
playlist_id = gpm_api.create_playlist(name=new_playlist_name, description='A playlist generated based on the current hot 100 submissions to /r/MetalCore', public=False)
song_ids_list = []

reddit = praw.Reddit(client_id='', client_secret='', user_agent='')
#reddit.read_only = True

if debug:
	print('finished init')


# parse song title and search Google Play Music 
for submission in reddit.subreddit(subreddit).hot(limit=100): # some SSL TLS error... avoidable for now.
	try:
		song_artist = submission.title[:submission.title.index('-')]
		song_artist = song_artist.strip()
		song_title  = submission.title[submission.title.index('-')+1:]
		song_title  = song_title[:dumbIndexOf(song_title, '[')] 
		song_title  = song_title[:dumbIndexOf(song_title, '(')] 
		#song_title  = submission.title[submission.title.index('-')+1:]
		song_title  = song_title.strip()
	except ValueError:
		# catch error from str.index when '-' not found
		if debug:
			print('did not find song name in: ' + submission.title)
		continue # go to the next submission

	if song_title!='' and song_artist!='':
		if debug:
			print('found song. Artist: ' + song_artist + ' Title: ' + song_title)
	else:
		if debug:
			try:
				print('did not find song name in: ' + str(submission.title))
			except UnicodeEncodeError:
				print('did not find sone name in: <unable to parse>')
		continue

	# Search GPM for the song, get the id
	song_dict = gpm_api.search(song_title+' '+song_artist, max_results=5)
	song_dict['song_hits']
	try:
		### too simple, need to ensure that song name matches ### 
		song_ids_list.append(song_dict['song_hits'][0]['track']['storeId']) # top song hit
	except IndexError:
		if debug:
			#print('Index error in collecting song ID')
			print('Song: '+song_title+' By: '+song_artist+' Not found in Google Play Music.')
		continue

# Add song to playlist
gpm_api.add_songs_to_playlist(playlist_id, song_ids_list)

if debug:
	print('added '+ str(len(song_ids_list)) +' songs to playlist')

gpm_api.logout()
