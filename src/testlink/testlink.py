#! /usr/bin/python
# -*- coding: UTF-8 -*-

#  Copyright 2012 pade (Patrick Dassier), TestLink-API-Python-client developers
#
#  Licensed under ???
#  see https://github.com/orenault/TestLink-API-Python-client/issues/4

from testlinkapi import TestlinkAPIClient, TestLinkHelper
from testlinkerrors import TestLinkError
from datetime import datetime

class TestCase(object):
    """Test case object"""

    def __init__(self):
        self.id = ''
        self.extid = ''
        self.version = ''
        self.is_open = False
        self.is_active = False
        self.name = ''
        self.summary = ''
        self.preconditions = ''
        # Must be 'auto' or 'manual'
        self.execution_type = ''
        self.testsuite = TestSuite()
        self.project = TestProject()

class TestSuite(object):
    """TestSuite object"""
    def __init__(self):
        self.id = ''
        self.details = ''
        self.name = ''
        self.node_order = ''
        self.node_type_id = ''
        self.parent = None
        self.is_root = False
        self.project = None

class TestProject(object):
    """TestProject object"""
    def __init__(self):
        self.id = ''
        self.is_active = False
        self.is_public = False
        self.name = ''

class TestLink(TestlinkAPIClient):
    """
    TestLink API library 
    provide a user friendly library, with more robustness and error management
    """

    def __init__(self, server_url, key):
        """
        Class initialisation
        """
        super(TestLink, self).__init__(server_url, key)

    def getTestProjectByID(self, testprojectid):
        """
        Return a project according to its id
        A TestLinkError is raised if id is not found
        """
        # First get all projects
        projects = self.getProjects()

        for p in projects:
            if p['id'] == testprojectid:
                prj = TestProject()
                prj.id = p['id']
                prj.is_active = p['active'] == '1'
                prj.is_public = p['is_public'] == '1'
                prj.name = p['name']
                return prj
        # No project found, raise an error
        raise TestLinkError("(getProjectByID) - Project with id %s is not found" % testprojectid)


    def getTestSuiteByID(self, testsuiteid):
        """docstring for getTestSuiteByID"""
        result = super(TestLink, self).getTestSuiteByID(testsuiteid)

        # Check error
        if type(result) == list and 'message' in result[0]:
            raise TestLinkError(result[0]['message'])

        ts = TestSuite()
        ts.id = result['id']
        ts.details = result['details']
        ts.name = result['name']
        ts.node_order = result['node_order']
        ts.node_type_id = result['node_type_id']

        # Is parent_id an id of a test suite ?
        try:
            ts_parent = self.getTestSuiteByID(result['parent_id'])
        except TestLinkError:
            # Parent is not a test suite, so it is a project
            ts.project = self.getTestProjectByID(result['parent_id'])
            ts.parent = None
            ts.is_root = True
        else:
            # Parent is a test suite
            # register it
            ts.parent = ts_parent
            ts.is_root = False

            # Also register the project
            # find it in parent object
            ts.project = ts.parent.project

        return ts

    def getTestCase(self, testcaseid=None, testcaseexternalid=None, version=None):
        """
        Return the TestCase object according to parameters
        """
        # Check parameters
        if testcaseid is None and testcaseexternalid is None:
            raise TestLinkError("(getTestCase) - You must specified 'testcaseid' or 'testcaseexternalid'")

        result = super(TestLink, self).getTestCase(testcaseid, testcaseexternalid, version)

        # Check error
        if 'message' in result[0]:
            raise TestLinkError(result[0]['message'])


        # Create TestCase object
        tc = TestCase()
        tc.id = result[0]['testcase_id']
        tc.extid = result[0]['full_tc_external_id']
        tc.version = result[0]['version']
        tc.is_active = result[0]['active'] == '1'
        tc.is_open = result[0]['is_open'] == '1'
        tc.name = result[0]['name']
        tc.summary = result[0]['summary']
        tc.preconditions = result[0]['preconditions']
        if result[0]['execution_type'] == '2':
            #Automatic test
            tc.execution_type = 'auto'
        else:
            # Manual testProjectName
            tc.execution_type = 'manual'
        tc.testsuite = self.getTestSuiteByID(result[0]['testsuite_id'])
        tc.project = tc.testsuite.project

        return tc

    def getTestCaseIDByName(self, testCaseName, testSuiteName, testProjectName):
        """
        Find a test case by its name, by its suite and its project
        Suite name must not be duplicate, so only one test case must be found 
        Return test case id if success 
        or raise TestLinkError exception with error message in case of error
        """    
        results = super(TestLink, self).getTestCaseIDByName(testCaseName, testSuiteName, testProjectName)
        if results[0].has_key("message"):
            raise TestLinkError(results[0]["message"])
        elif len(results) > 1:
            raise TestLinkError("(getTestCaseIDByName) - Several case test found. Suite name must not be duplicate for the same project")
        else:
            if results[0]["name"] == testCaseName:
                    return results[0]["id"]
            raise TestLinkError("(getTestCaseIDByName) - Internal server error. Return value is not expected one!")

    def getTestCasesForTestPlan(self, testProjectName, testPlanName):
        """
        Return a list of tests case object of testProjectName project, for the selected test plan
        """

        # Get test plan ID
        plan = self.getTestPlanByName(testProjectName, testPlanName)

        # Get tests cases
        results = super(TestLink, self).getTestCasesForTestPlan(plan["id"])

        ret_value = []
        for k in results.keys():
            # Get test case object associated of return test case id
            # and append it to test case list
            ret_value.append(self.getTestCase(testcaseid=k))

        return ret_value

    def getTestCaseCustomFieldDesignValue(self, customFieldName, testCaseObject):
        """
        Return custom fields value for the specified test case object
        Test case object is an object return by 'getTestCase' method
        A TestLinkError is raised is case of problem
        """

        extid = testCaseObject.extid
        version = testCaseObject.version
        projectid = testCaseObject.testsuite.project.id 

        results = super(TestLink, self).getTestCaseCustomFieldDesignValue(extid, version, projectid, customFieldName)

        return results

    def getTestProjectByName(self, testProjectName):
        """ Return project object correcponding to the testProjectName name
        or raise a TestLinkError if project name is not found
        """
        prj_id = self.getProjectIDByName(testProjectName)
        if prj_id == -1:
            raise TestLinkError("(getProjectByName) - Project %s is not found" % testProjectName)
        else:
            return self.getTestProjectByID(prj_id)

    def reportResult(self, testResult, testCase, testNotes="", **kwargs):
        """
        Report results for test case
        Arguments are:
        - testResult: "p" for passed, "b" for blocked, "f" for failed
        - testCase: the concern test case object
        - testNotes: optional, if empty will be replace by a default string. To let it blank, just set testNotes to " " characters
        - an anonymous dictionnary with followings keys:
            - testPlanName: the active test plan
            - buildName: the active build.
        Raise a TestLinkError error with the error message in case of trouble
        Return the execution id needs to attach files to test execution
        """
        
        # Check parameters
        for data in ["testPlanName", "buildName"]:
            if data not in kwargs:
                raise TestLinkError("(reportResult) - Missing key %s in anonymous dictionnary" % data)

        # Get project object
        project = testCase.project

        # Check if project is active
        if not project.is_active:
            raise TestLinkError("(reportResult) - Test project %s is not active" % project.name)

        # Check test plan name
        plan = self.getTestPlanByName(project.name, kwargs["testPlanName"])

        # Check is test plan is open and active
        if plan['is_open'] != '1' or plan['active'] != '1':
            raise TestLinkError("(reportResult) - Test plan %s is not active or not open" % kwargs["testPlanName"])
        # Memorise test plan id
        planId = plan['id']

        # Check build name
        build = self.getBuildByName(project.name, kwargs["testPlanName"], kwargs["buildName"])

        # Check if build is open and active
        if build['is_open'] != '1' or build['active'] != '1':
            raise TestLinkError("(reportResult) - Build %s in not active or not open" % kwargs["buildName"])

        # Check results parameters
        if testResult not in "pbf":
            raise TestLinkError("(reportResult) - Test result must be 'p', 'f' or 'b'")

        if testNotes == "":
            # Builds testNotes if empty
            today = datetime.today()
            testNotes = "%s - Test performed automatically" % today.strftime("%c")
        elif testNotes == " ":
            #No notes
            testNotes = ""

        # Now report results
        results = self.reportTCResult(testCase.id, planId, kwargs["buildName"], testResult, testNotes)
        # Check errors
        if results[0]["message"] != "Success!":
            raise TestLinkError(results[0]["message"])

        return results[0]['id']

