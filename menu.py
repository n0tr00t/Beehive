#!/usr/bin/env python
# coding: utf-8
# site  : www.beebeeto.com
# team  : n0tr00t security

import os
import sys
import optparse
import pyparsing
import pprint as pr
import textwrap as tw
import traceback as tb

from lib.scanner import Storm, Hunter, TestPlatform
from prettytable import PrettyTable
from lib.io import bprint, bprintPrefix
from lib import db, poc, cmd2, banners, pprint2
from SETTINGS import BEESCAN_DIR, POC_DIR, VERSION


# decorater to record last command return value
def recordCmdRet(valName):
    def _recordCmdRet(func):
        def __recordCmdRet(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)
            setattr(self, valName, ret)
            return
        return __recordCmdRet
    return _recordCmdRet



class BaseMenu(cmd2.Cmd):
    default_to_shell = True
    timing = False
    nonWhiteMsg = 'Please enter a non white space string.'

    def __init__(self):
        super(BaseMenu, self).__init__()
        self.database = db.Database(dbFilePath='./hive.db')
        self.retLastSearch = None  # the result of last search

    def postloop(self):
        self.database.dbConn.close()

    def postcmd(self, stop, line):
        return stop

    def do_status(self, arg):
        '''print status information.'''
        bprintPrefix('BeeHive Version: %s' % VERSION, msgType='ok')
        bprintPrefix('Exploits & PoCs: %d\n' % self.database.countAll()[0], 'ok')

    @recordCmdRet(valName='retLastSearch')
    def do_search(self, arg):
        # the func doc below cannot be automatically used as help doc
        # because this func is wrapped by a decorator.
        if not arg.strip():
            bprintPrefix(self.nonWhiteMsg, 'warning')
            return
        try:
            results = self.database.searchStr(arg.strip())
        except Exception, err:
            print '[-] ',
            print err
            return
        res_tb = PrettyTable(['Name', 'Datetime', 'Level',
                              'Author', 'Batch', 'Pid',])
        res_tb.align['Name'] = 'l'
        for r in results:
            res_tb.add_row(((r[1][:35]+'...').strip(),
                            r[5][:10],r[3],r[4][:10],
                            r[-2],r[0][4:]))
        print res_tb.get_string(sortby='Pid', reversesort=False)
        return results

    def help_search(self):
        print '''[*] Search for pocs/exps.'''

    def do_run(self, arg):
        bprintPrefix("Can't run this command under the root menu.", 'error')
        return

    def help_run(self):
        print '''[-] UNKOWN'''

    @cmd2.options([cmd2.make_option('-m', '--mode', action='store', help='Update database. (json / pocs)'),])
    def do_updatedb(self, arg, opts=None):
        ''''''
        if opts.mode == 'pocs':
            try:
                num_insert, num_all, num_err, err_list = self.database.updtDbFromPocs(pocDir=POC_DIR)
                print '[*] Scan local mode\n%s\nTotal: %s' % ('--'*10, num_all)
            except Exception, err:
                bprintPrefix(err, 'error')
        elif opts.mode == 'json':
            try:
                num_insert, num_all, num_err, err_list = self.database.updtDbFromJson('./pocdb.json')
                print '[*] JSON import mode\n%s\nTotal: %s' % ('--'*10, num_all)
            except Exception, err:
                bprintPrefix(err, 'error')
        else:
            bprintPrefix('WTF!?', 'warning')
            return
        bprint('Insert number: %s' % num_insert, 'ok')
        bprint('Error number: %s' % num_err, 'error')
        for i in err_list:
            print '    %s' % i

    def do_showloaded(self, arg):
        '''[*] Show current loaded poc(s)'''
        if hasattr(self, 'loadedPocs') and self.loadedPocs:
            if isinstance(self, (ShooterMenu, HunterMenu)):
                bprintPrefix('loaded poc: %s' % \
                      self.loadedPocs.poc_info.get('poc').get('id'), 'ok')
            elif isinstance(self, StormMenu):
                bprintPrefix('loaded pocs: ', 'ok')
                for pocPath in self.loadedPocs:
                    print '    %s' % os.path.basename(pocPath)
        else:
            bprint('[-] no poc has been loaded.', 'error')

    def do_lastret(self, arg):
        '''[*] Show the result of last scan.'''
        if hasattr(self, 'retLastScan') and self.retLastScan:
            try:
                print
                res_tb, ret = self.retLastScan
                print res_tb.get_string(sortby='Status', reversesort=False)
                print
            except Exception, e:
                bprintPrefix('%s\n'%str(e), 'warning')
        else:
            bprintPrefix('No scan result.\n', 'warning')

    def do_export(self, arg):
        '''[*] Save the result as a file.'''
        if not arg.strip():
            bprintPrefix(self.nonWhiteMsg, 'error')
            return
        if hasattr(self, 'retLastScan') and self.retLastScan:
            try:
                res_tb, ret = self.retLastScan
                _output = open(arg.strip(), 'a+')
                _output.write(str(ret))
                _output.close()
                bprintPrefix('Write file success: %s' % arg.strip(), 'ok')
            except Exception, e:
                bprintPrefix('%s\n'%str(e), 'warning')
        else:
            bprintPrefix('No scan result.\n', 'warning')

    def do_info(self, arg):
        '''[*] View code information and usage.'''
        if not arg.strip():
            bprintPrefix(self.nonWhiteMsg, 'error')
            return
        if not arg.strip().startswith('poc'):
            pocName = 'poc-' + arg.strip()
            if pocName.strip()[8] != '-':
                pocName = 'poc-' + pocName[-8:-4] + '-' + pocName[-4:]
        else:
            pocName = arg.strip()
        pocInfo = self.database.searchPoc(
            pocId=pocName.strip().replace('_', '-'))
        if pocInfo is None:
            bprintPrefix('Cannot find poc %s in database.' % arg, 'error')
            return
        pocId, name, rank, level, author, createDate, protocol, port, \
            layer4Protocol, appName, vulType, desc, tag, batchable, \
            path = pocInfo
        if not path or not os.path.exists(path):
            bprintPrefix('Poc file %s not exists, perhaps you have\'t bought '\
                  'it.\n' % path, 'error')
            return
        try:
            p = poc.Poc(path=os.path.join(POC_DIR, '%s.py' % \
                                          pocName.strip().replace('-', '_')),
                        batchable=batchable)
            mp = p.module.MyPoc(run_in_shell=False)
            mp._init_parser(do_parse=False)
            bprint('%s information:' % path, 'ok')
            pprint2.pprint(mp.poc_info)
            print
            bprint('%s help:' % path, 'ok')
            mp.base_parser.print_help()
            #return mp
        except Exception, err:
            bprintPrefix(err, 'error')

    @staticmethod
    def extRunPocOpt(option_list, arg_desc="arg"):
        '''
           Used as a decorator and passed a list of optparse-style options,
           alters a cmd2 method to populate its ``opts`` argument from its
           raw text argument.

           Example: transform
           def do_something(self, arg):

           into
           @extPocOpt([make_option('-q', '--quick', action="store_true",
                      help="Makes things fast")],
                      "source dest")
           def do_something(self, arg, opts):
               if opts.quick:
                   self.fast_button = True
        '''

        if not isinstance(option_list, list):
            option_list = [option_list]
        for opt in option_list:
            cmd2.options_defined.append(
                pyparsing.Literal(opt.get_opt_string())
            )

        def option_setup(func):
            optionParser = cmd2.OptionParser()
            for opt in option_list:
                optionParser.add_option(opt)
            optionParser.set_usage("%s [options] %s" % (func.__name__[3:], arg_desc))
            optionParser._func = func
            def new_func(instance, arg):
                try:
                    for opt in instance.loadedPocs.base_parser._get_all_options():
                        try:
                            optionParser._check_conflict(opt)
                            optionParser.add_option(opt)
                        except optparse.OptionConflictError as e:
                            pass
                    instance.runParser = optionParser
                    opts, newArgList = optionParser.parse_args(arg.split())
                    # Must find the remaining args in the original argument list, but
                    # mustn't include the command itself
                    #if hasattr(arg, 'parsed') and newArgList[0] == arg.parsed.command:
                    #    newArgList = newArgList[1:]
                    newArgs = cmd2.remaining_args(arg, newArgList)
                    if isinstance(arg, cmd2.ParsedString):
                        arg = arg.with_args_replaced(newArgs)
                    else:
                        arg = newArgs
                except optparse.OptParseError as e:
                    print (e)
                    optionParser.print_help()
                    return
                except AttributeError as e:
                    bprintPrefix('Please load a poc first.', 'warning')
                    return
                if hasattr(opts, '_exit'):
                    return None
                result = func(instance, arg, opts)
                return result
            new_func.__doc__ = '%s\n%s' % (func.__doc__, optionParser.format_help())
            return new_func
        return option_setup



