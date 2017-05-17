#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the SWAN database in a single pass.
"""

from .models import Client, File, Protocol, ProtocolPurpose, Base
from collections import defaultdict
from glob import glob
import json
import os
from sqlalchemy import and_

SITE_MAPPING = {
    '1': 'NTNU',
    '2': 'UIO',
    '3': 'MPH-FRA',
    '4': 'IDIAP',
    '6': 'MPH-IND',
}

MODALITY_MAPPING = {
    '1': 'face',
    '2': 'voice',
    '3': 'eye',
    '4': 'finger',
}

DEVICE_MAPPING = {
    'p': 'iPhone',
    't': 'iPad',
}

SESSION1_DATAFORMAT = '''01 p 1.png:rear,4032x3024
02 p 1.png:rear,4032x3024
03 p 1.png:rear,4032x3024
04 p 1.png:rear,4032x3024
05 p 1.png:rear,4032x3024
01 p 1.mp4:rear,1280x720,5s
02 p 1.mp4:rear,1280x720,5s
06 p 1.png:front,2576x1932
07 p 1.png:front,2576x1932
08 p 1.png:front,2576x1932
09 p 1.png:front,2576x1932
10 p 1.png:front,2576x1932
03 p 1.mp4:front,1280x720,5s
04 p 1.mp4:front,1280x720,5s
01 t 1.png:rear,3264x2448
02 t 1.png:rear,3264x2448
03 t 1.png:rear,3264x2448
04 t 1.png:rear,3264x2448
05 t 1.png:rear,3264x2448
01 t 1.mp4:rear,1280x720,5s
02 t 1.mp4:rear,1280x720,5s
06 t 1.png:front,1280x960
07 t 1.png:front,1280x960
08 t 1.png:front,1280x960
09 t 1.png:front,1280x960
10 t 1.png:front,1280x960
03 t 1.mp4:front,1280x720,5s
04 t 1.mp4:front,1280x720,5s
01 p 2.mp4:front,1280x720
02 p 2.mp4:front,1280x720
03 p 2.mp4:front,1280x720
04 p 2.mp4:front,1280x720
05 p 2.mp4:front,1280x720
06 p 2.mp4:front,1280x720
07 p 2.mp4:front,1280x720
08 p 2.mp4:front,1280x720
01 t 2.mp4:front,1280x720
02 t 2.mp4:front,1280x720
03 t 2.mp4:front,1280x720
04 t 2.mp4:front,1280x720
05 t 2.mp4:front,1280x720
06 t 2.mp4:front,1280x720
07 t 2.mp4:front,1280x720
08 t 2.mp4:front,1280x720
01 p 3.png:rear,4032x3024
02 p 3.png:rear,4032x3024
03 p 3.png:rear,4032x3024
04 p 3.png:rear,4032x3024
05 p 3.png:rear,4032x3024
01 p 3.mp4:rear,1280x720,5s
02 p 3.mp4:rear,1280x720,5s
06 p 3.png:front,2576x1932
07 p 3.png:front,2576x1932
08 p 3.png:front,2576x1932
09 p 3.png:front,2576x1932
10 p 3.png:front,2576x1932
03 p 3.mp4:front,1280x720,5s
04 p 3.mp4:front,1280x720,5s
01 t 3.png:rear,3264x2448
02 t 3.png:rear,3264x2448
03 t 3.png:rear,3264x2448
04 t 3.png:rear,3264x2448
05 t 3.png:rear,3264x2448
01 t 3.mp4:rear,1280x720,5s
02 t 3.mp4:rear,1280x720,5s
06 t 3.png:front,1280x960
07 t 3.png:front,1280x960
08 t 3.png:front,1280x960
09 t 3.png:front,1280x960
10 t 3.png:front,1280x960
03 t 3.mp4:front,1280x720,5s
04 t 3.mp4:front,1280x720,5s
01 p 4.png:rear,4032x3024
02 p 4.png:rear,4032x3024
03 p 4.png:rear,4032x3024
04 p 4.png:rear,4032x3024
05 p 4.png:rear,4032x3024
01 p 4.mp4:rear,1280x720,5s
02 p 4.mp4:rear,1280x720,5s
06 p 4.png:rear,4032x3024
07 p 4.png:rear,4032x3024
08 p 4.png:rear,4032x3024
09 p 4.png:rear,4032x3024
10 p 4.png:rear,4032x3024
03 p 4.mp4:rear,1280x720,5s
04 p 4.mp4:rear,1280x720,5s
11 p 4.png:rear,4032x3024
12 p 4.png:rear,4032x3024
13 p 4.png:rear,4032x3024
14 p 4.png:rear,4032x3024
15 p 4.png:rear,4032x3024
05 p 4.mp4:rear,1280x720,5s
06 p 4.mp4:rear,1280x720,5s
16 p 4.png:rear,4032x3024
17 p 4.png:rear,4032x3024
18 p 4.png:rear,4032x3024
19 p 4.png:rear,4032x3024
20 p 4.png:rear,4032x3024
07 p 4.mp4:rear,1280x720,5s
08 p 4.mp4:rear,1280x720,5s
01 t 4.png:rear,3264x2448
02 t 4.png:rear,3264x2448
03 t 4.png:rear,3264x2448
04 t 4.png:rear,3264x2448
05 t 4.png:rear,3264x2448
01 t 4.mp4:rear,1280x720,5s
02 t 4.mp4:rear,1280x720,5s
06 t 4.png:rear,3264x2448
07 t 4.png:rear,3264x2448
08 t 4.png:rear,3264x2448
09 t 4.png:rear,3264x2448
10 t 4.png:rear,3264x2448
03 t 4.mp4:rear,1280x720,5s
04 t 4.mp4:rear,1280x720,5s
11 t 4.png:rear,3264x2448
12 t 4.png:rear,3264x2448
13 t 4.png:rear,3264x2448
14 t 4.png:rear,3264x2448
15 t 4.png:rear,3264x2448
05 t 4.mp4:rear,1280x720,5s
06 t 4.mp4:rear,1280x720,5s
16 t 4.png:rear,3264x2448
17 t 4.png:rear,3264x2448
18 t 4.png:rear,3264x2448
19 t 4.png:rear,3264x2448
20 t 4.png:rear,3264x2448
07 t 4.mp4:rear,1280x720,5s
08 t 4.mp4:rear,1280x720,5s
'''

SESSION2_DATAFORMAT = '''01 p 1.mp4:front,1280x720,5s
02 p 1.mp4:front,1280x720,5s
01 p 2.mp4:front,1280x720
02 p 2.mp4:front,1280x720
03 p 2.mp4:front,1280x720
04 p 2.mp4:front,1280x720
05 p 2.mp4:front,1280x720
06 p 2.mp4:front,1280x720
07 p 2.mp4:front,1280x720
08 p 2.mp4:front,1280x720
01 p 3.png:rear,4032x3024
02 p 3.png:rear,4032x3024
03 p 3.png:rear,4032x3024
04 p 3.png:rear,4032x3024
05 p 3.png:rear,4032x3024
01 p 3.mp4:rear,1280x720,5s
02 p 3.mp4:rear,1280x720,5s
06 p 3.png:front,2576x1932
07 p 3.png:front,2576x1932
08 p 3.png:front,2576x1932
09 p 3.png:front,2576x1932
10 p 3.png:front,2576x1932
03 p 3.mp4:front,1280x720,5s
04 p 3.mp4:front,1280x720,5s
01 p 4.png:rear,4032x3024
02 p 4.png:rear,4032x3024
03 p 4.png:rear,4032x3024
04 p 4.png:rear,4032x3024
05 p 4.png:rear,4032x3024
01 p 4.mp4:rear,1280x720,5s
02 p 4.mp4:rear,1280x720,5s
06 p 4.png:rear,4032x3024
07 p 4.png:rear,4032x3024
08 p 4.png:rear,4032x3024
09 p 4.png:rear,4032x3024
10 p 4.png:rear,4032x3024
03 p 4.mp4:rear,1280x720,5s
04 p 4.mp4:rear,1280x720,5s
11 p 4.png:rear,4032x3024
12 p 4.png:rear,4032x3024
13 p 4.png:rear,4032x3024
14 p 4.png:rear,4032x3024
15 p 4.png:rear,4032x3024
05 p 4.mp4:rear,1280x720,5s
06 p 4.mp4:rear,1280x720,5s
16 p 4.png:rear,4032x3024
17 p 4.png:rear,4032x3024
18 p 4.png:rear,4032x3024
19 p 4.png:rear,4032x3024
20 p 4.png:rear,4032x3024
07 p 4.mp4:rear,1280x720,5s
08 p 4.mp4:rear,1280x720,5s
'''

KNOWLEDGE = {
    '01': {'total': 128, 'video': 24, 'image': 40, 'device': ['p', 't']},
    '02': {'total': 52, 'video': 22, 'image': 30, 'device': ['p']},
    '03': {'total': 52, 'video': 22, 'image': 30, 'device': ['p']},
    '04': {'total': 52, 'video': 22, 'image': 30, 'device': ['p']},
    '05': {'total': 52, 'video': 22, 'image': 30, 'device': ['p']},
    '06': {'total': 52, 'video': 22, 'image': 30, 'device': ['p']},
    '07': {'total': 52, 'video': 22, 'image': 30, 'device': ['p']},
}


def parse_data_format(lines):
    data_format = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    for line in lines.split('\n'):
        if not line:
            continue
        nrecording, device, biometrics = line.split()
        biometrics, extension = biometrics.split('.')
        extension, data = extension.split(':')
        data = data.split(',')
        data_format[device][biometrics][extension][nrecording] = data
    return json.loads(json.dumps(data_format))


KNOWLEDGE['01']['data'] = parse_data_format(SESSION1_DATAFORMAT)
__session2_data_format_loaded = parse_data_format(SESSION2_DATAFORMAT)
KNOWLEDGE['02']['data'] = __session2_data_format_loaded
KNOWLEDGE['03']['data'] = __session2_data_format_loaded
KNOWLEDGE['04']['data'] = __session2_data_format_loaded
KNOWLEDGE['05']['data'] = __session2_data_format_loaded
KNOWLEDGE['06']['data'] = __session2_data_format_loaded


def nodot(item):
    """Can be used to ignore hidden files, starting with the . character."""
    return item[0] != '.'


def add_clients_and_files(sql_session, datadir, verbose):
    """Add files to the SWAN database."""

    client_dict = {}

    def add_file(sql_session, fullpath, verbose):
        """Parse a single filename and add it to the list.
        Also add a client entry if not already in the database.
        Example: IDIAP/session_01/iPhone/00001/4_00001_m_01_01_p_1.mp4

        """
        basename = os.path.basename(fullpath)
        site, identity, gender, session, nrecording, device, biometrics = \
            basename.split('_')
        biometrics, extension = biometrics.split('.')

        try:
            camera = KNOWLEDGE[session]['data'][
                device][biometrics][extension][nrecording]
        except KeyError:
            print('File found but not in KNOWLEDGE! {}'.format(fullpath))
            return
        camera = camera[0]
        modality = MODALITY_MAPPING[biometrics]
        site = SITE_MAPPING[site]
        device = DEVICE_MAPPING[device]

        if extension == 'mp4':
            recording = 'video'
        elif extension == 'png':
            recording = 'photo'
        else:
            raise RuntimeError('Unknown file extension {}'.format(extension))

        full_bname = os.path.join(
            site, 'session_{}'.format(session), device, identity,
            basename)

        if gender == 'm':
            gender = 'male'
        elif gender == 'f':
            gender = 'female'
        else:
            raise RuntimeError('Unknown gender {}'.format(gender))

        # identify the group of this identity
        identity = int(identity)
        if identity < 25:
            group = 'world'
        elif identity < 41:
            group = 'dev'
        elif identity < 61:
            group = 'eval'
        else:
            raise RuntimeError('Unknown IDIAP identity {}'.format(identity))

        # check if the client has been added yet.
        client_key = (identity, site)
        if client_key not in client_dict:
            if verbose > 1:
                print("    Adding client {}, {}...".format(site, identity))
            client = Client(identity, group, gender, site)
            sql_session.add(client)
            # sql_session.flush()
            # sql_session.refresh(client)
            client_dict[client_key] = True
        else:
            client = sql_session.query(Client).filter(
                and_(Client.orig_id == identity,
                     Client.institute == site)).one()
        if verbose > 1:
            print("    Adding file '%s'..." % full_bname)
        sql_session.add(File(full_bname, client, int(session), device,
                             modality, camera, recording, int(nrecording)))

    if verbose:
        print("Adding clients and files ...")
    # files = open('files.txt').read().split()
    files = []
    for _, site in SITE_MAPPING.items():
        files += glob(os.path.join(datadir, site, '*', '*', '*', '*.mp4'))
        files += glob(os.path.join(datadir, site, '*', '*', '*', '*.png'))
    for fullpath in files:
        add_file(sql_session, fullpath, verbose)


def add_protocols(session, verbose):
    """Adds protocols"""

    # 1. DEFINITIONS
    mobile_tablet = ('iPhone', 'iPad')
    mobile = ('iPhone',)
    ididap_clients = list(range(1, 61))
    non_idiap_clients = [7, 8, 9, 23, 37, 44, 45, 53, 56, 57]
    ididap_clients = [x for x in ididap_clients if x not in non_idiap_clients]

    # Numbers in the lists correspond to session identifiers
    protocol_definitions = defaultdict(lambda: defaultdict(dict))
    protocol_definitions['idiap0-audio']['world']['train'] = \
        (mobile_tablet, [x for x in ididap_clients if x < 25],
         ('voice',), ('front',), ('video',), tuple(range(1, 7)), ('IDIAP', ))
    protocol_definitions['idiap0-audio']['dev']['enroll'] = \
        (mobile, [x for x in ididap_clients if (x >= 25) and (x < 41)],
         ('voice',), ('front',), ('video',), tuple(range(1, 2)), ('IDIAP', ))
    protocol_definitions['idiap0-audio']['dev']['probe'] = \
        (mobile, [x for x in ididap_clients if (x >= 25) and (x < 41)],
         ('voice',), ('front',), ('video',), tuple(range(2, 7)), ('IDIAP', ))
    protocol_definitions['idiap0-audio']['eval']['enroll'] = \
        (mobile, [x for x in ididap_clients if (x >= 41) and (x < 61)],
         ('voice',), ('front',), ('video',), tuple(range(1, 2)), ('IDIAP', ))
    protocol_definitions['idiap0-audio']['eval']['probe'] = \
        (mobile, [x for x in ididap_clients if (x >= 41) and (x < 61)],
         ('voice',), ('front',), ('video',), tuple(range(2, 7)), ('IDIAP', ))

    # 2. ADDITIONS TO THE SQL DATABASE
    protocolPurpose_list = [
        ('world', 'train'), ('dev', 'enroll'), ('dev', 'probe'),
        ('eval', 'enroll'), ('eval', 'probe')]

    for proto in protocol_definitions:
        p = Protocol(proto)
        # Add protocol
        if verbose:
            print("Adding protocol '%s'..." % (proto))
        session.add(p)
        session.flush()
        session.refresh(p)

        # Add protocol purposes
        for group, purpose in protocolPurpose_list:
            pu = ProtocolPurpose(p.id, group, purpose)
            if verbose > 1:
                print("  Adding protocol purpose ('%s','%s')..." %
                      (group, purpose))
            session.add(pu)
            session.flush()
            session.refresh(pu)

            # get the list of files for that group
            q = session.query(File).join(Client).filter(
                Client.sgroup == group).order_by(File.id)

            device_list = protocol_definitions[proto][group][purpose][0]
            if device_list:
                q = q.filter(File.device.in_(device_list))

            modality_list = protocol_definitions[proto][group][purpose][2]
            if modality_list:
                q = q.filter(File.modality.in_(modality_list))

            camera_list = protocol_definitions[proto][group][purpose][3]
            if camera_list:
                q = q.filter(File.camera.in_(camera_list))

            recording_list = protocol_definitions[proto][group][purpose][4]
            if recording_list:
                q = q.filter(File.recording.in_(recording_list))

            session_list = protocol_definitions[proto][group][purpose][5]
            if session_list:
                q = q.filter(File.session.in_(session_list))

            institute_list = protocol_definitions[proto][group][purpose][6]
            if institute_list:
                q = q.filter(Client.institute.in_(institute_list))

            # Adds 'protocol' files
            for k in q:
                if verbose > 1:
                    print("    Adding protocol file '%s'..." % (k.path))
                pu.files.append(k)


def create_tables(args):
    """Creates all necessary tables (only to be used at the first time)"""

    from bob.db.base.utils import create_engine_try_nolock

    engine = create_engine_try_nolock(
        args.type, args.files[0], echo=(args.verbose > 2))
    Base.metadata.create_all(engine)

# Driver API
# ==========


def create(args):
    """Creates or re-creates this database"""

    from bob.db.base.utils import session_try_nolock

    dbfile = args.files[0]

    if args.recreate:
        if args.verbose and os.path.exists(dbfile):
            print('unlinking %s...' % dbfile)
        if os.path.exists(dbfile):
            os.unlink(dbfile)

    if not os.path.exists(os.path.dirname(dbfile)):
        os.makedirs(os.path.dirname(dbfile))

    # the real work...
    create_tables(args)
    s = session_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
    add_clients_and_files(s, args.datadir, args.verbose)
    add_protocols(s, args.verbose)
    s.commit()
    s.close()


def add_command(subparsers):
    """Add specific subcommands that the action "create" can use"""

    parser = subparsers.add_parser('create', help=create.__doc__)

    parser.add_argument('-R', '--recreate', action='store_true',
                        help="If set, I'll first erase the current database")
    parser.add_argument('-v', '--verbose', action='count',
                        help="Do SQL operations in a verbose way?")
    parser.add_argument('-D', '--datadir', metavar='DIR', default=None,
                        help="Change the relative path to the directory "
                        "containing the data of the SWAN database.")
    parser.add_argument('-E', '--extensions', type=str, nargs='+',
                        default=['.mp4'], help="Change the extension of the "
                        "SWAN files used to create the database.")
    parser.set_defaults(func=create)  # action
