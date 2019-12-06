import sys
import logging
import argparse
import fun as f
import convert as c
import database as d
from database import conn


# INTERFACE DESIGN

parser = argparse.ArgumentParser(
    description='Freezam: process and identify audio files')
parser.add_argument('-v', '--version', action='version', version='Freezam 0.5 beta')
parser.add_argument("-vb", "--verbose", action="store_true", help="switch btw log levels")

# subcommands
subparsers = parser.add_subparsers(dest='subcommands')
# add
parser_add = subparsers.add_parser("add", help='add a song to database')
parser_add.add_argument('--pathfile', type=str, help='pathfile of the song')
# update (modify song info)
parser_update = subparsers.add_parser("update", help='update metadata of a song')
parser_update.add_argument('--title', type=str, help='song title')
parser_update.add_argument('--artist', type=str, help='song artist')
parser_update.add_argument('--album', type=str, help='song album')
# remove
parser_remove = subparsers.add_parser("remove", help='remove a song from database')
parser_remove.add_argument('--title', type=str, help='song title')
# construct (ingest an entire directory for database construction)
parser_fun = subparsers.add_parser("construct", help='construct database at 1-click')
# identify
parser_identify = subparsers.add_parser("identify", help='identify a snippet')
parser_identify.add_argument('--pathfile', type=str, help='pathfile of the snippet')
parser_identify.add_argument('--type', type=int, help='1 or 2, fingerprint method for identification')
# admin
parser_admin = subparsers.add_parser("admin", help='administrator mode. clean up database,etc.')
parser_admin.add_argument('--action', type=str, help='rm_dup - remove duplicates in database')
# list
parser_list = subparsers.add_parser("list", help='list all songs in database')

args = parser.parse_args()


# LOG SETUP

# set up logging to file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='shazam.log',
                    filemode='w')
# define a Handler which writes WARNING messages or higher to the sys.stderr
console = logging.StreamHandler(sys.stdout)
# set log level by verbose
if args.verbose:
    console.setLevel(logging.DEBUG)
else:
    console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger().addHandler(console)

log = logging.getLogger(__name__)


# MAIN FUNCTION

def main():
    """ execute the commands given in interface """

    # add
    if args.subcommands == "add":
        pathfile = args.pathfile
        f.add_single(conn, pathfile)

    # update
    if args.subcommands == "update":
        title = args.title
        artist = args.artist
        album = args.album
        if title is None:
            log.error('song title must be given for db search')
        else:
            if artist is not None:
                d.update_artist(title, artist, conn)
            if album is not None:
                d.update_album(title, album, conn)

    # remove
    if args.subcommands == "remove":
        title = args.title
        d.drop_song(conn, title)
        log.info('song %s removed from database', title)

    # construct
    if args.subcommands == "construct":
        f.firststep(conn)

    # identify
    if args.subcommands == 'identify':
        pathfile = args.pathfile
        type = args.type
        if pathfile is None:
            log.error('expected a pathfile for "identify" command')
        else:
            if type == 1:
                # match by local peak
                titlelist = f.identify1(conn, pathfile)
                for title in titlelist:
                    print('The best match is:', title)

            elif type == 2 or type is None:
                # match by maximum power per octave (default)
                titlelist = f.identify2(conn, pathfile)
                for title in titlelist:
                    print('The best match is:', title)

            else:
                log.error('expected 1 or 2 for "type"')


    # admin
    if args.subcommands == 'admin':
        action = args.action
        if action == "rm_dup":
            # remove duplicates
            d.drop_duplicate(conn)
            log.info('all duplicates removed from database')
        else:
            log.error('action not recognized, please checkout "python interface.py admin -h" for available choices')

    # list
    if args.subcommands == 'list':
        titles = d.list_all_songs(conn)
        for title in titles:
            print(title)
        


# RUN
main()


# TEST INPUT
# python interface.py identify --pathfile="./music/snippet/Track54.wav" --type=2



