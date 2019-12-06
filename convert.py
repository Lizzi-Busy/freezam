# RUN THIS PROGRAM TO:
# 1.convert mp3 to wav
# 2.extract mp3 metadata

from pydub import AudioSegment
import eyed3
import os
import logging

log = logging.getLogger(__name__)


def convert(infile):
    """convert mp3 to wav
    Param: infile(str): a mp3 file, like "music.mp3"
    Export: outfile: a wav file with the same name, like "music.wav"
    """
    try:
        # format outfile name
        filename = os.path.basename(infile)
        outfile = "./music/wav/" + filename[:-3] + "wav"
        # export wav
        sound = AudioSegment.from_mp3(infile)
        sound.export(outfile, format="wav")
    except OSError:
        log.Error("expected an mp3 file in the directory")


def meta(infile):
    """ get metadata (title,artist,etc) from mp3 """
    try:
        file = eyed3.load(infile)
        title = file.tag.title
        artist = file.tag.artist
        album = file.tag.album
        # create a tuple to store metadata
        tup = (title, artist, album)

        return tup

    except OSError:
        log.Error("expected an mp3 file in the directory")
    except AttributeError:
        log.Error('expected an mp3 file')
