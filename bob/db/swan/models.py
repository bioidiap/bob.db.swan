#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Table models and functionality for the SWAN database.
"""

import bob.db.base.utils
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base

Base = declarative_base()

protocolPurpose_file_association = Table(
    'protocolPurpose_file_association', Base.metadata,
    Column('protocolPurpose_id', Integer, ForeignKey(
        'protocolPurpose.id')),
    Column('file_id', Integer, ForeignKey('file.id')))


class Client(Base):
    """Database clients, marked by an integer identifier and the group they
    belong to"""

    __tablename__ = 'client'

    # Key identifier for the client
    id = Column(Integer, primary_key=True)
    # the id of the client in the database
    orig_id = Column(Integer)
    # Gender to which the client belongs to
    gender_choices = ('female', 'male')
    gender = Column(Enum(*gender_choices))
    # Group to which the client belongs to
    group_choices = ('world', 'dev', 'eval')
    sgroup = Column(Enum(*group_choices))  # do NOT use group (SQL keyword)
    # Institute to which the client belongs to
    institute_choices = ('IDIAP', 'MPH-FRA', 'MPH-IND', 'NTNU', 'UIO')
    institute = Column(Enum(*institute_choices))

    def __init__(self, orig_id, group, gender, institute):
        self.orig_id = orig_id
        self.sgroup = group
        self.gender = gender
        self.institute = institute

    def __repr__(self):
        return "Client(id={}, orig_id={}, group={}, gender={}, institute={})"\
            .format(self.id, self.orig_id, self.sgroup, self.gender,
                    self.institute)


class File(Base, bob.db.base.File):
    """Generic file container"""

    __tablename__ = 'file'

    # Key identifier for the file
    id = Column(Integer, primary_key=True)
    # Unique path to this file inside the database
    path = Column(String(100), unique=True)
    # Identifier of the session
    session = Column(Integer)
    # Identifier of the device
    device_choices = ('iPhone', 'iPad')
    device = Column(Enum(*device_choices))

    modality_choices = ('face', 'voice', 'eye', 'finger')
    modality = Column(Enum(*modality_choices))

    camera_choices = ('rear', 'front')
    camera = Column(Enum(*camera_choices))

    recording_choices = ('video', 'photo')
    recording = Column(Enum(*recording_choices))

    nrecording = Column(Integer)

    # Key identifier of the client associated with this file
    client_id = Column(Integer, ForeignKey('client.id'))  # for SQL
    # For Python: A direct link to the client object that this file belongs to
    client = relationship("Client", backref=backref("files", order_by=id))

    def __init__(self, path, client, session, device, modality,
                 camera, recording, nrecording):
        # call base class constructor
        bob.db.base.File.__init__(self, path=path)

        # fill the remaining bits of the file information
        self.client = client
        self.session = session
        self.device = device
        self.modality = modality
        self.camera = camera
        self.recording = recording
        self.nrecording = nrecording


class Protocol(Base):
    """SWAN protocols"""

    __tablename__ = 'protocol'

    # Unique identifier for this protocol object
    id = Column(Integer, primary_key=True)
    # Name of the protocol associated with this object
    name = Column(String(20), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Protocol({})".format(self.name)


class ProtocolPurpose(Base):
    """SWAN protocol purposes"""

    __tablename__ = 'protocolPurpose'

    # Unique identifier for this protocol purpose object
    id = Column(Integer, primary_key=True)
    # Id of the protocol associated with this protocol purpose object
    protocol_id = Column(Integer, ForeignKey('protocol.id'))  # for SQL
    # Group associated with this protocol purpose object
    group_choices = Client.group_choices
    sgroup = Column(Enum(*group_choices))
    # Purpose associated with this protocol purpose object
    purpose_choices = ('train', 'enroll', 'probe')
    purpose = Column(Enum(*purpose_choices))

    # For Python: A direct link to the Protocol object that this
    # ProtocolPurpose belongs to
    protocol = relationship(
        "Protocol", backref=backref("purposes", order_by=id))
    # For Python: A direct link to the File objects associated with this
    # ProtcolPurpose
    files = relationship("File", secondary=protocolPurpose_file_association,
                         backref=backref("protocol_purposes", order_by=id))

    def __init__(self, protocol_id, group, purpose):
        self.protocol_id = protocol_id
        self.sgroup = group
        self.purpose = purpose

    def __repr__(self):
        return "ProtocolPurpose({}, {}, {})".format(
            self.protocol.name, self.sgroup, self.purpose)
