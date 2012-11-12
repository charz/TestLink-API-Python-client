#! /usr/bin/python
# -*- coding: UTF-8 -*-

#  Copyright 2012 Paul Dassier, Luiko Czub, TestLink-API-Python-client developers
#
#  Licensed under ???
#  see https://github.com/orenault/TestLink-API-Python-client/issues/4

# this test works WITHOUT an online TestLink Server
# no calls are send to a TestLink Server

import unittest
from testlink import testlinkobjects
from testlinkapi_offline_test import DummyAPIClient

SCENARIO_TLOBJ = {'getTLObject' :
                  {'01' : [{'name' : 'Big Bird', 'id' : '01'}],
                   '02' : [{'name' : 'Small Bird', 'id' : '02'}]
                   }}
SCENARIO_TC = {'getTestCase' :
    {'07' :  [{'full_tc_external_id': 'NPROAPI-1', 'node_order': '0', 'is_open': '1', 
     'id': '8', 'author_last_name': 'Administrator', 'updater_login': '', 'layout': '1', 
     'tc_external_id': '1', 'version': '1', 'testsuite_id': '6', 'updater_id': '', 
     'status': '1', 'updater_first_name': '', 'testcase_id': '7', 'author_first_name': 'Testlink',
     'importance': '2', 'modification_ts': '', 'execution_type': '1', 'preconditions': 'these are the preconditions',
     'active': '1', 'creation_ts': '2012-11-03 16:22:33', 'name': 'TESTCASE_AA',
     'summary': 'This is the summary of the Test Case AA', 'updater_last_name': '',
     'steps': [{'step_number': '1', 'actions': 'Step action 1', 'execution_type': '1',
                'active': '1', 'id': '9', 'expected_results': 'Step result 1'}, 
               {'step_number': '2', 'actions': 'Step action 2', 'execution_type': '1',
                'active': '1', 'id': '10', 'expected_results': 'Step result 2'}, 
               {'step_number': '3', 'actions': 'Step action 3', 'execution_type': '1', 
                'active': '1', 'id': '11', 'expected_results': 'Step result 3'},
               {'step_number': '4', 'actions': 'Step action 4', 'execution_type': '1',
                'active': '1', 'id': '12', 'expected_results': 'Step result 4'},
               {'step_number': '5', 'actions': 'Step action 5', 'execution_type': '1',
                'active': '1', 'id': '13', 'expected_results': 'Step result 5'}],
     'author_id': '1', 'author_login': 'admin'}],
    '33' : [{'node_type_id': '3', 'tcversion_id': '24', 'name': 'TESTCASE_B', 
             'parent_id': '24', 'node_order': '0', 'node_table': 'testcases',
             'external_id': 'NPROAPI-2', 'id': '33'}]
        }}

class DummyAPIObject(DummyAPIClient):
    """ Dummy for Simulation TestLinkAPICLient. 
    Overrides _callServer() Method to return test scenarios
    """
    def _callServer(self, methodAPI, argsAPI=None):
        data = self.scenario_data[methodAPI]
        response = None
        if methodAPI in ['getTLObject']:
            response = data[argsAPI['testobjectid']]
        elif methodAPI in ['getTestCase']:
            response = data[argsAPI['testcaseid']]
        else:
            response = super(DummyAPIObject, self)._callServer(methodAPI, 
                                                               argsAPI)
        return response

class TLObject(testlinkobjects.TestLinkObject):
    """ Helper class for testing generic class TestLinkObject """

    # Name API getMethod for class data 
    APIGETMETHOD = 'getTLObject'
    # Name API fieldname for id
    APIIDFNAME = 'testobjectid'
      

class TestLinkObjectTestCase(unittest.TestCase):
    """ TestCases for TestLinkObject
    
    does not interacts with a TestLink Server
    works with DummyAPIObject which returns special test data
    """

    def setUp(self):
        self.api = DummyAPIObject('http://dummy_server_url', 'dummy_devKey')
        self.api.loadScenario(SCENARIO_TLOBJ)

#    def tearDown(self):
#        pass

    def test_init_without_args(self):
        """ init TestLinkObject without args """

        a_tlobj = TLObject(self.api)
        self.assertEqual(self.api, a_tlobj._api)
        self.assertDictEqual({}, a_tlobj._attributes)
        
    def test_init_with_args(self):
        """ init TestLinkObject with args """

        obj_data = {'name' : 'red bird', 'id': '11'}
        a_tlobj = TLObject(self.api, **obj_data)
        self.assertEqual(self.api, a_tlobj._api)
        self.assertDictEqual(obj_data, a_tlobj._attributes)

    def test_setAttributesFromAPI(self):
        """ set TestLinkObject attributes with return of server call """

        obj_data = SCENARIO_TLOBJ['getTLObject']['01'][0]
        a_tlobj = TLObject(self.api)
        a_tlobj.setAttributesFromAPI('01')
        self.assertDictEqual(obj_data, a_tlobj._attributes)

    def test__getattr(self):
        """ return ._attributes values as self attributes """
        a_tlobj = TLObject(self.api)
        a_tlobj._attributes['field01'] = 'value01'
        self.assertEqual('value01', a_tlobj.field01)

class TLTestCaseTestCase(unittest.TestCase):
    """ TestCases for TLTestCase
    
    does not interacts with a TestLink Server
    works with DummyAPIObject which returns special test data
    """

    def setUp(self):
        self.api = DummyAPIObject('http://dummy_server_url', 'dummy_devKey')
        self.api.loadScenario(SCENARIO_TC)

#    def tearDown(self):
#        pass

    def test_setAttributes_with_steps(self):
        """ set TestCase attributes with API data including steps """

        a_tlobj = testlinkobjects.TLTestCase(self.api)
        a_tlobj.setAttributesFromAPI('07')
        self.assertEqual('2012-11-03 16:22:33', a_tlobj.creation_ts)

    def test_setAttributes_without_steps(self):
        """ set TestCase attributes with API data without steps """

        a_tlobj = testlinkobjects.TLTestCase(self.api)
        a_tlobj.setAttributesFromAPI('33')
        self.assertEqual('24', a_tlobj.parent_id)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()