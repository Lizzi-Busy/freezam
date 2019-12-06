# RUN THIS PROGRAM TO:
# construct database

# TODO:
# 1.fast search, hashing


import psycopg2
from credentials import DB_USER, DB_PASSWORD


# connect to database
conn = psycopg2.connect(
    host="sculptor.stat.cmu.edu",
    database=DB_USER,
    user=DB_USER,
    password=DB_PASSWORD
)


def test_connect(conn):
    """ check connection to postgresql """
    if conn.closed == 0:
        print('Connected to MySQL database')
    else:
        print('Unable to connect')


def create_table(conn):
    """ create two tables: music & fingerprint

    MUSIC
    + store song info (title, artist, album, etc.)
    + indicate whether a song is fingerprinted or not
    + fingerprinted default = 0, update when completed

    FINGERPRINT
    + store all info required for fingerprint (hash, windows, etc)
    + foreign key song_id to link two tables
    + delete a song in music = delete all same song_id in fingerprint

    JUSTIFICATION
    WHY TWO TABLES?
    + we'll mostly be working with fingerprint table (calc windows, etc)
    + no need to search song info every time
    HOW IT WORKS
    + do all the calc in fingerprint table
    + then link to music table for song info in last step
    """
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS fingerprint")
    cur.execute("DROP TABLE IF EXISTS music")

    cur.execute(
        """CREATE TABLE IF NOT EXISTS music (
            song_id SERIAL PRIMARY KEY,
            title TEXT not null,
            artist TEXT,
            album TEXT,
            address TEXT,
            url TEXT,
            fingerprinted INT default 0
            )""")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS fingerprint (
            sig_id SERIAL PRIMARY KEY,
            song_id INT REFERENCES music (song_id) ON DELETE CASCADE,
            center INT,
            signature1 NUMERIC,
            signature2 NUMERIC ARRAY
            )""")

    conn.commit()


def add_song(tup, conn):
    """ add song to music """
    if isinstance(tup, tuple) or isinstance(tup, list):
        cur = conn.cursor()
        query = "INSERT INTO music (title, artist, album) VALUES (%s, %s, %s)"
        cur.execute(query, tup)
        conn.commit()
    else:
        print("tup should be a tuple or list")


def add_fingerprint(filename, t, fingerprints1, fingerprints2, conn):
    """ add fingerprints (ver.1 & ver.2) of a song"""
    query = 'INSERT INTO fingerprint (song_id, center, signature1, signature2) VALUES (%s,%s,%s,%s)'
    song_id = select_songid(filename, conn)
    for i in range(len(t)):
        val = (song_id, t[i], fingerprints1[i], list(fingerprints2[i]))
        cur = conn.cursor()
        cur.execute(query, val)
        conn.commit()


def drop_song(title, conn):
    """ delete song from music """
    cur = conn.cursor()
    query = 'DELETE FROM music WHERE title = %s'
    cur.execute(query, (title,))
    conn.commit()


def drop_unfingerprinted(conn):
    """ delete unfingerprinted song from music """
    cur = conn.cursor()
    query = 'DELETE FROM music WHERE fingerprinted = 0'
    cur.execute(query)
    conn.commit()


def drop_duplicate(conn):
    """ delete duplicate rows from music """
    cur = conn.cursor()
    cur.execute(
        """DELETE FROM music a USING music b
        WHERE a.song_id > b.song_id
        AND a.title = b.title
        """)
    conn.commit()


def update_fingerprinted(song_id, conn):
    """ set fingerprinted = 1 when done """
    cur = conn.cursor()
    query = 'UPDATE music SET fingerprinted = 1 where song_id = %s'
    cur.execute(query, (song_id,))
    conn.commit()


def update_artist(title, artist, conn):
    """ update metadata: song artist """
    cur = conn.cursor()
    cur.execute('UPDATE music SET artist = %s where title = %s', (artist, title))
    conn.commit()


def update_album(title, album, conn):
    """ update metadata: song album """
    cur = conn.cursor()
    cur.execute('UPDATE music SET album = %s where title = %s', (album, title))
    conn.commit()


def select_songid(filename, conn):
    """ return song_id of a song """
    cur = conn.cursor()
    query = 'SELECT song_id from music WHERE title = %s'
    # get rid of the suffix (.wav) in filename
    val = (filename[:-4],)
    cur.execute(query, val)
    # the output should be a single str
    records = cur.fetchall()
    # convert to str
    return records[0][0]


def select_title(song_id, conn):
    """ select song title by song id """
    cur = conn.cursor()
    query = 'SELECT title from music WHERE song_id = %s'
    cur.execute(query, (song_id,))
    records = cur.fetchall()
    return records[0][0]


def select_max_song_id(conn):
    """ select the maximum song_id (to loop over all songs) """
    cur = conn.cursor()
    cur.execute('SELECT MAX(song_id) from music')
    records = cur.fetchall()
    return records[0][0]


def select_fingerprint1(conn, song_id):
    """ select all fingerprints (ver.1) of a song """
    cur = conn.cursor()
    cur.execute('select signature1 from fingerprint where song_id=%s', (song_id,))
    records = cur.fetchall()
     # convert decimal tuple to float num
    records = [float(elem[0]) for elem in records]
    return records


def select_fingerprint2(conn, song_id):
    """ select all fingerprints (ver.2) of a song """
    cur = conn.cursor()
    cur.execute('select signature2 from fingerprint where song_id=%s', (song_id,))
    records = cur.fetchall()
    # convert f1 from decimal tuple to float list
    records = [list(map(float, list(elem[0]))) for elem in records]
    return records


def list_all_songs(conn):
    """ list all song titles in database """
    cur = conn.cursor()
    cur.execute('SELECT title from music')
    records = cur.fetchall()
    # convert tuple list to list of strings
    records = [ elem[0] for elem in records ]
    return records


def fast_search(conn):
    """ create Generalized Inverted Indexes (GIN) for fast search,
    good for searching k-nearest neighbors"""
    pass


# TRASH BELOW

# exact match
def search_match(sig, conn):
    """ search the database for matches, return song info accordingly

    USER GUIDE
    retrieve by: print(search_match.__doc__)

    TO PRINT SONG INFO
    records = search_match(sig, conn)[0]
    for row in records:
        print("title = ", row[0])
        print("artist = ", row[1])
        print("album = ", row[2])
        print("song_id = ", row[3])

    TO PRINT NUMBER OF MATCHES
    count = search_match(sig, conn)[1]
    print(count)
    """
    cur = conn.cursor()
    query = """SELECT a.title, a.artist, a.album, a.song_id FROM music a
    INNER JOIN (SELECT song_id FROM fingerprint WHERE signature1 = %s) b
    ON a.song_id = b.song_id"""
    val = (sig,)
    cur.execute(query, val)
    # record song_id of all matches
    records = cur.fetchall()
    # count number of matches
    count = cur.rowcount

    return records, count
