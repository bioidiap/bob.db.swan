#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This module provides the Dataset interface allowing the user to query the
SWAN database in the most obvious ways.
"""

from .driver import Interface
from .models import File, Client, Protocol, ProtocolPurpose
from sqlalchemy import and_, not_
import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
    """The dataset class opens and maintains a connection opened to the
    Database.

    It provides many different ways to probe for the characteristics of the
    data and for the data itself inside the database.
    """

    def __init__(self, original_directory=None, original_extension=None,
                 annotation_directory=None, annotation_extension='.pos'):
        # call base class constructors to open a session to the database
        super(Database, self).__init__(
            SQLITE_FILE, File, original_directory, original_extension)

        self.annotation_directory = annotation_directory
        self.annotation_extension = annotation_extension

    def groups(self, protocol=None):
        """Returns the names of all registered groups"""

        return Client.group_choices

    def genders(self):
        """Returns the list of genders"""

        return Client.gender_choices

    def institutes(self):
        """Returns the list of institutes"""

        return Client.institute_choices

    def protocol_names(self):
        """Returns all registered protocol names"""

        retval = [str(k.name) for k in self.protocols()]
        return retval

    def protocols(self):
        """Returns all registered protocols"""

        return list(self.query(Protocol))

    def has_protocol(self, name):
        """Tells if a certain protocol is available"""

        return self.query(Protocol).filter(Protocol.name == name).count() != 0

    def protocol(self, name):
        """Returns the protocol object in the database given a certain name.
        Raises an error if that does not exist."""

        return self.query(Protocol).filter(Protocol.name == name).one()

    def protocol_purposes(self):
        """Returns all registered protocol purposes"""

        return list(self.query(ProtocolPurpose))

    def purposes(self):
        """Returns the list of allowed purposes"""

        return ProtocolPurpose.purpose_choices

    def clients(self, protocol=None, groups=None, gender=None, institute=None):
        """Returns a list of Clients for the specific query by the user.

        Parameters
        ----------
        protocol : :py:obj:`str` or :py:obj:`None`, optional
            One of the SWAN protocols. See :py:meth:`protocol_names`
        groups : :py:obj:`str` or :py:obj:`None`, optional
            The groups to which the clients belong ('dev', 'eval', 'world')
        gender : :py:obj:`str` or :py:obj:`None`, optional
            The gender to consider ('male', 'female')
        institute : :py:obj:`str` or :py:obj:`None`, optional
            The institute of the client. See :py:meth:`institutes`.

        Returns
        -------
        list of :py:class:`bob.db.swan.models.Client`
            A list containing all the clients which have the given properties.
        """
        protocol = self.check_parameters_for_validity(
            protocol, "protocol", self.protocol_names(), [])
        groups = self.check_parameters_for_validity(
            groups, "group", self.groups(), self.groups())
        gender = self.check_parameters_for_validity(
            gender, "gender", self.genders(), [])

        # List of the clients
        retval = []
        if 'world' in groups:
            q = self.query(Client).filter(Client.sgroup == 'world')
            if gender:
                q = q.filter(Client.gender.in_(gender))
            q = q.order_by(Client.id)
            retval += list(q)

        dev_eval = []
        if 'dev' in groups:
            dev_eval.append('dev')
        if 'eval' in groups:
            dev_eval.append('eval')
        if dev_eval:
            protocol_gender = None
            if protocol:
                q = self.query(Protocol).filter(
                    Protocol.name.in_(protocol)).one()
                protocol_gender = [q.gender]
            q = self.query(Client).filter(Client.sgroup.in_(dev_eval))
            if protocol_gender:
                q = q.filter(Client.gender.in_(protocol_gender))
            if gender:
                q = q.filter(Client.gender.in_(gender))
            q = q.order_by(Client.id)
            retval += list(q)

        return retval

    def has_client_id(self, id):
        """Returns True if we have a client with a certain integer identifier"""

        return self.query(Client).filter(Client.id == id).count() != 0

    def client(self, id):
        """Returns the Client object in the database given a certain id. Raises
        an error if that does not exist."""

        return self.query(Client).filter(Client.id == id).one()

    def models(self, protocol=None, groups=None, subworld=None, gender=None):
        """Returns a set of models for the specific query by the user.

        Keyword Parameters:

        protocol
            One of the SWAN protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
                'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
            'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

        groups
            The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')
            Please note that world data are protocol/gender independent

        subworld
            Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
            In order to be considered, 'world' should be in groups and only one
            split should be specified.

        gender
            The gender to consider ('male', 'female')

        Returns: A list containing all the models belonging to the given group.
        """

        return self.clients(protocol, groups, subworld, gender)

    def model_ids(self, protocol=None, groups=None, subworld=None, gender=None):
        """Returns a set of models ids for the specific query by the user.

        Keyword Parameters:

        protocol
            One of the SWAN protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
                'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
            'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

        groups
            The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')
            Please note that world data are protocol/gender independent

        subworld
            Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
            In order to be considered, 'world' should be in groups and only one
            split should be specified.

        gender
            The gender to consider ('male', 'female')

        Returns: A list containing the ids of all models belonging to the given group.
        """

        return [client.id for client in self.clients(protocol, groups, subworld, gender)]

    def get_client_id_from_model_id(self, model_id, **kwargs):
        """Returns the client_id attached to the given model_id

        Keyword Parameters:

        model_id
            The model_id to consider

        Returns: The client_id attached to the given model_id
        """
        return model_id

    def objects(self, protocol=None, purposes=None, model_ids=None,
                groups=None, gender=None, device=None):
        """Returns a set of Files for the specific query by the user.

        Keyword Parameters:

        protocol
            One of the SWAN protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
                'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
            'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

        purposes
            The purposes required to be retrieved ('enroll', 'probe') or a tuple
            with several of them. If 'None' is given (this is the default), it is
            considered the same as a tuple with all possible values. This field is
            ignored for the data from the "world" group.

        model_ids
            Only retrieves the files for the provided list of model ids (claimed
            client id).  If 'None' is given (this is the default), no filter over
            the model_ids is performed.

        groups
            One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
            If 'None' is given (this is the default), it is considered the same as a
            tuple with all possible values.

        gender
            The gender to consider ('male', 'female')

        device
            The device to consider ('laptop', 'mobile')

        Returns: A set of Files with the given properties.
        """

        protocol = self.check_parameters_for_validity(
            protocol, "protocol", self.protocol_names())
        purposes = self.check_parameters_for_validity(
            purposes, "purpose", self.purposes())
        groups = self.check_parameters_for_validity(
            groups, "group", self.groups())
        gender = self.check_parameters_for_validity(
            gender, "gender", self.genders(), [])
        device = self.check_parameters_for_validity(
            device, "device", File.device_choices, [])

        import collections
        if(model_ids is None):
            model_ids = ()
        elif not isinstance(model_ids, collections.Iterable):
            model_ids = (model_ids,)

        # Now query the database
        retval = []
        if 'world' in groups and 'train' in purposes:
            q = self.query(File).join(Client).filter(Client.sgroup == 'world').join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol),
                            ProtocolPurpose.sgroup == 'world'))
            if gender:
                q = q.filter(Client.gender.in_(gender))
            if device:
                q = q.filter(File.device.in_(device))
            if model_ids:
                q = q.filter(File.client_id.in_(model_ids))
            q = q.order_by(File.client_id, File.session, File.device)
            retval += list(q)

        if ('dev' in groups or 'eval' in groups):
            if('enroll' in purposes):
                q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                    filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                        groups), ProtocolPurpose.purpose == 'enroll'))
                if gender:
                    q = q.filter(Client.gender.in_(gender))
                if device:
                    q = q.filter(File.device.in_(device))
                if model_ids:
                    q = q.filter(Client.id.in_(model_ids))
                q = q.order_by(File.client_id, File.session, File.device)
                retval += list(q)

            if('probe' in purposes):
                q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                    filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                        groups), ProtocolPurpose.purpose == 'probe'))
                if gender:
                    q = q.filter(Client.gender.in_(gender))
                if device:
                    q = q.filter(File.device.in_(device))
                if model_ids:
                    q = q.filter(Client.id.in_(model_ids))
                q = q.order_by(File.client_id, File.session, File.device)
                retval += list(q)

                q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                    filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                        groups), ProtocolPurpose.purpose == 'probe'))
                if gender:
                    q = q.filter(Client.gender.in_(gender))
                if device:
                    q = q.filter(File.device.in_(device))
                if len(model_ids) == 1:
                    q = q.filter(not_(File.client_id.in_(model_ids)))
                q = q.order_by(File.client_id, File.session, File.device)
                retval += list(q)

        return list(set(retval))  # To remove duplicates

    def annotations(self, file):
        """Reads the annotations for the given file id from file and returns them in a dictionary.

        If you don't have a copy of the annotation files, you can download them under http://www.idiap.ch/resource/biometric.

        Keyword parameters:

        file
            The ``File`` object for which the annotations should be read.

        Return value
            The annotations as a dictionary: {'reye':(re_y,re_x), 'leye':(le_y,le_x)}
        """
        if self.annotation_directory is None:
            return None

        self.assert_validity()
        annotation_file = file.make_path(
            self.annotation_directory, self.annotation_extension)

        # return the annotations as read from file
        return bob.db.base.read_annotation_file(annotation_file, 'eyecenter')
