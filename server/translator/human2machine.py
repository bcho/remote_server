#coding: utf-8

from server.base import logger
from dictionary import ch_d, action_type_d, h_d, l_d, t_d


# Buggy translating
#
# Short: this is a simple dictionary to translate the human order to machine
#        order, everything is hardcode.
#
# In order to translate the human sentence to machine order, we first do a
# language segment (currently using [jieba](), slow but very useful), to
# seperate and flag the words. Then, we look up the word from our
# set dictionary (called `ch_d` here). Additonly, we use `action_type_d`
# dictionary to determain the action type.
#
# I know it's really hard-coded, buggy and useless, but NLP is not a easy
# task for me now...

def classify(words, required_flags=None):
    '''Classify the words basic on their flag'''
    required_flags = required_flags or []
    ret = dict.fromkeys(required_flags)
    for k in ret.keys():
        ret[k] = []
    for word in words:
        for k, v in l_d.items():
            if word.flag in v:
                ret[k].append(word.word)
                break
    for flag in set(ret.keys()) - set(required_flags):
        ret.pop(flag, None)
    return ret


def find_repeated(d):
    '''Find repeated duration'''
    if not d.get('num', None) or \
       not (d.get('measure', None) or d.get('noun', None)):
        return None

    basic, unit = None, None
    for n in d['num']:
        try:
            basic = int(n)
        except:
            pass
    for m in d.get('measure', []) + d.get('noun', []):
        unit = t_d.get(ch_d.get(m, None)[0], None) or unit
    if basic and unit:
        return unit(basic)
    return None


def human2machine(msg):
    if not isinstance(msg, unicode):
        msg = msg.decode('utf-8')

    #: process with some hard coded translations first
    for k, v in h_d.items():
        if k in msg.split('@3bugs')[-1]:
            return v[0]

    action = None
    action_type = None
    obj = None
    repeated_duration = 0

    import jieba.posseg as pseg
    seg = classify(pseg.cut(msg), l_d.keys())

    for v in seg['verb']:
        action = ch_d.get(v, None)[0] or action
    action_type = action_type_d.get(action, None)[0]

    for n in seg['noun']:
        obj = ch_d.get(n, None)[0] or obj

    repeated_duration = find_repeated(seg) or 0

    if action and (action_type is not None) and \
            (action == 'capture' or obj):
        return action, action_type, obj, repeated_duration
    else:
        logger.info('Found unknown command %s' % msg)
        logger.debug('%s %s %s %s' % (str(action), str(action_type), str(obj),
                str(repeated_duration)))
        logger.debug(seg)
        return None
