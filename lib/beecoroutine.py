#!/usr/bin/env python
# coding: utf-8
# author: windows2000
# site  : beebeeto.com
# team  : n0tr00t security

import gevent.monkey

from copy import deepcopy
from gevent.pool import Pool

gevent.monkey.patch_all()



class WorkerPool(object):
    JOB_UNSTART = 0  # poc not run
    JOB_RUNNING = 1
    JOB_FINISHED = 2  # poc run ok
    JOB_ERROR = -1  # error encountered when run poc
    JOB_ABORT = -2  # running poc is abort, viz unfinished

    def __init__(self, concurrency=10):
        self.concurrency = concurrency
        self.jobPool = Pool(size=concurrency)
        self.errNum = 0  # failed job(run time error but not aborted)
        self.successNum = 0
        self.totalNum = 0
        self.results = {}

    def work(self, iterJobFuncArgs, jobFunc, timeout=None):
        for jobFuncArgs in iterJobFuncArgs:
            self.results[hash(str(jobFuncArgs))] = {
                'state': self.JOB_UNSTART,
                'args': jobFuncArgs,
            }
            self.totalNum += 1
            self.jobPool.add(
                self.jobPool.apply_async(
                    self._doJob,
                    args=(jobFunc, jobFuncArgs,),
                    kwds=None,
                    callback=self._cbJobFinished
                )
            )
        self.jobPool.join(timeout=timeout, raise_error=False)
        return self.results

    def _cbJobFinished(self, jobResult):
        if jobResult['state'] == self.JOB_ERROR:
            self.errNum += 1
        elif jobResult['state'] == self.JOB_FINISHED:
            self.successNum += 1

    def _doJob(self, jobFunc, jobFuncArgs):
        self.results[hash(str(jobFuncArgs))]['state'] = self.JOB_RUNNING
        try:
            self.results[hash(str(jobFuncArgs))]['jobRet'] = \
                jobFunc(*jobFuncArgs) if isinstance(jobFuncArgs, list) \
                                      else jobFunc(jobFuncArgs)
            self.results[hash(str(jobFuncArgs))]['state'] = self.JOB_FINISHED
        except Exception as err:
            self.results[hash(str(jobFuncArgs))]['exception'] = str(err)
            self.results[hash(str(jobFuncArgs))]['state'] = self.JOB_ERROR
        return self.results[hash(str(jobFuncArgs))]

    def handleAbort(self):
        for jobId in self.results.keys():
            if self.results[jobId]['state'] in (self.JOB_RUNNING,
                                                self.JOB_UNSTART):
                self.results[jobId]['state'] = self.JOB_ABORT


if __name__ == '__main__':
    # testing code
    import time
    from random import randint
    from pprint import pprint

    def test(index, sleepTime):
        time.sleep(sleepTime)
        if sleepTime % 3 == 0:
            raise ValueError("%d - %d : 3's multiple!" % (index,
                                                          sleepTime))
        else:
            return True

    try:
        wp = WorkerPool(concurrency=10)
        wp.work([(i, randint(1, 3)) for i in xrange(20)], test, timeout=None)
        pprint(wp.results)
    except KeyboardInterrupt, SystemExit:
        wp.handleAbort()
        pprint(wp.results)
        exit()
    finally:
        print 'errNum %d, successNum %d, totalNum %d' % \
              (wp.errNum, wp.successNum, wp.totalNum)
