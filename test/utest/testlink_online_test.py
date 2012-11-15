#! /usr/bin/python
# -*- coding: UTF-8 -*-

#  Copyright 2012 Luiko Czub, TestLink-API-Python-client developers
#
#  Licensed under ???
#  see https://github.com/orenault/TestLink-API-Python-client/issues/4

# this test requires an online TestLink Server, which connection parameters
# are defined in environment variables
#     TESTLINK_API_PYTHON_DEVKEY and TESTLINK_API_PYTHON_DEVKEY
#
# works with the example project NEW_PROJECT_API  (see TestLinkExample.py)

import unittest
from testlink import TestLink, TestLinkHelper

class TestLinkOnlineTestCase(unittest.TestCase):
    """ TestCases for TestLink - interacts with a TestLink Server.
    works with the example project NEW_PROJECT_API (see TestLinkExample.py)
    """

    def setUp(self):
        self.client = TestLinkHelper().connect(TestLink)


#    def tearDown(self):
#        pass


    def checkFields(self, tl_obj, **fieldvalues):
        for fname, valueTarget in fieldvalues.iteritems():
            valueCurrent = getattr(tl_obj, fname)
            self.assertEqual(valueTarget, valueCurrent)
            
    def test_getTestCase_manual(self):
        " test .getTestCase() with externalid -> TestCase obj (manual)"
        a_tc = self.client.getTestCase(testcaseexternalid='NPROAPI-1')
        self.checkFields(a_tc, name='TESTCASE_AA', extid='NPROAPI-1',
                         version='1', is_active=True, is_open=True,
                         summary='This is the summary of the Test Case AA', 
                         preconditions='these are the preconditions',
                         execution_type='manual')
        
    def test_getTestCase_auto(self):
        " test .getTestCase() with testcaseid -> TestCase obj (auto)"
        a_tc = self.client.getTestCase(testcaseexternalid='NPROAPI-2')
        self.checkFields(a_tc, name='TESTCASE_B', extid='NPROAPI-2',
                         version='1', is_active=True, is_open=True,
                         summary='This is the summary of the Test Case B', 
                         preconditions='these are the preconditions',
                         execution_type='auto')        
        
    def test_getTestProjectByID(self):
        " test .getTestProjectByID "
        projID = self.client.getProjectIDByName('NEW_PROJECT_API')
        a_tp = self.client.getTestProjectByID(projID)
        self.checkFields(a_tp, name='NEW_PROJECT_API', id=projID,
                         is_active=True, is_public=True)        
        
    def test_getTestSuiteByID_nonroot(self):
        " test .getTestProjectByID "
        tcData = self.client._callServer('getTestCase', 
                                          {'devKey' : self.client.devKey,
                                           'testcaseexternalid' : 'NPROAPI-1'})
        tsID = tcData[0]['testsuite_id']
        a_ts = self.client.getTestSuiteByID(tsID)
        self.checkFields(a_ts, name='AA - Second Level', id=tsID,
                         details='Details of the Test Suite AA',
                         node_order='0', node_type_id='2', is_root=False)
                
    def test_getTestSuiteByID_root(self):
        " test .getTestProjectByID "
        tcData = self.client._callServer('getTestCase', 
                                          {'devKey' : self.client.devKey,
                                           'testcaseexternalid' : 'NPROAPI-1'})
        tsChildID = tcData[0]['testsuite_id']
        tsChildData = self.client._callServer('getTestSuiteByID', 
                                          {'devKey' : self.client.devKey,
                                           'testsuiteid' : tsChildID})
        tsID = tsChildData['parent_id']
        a_ts = self.client.getTestSuiteByID(tsID)
        self.checkFields(a_ts, name='A - First Level', id=tsID,
                         details='Details of the Test Suite A',
                         node_order='0', node_type_id='2', is_root=True)        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()