#!/usr/bin/env python
# coding: utf-8
# site  : beebeeto.com
# team  : n0tr00t security

import os
import re
import imp

from pprint import pprint
from optparse import Option
from cStringIO import StringIO


from exception import LoadDefaultArgsException


class Poc(object):
    def __init__(self, path, batchable=None):
        self.path = path
        self.batchable = batchable
        self.name = os.path.split(path)[1].rstrip('.py')
        self.module = imp.load_source(self.name, path)

    def showInfo(self):
        '''print poc_info'''
        from pprint import pprint
        pprint(self.module.MyPoc.poc_info)

    def _getDefaultOpts(self):
        # get the code segment of _init_user_parser()
        with open(self.path, 'rbU') as f:
            code = f.read()
            try:
                funcStart = code.index('_init_user_parser(self):')
                f.seek(0)
                f.read(funcStart)
                f.readline()  # escape line "def _init_user_parser(self):"
                userParserCode = ''
                nextLine = f.readline()
                while not re.findall('(?:^    \S)|(?:^\S\S)', nextLine):
                    userParserCode += nextLine
                    nextLine = f.readline()
                pass
            except ValueError:  # no user defined parser
                return {}

        # strip whitespace characters
        codeStream = StringIO(userParserCode)
        options = []
        argsStr = ''
        for eachLine in codeStream:
            if eachLine.strip().startswith('self.user_parser.add_option'):
                options.append(argsStr)
                argsStr = eachLine.strip()
            else:
                argsStr += eachLine.strip()
        options.append(argsStr)

        # convert string args into variable instance
        reStr = r"([dest|default|type|help|action]+)\s?=\s?(.*?)[,|\)]"
        pattern = re.compile(reStr)
        optDict = {}
        for argsStr in options[1:]:
            args = pattern.findall(argsStr)
            dictStr = '{%s}' % ','.join("'%s':%s" % \
                                        (i[0], i[1]) for i in args if i[0] != 'help')
            argsDict = eval(dictStr)
            opt = Option('--arbitrary', **argsDict)
            optDict.setdefault(argsDict['dest'], opt.default)
        return optDict

    def run(self, target, verify=True):
        try:
            options = self._getDefaultOpts()
        except Exception, err:
            raise LoadDefaultArgsException(str(err))
        options.update({
            'target': self.module.MyPoc.normalize_target(target),
            'verify': verify,
            'verbose': False,
        })
        args = {
            'options': options,
            'success': None,
            'poc_ret': {},
        }
        result = {}
        if options['verify']:
            ret = self.module.MyPoc.verify(args)
        else:
            ret = self.module.MyPoc.exploit(args)
        result.update(ret)
        return result

if __name__ == '__main__':
    # testing code
    import os
    import sys
    BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                             '..',
                                             '..',
                                             '..'))
    FRAMEWORK_DIR = os.path.abspath(os.path.join(BASE_DIR,
                                                  'beebeeto-framework'))
    sys.path.extend([BASE_DIR, FRAMEWORK_DIR])

    p = Poc('../pocs/poc_2014_0014.py')

    def test_GetDefaultOpts():
        print p._getDefaultOpts()

    def test_run():
        print p.run(target='www.baidu.com')

    #test_GetDefaultOpts()
    test_run()
