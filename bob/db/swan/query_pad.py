#!/usr/bin/env python

from bob.pad.voice.database import PadVoiceFile
from bob.pad.face.database import VideoPadFile
from bob.bio.video.utils import FrameSelector
from bob.pad.base.database import FileListPadDatabase
import bob.io.base
import bob.io.video
import numpy as np
from bob.extension import rc
from .common import read_audio
from .query_bio import SwanBioFile


class SwanAudioPadFile(PadVoiceFile, SwanBioFile):
    """SwanAudioPadFile are video files actually"""

    def __init__(self, **kwargs):
        super(SwanAudioPadFile, self).__init__(**kwargs)

    def load(self, directory=None, extension=None):
        if extension is None:
            video_path = self.make_path(directory, extension)
            rate, audio = read_audio(video_path)
            return rate, np.cast['float'](audio)
        else:
            return super(SwanAudioPadFile, self).load(directory, extension)


class SwanVideoPadFile(VideoPadFile, SwanBioFile):
    """SwanVideoPadFile are video files actually"""

    def __init__(self, **kwargs):
        super(SwanVideoPadFile, self).__init__(**kwargs)

    def swap(self, data):
        # rotate the video or image since SWAN videos are not upright!
        return np.swapaxes(data, -2, -1)

    def load(self, directory=None, extension=None,
             frame_selector=FrameSelector(selection_style='all')):
        if extension is None:
            video_path = self.make_path(directory or self.original_directory,
                                        extension)
            video = bob.io.base.load(video_path)
            video = self.swap(video)
            return frame_selector(video)
        else:
            return super(SwanVideoPadFile, self).load(
                directory, extension, frame_selector)

    @property
    def frames(self):
        """Yields the frames of the padfile one by one.

        Parameters
        ----------
        padfile : :any:`SwanVideoPadFile`
            The high-level pad file

        Yields
        ------
        :any:`numpy.array`
            A frame of the video. The size is (3, 1280, 720).
        """
        vfilename = self.make_path(directory=self.original_directory)
        reader = bob.io.video.reader(vfilename)
        for frame in reader:
            yield self.swap(frame)

    @property
    def number_of_frames(self):
        """Returns the number of frames in a video file.

        Parameters
        ----------
        padfile : :any:`SwanVideoPadFile`
            The high-level pad file

        Returns
        -------
        int
            The number of frames.
        """
        vfilename = self.make_path(directory=self.original_directory)
        return bob.io.video.reader(vfilename).number_of_frames

    @property
    def frame_shape(self):
        """Returns the size of each frame in this database.

        Returns
        -------
        (int, int, int)
            The (#Channels, Height, Width) which is (3, 1920, 1080).
        """
        return (3, 1280, 720)


class Database(FileListPadDatabase):
    """Wrapper class for the SWAN database for PAD
    (http://www.idiap.ch/dataset/swan).
    """

    def __init__(self, original_directory=rc['bob.db.swan.directory'],
                 pad_file_class=SwanAudioPadFile,
                 annotation_directory=rc['bob.db.swan.annotation_dir'],
                 annotation_extension='.json',
                 annotation_type='json',
                 name='swan', **kwargs):
        # call base class constructor
        from pkg_resources import resource_filename
        folder = resource_filename(__name__, 'lists')
        super(Database, self).__init__(
            folder, name=name, pad_file_class=pad_file_class,
            annotation_directory=annotation_directory,
            annotation_extension=annotation_extension,
            annotation_type=annotation_type,
            original_directory=original_directory,
            training_depends_on_protocol=True, models_depend_on_protocol=True,
            **kwargs
        )

    def objects(self, groups=None, protocol=None, purposes=None,
                model_ids=None, classes=None, **kwargs):
        files = super(Database, self).objects(
            groups=groups, protocol=protocol, purposes=purposes,
            model_ids=model_ids, classes=classes, **kwargs)
        for f in files:
            f.original_directory = self.original_directory
        return files

    def frames(self, padfile):
        for frame in padfile.frames:
            yield frame

    def number_of_frames(self, padfile):
        return padfile.number_of_frames

    @property
    def frame_shape(self):
        return (3, 1280, 720)
