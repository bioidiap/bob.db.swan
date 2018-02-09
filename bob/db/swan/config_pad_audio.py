#!/usr/bin/env python

from bob.db.swan import Database, SwanAudioPadFile

database = Database(
    pad_file_class=SwanAudioPadFile,
    annotation_directory=None,  # no annotations for the voice part
)
