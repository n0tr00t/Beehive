#!/usr/bin/env python
# coding: utf-8
# site  : www.beebeeto.com
# team  : n0tr00t security

import os
import sys
sys.path.append('../')
import lib
import time
import socket
import random
import string
import platform

from lib.poc import Poc

try:
    from lib import beecoroutine as bc, beethread as bt
except:
    from lib import beethread as bt


socket.setdefaulttimeout(10)


def TestPlatform():
    plat = platform.platform()
    if 'windows' in str(plat).lower():
        platstr = 'beethread'
    else:
        platstr = 'beecoroutine'
    return platstr

class Storm(object):
    '''scanner scanning a particular target with a list of pocs.'''
    def __init__(self, target, listPocPaths, poolModule='beethread',
                 concurrency=20, verify=True):
        '''
        target - a target to scan.
        listPocPaths - a list containing man pocs' paths, the pocs must be
            batchable.
        poolModule - can be 'beethread' or 'beecoroutine', meaning using
            thread pool or coroutine pool to manage concurrency.
        concurrency - how many work to run in concurrency.
        verify - run the pocs' verfiy mode or exploit mode.
        '''
        self.target = target
        self.verify = verify
        self._pocObjs = self._loadPocs(listPocPaths)
        self._poolModule = poolModule
        self._workerPool = self._initWorkerPool(poolModule)(concurrency=concurrency)
        self.r_num = random.randint(10000, 99999)

    def _view_bar(self, num=1, sum=0, bar_word=':'):
        rate = float(num) / float(sum)
        rate_num = int(rate * 100)
        str_lsit = ['-', '|', '/', '\\']
        print '\r[%s] Scanning... (%d%%)' % (random.choice(str_lsit), rate_num),
        sys.stdout.flush()

    def _loadPocs(self, listPocPaths):
        pocObjs = []
        for pocPath in listPocPaths:
            pocObjs.append(Poc(path=pocPath))
        return pocObjs

    def _initWorkerPool(self, poolModule='beethread'):
        if poolModule is 'beethread':
            return bt.WorkerPool
        elif poolModule is 'beecoroutine':
            return bc.WorkerPool

    def _runPoc(self, pocName, pocObj, verbose=True):
        if verbose:
            tmp_schedule = open('./tmp/t_%d.txt' % self.r_num, 'a+')
            tmp_schedule.write(pocName+'\n')
            tmp_count = len(open('./tmp/t_%d.txt' % self.r_num ,'rU').readlines())
            self._view_bar(num=tmp_count, sum=len(self._pocObjs))
            tmp_schedule.close()
        return pocObj.run(target=self.target, verify=self.verify)

    def scan(self, timeout=None, verbose=True):
        print
        self._workerPool.work(iterJobFuncArgs=[[pocObj.name, pocObj, True] \
                                               for pocObj in self._pocObjs],
                              jobFunc=self._runPoc,
                              timeout=timeout)
        try:
            os.remove('./tmp/t_%d.txt' % self.r_num)
        except Exception, err:
            pass
        return self._workerPool.results


class Hunter(object):
    '''scanner scanning a list of targets with a particular poc.'''
    def __init__(self, iterTarget, pocPath, poolModule='beethread',
                 concurrency=20, verify=True):
        self.iterTarget = iterTarget
        self.verify = verify
        self._pocObj = Poc(path=pocPath)
        self._poolModule = poolModule
        self._workerPool = self._initWorkerPool(poolModule)(concurrency=concurrency)

    def _initWorkerPool(self, poolModule='beethread'):
        if poolModule is 'beethread':
            return bt.WorkerPool
        elif poolModule is 'beecoroutine':
            return bc.WorkerPool

    def _runPoc(self, target):
        # TODO: need to normalize target in Poc
        target = target.strip()
        return self._pocObj.run(target=target, verify=self.verify)

    def scan(self, timeout=None):
        self._workerPool.work(iterJobFuncArgs=self.iterTarget,
                              jobFunc=self._runPoc,
                              timeout=timeout)
        return self._workerPool.results



if __name__ == '__main__':
    from pprint import pprint

    # testing Storm
    '''
    pocPaths = [
        './pocs/poc_2014_0014.py',
        './pocs/poc_2014_0010.py',
    ]
    s = Storm(listPocPaths=pocPaths, target='baidu.com', poolModule='beecoroutine')
    pprint(s.scan())
    '''

    # testing Hunter
    '''
    targets = ['baidu.com',
               'https://8.8.8.8']
    h = Hunter(iterTarget=targets,
               pocPath='../pocs/poc_2014_0011.py',
               poolModule='beethread')
    pprint(h.scan())
    '''