class MainMenu(BaseMenu):
    prompt = 'beehive > '

    def preloop(self):
        num_count = str(self.database.countAll()[0])
        print banners.getBanner()
        bprint('%sn0tr00t security team\n' % (' '*20), 'warning')
        sys.stdout.write('Beehive Version: ')
        bprint(VERSION, 'ok')
        sys.stdout.write('Exploits & Pocs: ')
        bprint(num_count, 'ok')
        sys.stdout.write('Contact: ')
        bprint('root@beebeeto.com', 'ok')
        sys.stdout.write('Forum: ')
        bprint('  http://buzz.beebeeto.com', 'ok')
        print

    def do_shooter(self, arg):
        '''[*] Go to the shooter(1 poc --> 1 target) sub menu.'''
        sm = ShooterMenu()
        sm.cmdloop()

    def do_storm(self, arg):
        '''[*] Go to the storm(N poc --> 1 target) sub menu.'''
        sm = StormMenu()
        sm.cmdloop()

    def do_hunter(self, arg):
        '''[*] Go to the hunter(1 poc --> N targets) sub menu.'''
        hm = HunterMenu()
        hm.cmdloop()



class StormMenu(BaseMenu):
    prompt = 'beehive.storm > '

    @recordCmdRet(valName='loadedPocs')
    def do_loadsearched(self, arg):
        if not self.retLastSearch:
            bprint('[-] please make a search first.', 'error')
            return
        batchablePocPaths = []
        unbatchablePocPaths = []
        for pocInfo in self.retLastSearch:
            pocId, name, rank, level, author, createDate, protocol, port, \
                layer4Protocol, appName, vulType, desc, tag, batchable, \
                path = pocInfo
            if batchable:
                batchablePocPaths.append(path)
            else:
                unbatchablePocPaths.append(path)
        if unbatchablePocPaths:
            bprintPrefix('These pocs in last search results are not batchable:', 'warning')
            bprintPrefix('They cannot be loaded in Storm mode, please load them '\
                  'singlely in the Shooter mode.', 'warning')
            for pocPath in unbatchablePocPaths:
                print '    %s' % os.path.basename(pocPath)
        if unbatchablePocPaths and batchablePocPaths:
            print
        if batchablePocPaths:
            bprintPrefix('These pocs in last search results are batchable:', 'ok')
            bprintPrefix('They are going to be used to load Storm mode scan.', 'ok')
            for pocPath in batchablePocPaths:
                print '    %s' % os.path.basename(pocPath)
            return batchablePocPaths
        else:
            bprintPrefix('None of the poc in last search result is batchable.', 'warning')
            return None

    def help_loadsearched(self):
        bprintPrefix('load last searched result(s) to test a target.', 'info')

    @recordCmdRet(valName='retLastScan')
    def do_run(self, arg):
        if not hasattr(self, 'loadedPocs') or not self.loadedPocs:
            bprintPrefix('Please load a poc first.', 'warning')
            return
        if not arg.strip():
            bprintPrefix('Please enter the target.', 'error')
            return
        s = Storm(target=arg,
                  listPocPaths=self.loadedPocs,
                  poolModule=TestPlatform(),
                  concurrency=20, verify=True)
        ret = s.scan()
        JOB_UNSTART = 0  # poc not run
        JOB_RUNNING = 1
        JOB_FINISHED = 2  # poc run ok
        JOB_ERROR = -1  # error encountered when run poc
        JOB_ABORT = -2  # running poc is abort, viz unfinished
        print
        bprintPrefix('Scan end, Results:\n', 'ok')
        res_tb = PrettyTable(['Vulnerability', 'Pid', 'Status', 'Result',])
        res_tb.align['Vulnerability'] = 'l'
        for r in ret.values():
            pid = r['args'][0].replace('_', '-')
            poc_info = self.database.searchPoc(pid)
            state = r['state']
            if state == JOB_FINISHED:
                status = str(r['jobRet']['success'])
                result = str(r['jobRet']['poc_ret'])
                if status == 'None':
                    status = 'False'
                    result = 'N/A'
                elif status == 'False':
                    result = 'Not Vulnerable'
            elif state == JOB_ERROR:
                status = 'Error'
                result = r['exception']
            else:
                status = 'Error'
            res_tb.add_row([poc_info[1][:25]+'...', pid,
                            status, result[:25]])
        print res_tb.get_string(sortby='Status', reversesort=False)
        print
        return res_tb, ret

    def help_run(self):
        bprintPrefix('Run loaded poc(s)', 'info')

    @recordCmdRet(valName='loadedPocs')
    def do_loadall(self, arg):
        try:
            batchablePocs = self.database.getBatchable()
            pocPaths = []
            [pocPaths.append(i[-1]) for i in batchablePocs]
            bprintPrefix('%d batchable pocs (%d total pocs) loaded.' % (
                len(pocPaths),
                self.database.countAll()[0],
            ), 'ok')
            return pocPaths
        except Exception, err:
            print '[-] ',
            print err
            return

    def help_loadall(self):
        bprintPrefix('Load all poc to storm a target.', 'info')



