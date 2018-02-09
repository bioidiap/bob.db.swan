from functools import partial
from bob.bio.video.annotator import FailSafeVideo
from bob.bio.face.annotator.bobipfacedetect import BobIpFacedetect
from bob.bio.face.annotator.bobipflandmark import BobIpFlandmark
from bob.bio.face.annotator.bobipmtcnn import BobIpMTCNN
from bob.bio.face.annotator.bobipdlib import BobIpDlib
from bob.bio.face.annotator import min_face_size_validator
from bob.bio.base.annotator import FailSafe
from .query_bio import load_frames

required_keys = ['leye', 'reye']

flandmark_annotator = FailSafe(
    [BobIpFacedetect(), BobIpFlandmark()],
    required_keys,
)

annotator = FailSafeVideo(
    [BobIpMTCNN(), BobIpDlib(), flandmark_annotator],
    required_keys,
    validator=partial(min_face_size_validator, min_face_size=(256, 256)),
    read_original_data=load_frames)
