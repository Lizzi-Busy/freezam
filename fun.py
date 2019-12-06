# ❤ GO DOWN THE RABBIT HOLE! ❤
#
# DESCRIPTION
#
# This program integrates functions from other modules to:
# + create a database
# + import metadata
# + convert mp3 to wav
# + identify a snippet
# + used features: user interaction
#   (intro, prompt user input, inform user when completed)

# TODO: read from url


import os
import logging
import analyze as a
import convert as c
import database as d
from database import conn


log = logging.getLogger(__name__)


def firststep(conn):
    """ ingest a directory of music for database construction

    USAGE
    + this is the prerequisite for all analyses/identification
    + run this function to get a nicely-built music database
    + which will be used as the reference for audio matching
    
    WHAT IT DOES
    + sql database contruction
    + read all mp3 files from a local dir
    + read metadata
    + convert mp3 to wav
    + compute spectrograms and fingerprints
    + record all info in the database

    GOOD FOR
    + lazy guys like me who don't want to contruct db manually
    """

    # create tables if non-exist
    d.create_table(conn)
    log.info("database created")
    # construct database
    for file in os.listdir("./music/mp3"):
        if file.endswith(".mp3"):
            pathfile = "./music/mp3/" + file
            # read metadata
            tup = c.meta(pathfile)
            d.add_song(tup, conn)
            # convert mp3 to wav
            c.convert(pathfile)
    log.info('all metadata recorded in the database')
    log.info('all audio converted to wav')

    for file in os.listdir("./music/wav"):
        if file.endswith(".wav"):
            pathfile = "./music/wav/" + file
            # compute spectrogram and fingerprints
            framerate, f, t, spect = a.spectrogram(pathfile)
            fingerprints1 = a.fingerprint(f, spect)
            fingerprints2 = a.fingerprint2(f, spect, framerate)
            song_id = d.select_songid(file, conn)
            log.info('audio file no. %s recorded in the database', song_id)
            # add fingerprints to database
            d.add_fingerprint(file, t, fingerprints1, fingerprints2, conn)
            # update fingerprinted status
            d.update_fingerprinted(song_id, conn)

    print('Done! Please check out your database ❤')


def add_single(conn, pathfile):
    """ add a single song to database """
    if pathfile.endswith(".mp3"):
            # read metadata
            tup = c.meta(pathfile)
            d.add_song(tup, conn)
            log.info('metadata recorded in the database')
            # convert mp3 to wav
            c.convert(pathfile)
            log.info('audio converted to wav')
            # read the wav from local directory
            filename = os.path.basename(pathfile)
            pathwav = "./music/wav/" + filename[:-3] + "wav"
             # compute spectrogram and fingerprints
            framerate, f, t, spect = a.spectrogram(pathwav)
            fingerprints1 = a.fingerprint(f, spect)
            fingerprints2 = a.fingerprint2(f, spect, framerate)
            song_id = d.select_songid(filename, conn)
            log.info('audio file no. %s recorded in the database', song_id)
            # add fingerprints to database
            d.add_fingerprint(filename, t, fingerprints1, fingerprints2, conn)
            # update fingerprinted status
            d.update_fingerprinted(song_id, conn)

            print('Done!', filename, 'added to your database ❤')


def identify1(conn, pathfile):
    """ identify a snippet (wav) with fingerprint ver.1 """

    # read snippet and compute fingerprints
    _, f, _, spect = a.spectrogram(pathfile)
    f_snippet = a.fingerprint(f, spect)
    # create a list to store number of matches for each song
    match_count = []

    # iterate through all songs in database
    log.info("iterating through all songs in database")
    max_song_id = d.select_max_song_id(conn)
    for i in range(1, max_song_id+1):
        count = 0
        # get all fingerprints (ver.1) of the song
        records = d.select_fingerprint1(conn, i)
        # iterate through the fingerprints
        for f1 in records:
            for f2 in f_snippet:
                if a.match(f1, f2):
                    count += 1
        # record number of matches for each song
        match_count.append(count)

    # find the best match
    max_count = max(match_count)
    log.info("best match found")
    # find all song_ids of the best match(es)
    l_songid = [i+1 for i, j in enumerate(match_count) if j == max_count]
    # get the song titles
    titlelist = []
    for song_id in l_songid:
        title = d.select_title(song_id, conn)
        titlelist.append(title)
        log.info('song title found for best match with song_id=%s', song_id)

    return titlelist


def identify2(conn, pathfile):
    """ identify a snippet (wav) with fingerprint ver.2 """

    # read snippet and compute fingerprints
    framerate, f, _, spect = a.spectrogram(pathfile)
    f_snippet = a.fingerprint2(f, spect, framerate)
    # create a list to store number of matches for each song
    match_count = []

    # iterate through all songs in database
    log.info("iterating through all songs in database")
    max_song_id = d.select_max_song_id(conn)
    for i in range(1, max_song_id+1):
        count = 0
        # get all fingerprints (ver.2) of the song
        records = d.select_fingerprint2(conn, i)
        # iterate through the fingerprints
        for f1 in records:
            # look at the first window (0-10s) of f2 only
            f2 = f_snippet[0]
            if a.match2(f1, f2):
                count += 1
        # record number of matches for each song
        match_count.append(count)

    # find the best match
    max_count = max(match_count)
    log.info("best match found")
    # find all song_ids of the best match(es)
    l_songid = [i+1 for i, j in enumerate(match_count) if j == max_count]
    # get the song titles
    titlelist = []
    for song_id in l_songid:
        title = d.select_title(song_id, conn)
        titlelist.append(title)
        log.info('song title found for best match with song_id=%s', song_id)

    return titlelist


# TEST OUTPUT
# identify2(conn, "./music/snippet/Track52.wav")


# UNUSED STUFF BELOW

def interact():
    """ interaction! """
    print("""
    Hi! Welcome to Freezam program!

    This program is able to read a snippet from
    your local directory, and identify the song for you!'

    Ready to go?

    'Features available:
    1.construct a library for reference
    2....
    """)
    opt = int(input('Please select an option above: '))

    if opt == 1:
        firststep(conn)
    elif opt == 2:
        print('Oops, the feature is in progress. See you in the next release!')
    else:
        print('Please enter a valid index')
        choice = str(input('Hit Q to quit or hit ANY OTHER KEY to try again:'))
        if choice == 'Q' or choice == 'q':
            print()
            print(' ~See ya~ ')
        else:
            interact()


def main():
    try:
        interact()
    except ValueError:
        print('Oops, please enter a valid index :(')
        choice = str(input('Hit Q to quit or hit ANY OTHER KEY to try again:'))
        if choice == 'Q' or choice == 'q':
            print()
            print(' ~See ya~ ')
        else:
            interact()
