import os
import smtplib
import logging
from email.message import EmailMessage


def find_or_create_archive(sp, user_id, output_playlist):
    archive = get_playlist_by_name(sp, user_id, playlist_name=output_playlist)
    if archive:
        return archive

    return create_archive(sp, user_id)


def create_archive(sp, user_id, output_playlist):
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
        if playlist['name'] == playlist_name:
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

    return [track['track']['uri']
            for track in playlist_tracks['items']]
