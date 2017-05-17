#!/usr/bin/env python

"""Commands the Swan database can respond to.
"""

import os
import sys
from bob.db.base.driver import Interface as BaseInterface


def dumplist(args):
    """Dumps lists of files based on your criteria"""

    from .query import Database
    db = Database()

    r = db.objects(
        purposes=args.purpose,
        groups=args.group,
    )

    output = sys.stdout
    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    for f in r:
        output.write('%s\n' % f.make_path(
            directory=args.directory, extension=args.extension))

    return 0


def checkfiles(args):
    """Checks existence of files based on your criteria"""

    from .query import Database
    db = Database()

    r = db.objects()

    # go through all files, check if they are available on the filesystem
    good = []
    bad = []
    for f in r:
        if os.path.exists(f.make_path(args.directory, args.extension)):
            good.append(f)
        else:
            bad.append(f)

    # report
    output = sys.stdout
    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    if bad:
        for f in bad:
            output.write('Cannot find file "%s"\n' %
                         f.make_path(args.directory, args.extension))
        output.write('%d files (out of %d) were not found at "%s"\n' %
                     (len(bad), len(r), args.directory))

    return 0


class Interface(BaseInterface):

    def name(self):
        return 'swan'

    def version(self):
        import pkg_resources  # part of setuptools
        return pkg_resources.require('bob.db.%s' % self.name())[0].version

    def files(self):
        return ()

    def type(self):
        return 'text'

    def add_commands(self, parser):

        from . import __doc__ as docs

        subparsers = self.setup_parser(parser,
                                       "Swan database", docs)

        import argparse

        # the "dumplist" action
        parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)
        parser.add_argument('-d', '--directory', default='',
                            help="if given, this path will be prepended to every entry returned.")
        parser.add_argument('-e', '--extension', default='',
                            help="if given, this extension will be appended to every entry returned.")
        parser.add_argument(
            '-u', '--purpose', help="if given, this value will limit the output files to those designed for the given purposes.", choices=('enroll', 'probe', ''))
        parser.add_argument('-g', '--group', help="if given, this value will limit the output files to those belonging to a particular protocolar group.",
                            choices=('dev', 'eval', 'world', ''))
        parser.add_argument('--self-test', dest="selftest",
                            action='store_true', help=argparse.SUPPRESS)
        parser.set_defaults(func=dumplist)  # action

        # the "checkfiles" action
        parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)
        parser.add_argument('-l', '--list-directory', required=True,
                            help="The directory which contains the file lists.")
        parser.add_argument('-d', '--directory', dest="directory", default='',
                            help="if given, this path will be prepended to every entry returned.")
        parser.add_argument('-e', '--extension', dest="extension", default='',
                            help="if given, this extension will be appended to every entry returned.")
        parser.add_argument('--self-test', dest="selftest",
                            action='store_true', help=argparse.SUPPRESS)

        parser.set_defaults(func=checkfiles)  # action
