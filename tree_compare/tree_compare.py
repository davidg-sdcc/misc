import argparse
import logging
import os

from functions import t_read, t_write


def _res_dict(added, changed, removed):
    d = {}
    if added:
        d['insert'] = added
    if changed:
        d['change'] = changed
    if removed:
        d['delete'] = removed
    return d


class JsonTreeCompare(object):

    def _list_comp(self, j1, j2):
        changed = {}
        l1 = len(j1)
        l2 = len(j2)
        n = min(l1, l2)
        for i in range(n):
            d = self._do_comp(j1[i], j2[i])
            if d:
                changed[i] = d

        removed = dict((k+l2, v) for k, v in enumerate(j2[l2:l1])) if l1 > l2 else {}
        added = dict((k+l1, v) for k, v in enumerate(j2[l1:l2])) if l2 > l1 else {}

        return _res_dict(added, changed, removed)

    def _dict_comp(self, j1, j2):
        removed = {}
        changed = {}
        for k, v in j1.items():
            w = j2.get(k)
            if w is None:
                removed[k] = v
            else:
                d = self._do_comp(v, w)
                if d:
                    changed[k] = d

        added = {}
        for k, v in j2.items():
            if k not in j1:
                added[k] = v

        return _res_dict(added, changed, removed)

    def _do_comp(self, j1, j2):
        if j1 == j2:
            res = {}
        elif isinstance(j1, dict) and isinstance(j2, dict):
            res = self._dict_comp(j1, j2)
        elif isinstance(j1, list) and isinstance(j2, list):
            res = self._list_comp(j1, j2)
        elif j1 != j2:
            res = _res_dict(j2, {}, j1)
        else:
            raise ValueError('Unknown type: Tree 1 type is {0}, Tree 2 type is {1}'.format(type(j1).__name__,
                                                                                           type(j2).__name__))
        return res

    def compare(self, j1, j2):
        d = self._do_comp(j1, j2)
        return d


def _main():
    try:
        logger.info('Start Tree compare')

        parser = argparse.ArgumentParser(description='Tree compare')
        parser.add_argument('-a', '--fist_file', help='First file to be compared', default='tree1.txt')
        parser.add_argument('-b', '--second_file', help='Second file to be compared', default='tree2.txt')
        parser.add_argument('-o', '--operation', help=' "diff" or "merge", default is "diff"',
                            default='diff')
        parser.add_argument('-f', '--force', help='Force merge operation, without verification, default is False',
                            action='store_true', required=False, default=False)

        args = vars(parser.parse_args())

        fn1 = args.get('fist_file')
        fn2 = args.get('second_file')
        force = args.get('force')
        op = args.get('operation')
        logger.info('Files: {} {}'.format(fn1, fn2))

        file_1 = t_read(fn1)
        logger.debug('File 1: {}'.format(file_1))
        file_2 = t_read(fn2)
        logger.debug('File 2: {}'.format(file_2))

        d = {}
        jc = JsonTreeCompare()
        if op == 'diff':
            d = jc.compare(file_1, file_2)
        elif op == 'merge':
            raise NotImplemented('Operation {} is not implemented yet'.format(op))
        else:
            logging.error('Operation is not defined: {}'.format(op))

        logger.info('Result: {}'.format(d))

    except Exception as e:
        logger.exception(e)
    finally:
        logger.info('Finish Tree compare')


DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(filename)s:%(funcName)s:%(lineno)s] %(message)s"
DEFAULT_LOG_LEVEL = 'DEBUG'

script_name = os.path.basename(__file__).split('.')[0]

logger = logging.getLogger(script_name)
logger.level = logging.getLevelName(DEFAULT_LOG_LEVEL)
fmt = logging.Formatter(fmt=DEFAULT_LOG_FORMAT)

LOG_DIR = '/var/log/tree_compare'

fh = None
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
        log_file = "{0}.log".format(os.path.join(LOG_DIR, script_name))
        fh = logging.FileHandler(log_file)
    except OSError as e:
        fh = logging.StreamHandler()
if fh:
    fh.setFormatter(fmt)
    logger.addHandler(fh)

if __name__ == '__main__':
    _main()
