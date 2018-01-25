#!/usr/bin/env python

from bob.bio.spear.database import AudioBioFile
from bob.bio.video.database import VideoBioFile
from bob.bio.video.utils import FrameSelector
import bob.bio.base
import bob.io.base
import bob.io.video
import numpy as np
from bob.extension import rc
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
            return super(SwanVideoBioFile, self).load(
                directory, extension, frame_selector)

    def frames(self):
        """Yields the frames of the biofile one by one.

        Parameters
        ----------
        biofile : :any:`SwanVideoBioFile`
            The high-level bio file

        Yields
        ------
        :any:`numpy.array`
            A frame of the video. The size is (3, 1280, 720).
        """
        vfilename = self.make_path(directory=self.original_directory)
        reader = bob.io.video.reader(vfilename)
        for frame in reader:
            yield self.swap(frame)

    def number_of_frames(self):
        """Returns the number of frames in a video file.

        Parameters
        ----------
        biofile : :any:`SwanVideoBioFile`
            The high-level bio file

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


class Database(bob.bio.base.database.FileListBioDatabase):
    """Wrapper class for the SWAN database for speaker recognition
    (http://www.idiap.ch/dataset/swan). This class defines a simple protocol
    for training, dev and and by splitting the audio files of the database in
    three main parts.
    """

    def __init__(self, original_directory=rc['bob.db.swan.directory'],
                 bio_file_class=SwanAudioBioFile, name='swan', **kwargs):
        # call base class constructor
        from pkg_resources import resource_filename
        folder = resource_filename(__name__, 'lists')
        super(Database, self).__init__(
            folder, name=name, bio_file_class=bio_file_class,
            original_directory=original_directory,
            training_depends_on_protocol=True,
            models_depend_on_protocol=True,
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


def load_frames(biofile, directory, extension):
    for frame in biofile.frames():
        yield frame
