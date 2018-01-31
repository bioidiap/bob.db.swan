from collections import OrderedDict, defaultdict
from os.path import join, dirname, abspath, sep
from glob import glob
import random
import pkg_resources
from bob.extension import rc
from bob.io.base import create_directories_safe
from .common import swan_bio_file_metadata


class OrderedDefaultDict(OrderedDict, defaultdict):
    # from https://stackoverflow.com/a/35968897/1286165
    def __init__(self, default_factory=None, *args, **kwargs):
        # in python3 you can omit the args to super
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory


def create_subparser(subparsers):
    parser = subparsers.add_parser(
        'create', help="Creates the PAD file lists of the dataset.")
    parser.add_argument(
        '-d', '--directory', default=rc['bob.db.swan.directory'],
        help="The path to the root directory of raw database")
    parser.set_defaults(func=_create)  # action


PAD_PROTOCOLS = OrderedDefaultDict(
    lambda: OrderedDefaultDict(OrderedDefaultDict))
PAD_PROTOCOLS['PA.F.1']['attack']['train'] = ([1], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['attack']['dev'] = ([1], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['attack']['eval'] = ([1], .3, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['real']['eval'] = ([2, 3, 4, 5, 6], .3, 'iPhone')

PAD_PROTOCOLS['PA.F.5']['attack']['train'] = ([1], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['attack']['dev'] = ([1], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['attack']['eval'] = ([1], .3, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['real']['eval'] = ([2, 3, 4, 5, 6], .3, 'iPhone')

PAD_PROTOCOLS['PA.F.6']['attack']['train'] = ([1], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['attack']['dev'] = ([1], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['attack']['eval'] = ([1], .3, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['real']['eval'] = ([2, 3, 4, 5, 6], .3, 'iPhone')

PAD_PROTOCOLS['PA.V.4']['attack']['train'] = ([1], .5, 'iPad')
PAD_PROTOCOLS['PA.V.4']['attack']['dev'] = ([1], .2, 'iPad')
PAD_PROTOCOLS['PA.V.4']['attack']['eval'] = ([1], .3, 'iPad')
PAD_PROTOCOLS['PA.V.4']['real']['train'] = ([2], .5, 'iPad')
PAD_PROTOCOLS['PA.V.4']['real']['dev'] = ([2], .2, 'iPad')
PAD_PROTOCOLS['PA.V.4']['real']['eval'] = ([2, 3, 4, 5, 6], .3, 'iPad')

PAD_PROTOCOLS['PA.V.7']['attack']['train'] = ([1], .5, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['attack']['dev'] = ([1], .2, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['attack']['eval'] = ([1], .3, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['real']['eval'] = ([2, 3, 4, 5, 6], .3, 'iPhone')


def _remove_root(file_list, root):
    root = abspath(root) + sep
    return [f.replace(root, '') for f in file_list]


def _add_clientid(file_list, attack_type):
    if attack_type is None:
        return ['{} {}'.format(
            f, swan_bio_file_metadata(f)[0].id) for f in file_list]
    else:
        return ['{} {} {}'.format(
            f, swan_bio_file_metadata(f)[0].id, attack_type)
            for f in file_list]


def _create(args):
    root = args.directory
    K = 10
    random.seed(K)
    # list all files
    for k in range(K):
        for pa_type in PAD_PROTOCOLS:
            modality = pa_type[3]
            modality_name = 'Face' if modality == 'F' else 'Voice'
            modality_number = '1' if modality == 'F' else '2'
            protocol = '{}-{}'.format(pa_type, k)
            for real in PAD_PROTOCOLS[pa_type]:
                all_sessions, _, device = PAD_PROTOCOLS[pa_type][real]['eval']
                real_files, rest_real_files = [], []
                if real == 'attack':
                    attack_files = glob(
                        join(root, 'pa-database', modality_name, pa_type, '*'))
                    attack_files = _remove_root(sorted(attack_files), root)
                    random.shuffle(attack_files)
                else:
                    attack_files = []
                    # IDIAP/session_01/iPad/00001/4_00001_m_01_01_t_1.mp4
                    for sess in all_sessions:
                        files = real_files if sess == 2 else rest_real_files
                        for site in ['IDIAP', 'NTNU', 'MPH-FRA', 'MPH-IND']:
                            files += glob(
                                join(root, site, 'session_0{}'.format(sess),
                                     device, '*',
                                     '*_{}.mp4'.format(modality_number)))
                    real_files = _remove_root(sorted(real_files), root)
                    rest_real_files = _remove_root(
                        sorted(rest_real_files), root)
                    random.shuffle(real_files)
                file_lists = {'real': [real_files, rest_real_files],
                              'attack': attack_files}
                index = 0
                for grp in PAD_PROTOCOLS[pa_type][real]:
                    _, number, _ = PAD_PROTOCOLS[pa_type][real][grp]
                    if real == 'real':
                        if isinstance(number, float):
                            number = int(len(file_lists[real][0]) * number)
                        files = file_lists[real][0][index:index + number]
                        if grp == 'eval':
                            files += file_lists[real][1]
                        files = _add_clientid(files, None)
                    else:
                        if isinstance(number, float):
                            number = int(len(file_lists[real]) * number)
                        files = file_lists[real][index:index + number]
                        files = _add_clientid(files, pa_type)
                    path = 'lists/{p}/{g}/for_{r}.lst'.format(
                        p=protocol, g=grp, r=real)
                    path = pkg_resources.resource_filename(__name__, path)
                    create_directories_safe(dirname(path))
                    with open(path, 'wt') as f:
                        f.write('\n'.join(sorted(files)))
                    index += number
