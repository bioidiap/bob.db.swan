#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the SWAN database in a single pass.
"""

import os

from .models import Client, File, Protocol, ProtocolPurpose, Base


def nodot(item):
    """Can be used to ignore hidden files, starting with the . character."""
    return item[0] != '.'


def add_clients_and_files(sql_session, datadir, extensions, verbose):
    """Add files to the SWAN database."""

    def add_file(session, datadir, location, client_id_dir, session_device, basename, verbose):
        """Parse a single filename and add it to the list.
             Also add a client entry if not already in the database."""
        v = os.path.splitext(basename)[0].split('_')
        bname = os.path.splitext(basename)[0]
        full_bname = os.path.join(
            location, client_id_dir, session_device, bname)

        gender = ''
        if v[0][0] == 'm':
            gender = 'male'
        if v[0][0] == 'f':
            gender = 'female'
        institute = int(v[0][1])
        institute_dir = ''
        if institute == 0:
            institute = 'idiap'
            institute_dir = 'idiap'
        elif institute == 1:
            institute = 'manchester'
            institute_dir = 'uman'
        elif institute == 2:
            institute = 'surrey'
            institute_dir = 'unis'
        elif institute == 3:
            institute = 'oulu'
            institute_dir = 'uoulu'
        elif institute == 4:
            institute = 'brno'
            institute_dir = 'but'
        elif institute == 5:
            institute = 'avignon'
            institute_dir = 'lia'
        if institute_dir != location:
            error_msg = "File: %s -- Find location %s in directory of location %s!" % (
                full_bname, location, institute_dir)
            raise RuntimeError(error_msg)
        client_id = v[0][1:4]
        if v[0][0:4] != client_id_dir:
            error_msg = "File: %s -- Find identity %s in directory of identity %s!" % (
                full_bname, v[0][0:4], client_id)
            raise RuntimeError(error_msg)
        if not (client_id in client_dict):
            if (institute == 'surrey' or institute == 'avignon'):
                group = 'world'
            elif (institute == 'manchester' or institute == 'oulu'):
                group = 'dev'
            elif (institute == 'idiap' or institute == 'brno'):
                group = 'eval'
            if verbose > 1:
                print("  Adding client %d..." % int(client_id))
            session.add(Client(int(client_id), group, gender, institute))
            client_dict[client_id] = True

        w = session_device.split('_')
        session_id_from_dir = int(w[0])
        device_from_dir = w[1]

        session_id = int(v[1])
        speech_type = v[2][0]
        shot_id = v[2][1:3]
        environment = v[3][0]
        device = v[3][1]
        if(device == '0'):
            device = 'mobile'
        elif(device == '1'):
            device = 'laptop'
        if device != device_from_dir:
            error_msg = "File: %s -- Find device %s in directory of device %s!" % (
                full_bname, device, device_from_dir)
            raise RuntimeError(error_msg)
        if session_id != session_id_from_dir:
            error_msg = "File: %s -- Find session_id %d in directory of session_id %d!" % (
                full_bname, session_id, session_id_from_dir)
            raise RuntimeError(error_msg)
        channel = int(v[4][0])

        if verbose > 1:
            print("    Adding file '%s'..." % full_bname)
        session.add(File(int(client_id), full_bname, session_id,
                         speech_type, shot_id, environment, device, channel))

    client_dict = {}
    if verbose:
        print("Adding clients and files ...")
    for location in filter(nodot, os.listdir(datadir)):
        location_dir = os.path.join(datadir, location)
        if os.path.isdir(location_dir):
            for client_id in filter(nodot, os.listdir(location_dir)):
                client_dir = os.path.join(location_dir, client_id)
                if os.path.isdir(client_dir):
                    for session_device in filter(nodot, os.listdir(client_dir)):
                        session_device_dir = os.path.join(
                            client_dir, session_device)
                        if os.path.isdir(session_device_dir):
                            for filename in filter(nodot, os.listdir(session_device_dir)):
                                for ext in extensions:
                                    if filename.endswith(ext):
                                        add_file(sql_session, datadir, location, client_id, session_device, os.path.basename(
                                            filename), verbose)


def add_protocols(session, verbose):
    """Adds protocols"""

    # 1. DEFINITIONS
    # Numbers in the lists correspond to session identifiers
    protocol_definitions = {}

    # Split male and female clients: list of (client_id, first_session_id) #
    # few exceptions with 2 as first session
    clients_male = [(1, 1), (2, 1), (4, 1), (8, 1), (11, 1), (12, 1), (15, 1), (16, 1), (17, 1), (19, 2),
                    (21, 1), (23, 1), (24, 1), (25, 1), (26,
                                                         1), (28, 1), (29, 1), (30, 1), (31, 1), (33, 1),
                    (34, 1), (103, 1), (104, 1), (106, 1), (107,
                                                            1), (108, 1), (109, 1), (111, 1), (112, 1), (114, 1),
                    (115, 1), (116, 1), (117, 1), (119, 1), (120,
                                                             1), (301, 1), (304, 1), (305, 1), (308, 1), (310, 1),
                    (313, 1), (314, 1), (315, 1), (317, 1), (319,
                                                             1), (416, 1), (417, 1), (418, 1), (419, 1), (420, 1),
                    (421, 1), (422, 1), (423, 1), (424, 1), (425,
                                                             1), (426, 1), (427, 1), (428, 1), (429, 1), (430, 1),
                    (431, 1), (432, 1)]
    clients_female = [(7, 2), (9, 1), (10, 1), (22, 1), (32, 1), (118, 1), (122, 1), (123, 1), (125, 1), (126, 1),
                      (127, 1), (128, 1), (129, 1), (130, 1), (131,
                                                               1), (133, 1), (302, 1), (303, 1), (306, 1), (307, 1),
                      (309, 1), (311, 1), (320, 1), (401, 1), (402,
                                                               1), (403, 1), (404, 1), (405, 2), (406, 1), (407, 1),
                      (408, 1), (409, 1), (410, 1), (411, 1), (412, 1), (413, 1), (415, 1), (433, 1)]
    train_mobile = ['mobile']
    train_all = None
    enroll_laptop = [['laptop'], ['p']]
    enroll_mobile = [['mobile'], ['p']]
    enroll_laptop_mobile = [['laptop', 'mobile'], ['p']]
    probe = [['mobile'], ['r', 'f']]
    gender_male = 'male'
    gender_female = 'female'
    protocol_definitions['mobile0-male'] = [clients_male,
                                            train_mobile, enroll_mobile, probe, gender_male]
    protocol_definitions['mobile0-female'] = [clients_female,
                                              train_mobile, enroll_mobile, probe, gender_female]
    protocol_definitions['mobile1-male'] = [clients_male,
                                            train_all, enroll_mobile, probe, gender_male]
    protocol_definitions['mobile1-female'] = [clients_female,
                                              train_all, enroll_mobile, probe, gender_female]
    protocol_definitions['laptop1-male'] = [clients_male,
                                            train_all, enroll_laptop, probe, gender_male]
    protocol_definitions['laptop1-female'] = [clients_female,
                                              train_all, enroll_laptop, probe, gender_female]
    protocol_definitions['laptop_mobile1-male'] = [clients_male,
                                                   train_all, enroll_laptop_mobile, probe, gender_male]
    protocol_definitions['laptop_mobile1-female'] = [clients_female,
                                                     train_all, enroll_laptop_mobile, probe, gender_female]

    # 2. ADDITIONS TO THE SQL DATABASE
    protocolPurpose_list = [('world', 'train'), ('dev', 'enroll'),
                            ('dev', 'probe'), ('eval', 'enroll'), ('eval', 'probe')]
    for proto in protocol_definitions:
        p = Protocol(proto, protocol_definitions[proto][4])
        # Add protocol
        if verbose:
            print("Adding protocol '%s'..." % (proto))
        session.add(p)
        session.flush()
        session.refresh(p)

        # Add protocol purposes
        for key in range(len(protocolPurpose_list)):
            purpose = protocolPurpose_list[key]
            pu = ProtocolPurpose(p.id, purpose[0], purpose[1])
            if verbose > 1:
                print("  Adding protocol purpose ('%s','%s')..." %
                      (purpose[0], purpose[1]))
            session.add(pu)
            session.flush()
            session.refresh(pu)

            # Add files attached with this protocol purpose
            client_group = ""
            device_list = []
            speech_list = []
            if(key == 0):
                client_group = "world"
            elif(key == 1 or key == 2):
                client_group = "dev"
            elif(key == 3 or key == 4):
                client_group = "eval"
            if(key == 0):
                world_list = True
                session_list_in = False
                device_list = protocol_definitions[proto][1]
            if(key == 1 or key == 3):
                world_list = False
                session_list_in = True
                device_list = protocol_definitions[proto][2][0]
                speech_list = protocol_definitions[proto][2][1]
            elif(key == 2 or key == 4):
                world_list = False
                session_list_in = False
                device_list = protocol_definitions[proto][3][0]
                speech_list = protocol_definitions[proto][3][1]

            # Adds 'protocol' files
            # World set
            if world_list:
                q = session.query(File).join(Client).filter(
                    Client.sgroup == 'world').order_by(File.id)
                if device_list:
                    q = q.filter(File.device.in_(device_list))
                for k in q:
                    if verbose > 1:
                        print("    Adding protocol file '%s'..." % (k.path))
                    pu.files.append(k)
            # Dev/eval set
            else:
                for client in protocol_definitions[proto][0]:
                    cid = client[0]  # client id
                    sid = client[1]  # session id
                    q = session.query(File).join(Client).\
                        filter(Client.sgroup == client_group).filter(
                            Client.id == cid)
                    if session_list_in:
                        q = q.filter(File.session_id == sid)
                    else:
                        q = q.filter(File.session_id != sid)
                    if device_list:
                        q = q.filter(File.device.in_(device_list))
                    if speech_list:
                        q = q.filter(File.speech_type.in_(speech_list))
                    q = q.order_by(File.id)
                    for k in q:
                        if verbose > 1:
                            print("    Adding protocol file '%s'..." %
                                  (k.path))
                        pu.files.append(k)

        # Add protocol
        speech_type = ['p', 'l', 'r', 'f']
        mobile_only = False
        if 'mobile0' in proto:
            mobile_only = True
        add_tmodels(session, p.id, mobile_only, speech_type, verbose)


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
    add_files(s, args.datadir, args.extensions, args.verbose)
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
