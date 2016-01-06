#!/usr/bin/env python
# coding: utf-8
# site  : www.beebeeto.com
# team  : n0tr00t security

import os
import sys
import platform
try:
    from lib.io import bprintPrefix
except ImportError as err:
    def bprintPrefix(msg, key):
        print("%s %s" % (msg, key))

def TestPlatform():
    plat = platform.platform()
    platstr = 'other'
    if 'windows' in str(plat).lower():
        platstr = 'windows'
    return plat, platstr

def Framework_check():
    plat, platstr = TestPlatform()
    if platstr == 'windows':
        framework_path = '%s\\Beebeeto-framework\\' % ('\\'.join(os.getcwd().split('\\')[:-1]))
    else:
        framework_path = '%s/Beebeeto-framework/' % ('/'.join(os.getcwd().split('/')[:-1]))
    if os.path.exists(framework_path) == True:
        return True
    else:
        return False

def Requirements():
    requirements = []
    [requirements.append(r.strip()) for r in open('requirements.txt', 'r').readlines()]
    return requirements

def Install(name, pip_proxy=False):
    print
    pip_proxy_address = 'http://mirrors.aliyun.com/pypi/simple/'
    pip_proxy_host = 'mirrors.aliyun.com'
    bprintPrefix('%s installing...' % name, 'ok')
    if pip_proxy == True:
        os.system('pip install %s -i %s --trusted-host %s' % (name, pip_proxy_address, pip_proxy_host))
    else:
        os.system('pip install %s' % name)

def Main(pip_proxy):
    try:
        bprintPrefix('pip version: %s' % (os.popen('pip --version').readlines()[0].strip()), 'info')
    except Exception as err:
        bprintPrefix(str(err), 'error')
        sys.exit()
    requirements = Requirements()
    plat, platstr = TestPlatform()
    if platstr == 'windows':
        requirements.remove('gevent')
    else:
        requirements.append('readline')
    bprintPrefix('Platform: %s' % plat, 'info')
    if Framework_check() == True:
        bprintPrefix('Beebeeto-framework check: ok', 'ok')
    else:
        bprintPrefix('Beebeeto-framework check: false', 'error')
        bprintPrefix('Installing...', 'info')
        if platstr == 'windows':
            os.system('cd .. & git clone https://github.com/n0tr00t/Beebeeto-framework')
        else:
            os.system('cd ../ ; git clone https://github.com/n0tr00t/Beebeeto-framework')
    [Install(r, pip_proxy) for r in requirements]
    bprintPrefix('Finish :)', 'ok')

if __name__ == '__main__':
    pip_proxy= False
    if len(sys.argv) > 1 and sys.argv[1] == 'proxy':
        pip_proxy = True
    Main(pip_proxy)
