#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Test Units
"""

from .query_bio import Database
import logging

logger = logging.getLogger(__name__)


def _test_numbers(files, n_total_files, n_clients, n_recordings,
                  n_devices, n_sessions, session_list, sites):
    n_clients_ = len(set(f.client_id for f in files))
    assert n_clients_ == n_clients, n_clients_

    n_recordings_ = len(set(f.nrecording for f in files))
    assert n_recordings_ == n_recordings, n_recordings_

    n_devices_ = len(set(f.device for f in files))
    assert n_devices_ == n_devices, n_devices_

    n_sessions_ = len(set(f.session for f in files))
    assert n_sessions_ == n_sessions, n_sessions_

    session_list_ = set(f.session for f in files)
    assert session_list_ == set(session_list), session_list_

    sites_ = set(f.client.institute for f in files)
    assert sites_ == set(sites), sites_

    assert len(files) == n_total_files, len(files)


def _test_annotation(db, files):
    try:
        annot = db.annotations(files[0])
        assert annot is None or isinstance(annot, dict), type(annot)
    except AssertionError:
        raise
    except Exception:
        logger.warn(
            "annotations tests failed. Maybe the annotations files are "
            "missing?", exc_info=True)


# def test_idiap0_voice():
#     protocol = 'idiap0-voice-bio'
#     db = Database(protocol=protocol)

#     files = db.objects(protocol=protocol, groups='world')
#     # 20 clients, 8 recordings, (2 devices in session 1 and 1 device in
#     # sessions 2-6) == like it is 1 device and 7 sessions
#     _test_numbers(files, 20 * 8 * 1 * 7, 20, 8, 2, 6, range(1, 7), ['IDIAP'])
#     assert all(int(f.client.id_in_site) < 25 for f in files)

#     files = db.objects(protocol=protocol, groups='dev', purposes='enroll')
#     _test_numbers(files, 15 * 8 * 2 * 1, 15, 8, 2, 1, range(1, 2), ['IDIAP'])
#     assert all(int(f.client.id_in_site) >=
#                25 and int(f.client.id_in_site) < 41 for f in files)

#     files = db.objects(protocol=protocol, groups='dev', purposes='probe')
#     _test_numbers(files, 15 * 8 * 1 * 5, 15, 8, 1, 5, range(2, 7), ['IDIAP'])
#     assert all(int(f.client.id_in_site) >=
#                25 and int(f.client.id_in_site) < 41 for f in files)

#     files = db.objects(protocol=protocol, groups='eval', purposes='enroll')
#     _test_numbers(files, 15 * 8 * 2 * 1, 15, 8, 2, 1, range(1, 2), ['IDIAP'])
#     assert all(int(f.client.id_in_site) >=
#                41 and int(f.client.id_in_site) < 61 for f in files)

#     files = db.objects(protocol=protocol, groups='eval', purposes='probe')
#     _test_numbers(files, 15 * 8 * 1 * 5, 15, 8, 1, 5, range(2, 7), ['IDIAP'])
#     assert all(int(f.client.id_in_site) >=
#                41 and int(f.client.id_in_site) < 61 for f in files)

#     model_ids = db.model_ids_with_protocol(groups='world', protocol=protocol)
#     assert len(model_ids) == 20, len(model_ids)
#     model_ids = db.model_ids_with_protocol(groups='dev', protocol=protocol)
#     assert len(model_ids) == 15, len(model_ids)
#     model_ids = db.model_ids_with_protocol(groups='eval', protocol=protocol)
#     assert len(model_ids) == 15, len(model_ids)

#     _test_annotation(db, files)


# def test_grandtest0_voice():
#     protocol = 'grandtest0-voice-bio'
#     db = Database(protocol=protocol)

#     files = db.objects(protocol=protocol, groups='dev', purposes='enroll')
#     _test_numbers(files, 56 * 8 * 1 * 1, 56, 8, 1, 1,
#                   [2], ['IDIAP', 'MPH-FRA'])

#     files = db.objects(protocol=protocol, groups='dev', purposes='probe')
#     _test_numbers(files, 2640, 56, 8, 2, 5,
#                   [1, 3, 4, 5, 6], ['IDIAP', 'MPH-FRA'])

#     files = db.objects(protocol=protocol, groups='eval', purposes='enroll')
#     _test_numbers(files, 94 * 8 * 1 * 1, 94, 8, 1, 1,
#                   [2], ['MPH-IND', 'NTNU'])

#     files = db.objects(protocol=protocol, groups='eval', purposes='probe')
#     _test_numbers(files, 4512, 94, 8, 2, 5,
#                   [1, 3, 4, 5, 6], ['MPH-IND', 'NTNU'])

#     model_ids = db.model_ids_with_protocol(groups='dev', protocol=protocol)
#     assert len(model_ids) == 56, len(model_ids)
#     model_ids = db.model_ids_with_protocol(groups='eval', protocol=protocol)
#     assert len(model_ids) == 94, len(model_ids)

#     _test_annotation(db, files)
