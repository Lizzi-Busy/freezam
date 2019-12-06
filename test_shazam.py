# pytest -v test_shazam.py

import os
import pytest
import analyze as a
import convert as c
import fun as f

no_db = False

try:
    import psycopg2
except ModuleNotFoundError:
    no_db = True
try:
    import database as d
except ModuleNotFoundError:
    no_db = True
try:
    from database import conn
except ModuleNotFoundError:
    no_db = True


def test_convert():
    """test if convert() generates the desired wav from mp3"""
    filename = os.listdir("./music/mp3")[0]
    pathfile = "./music/mp3/" + filename
    # convert mp3 to wav
    c.convert(pathfile)

    find = False
    for file in os.listdir("./music/wav"):
        if file.endswith(".wav"):
            if file[:-4] == filename[:-4]:
                find = True

    assert find, "convert wav works"


@pytest.mark.skipif(no_db, reason="requires postgresql")
def test_drop_song(conn):
    """test if drop_song works as expected"""
    filename = os.listdir("./music/mp3")[0]
    title = filename[:-4]
    d.drop_song(title, conn)
    # check if the song exists in database
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM music where title = %s', (title,))
    rowcount = cur.fetchall()
    assert rowcount[0][0] == 0, "drop_song works"


@pytest.mark.skipif(no_db, reason="requires postgresql")
def test_add_song(conn):
    """test if add_song works as expected"""
    filename = os.listdir("./music/mp3")[0]
    pathfile = "./music/mp3/" + filename
    tup = c.meta(pathfile)
    d.add_song(tup, conn)
    # check if the song is added
    cur = conn.cursor()
    query = 'SELECT count(*) FROM music where title = %s'
    val = (filename[:-4],)
    cur.execute(query, val)
    rowcount = cur.fetchall()
    assert rowcount[0][0] != 0, "add_song works"


@pytest.mark.skipif(no_db, reason="requires postgresql")
def test_drop_duplicate(conn):
    """make sure no duplicate exists"""
    d.drop_duplicate(conn)
    # check if count song == count distinct song
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM music')
    count1 = cur.fetchall()
    cur.execute('SELECT count(distinct title) FROM music')
    count2 = cur.fetchall()
    assert count1 == count2, "no duplicate exists in music"


@pytest.mark.skipif(no_db, reason="requires postgresql")
def test_add_fingerprint(conn):
    """test if add_fingerprint works"""
    # use the newly-added song in previous test
    filename = os.listdir("./music/wav")[0]
    pathfile = "./music/wav/" + filename
    song_id = d.select_songid(filename, conn)
    # compute and add fingerprints to database
    framerate, f, t, spect = a.spectrogram(pathfile)
    fingerprints1 = a.fingerprint(f, spect)
    fingerprints2 = a.fingerprint2(f, spect, framerate)
    # add fingerprints to database
    d.add_fingerprint(filename, t, fingerprints1, fingerprints2, conn)
    # update fingerprinted status (prepare for the next test)
    d.update_fingerprinted(song_id, conn)
    # should have len(t) number of fingerprints added
    # since number of window = len(t)
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM fingerprint where song_id = %s', (song_id,))
    rowcount = cur.fetchall()
    assert rowcount[0][0] == len(t), "add_fingerprint works"


@pytest.mark.skipif(no_db, reason="requires postgresql")
def test_update_fingerprinted(conn):
    """test update_fingerprinted status when done"""
    # use the newly-added fingerprints in previous test
    filename = os.listdir("./music/wav")[0]
    song_id = d.select_songid(filename, conn)
    cur = conn.cursor()
    cur.execute('SELECT fingerprinted FROM music where song_id = %s', (song_id,))
    status = cur.fetchall()
    assert status[0][0] == 1, "update_fingerprinted works"


@pytest.mark.skipif(no_db, reason="requires postgresql")
def test_snippet(conn):
    """ test accuracy of matching

    pass a snippet of an uploaded song in db,
    should get the correct song back.
    """
    pathfile = "./music/snippet/Track54.wav"
    title = f.identify2(conn, pathfile)
    assert title == "A Tender Feeling", "the answer is correct"


# NOTE:
# this program incorporates two fingerprint methods (opt.4-5 in handout)
# opt.4 given by f.identify1() runs faster
# op4.5 given by f.identify2() gives better guesses
#
# Example:
# the test above passes with f.identify2(), but fails with f.identify()


# TODO:

@pytest.mark.skipif(no_db, reason="requires postgresql")
def test_dummy(conn):
    """ dummy!

    pass dummy sinusoids as snippets,
    match against the actual sinusoid
    """
    assert 1 == 1


@pytest.mark.skipif(no_db, reason="requires postgresql")
def test_noise(conn):
    """ test match with noise

    pass live version of a snippet,
    should get the correct song back.
    (fingerprint should be noise robust)
    (non-exact matching allowed)
    """
    assert 1 == 1