class ShooterMenu(BaseMenu):
    prompt = 'beehive.shooter > '

    @recordCmdRet(valName='loadedPocs')
    def do_loadpoc(self, arg):
        if not arg.strip().startswith('poc'):
            pocName = 'poc-' + arg.strip()
            if pocName.strip()[8] != '-':
                pocName = 'poc-' + pocName[-8:-4] + '-' + pocName[-4:]
        else:
            pocName = arg.strip()
        pocInfo = self.database.searchPoc(
            pocId=pocName.strip().replace('_', '-'))
        if pocInfo is None:
            bprintPrefix('Cannot find poc %s in database.' % arg, 'error')
            return
        pocId, name, rank, level, author, createDate, protocol, port, \
            layer4Protocol, appName, vulType, desc, tag, batchable, \
            path = pocInfo
        if not path or not os.path.exists(path):
            bprintPrefix('Poc file %s not exists, perhaps you have\'t bought '\
                  'it.\n' % path, 'error')
            return
        try:
            p = poc.Poc(path=os.path.join(POC_DIR, '%s.py' % \
                                          pocName.strip().replace('-', '_')),
                        batchable=batchable)
            mp = p.module.MyPoc(run_in_shell=False)
            mp._init_parser(do_parse=False)
            bprintPrefix('load %s success!' % path, 'ok')
            return mp
        except Exception, err:
            bprintPrefix(err, 'error')

    def help_loadpoc(self):
        bprintPrefix('Load a poc to test a target.', 'info')

    @recordCmdRet(valName='retLastScan')
    @BaseMenu.extRunPocOpt([
        cmd2.make_option('-d', '--debug', action="store_true", help="debug mode",)
    ])
    def do_run(self, arg, opts=None):
        if not hasattr(self, 'loadedPocs') or not self.loadedPocs:
            bprintPrefix('Please load a poc first.', 'warning')
            return
        if not opts.target:
            bprintPrefix('No target input!\n', 'warning')
            self.runParser.print_help()
            return
        print
        ret = self.loadedPocs.run(options=opts.__dict__, debug=opts.debug)
        bprintPrefix('%s:\n' % self.loadedPocs.poc_info['poc']['id'], 'info')
        # results view
        if ret['options']:
            print '%starget: %s' % (' '*4, ret['options']['target'])
        try:
            if ret['exception']:
                print '%sexception: %s' % (' '*4, ret['exception'])
        except Exception, err:
            pass
        if ret['success'] == True:
            print ' '*4,
            bprintPrefix('success: %s' % ret['success'], 'ok')
            print ' '*3,
            bprintPrefix('poc_ret: %s' % ret['poc_ret'], 'ok')
        else:
            print '%ssuccess: %s' % (' '*4, ret['success'])
        print
        return ret

    def help_run(self):
        bprintPrefix('Run poc to shoot a target.', 'info')



