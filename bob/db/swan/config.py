#!/usr/bin/env python

from bob.db.swan import Database

swan_raw_data_directory = "[YOUR_SWAN_DIRECTORY]"

database = Database(
    original_directory=swan_raw_data_directory,
    original_extension=".mp4",
)
