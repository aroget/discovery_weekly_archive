import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
import smtplib
import logging
from email.message import EmailMessage

from settings import SCOPE

def authenticate(username):
    '''
    authenticate with the spotify service
    '''

    oauth_manager = SpotifyOAuth(username=username, scope=SCOPE)
    sp = spotipy.Spotify(oauth_manager=oauth_manager)
    user = sp.current_user()

    token_expired = oauth_manager.is_token_expired(
        oauth_manager.get_cached_token())

    if token_expired:
        # refresh token
        logging.debug('Refreshing token for user {}'.format(user['id']))
        oauth_manager.refresh_access_token(
            oauth_manager.get_cached_token()['refresh_token'])

    return oauth_manager, sp, user


def find_or_create_archive(sp, user_id, output_playlist):
    '''
    given a playlist name returns the playlist if
    found else creates a new one with the name and returns it
    '''

    archive = get_playlist_by_name(sp, user_id, playlist_name=output_playlist)
    if archive:
        return archive

    return create_archive(sp, user_id, output_playlist)


def create_archive(sp, user_id, output_playlist):
    '''
    creates a playlist
    '''
    description = 'A copy of your discovery weekly'
    return sp.user_playlist_create(user=user_id, name=output_playlist, public=False)


def email_results():
    gmail_user = 'andresroget@gmail.com'
    gmail_password = os.environ['GMAIL_PASSWORD']

    sent_from = gmail_user
    to = gmail_user
    email_text = """\
        New Songs added to playlist
        """
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        logging.info('Email sent!')
    except BaseException:
        logging.error('Something went wrong while sending your email')


def get_playlist_by_name(sp, user_id, playlist_name):
    '''
    iterate over all playlists from a given user_id
    and return the playlist matching the name
    '''
    limit = 50
    offset = 0
    next = True
    playlists = []
    matched_playlist = None

    while next:
        user_playlists = sp.current_user_playlists(
            limit=limit, offset=offset)
        next = user_playlists['next'] is not None
        offset = user_playlists['offset'] + limit
        playlists += user_playlists['items']

    for playlist in playlists:
        if playlist['name'].lower() == playlist_name.lower():
            matched_playlist = playlist
            break

    return matched_playlist


def get_track_uris_by_playlist_name(
        sp, user_id, playlist_name='Discover Weekly'):
    user_playlist = get_playlist_by_name(sp, user_id, playlist_name)

    if not user_playlist:
        logging.info('{} playlist not found'.format(playlist_name))
        return []

    # get track uris in playlist
    playlist_tracks = sp.user_playlist_tracks(
        user=user_id, playlist_id=user_playlist['id'])

    if playlist_tracks["next"]:
        track_uris = []
        while playlist_tracks["next"]:
            playlist_tracks = sp.next(playlist_tracks)
            track_uris += [track['track']['uri'] for track in playlist_tracks['items']]
        return track_uris

    return [track['track']['uri'] for track in playlist_tracks['items']]

def get_playlists_by_user_id(sp, user_id):
    return sp.user_playlists(user_id)


def get_track_uri_by_playlists_id(sp, playlist_id):
    return [item["track"]["id"] for item in sp.playlist_tracks(playlist_id)["items"]]


def copy_user_playlists(sp, source_user_id, current_user_id):
    playlists = get_playlists_by_user_id(sp, source_user_id)

    if not playlists:
        logging.debug('No Public playlists found for {}'.format(source_user_id))
        return

    playlists_uris_dict = {}
    for playlist in playlists["items"]:
        track_uris = get_track_uri_by_playlists_id(sp, playlist["id"])

        if not track_uris:
            logging.debug('Playlist has no tracks {}'.format(playlist["name"]))
            return

        try:
            playlist_copy = find_or_create_archive(sp, current_user_id, playlist["name"])

            sp.user_playlist_add_tracks(
                user=current_user_id,
                playlist_id=playlist_copy['id'],
                tracks=track_uris)
            logging.info('Successfully copied {}'.format(playlist["name"]))
        except Exception as e:
            logging.debug('ERROR', e)


def remove_dupes_from_playlist(user_id, playlist_name):
    track_uris = get_track_uris_by_playlist_name(sp, user_id, playlist_name)
    unique_uris = list(set(track_uris))

    duplicate_uris = [track_uri for track_uri in track_uris if track_uris.count(track_uri) > 1]

    sp.user_playlist_remove_all_occurrences_of_tracks(user_id, '3CjZUmNFYD3iH70iY9vqo2', list(set(duplicate_uris)))
    sp.user_playlist_add_tracks(user_id, '3CjZUmNFYD3iH70iY9vqo2', list(set(duplicate_uris)))


