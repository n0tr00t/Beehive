#!/usr/bin/env python
# coding: utf-8
# site  : beebeeto.com
# team  : n0tr00t security

import os
import sys
import sqlite3 as sq3
import collections as clt

try:
    import simplejson as json
except ImportError:
    import json

from poc import Poc


class Database(object):
    tables = {
        'poc': [
            'id',
            'name',
            'rank',
            'level',
            'author',
            'create_date',
            'protocol',
            'port',
            'layer4_protocol',
            'app_name',
            'vul_type',
            'tag',
            'desc',
            'batchable',
            'path',
        ],
    }

    def __init__(self, dbFilePath='./hive.db', pocDir='./pocs'):
        self.dbConn = sq3.connect(dbFilePath)
        self.pocDir = pocDir
        self.cursor = self.dbConn.cursor()

    def updtDbFromPocs(self, pocDir='../pocs/'):
        '''
        Update local sqlite database according to the
        poc_info in the pocs' source code online database.
        '''
        updatedNum = 0
        insertedNum = 0
        errNum = 0
        errPocs = []
        for pocFileName in os.listdir(pocDir):
            if pocFileName.startswith('poc') and pocFileName.endswith('py'):
                try:
                    pocInfo = Poc(os.path.join(pocDir, pocFileName),
                                  batchable=False).module.MyPoc.poc_info
                    status = self.__updtFromPocInfo(pocInfo)
                    if status == 'inserted':
                        insertedNum += 1
                    elif status == 'updated':
                        updatedNum += 1
                except Exception, err:
                    errNum += 1
                    errPocs.append('%s:%s...' % (pocFileName, str(err)[:50]))
        self.dbConn.commit()
        return (insertedNum, updatedNum, errNum, errPocs)

    def __updtFromPocInfo(self, pocInfo):
        self.cursor.execute('SELECT * FROM poc WHERE id=?',
                            (pocInfo['poc']['id'],))
        pocPath = os.path.join(self.pocDir,
                               '%s.py' % pocInfo['poc']['id'].replace('-', '_'))
        if not self.cursor.fetchone():
            args = [
                pocInfo['poc']['id'],
                pocInfo['poc']['name'].decode('utf-8', 'ignore'),
                None,
                None,
                pocInfo['poc']['author'].decode('utf-8', 'ignore'),
                pocInfo['poc']['create_date'],
                pocInfo['protocol']['name'],
                '%s' % ','.join([str(i) for i in pocInfo['protocol']['port']]),
                '%s' % ','.join(pocInfo['protocol']['layer4_protocol']),
                pocInfo['vul']['app_name'].decode('utf-8', 'ignore'),
                pocInfo['vul']['type'],
                '%s' % ','.join([i.decode('utf-8', 'ignore') for i in pocInfo['vul']['tag']]),
                pocInfo['vul']['desc'].decode('utf-8', 'ignore'),
                None,
                pocPath if os.path.exists(pocPath) else None,
            ]
            sql = 'INSERT INTO poc VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            self.cursor.execute(sql, args)
            return 'inserted'
        else:
            args = [
                pocInfo['poc']['name'].decode('utf-8', 'ignore'),
                pocInfo['poc']['author'].decode('utf-8', 'ignore'),
                pocInfo['poc']['create_date'],
                pocInfo['protocol']['name'],
                '%s' % ','.join([str(i) for i in pocInfo['protocol']['port']]),
                '%s' % ','.join(pocInfo['protocol']['layer4_protocol']),
                pocInfo['vul']['app_name'].decode('utf-8', 'ignore'),
                pocInfo['vul']['type'],
                '%s' % ','.join([i.decode('utf-8', 'ignore') for i in pocInfo['vul']['tag']]),
                pocInfo['vul']['desc'].decode('utf-8', 'ignore'),
                pocPath if os.path.exists(pocPath) else None,
                pocInfo['poc']['id'],
            ]
            sql = 'UPDATE poc SET name=?, author=?, create_date=?, '\
                  'protocol=?, port=?, layer4_protocol=?, app_name=?, '\
                  'vul_type=?, tag=?, desc=?, path=? WHERE id=?'
            self.cursor.execute(sql, args)
            return 'updated'

    def updtDbFromJson(self, jsonFile):
        '''
        Update local sqlite database according to the
        dumped json file export from beebeeto.com.
        '''
        updatedNum = 0
        insertedNum = 0
        errNum = 0
        errPocs = []
        f = open(jsonFile, 'rbU')
        for row in f:
            try:
                status = self.__updtFromJsonRow(
                    dictRow=json.loads(row.strip())
                )
                if status == 'inserted':
                    insertedNum += 1
                elif status == 'updated':
                    updatedNum += 1
            except Exception, err:
                errNum += 1
                errPocs.append('%s:%s...' % (row.strip(), str(err)[:50]))
        self.dbConn.commit()
        f.close()
        return (insertedNum, updatedNum, errNum, errPocs)

    def __updtFromJsonRow(self, dictRow):
        pocId = dictRow.get('id')
        if not pocId:
            return
        pocPath = os.path.join(self.pocDir,
                               '%s.py' % pocId.replace('-', '_'))
        pocFile = open(pocPath, 'wb')
        pocFile.write(dictRow.get('source_code').encode('utf-8', 'ignore'))
        pocFile.close()
        dbMapping = [
            ('id', pocId, ),
            ('name', dictRow.get('name'), ),
            ('rank', dictRow.get('rank'), ) ,
            ('level', dictRow.get('level'), ),
            ('author', dictRow.get('author'),),
            ('create_date', dictRow.get('create_date'), ),
            ('protocol', None, ),
            ('port', None, ),
            ('layer4_protocol', None, ),
            ('app_name', dictRow.get('app_name'), ),
            ('vul_type', dictRow.get('vul_type'), ),
            ('tag', dictRow.get('tag'), ),
            ('desc', dictRow.get('desc'), ),
            ('batchable', dictRow.get('batchable'), ),
            ('path', pocPath if os.path.exists(pocPath) else None, ),
        ]
        self.cursor.execute('SELECT * FROM poc WHERE id=?',(pocId,))
        if not self.cursor.fetchone():
            sql = ' '.join([
                'INSERT INTO poc VALUES',
                '(%s)' % ','.join('?' * len(dbMapping)),
            ])
            self.cursor.execute(sql, map(lambda i: i[1], dbMapping))
            return 'inserted'
        else:
            sql1 = 'UPDATE poc SET'
            sql2 = ', '.join(['%s=?' % i[0] for i in dbMapping[1:] if i[1] is not None])
            sql3 = 'WHERE id=?'
            sql = ' '.join([sql1, sql2, sql3])
            args = [i[1] for i in dbMapping[1:] if i[1] is not None]
            args.append(pocId)
            self.cursor.execute(sql, args)
            return 'updated'

    def searchStr(self, item):
        columns = [
            'name',
            'app_name',
            'tag',
            'desc',
        ]
        sql = 'SELECT * FROM poc WHERE ' + ' or '.join(
            ['LOWER(%s) like "%%%s%%"' % (col, item.lower()) for col in columns]
        )
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def searchPoc(self, pocId):
        sql = 'SELECT * FROM poc WHERE id=?'
        self.cursor.execute(sql, (pocId,))
        return self.cursor.fetchone()

    def getBatchable(self):
        sql = 'SELECT * FROM poc WHERE batchable=1'
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def countAll(self):
        sql = 'SELECT count(*) FROM poc'
        self.cursor.execute(sql)
        return self.cursor.fetchone()


if __name__ == '__main__':
    # testing code
    sys.path.append('../')
    from SETTINGS import FRAMEWORK_DIR
    sys.path.append(FRAMEWORK_DIR)

    from pprint import pprint as pr

    db = Database(dbFilePath='../hive.db',
                  pocDir='../pocs/')

    #print db.updtDbFromBB2Db(bb2DbFile='../pocdb.json')
    #print db.updtDbFromPocs(pocDir='../pocs')

    #pr(db.searchStr(item='discuz'))
    #pr(db.countAll())
    #pr(db.searchPoc(pocId='poc-2014-0019'))

    #pr(db.getBatchable())
    pr(db.updtDbFromJson(jsonFile='../pocdb.json'))
