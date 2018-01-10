#!/usr/bin/env python

from bob.db.swan import Database, SwanAudioBioFile

swan_raw_data_directory = "[YOUR_SWAN_DIRECTORY]"

database = Database(
    original_directory=swan_raw_data_directory,
    bio_file_class=SwanAudioBioFile,
)
