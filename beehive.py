#!/usr/bin/env python
# coding: utf-8
# site  : www.beebeeto.com
# team  : n0tr00t security

import sys
import menu
import SETTINGS

from lib.exception import *

def checkPythonVersion(major=2, minorLowest=6):
    if sys.version_info.major != major or \
       sys.version_info.minor < minorLowest:
        errInfo = 'your python version is too low, version>=%d.%d.x '\
                  'is needed.' % (major, minorLowest)
        raise BeeScanLaunchException(errInfo)
    return True

if __name__ == '__main__':
    mm = menu.MainMenu()
    mm.cmdloop()
