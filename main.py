import spotipy
import logging
from spotipy.oauth2 import SpotifyOAuth

from settings import SCOPE, ARCHIVE_NAME
from helpers import (
    email_results,
    create_archive,
    get_playlist_by_name,
    find_or_create_archive,
    get_track_uris_by_playlist_name,
)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.ERROR)


def run():
    try:
        oauth_manager = SpotifyOAuth(username='aroget', scope=SCOPE)
        sp = spotipy.Spotify(oauth_manager=oauth_manager)
        user = sp.current_user()

        token_expired = oauth_manager.is_token_expired(
            oauth_manager.get_cached_token())

        logging.debug('Refreshing token for user {}'.format(user['id']))

        if token_expired:
            # refresh token
            logging.debug('Refreshing token for user {}'.format(user['id']))
            oauth_manager.refresh_access_token(
                oauth_manager.get_cached_token()['refresh_token'])

        # create archive playlist
        archive = find_or_create_archive(sp, user_id=user['id'])

        archive_track_uris = get_track_uris_by_playlist_name(
            sp=sp, user_id=user['id'], playlist_name=ARCHIVE_NAME)
        discovery_weekly_track_uris = get_track_uris_by_playlist_name(
            sp=sp, user_id=user['id'])

        # remove track uris which exist in archive already
        discovery_weekly_track_uris = list(
            set(discovery_weekly_track_uris) -
            set(archive_track_uris))

        if discovery_weekly_track_uris:
            sp.user_playlist_add_tracks(
                user=user['id'],
                playlist_id=archive['id'],
                tracks=discovery_weekly_track_uris)

        logging.info('Added {} songs to {} playlist'.format(
            len(discovery_weekly_track_uris),
            ARCHIVE_NAME))

        email_results()
    except Exception as e:
        logging.error('Error', e)


if __name__ == '__main__':
    run()