#    def getTestProjectByName(self, testProjectName):
        #"""
        #Return project
        #A TestLinkError is raised in case of error
        #"""
        #results = super(TestLink, self).getTestProjectByName(testProjectName)
        #if results[0].has_key("message"):
            #raise TestLinkError(results[0]["message"])

        #return results[0]

    def getTestPlanByName(self, testProjectName, testPlanName):
        """
        Return test plan
        A TestLinkError is raised in case of error
        """
        results = super(TestLink, self).getTestPlanByName(testProjectName, testPlanName)
        if "message" in results[0]:
            raise TestLinkError(results[0]["message"])

        return results[0]

    def getBuildByName(self, testProjectName, testPlanName, buildName):
        """
        Return build corresponding to buildName
        A TestLinkError is raised in case of error
        """
        plan = self.getTestPlanByName(testProjectName, testPlanName)
        builds = self.getBuildsForTestPlan(plan['id'])

        # Check if a builds exists
        if builds == '':
            raise TestLinkError("(getBuildByName) - Builds %s does not exists for test plan %s" % (buildName, testPlanName))

        # Search the correct build name in the return builds list
        for build in builds:
            if build['name'] == buildName:
                return build

        # No build found with builName name
        raise TestLinkError("(getBuildsByName) - Builds %s does not exists for test plan %s" % (buildName, testPlanName))

    def getTestCaseByExtID(self, testCaseExternalID):
        """Return test case by its external ID
        Error are managed by getTestCase method"""
        return self.getTestCase(testcaseexternalid=testCaseExternalID)



if __name__ == "__main__":
    tl_helper = TestLinkHelper()
    tl_helper.setParamsFromArgs()
    myTestLink = tl_helper.connect(TestLink)
    print myTestLink
    print myTestLink.about()
