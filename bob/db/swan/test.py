#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Test Units
"""

from .query import Database


def test_idiap0_audio():
    protocol = 'idiap0-audio'
    db = Database()
    files = db.objects(protocol=protocol, groups='world', purposes='train')
    # 20 clients, 8 recordings, (2 devices in session 1 and 1 device in
    # sessions 2-6) == like it is 1 device and 7 sessions
    assert len(files) == 20 * 8 * 1 * 7, len(files)
    assert len(set(f.client.id for f in files)) == 20
    assert len(set(f.nrecording for f in files)) == 8
    assert len(set(f.device for f in files)) == 2
    assert len(set(f.session for f in files)) == 6
    assert set(f.client.institute for f in files) == set(['IDIAP'])
    assert all(f.client.orig_id < 25 for f in files)
    files = db.objects(protocol=protocol, groups='dev', purposes='enroll')
    assert len(files) == 15 * 8 * 1 * 1, len(files)
    assert len(set(f.client.id for f in files)) == 15
    assert len(set(f.nrecording for f in files)) == 8
    assert len(set(f.device for f in files)) == 1
    assert all(f.session == 1 for f in files)
    assert set(f.client.institute for f in files) == set(['IDIAP'])
    assert all(f.client.orig_id >= 25 and f.client.orig_id < 41 for f in files)
    files = db.objects(protocol=protocol, groups='dev', purposes='probe')
    assert len(files) == 15 * 8 * 1 * 5, len(files)
    assert len(set(f.client.id for f in files)) == 15
    assert len(set(f.nrecording for f in files)) == 8
    assert len(set(f.device for f in files)) == 1
    assert len(set(f.session for f in files)) == 5
    assert all(f.session > 1 for f in files)
    assert set(f.client.institute for f in files) == set(['IDIAP'])
    assert all(f.client.orig_id >= 25 and f.client.orig_id < 41 for f in files)
    files = db.objects(protocol=protocol, groups='eval', purposes='enroll')
    assert len(files) == 15 * 8 * 1 * 1, len(files)
    assert len(set(f.client.id for f in files)) == 15
    assert len(set(f.nrecording for f in files)) == 8
    assert len(set(f.device for f in files)) == 1
    assert all(f.session == 1 for f in files)
    assert set(f.client.institute for f in files) == set(['IDIAP'])
    assert all(f.client.orig_id >= 41 and f.client.orig_id < 61 for f in files)
    files = db.objects(protocol=protocol, groups='eval', purposes='probe')
    assert len(files) == 15 * 8 * 1 * 5, len(files)
    assert len(set(f.client.id for f in files)) == 15
    assert len(set(f.nrecording for f in files)) == 8
    assert len(set(f.device for f in files)) == 1
    assert len(set(f.session for f in files)) == 5
    assert all(f.session > 1 for f in files)
    assert set(f.client.institute for f in files) == set(['IDIAP'])
    assert all(f.client.orig_id >= 41 and f.client.orig_id < 61 for f in files)
