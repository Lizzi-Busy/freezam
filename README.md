# Shazam-like Audio Recognition Algorithm

Audio fingerprinting and recognition algorithm implemented in Python. 

This program will match the recorded snippet against the fingerprints held in the database, returning the title of the song being played. Main functionality of this program has been tested on Windows 10.

## Description

This program has the following functionalities:

**Database construction**

This program allows you to build your own music database at 1-click! 
 
To get started, please copy your music files (preferably in mp3 format) into the shazam/music/mp3 folder. You'll notice that the folder already contains some pre-downloaded music files for testing purposes. Feel free to add or remove files in the folder. 

Then run the following command in the terminal:

```bash
cd shazam
$python interface.py construct
```

The program will print a message when it is done.

**Database management**

Currently the program supports the following manipulations of database:

- add a song to database

```
python interface.py add [-h] [--pathfile PATHFILE]
```

- modify song info

```
python interface.py update [-h] [--title TITLE] [--artist ARTIST] [--album ALBUM]
```

- remove a song from database

```
python interface.py remove [-h] [--title TITLE]
```

- list all songs in database

```
python interface.py list [-h]
```

- check and remove duplicate entries (should run regularly for database maintenance)

```
python interface.py admin --action=rm_dup
```

- More to come...

**Identify a snippet**

```
python interface.py identify [-h] [--pathfile PATHFILE] --type=1
```
or
```
python interface.py identify [-h] [--pathfile PATHFILE] --type=2
```

This program implements two types of fingerprints for audio identification:

- `type=1` computes a signature from local periodograms using the peak positive frequency method.
- `type=2` computes a signature by finding the maximum power per octave in local periodograms.

For faster identification, choose `type=1`; for better precision, choose `type=2`. The default option is `type=2`.

**Logging**

The application writes a message for each action taken to a designated log file shazam.log. Warnings and error messages go to the log file but also to standard error. You can customize the log level by turning on the `-vb` (verbose) option, so that all log entries will be output to standard error as well as the log file. For example:

```
python interface.py -vb identify --pathfile="./music/snippet/Track54.wav" --type=2
```


## Dependencies

**Software**
- `ffmpeg` for converting audio files to .wav format
- `PostgreSQL` for database construction

**Python packages**
- `pydub` a Python ffmpeg wrapper
- `eyed3` for reading mp3 metadata
- `numpy` for audio signals transformations
- `scipy` used in spectrogram and peak finding algorithms
- `matplotlib` used for spectrogram plots
- `psycopg2` a Python-PostgreSQL database adapter


## Installation

First, install the above dependencies.

Second, git clone the project into a local git directory.

Third, you'll allow the program to access your PostgreSQL database where fingerprints can be stored. In the shazam folder, create a python file named `credentials.py`:

```
#credentials.py

DB_USER = 'your-db-username'
DB_PASSWORD = your-db-password
```

Now you're ready to start fingerprinting your audio collection!


## Example

```
cd shazam
# create music database
python interface.py -vb construct
# identify a snippet (pre-downloaded)
python interface.py -vb identify --pathfile="./music/snippet/Track54.wav" --type=2
```


## Running the tests

To run the automated tests for this application:

```
cd shazam
pytest -v test_shazam.py
```

## Author

* Chu Pan [chup@andrew.cmu.edu], Carnegie Mellon University





