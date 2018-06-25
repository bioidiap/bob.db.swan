from collections import OrderedDict
from os.path import join, dirname, abspath, sep
from glob import glob
import numpy as np
import pkg_resources
from bob.extension import rc
from bob.io.base import create_directories_safe
from .common import swan_file_metadata


def create_subparser(subparsers):
    parser = subparsers.add_parser(
        'create', help="Creates the PAD file lists of the dataset.")
    parser.add_argument(
        '-d', '--directory', default=rc['bob.db.swan.directory'],
        help="The path to the root directory of raw database")
    parser.set_defaults(func=_create)  # action


PAD_PROTOCOLS = OrderedDict()
for pa in ['PA.F.1', 'PA.F.5', 'PA.F.6', 'PA.V.4', 'PA.V.7']:
    PAD_PROTOCOLS[pa] = OrderedDict()
    PAD_PROTOCOLS[pa]['attack'] = OrderedDict()
    PAD_PROTOCOLS[pa]['real'] = OrderedDict()

PAD_PROTOCOLS['PA.F.1']['extension'] = '.mp4'
PAD_PROTOCOLS['PA.F.1']['attack']['train'] = ([1], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['attack']['dev'] = ([1], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['attack']['eval'] = ([1], .4, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.1']['real']['eval'] = ([2, 3, 4, 5, 6], .4, 'iPhone')

PAD_PROTOCOLS['PA.F.5']['extension'] = '.mp4'
PAD_PROTOCOLS['PA.F.5']['attack']['train'] = ([1], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['attack']['dev'] = ([1], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['attack']['eval'] = ([1], .4, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.5']['real']['eval'] = ([2, 3, 4, 5, 6], .4, 'iPhone')

PAD_PROTOCOLS['PA.F.6']['extension'] = '.mp4'
PAD_PROTOCOLS['PA.F.6']['attack']['train'] = ([1], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['attack']['dev'] = ([1], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['attack']['eval'] = ([1], .4, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.F.6']['real']['eval'] = ([2, 3, 4, 5, 6], .4, 'iPhone')

PAD_PROTOCOLS['PA.V.4']['extension'] = '.wav'
PAD_PROTOCOLS['PA.V.4']['attack']['train'] = ([1], .5, 'iPad')
PAD_PROTOCOLS['PA.V.4']['attack']['dev'] = ([1], .2, 'iPad')
PAD_PROTOCOLS['PA.V.4']['attack']['eval'] = ([1], .4, 'iPad')
PAD_PROTOCOLS['PA.V.4']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.V.4']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.V.4']['real']['eval'] = ([2, 3, 4, 5, 6], .4, 'iPhone')

PAD_PROTOCOLS['PA.V.7']['extension'] = '.wav'
PAD_PROTOCOLS['PA.V.7']['attack']['train'] = ([1], .5, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['attack']['dev'] = ([1], .2, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['attack']['eval'] = ([1], .4, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['real']['train'] = ([2], .5, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['real']['dev'] = ([2], .2, 'iPhone')
PAD_PROTOCOLS['PA.V.7']['real']['eval'] = ([2, 3, 4, 5, 6], .4, 'iPhone')


def _remove_root(file_list, root):
    root = abspath(root) + sep

    def _filter_files(path):
        # NTNU_00011: the person changes at session 5 and 6 and audio is mute
        if 'NTNU' in path and '00011' in path:
            return False
        return True

    return filter(_filter_files, (f.replace(root, '') for f in file_list))


def _add_clientid(file_list, attack_type):
    if attack_type is None:
        return ['{} {}'.format(
            f, swan_file_metadata(f)[0].id) for f in file_list]
    else:
        return ['{} {} {}'.format(
            f, swan_file_metadata(f)[0].id, attack_type)
            for f in file_list]


def _create_aggregate_pad_protocol(protocol_name, protocols):
    path_mask = 'lists/{p}/{g}/for_{r}.lst'
    path_mask = pkg_resources.resource_filename(__name__, path_mask)
    for g in ('train', 'dev', 'eval'):
        for real in ('real', 'attack'):
            file_list = []
            for i, p in enumerate(protocols):
                if i != 0 and real == 'real':
                    continue
                file_list += open(
                    path_mask.format(p=p, g=g, r=real)).readlines()
                if not file_list[-1].endswith('\n'):
                    file_list[-1] += '\n'
            path = path_mask.format(p=protocol_name, g=g, r=real)
            create_directories_safe(dirname(path))
            with open(path, 'wt') as f:
                f.writelines(file_list)


def _create(args):
    root = args.directory
    K = 10
    np.random.seed(K)
    # list all files
    for k in range(K):
        for pa_type in PAD_PROTOCOLS:
            modality = pa_type[3]
            modality_name = 'Face' if modality == 'F' else 'Voice'
            modality_number = '1' if modality == 'F' else '2'
            protocol = '{}-{}'.format(pa_type, k)
            extension = PAD_PROTOCOLS[pa_type]['extension']
            for real in PAD_PROTOCOLS[pa_type]:
                if real == 'extension':
                    continue
                all_sessions, _, device = PAD_PROTOCOLS[pa_type][real]['eval']
                real_files, rest_real_files, attack_files = [], [], []
                if real == 'attack':
                    attack_files = glob(
                        join(root, 'pa-database', modality_name, pa_type,
                             '*' + extension))
                    attack_files = sorted(_remove_root(attack_files, root))
                    np.random.shuffle(attack_files)
                else:
                    # IDIAP/session_01/iPad/00001/4_00001_m_01_01_t_1.mp4
                    for sess in all_sessions:
                        files = real_files if sess == 2 else rest_real_files
                        for site in ['IDIAP', 'NTNU', 'MPH-FRA', 'MPH-IND']:
                            files += glob(
                                join(root, site, 'session_0{}'.format(sess),
                                     device, '*',
                                     '*_{}.mp4'.format(modality_number)))
                    real_files = sorted(_remove_root(real_files, root))
                    rest_real_files = sorted(_remove_root(
                        rest_real_files, root))
                    np.random.shuffle(real_files)
                file_lists = {'real': [real_files, rest_real_files],
                              'attack': attack_files}
                index = 0
                for grp in PAD_PROTOCOLS[pa_type][real]:
                    _, number, _ = PAD_PROTOCOLS[pa_type][real][grp]
                    if real == 'real':
                        if isinstance(number, float):
                            number = round(len(file_lists[real][0]) * number)
                        files = file_lists[real][0][index:index + number]
                        if grp == 'eval':
                            files += file_lists[real][1]
                        files = _add_clientid(files, None)
                    else:
                        if isinstance(number, float):
                            number = round(len(file_lists[real]) * number)
                        files = file_lists[real][index:index + number]
                        files = _add_clientid(files, pa_type)
                    path = 'lists/{p}/{g}/for_{r}.lst'.format(
                        p=protocol, g=grp, r=real)
                    path = pkg_resources.resource_filename(__name__, path)
                    create_directories_safe(dirname(path))
                    with open(path, 'wt') as f:
                        f.write('\n'.join(sorted(files)))
                    index += number
    _create_aggregate_pad_protocol(
        'PA_F', ['PA.F.1-0', 'PA.F.5-0', 'PA.F.6-0'])
    _create_aggregate_pad_protocol(
        'PA_V', ['PA.V.4-0', 'PA.V.7-0'])
