import logging
import sys

from helpers import (
    authenticate,
    find_or_create_archive,
    get_track_uris_by_playlist_name,
)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
logging.getLogger('apscheduler').setLevel(logging.ERROR)



def run(username, source_playlist, output_playlist):
    try:
        oauth_manager, sp, user = authenticate(username)

        # create archive playlist
        archive = find_or_create_archive(
            sp, user_id=user['id'], output_playlist=output_playlist)

        output_playlist_track_uris = get_track_uris_by_playlist_name(
            sp=sp, user_id=user['id'], playlist_name=output_playlist)
        source_playlist_track_uris = get_track_uris_by_playlist_name(
            sp=sp, user_id=user['id'], playlist_name=source_playlist)

        # remove track uris which exist in archive already
        source_playlist_track_uris = list(
            set(source_playlist_track_uris) -
            set(output_playlist_track_uris))

        if source_playlist_track_uris:
            sp.user_playlist_add_tracks(
                user=user['id'],
                playlist_id=archive['id'],
                tracks=source_playlist_track_uris)

        logging.info('Added {} songs to {} playlist'.format(
            len(source_playlist_track_uris),
            output_playlist))
    except Exception as e:
        logging.error('Error', e)


if __name__ == '__main__':
    try:
        username = sys.argv[1]
        source_playlist = sys.argv[2]
        output_playlist = sys.argv[3]

        run(username=username, source_playlist=source_playlist,
            output_playlist=output_playlist)
    except IndexError as e:
        logging.error(
            'Missing required params main.py <username> <source_playlist> <output_playlist>')
