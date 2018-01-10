#!/usr/bin/env python

from bob.bio.spear.database import AudioBioFile
from bob.bio.video.database import VideoBioFile
from bob.bio.video.utils import FrameSelector
import bob.bio.base
import bob.io.base
import bob.io.video
import numpy as np
from .common import swan_bio_file_metadata, read_audio


class SwanBioFile(object):
    """A base class for SWAN bio files which can handle the metadata."""

    def __init__(self, **kwargs):
        super(SwanBioFile, self).__init__(**kwargs)
        (
            self.client, self.session, self.nrecording,
            self.device, self.modality
        ) = swan_bio_file_metadata(self.path)


class SwanAudioBioFile(AudioBioFile, SwanBioFile):
    """SwanAudioBioFile are video files actually"""

    def __init__(self, **kwargs):
        super(SwanAudioBioFile, self).__init__(**kwargs)

    def load(self, directory=None, extension=None):
        if extension is None:
            video_path = self.make_path(directory, extension)
            rate, audio = read_audio(video_path)
            return rate, np.cast['float'](audio)
        else:
            return super(SwanAudioBioFile, self).load(directory, extension)


class SwanVideoBioFile(VideoBioFile, SwanBioFile):
    """SwanVideoBioFile are video files actually"""

    def __init__(self, **kwargs):
        super(SwanVideoBioFile, self).__init__(**kwargs)

    def load(self, directory=None, extension=None,
             frame_selector=FrameSelector(selection_style='all')):
        if extension is None:
            video_path = self.make_path(directory, extension)
            video = bob.io.base.load(video_path)
            # rotate the video since SWAN videos are not upright!
            video = np.swapaxes(video, -2, -1)
            return frame_selector(video)
        else:
            return super(SwanVideoBioFile, self).load(
                directory, extension, frame_selector)


class Database(bob.bio.base.database.FileListBioDatabase):
    """Wrapper class for the SWAN database for speaker recognition
    (http://www.idiap.ch/dataset/swan). This class defines a simple protocol
    for training, dev and and by splitting the audio files of the database in
    three main parts.
    """

    def __init__(self, original_directory=None,
                 bio_file_class=SwanAudioBioFile, name='swan', **kwargs):
        # call base class constructor
        from pkg_resources import resource_filename
        folder = resource_filename(__name__, 'lists/bio')
        super(Database, self).__init__(
            folder, name=name, bio_file_class=bio_file_class,
            original_directory=original_directory,
            **kwargs
        )