class HunterMenu(BaseMenu):
    prompt = 'beehive.hunter > '

    @recordCmdRet(valName='loadedPocs')
    def do_loadpoc(self, arg):
        if not arg.strip().startswith('poc'):
            pocName = 'poc-' + arg.strip()
            if pocName.strip()[8] != '-':
                pocName = 'poc-' + pocName[-8:-4] + '-' + pocName[-4:]
        else:
            pocName = arg.strip()
        pocInfo = self.database.searchPoc(
            pocId=pocName.strip().replace('_', '-'))
        if pocInfo is None:
            bprintPrefix('Cannot find poc %s in database.' % arg, 'error')
            return
        pocId, name, rank, level, author, createDate, protocol, port, \
            layer4Protocol, appName, vulType, desc, tag, batchable, \
            path = pocInfo
        if not path or not os.path.exists(path):
            bprintPrefix('Poc file %s not exists, perhaps you have\'t bought '\
                  'it.\n' % path, 'error')
            return
        try:
            p = poc.Poc(path=os.path.join(POC_DIR, '%s.py' % \
                                          pocName.strip().replace('-', '_')),
                        batchable=batchable)
            mp = p.module.MyPoc(run_in_shell=False)
            mp._init_parser(do_parse=False)
            bprintPrefix('load %s success!' % path, 'ok')
            return mp
        except Exception, err:
            bprintPrefix(err, 'error')

    def help_loadpoc(self):
        bprintPrefix('Load a poc to test a target.', 'info')

    @recordCmdRet(valName='retLastScan')
    @BaseMenu.extRunPocOpt([
        cmd2.make_option('-f', '--file', action="store", help="debug mode"),
    ])
    def do_run(self, arg, opts=None):
        if not hasattr(self, 'loadedPocs') or not self.loadedPocs:
            bprintPrefix('Please load a poc first.', 'warning')
            return
        file_alert = 'Need to load a targets file. (domains)'
        if not opts.file:
            bprintPrefix(file_alert, 'warning')
            return
        if opts.file:
            filename = opts.file
            if filename[0] == "'":
                filename = filename.strip("'")
            elif filename[0] == '"':
                filename = filename.strip('"')
        try:
            f_req = open(filename, 'r')
            if os.stat(filename).st_size == 0:
                bprintPrefix('File content is empty?', 'warning')
                return
        except Exception, err:
            bprintPrefix(str(err), 'error')
            return

        # scan main
        pocid = self.loadedPocs.poc_info.get('poc').get('id')
        (options, args) = self.loadedPocs.base_parser.parse_args(
            arg.strip().split())
        h = Hunter(iterTarget=f_req,
                   pocPath=('./pocs/%s.py' % pocid.replace('-', '_')),
                   poolModule=TestPlatform())
        ret = h.scan()

        # view table
        JOB_UNSTART = 0  # poc not run
        JOB_RUNNING = 1
        JOB_FINISHED = 2  # poc run ok
        JOB_ERROR = -1  # error encountered when run poc
        JOB_ABORT = -2  # running poc is abort, viz unfinished
        print
        res_tb = PrettyTable(['Target', 'Status', 'Result',])
        res_tb.align['Target'] = 'l'
        try:
            for r in ret.values():
                target = r['args']
                pid = r['args'][0].replace('_', '-')
                poc_info = self.database.searchPoc(pid)
                state = r['state']
                if state == JOB_FINISHED:
                    status = str(r['jobRet']['success'])
                    result = str(r['jobRet']['poc_ret'])
                    if status == 'None':
                        status = 'False'
                        result = 'N/A'
                    elif status == 'False':
                        result = 'Not Vulnerable'
                elif state == JOB_ERROR:
                    status = 'Error'
                    result = r['exception']
                else:
                    status = 'Error'
                res_tb.add_row([target, status, result[:25]])
        except Exception, err:
            import traceback
            traceback.print_exc()
        print res_tb.get_string(sortby='Status', reversesort=False)
        print
        return res_tb, ret

    def help_run(self):
        bprintPrefix('Run loaded poc(s)', 'info')


if __name__ == '__main__':
    mm = MainMenu()
    mm.cmdloop()
