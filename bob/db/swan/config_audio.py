#!/usr/bin/env python

from bob.db.swan import Database, SwanAudioBioFile

database = Database(
    bio_file_class=SwanAudioBioFile,
)
