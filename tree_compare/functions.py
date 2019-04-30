import json


def t_read(fn, log=None):
    try:
        with open(fn, 'r') as json_file:
            data = json.load(json_file, encoding='utf-8')
            return data
    except Exception as e:
        if log:
            log.exception(e)
        return {}


def t_write(fn, data):
    with open(fn, 'w') as outfile:
        d = json.dumps(data, indent=4, sort_keys=True)
        outfile.write(d)
        outfile.write('\n')


