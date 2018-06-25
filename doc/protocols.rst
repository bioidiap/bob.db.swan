

Dataset Protocols
=================

Biometric Recognition
---------------------

The biometric recognition protocol for both face and voice is
``grandtest0-voice-bio``. In this protocol, session 2 data is used for
enrollment and all other sessions are used for probing. The IDIAP and MPH-FRA
are used for development and NTNU and MPH-IND are used for evaluation. Voice
videos are used for both face and voice. That is why the protocol has the word
``voice`` in its name.


Vulnerability Analysis
----------------------

The vulnerability analysis protocols consist of evaluating a biometric system
twice: once using only bona-fide samples consisting of genuines and
zero-effort-impostors and using only bona-fide genuines (no
zero-effort-impostors) and presentation attacks. The protocols are called
*licit* and *spoof*, respectively. The ``grandtest1-voice-licit`` protocol is
used for both face and voice modalities. The licit protocol is very similar to
the biometric recognition protocol except that only session 1 is used for
probing. Only session 1 is used in probing because the presentation attacks are
created from session 1 and this allows a comparison with minimal differences
between bona-fide and presentation attacks.

``grandtest1-voice-spoof`` and ``grandtest1-face-spoof`` are used as spoof
protocols of voice and face modalities, respectively. All presentation attacks
are used in spoof protocols as probes.


Presentation Attack Detection
-----------------------------

PAD protocols are created according to the ``SWAN-PAD-protocols`` document.
Bona-fide session 2 data is split into 3 sets of training, development, and
evaluation. The bona-fide data from sessions 3,4,5,6 are used for evaluation as
well. PA samples are randomly split into 3 sets of training, development, and
evaluation. All the random splits are done 10 times to created 10 different
protocols. The PAD protocols contain only one type of attacks. For convenience,
PA_F and PA_V protocols are created for face and voice, respectively which
contain all the attacks.
