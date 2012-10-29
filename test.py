#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
 Source file
 File name: test.py
 Creation date: 04-10-2012
 Author: dassier

'''

'''
Fichier de test pour le module "TestLinkAPI.py"
'''

import re
from testlink import TestLink, TestLinkErrors
from nose.tools import *

class TestClass():
    def setUp(self):
        """Initialisation
        """

        SERVEUR_URL = "http://localhost/testlink/lib/api/xmlrpc.php"
        KEY = "7ec252ab966ce88fd92c25d08635672b"
        self.client = TestLink(server_url=SERVEUR_URL, key=KEY)

    def test_getTestCaseIDByName(self):
        """ getTestCaseIDByName test
        """
        val = self.client.getTestCaseIDByName("Fin de programme", "Séquence 2", "Test 2")
        # 31 is test case id
        assert_equal(val, '31' )

        # Check if an error is raised in case of bad parameters
        assert_raises(TestLinkErrors, self.client.getTestCaseIDByName, "Initialisation", "Séquence 1", "Test 2")

    def test_getTestProjectByName(self):
        project = self.client.getTestProjectByName("Test 2")
        assert_equals(type(project), dict)
        # Check if an error is raised in case of bad parameters
        assert_raises(TestLinkErrors, self.client.getTestProjectByName, "Unknown project")

    def test_getTestPlanByName(self):
        plan_ok = self.client.getTestPlanByName("Test 2", "Full")

        # Assume that plan id is 33
        assert_equal(plan_ok['id'], '33')

        assert_raises(TestLinkErrors, self.client.getTestPlanByName, "Test 2", "Name Error")

    def test_getBuildByName(self):
        pass

    def test_reportResult(self):
        dico = {'testProjectName': 'Automatique',
                'testPlanName': 'FullAuto',
                'buildName': 'V0.1'}
        execid = self.client.reportResult("p", "test1", "S1", "An example of note", **dico)
        assert_equal(type(execid), str)

        execid = self.client.reportResult("f", "test2", "S1", **dico)
        assert_equal(type(execid), str)

    def test_getTestCasesForTestPlan(self):
        results = self.client.getTestCasesForTestPlan("Automatique", "FullAuto")
        for result in results:
            print result

        assert_equal(type(results), list)

        for elem in results:
            assert_equal(type(elem), dict)

    def test_getTestCaseCustomFieldDesignValue(self):
        test_list = self.client.getTestCasesForTestPlan("Automatique", "FullAuto")
        for test in test_list:
            #print test
            results = self.client.getTestCaseCustomFieldDesignValue("AutomaticTestFunction", "Automatique", test )
            if results != '':
                assert_equal(results, 'Fonction_auto-5')

    def test_getProjectIDByName(self):
        projectid = self.client.getProjectIDByName("Automatique")
        assert_equal(projectid, '52')

    def test_getTestCaseByExtID(self):
        """getTestCaseByExtID test method"""

        assert_raises(TestLinkErrors, self.client.getTestCaseByExtID, 'Id not known')

        extid = 'auto-5'
        results = self.client.getTestCaseByExtID(extid)
        assert_equal(results['full_tc_external_id'], extid)


