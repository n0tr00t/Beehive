#!/usr/bin/env python
# coding: utf-8
# author: windows2000
# site  : beebeeto.com
# team  : n0tr00t security


import threadpool as tp

from copy import deepcopy


class WorkerPool(object):
    JOB_UNSTART = 0  # poc not run
    JOB_RUNNING = 1
    JOB_FINISHED = 2  # poc run ok
    JOB_ERROR = -1  # error encountered when run poc
    JOB_ABORT = -2  # running poc is abort, viz unfinished

    def __init__(self, concurrency=10):
        self.concurrency = concurrency
        self.jobPool = tp.ThreadPool(num_workers=concurrency)
        self.errNum = 0
        self.successNum = 0
        self.totalNum = 0
        self.results = {}

    def work(self, iterJobFuncArgs, jobFunc, timeout=None):
        def argsGenerator():
            for jobFuncArgs in iterJobFuncArgs:
                self.results[hash(str(jobFuncArgs))] = {
                    'state': self.JOB_UNSTART,
                    'args': jobFuncArgs,
                }
                self.totalNum += 1
                yield ((jobFunc, jobFuncArgs), {})

        requests = tp.makeRequests(callable_=self._doJob,
                                   args_list=argsGenerator(),
                                   callback=self._cbJobFinished,
                                   exc_callback=self._cbHandleErr)
        [self.jobPool.putRequest(req) for req in requests]
        self.jobPool.wait()
        self.jobPool.dismissWorkers(self.concurrency, do_join=True)
        return self.results

    def _doJob(self, jobFuc, jobFuncArgs):
        self.results[hash(str(jobFuncArgs))]['state'] = self.JOB_RUNNING
        jobRet = jobFuc(*jobFuncArgs) if isinstance(jobFuncArgs, list) \
                                      else jobFuc(jobFuncArgs)
        self.results[hash(str(jobFuncArgs))]['jobRet'] = jobRet
        return jobRet

    def _cbJobFinished(self, request, result):
        self.results[hash(str(request.args[1]))]['state'] = self.JOB_FINISHED
        self.successNum += 1

    def _cbHandleErr(self, request, exc_info):
        self.results[hash(str(request.args[1]))]['state'] = self.JOB_ERROR
        self.results[hash(str(request.args[1]))]['exception'] = str(exc_info[1])
        self.errNum += 1

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
