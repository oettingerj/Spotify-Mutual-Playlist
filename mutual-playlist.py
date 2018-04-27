import sys, os
import spotipy
import spotipy.util as util

os.environ['SPOTIPY_CLIENT_ID'] = 'efcab495355a4679bb3b5739d607540b'
os.environ['SPOTIPY_CLIENT_SECRET'] = '4c1ba851cfa94359ad393f4368670100'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost/callback/'
scope = 'user-library-read playlist-modify-public playlist-modify-private playlist-read-private'

def getUserTracks(token):
    sp = spotipy.Spotify(auth=token)
    tracks = []
    hasMoreTracks = True
    offset = 0
    while hasMoreTracks:
        results = sp.current_user_saved_tracks(50, offset)
        if len(results['items']) < 50:
            hasMoreTracks = False

        for item in results['items']:
            track = item['track']
            tracks.append(track)
        offset += 50
    return tracks

def getMutualTracks(tracks1, tracks2):
    tracks = []
    for track1 in tracks1:
        title1 = track1['name']
        artist1 = track1['artists'][0]['name']
        for track2 in tracks2:
            title2 = track2['name']
            artist2 = track2['artists'][0]['name']
            if title1 == title2 and artist1 == artist2:
                tracks.append(track1['id'])
                break
    return tracks

def createMutualPlaylist(tracks, token1, token2):
    splitTracks = []
    for i in range(0, (len(tracks) // 100) + 1):
        splitTracks.append(tracks[i*100:(i+1)*100])

    sp1 = spotipy.Spotify(auth=token1)
    id1 = sp1.current_user()['id']
    name1 = sp1.current_user()['display_name']
    sp2 = spotipy.Spotify(auth=token2)
    id2 = sp2.current_user()['id']
    name2 = sp2.current_user()['display_name']

    playlistName = "%s and %s's Mutual Playlist" %(name1, name2)

    playlist1 = sp1.user_playlist_create(id1, playlistName, public=False)
    for subArray in splitTracks:
        sp1.user_playlist_add_tracks(id1, playlist1['id'], subArray)

    playlist2 = sp2.user_playlist_create(id2, playlistName, public=False)
    for subArray in splitTracks:
        sp2.user_playlist_add_tracks(id2, playlist2['id'], subArray)


if len(sys.argv) > 2:
    username1 = sys.argv[1]
    username2 = sys.argv[2]
else:
    print("Please enter two usernames. Ex: %s username1 username2" % (sys.argv[0]))
    sys.exit()

token1 = util.prompt_for_user_token(username1, scope)
input('Log out of your account in your browser and press ENTER.')
token2 = util.prompt_for_user_token(username2, scope)

if token1 and token2:
    print("Loading user tracks...")
    tracks1 = getUserTracks(token1)
    tracks2 = getUserTracks(token2)
    print("Finding mutual tracks...")
    mutualTracks = getMutualTracks(tracks1, tracks2)
    print("Adding playlist to library...")
    createMutualPlaylist(mutualTracks, token1, token2)
    print("Mutual playlist has been added to both users' libraries.")
else:
    print("Couldn't authenticate for %s and %s" %(username1, username2))
