# -*- coding: utf-8 -*-

from testlinkapi import TestlinkAPIClient, TestLinkHelper
from testlinkerrors import TestLinkError

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

class TestLink(TestLinkAPIClient):
    """
    TestLink API library
    """

    __VERSION__ = "0.1"

    def __init__(self, server_url, key):
        """
        Class initialisation
        """
        super(TestLink, self).__init__(server_url, key)

    def getTestProjectByID(self, testprojectid):
        """
        Return a project according to its id
        A TestLinkErrors is raised if id is not found
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
        raise TestLinkErrors("(getProjectByID) - Project with id %s is not found" % testprojectid)


    def getTestSuiteByID(self, testsuiteid):
        """docstring for getTestSuiteByID"""
        result = super(TestLink, self).getTestSuiteByID(testsuiteid)

        # Check error
        if type(result) == list and 'message' in result[0]:
            raise TestLinkErrors(result[0]['message'])

        ts = TestSuite()
        ts.id = result['id']
        ts.details = result['details']
        ts.name = result['name']
        ts.node_order = result['node_order']
        ts.node_type_id = result['node_type_id']

        # Is parent_id an id of a test suite ?
        try:
            ts_parent = self.getTestSuiteByID(result['parent_id'])
        except TestLinkErrors:
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
            raise TestLinkErrors("(getTestCase) - You must specified 'testcaseid' or 'testcaseexternalid'")

        result = super(TestLink, self).getTestCase(testcaseid, testcaseexternalid, version)

        # Check error
        if 'message' in result[0]:
            raise TestLinkErrors(result[0]['message'])


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

        return tc

    def getTestCaseIDByName(self, testCaseName, testSuiteName, testProjectName):
        """
        Find a test case by its name, by its suite and its project
        Suite name must not be duplicate, so only one test case must be found 
        Return test case id if success 
        or raise TestLinkErrors exception with error message in case of error
        """    
        results = super(TestLink, self).getTestCaseIDByName(testCaseName, testSuiteName, testProjectName)
        if results[0].has_key("message"):
            raise TestLinkErrors(results[0]["message"])
        elif len(results) > 1:
            raise TestLinkErrors("(getTestCaseIDByName) - Several case test found. Suite name must not be duplicate for the same project")
        else:
            if results[0]["name"] == testCaseName:
                    return results[0]["id"]
            raise TestLinkErrors("(getTestCaseIDByName) - Internal server error. Return value is not expected one!")

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
        A TestLinkErrors is raised is case of problem
        """

        extid = testCaseObject.extid
        version = testCaseObject.version
        projectid = testCaseObject.testsuite.project.id 

        results = super(TestLink, self).getTestCaseCustomFieldDesignValue(extid, version, projectid, customFieldName)

        return results

    def getTestProjectByName(self, testProjectName):
        """ Return project object correcponding to the testProjectName name
        or raise a TestLinkErrors if project name is not found
        """
        prj_id = self.getProjectIDByName(testProjectName)
        if prj_id == -1:
            raise TestLinkErrors("(getProjectByName) - Project %s is not found" % testProjectName)
        else:
            return self.getTestProjectByID(prj_id)

    def reportResult(self, testResult, testCaseName, testSuiteName, testNotes="", **kwargs):
        """
        Report results for test case
        Arguments are:
        - testResult: "p" for passed, "b" for blocked, "f" for failed
        - testCaseName: the test case name to report
        - testSuiteName: the test suite name that support the test case
        - testNotes: optional, if empty will be replace by a default string. To let it blank, just set testNotes to " " characters
        - an anonymous dictionnary with followings keys:
            - testProjectName: the project to fill
            - testPlanName: the active test plan
            - buildName: the active build.
        Raise a TestLinkErrors error with the error message in case of trouble
        Return the execution id needs to attach files to test execution
        """
        
        # Check parameters
        for data in ["testProjectName", "testPlanName", "buildName"]:
            if not kwargs.has_key(data):
                raise TestLinkErrors("(reportResult) - Missing key %s in anonymous dictionnary" % data)

        # Get project id
        project = self.getTestProjectByName(kwargs["testProjectName"])

        # Check if project is active
        if project['active'] != '1':
            raise TestLinkErrors("(reportResult) - Test project %s is not active" % kwargs["testProjectName"])

        # Check test plan name
        plan = self.getTestPlanByName(kwargs["testProjectName"], kwargs["testPlanName"])

        # Check is test plan is open and active
        if plan['is_open'] != '1' or plan['active'] != '1':
            raise TestLinkErrors("(reportResult) - Test plan %s is not active or not open" % kwargs["testPlanName"])
        # Memorise test plan id
        planId = plan['id']

        # Check build name
        build = self.getBuildByName(kwargs["testProjectName"], kwargs["testPlanName"], kwargs["buildName"])

        # Check if build is open and active
        if build['is_open'] != '1' or build['active'] != '1':
            raise TestLinkErrors("(reportResult) - Build %s in not active or not open" % kwargs["buildName"])

        # Get test case id
        caseId = self.getTestCaseIDByName(testCaseName, testSuiteName, kwargs["testProjectName"])

        # Check results parameters
        if testResult not in "pbf":
            raise TestLinkErrors("(reportResult) - Test result must be 'p', 'f' or 'b'")

        if testNotes == "":
            # Builds testNotes if empty
            today = datetime.today()
            testNotes = "%s - Test performed automatically" % today.strftime("%c")
        elif testNotes == " ":
            #No notes
            testNotes = ""

        print "testNotes: %s" % testNotes
        # Now report results
        results = self.reportTCResult(caseId, planId, kwargs["buildName"], testResult, testNotes)
        # Check errors
        if results[0]["message"] != "Success!":
            raise TestLinkErrors(results[0]["message"])
    
        return results[0]['id']

    def getTestProjectByName(self, testProjectName):
        """
        Return project
        A TestLinkErrors is raised in case of error
        """
        results = super(TestLink, self).getTestProjectByName(testProjectName)
        if results[0].has_key("message"):
             raise TestLinkErrors(results[0]["message"])

        return results[0]

    def getTestPlanByName(self, testProjectName, testPlanName):
        """
        Return test plan
        A TestLinkErrors is raised in case of error
        """
        results = super(TestLink, self).getTestPlanByName(testProjectName, testPlanName)
        if "message" in results[0]:
            raise TestLinkErrors(results[0]["message"])

        return results[0]

    def getBuildByName(self, testProjectName, testPlanName, buildName):
        """
        Return build corresponding to buildName
        A TestLinkErrors is raised in case of error
        """
        plan = self.getTestPlanByName(testProjectName, testPlanName)
        builds = self.getBuildsForTestPlan(plan['id'])

        # Check if a builds exists
        if builds == '':
            raise TestLinkErrors("(getBuildsByName) - Builds %s does not exists for test plan %s" % (buildName, testPlanName))

        # Search the correct build name in the return builds list
        for build in builds:
            if build['name'] == buildName:
                return build

        # No build found with builName name
        raise TestLinkErrors("(getBuildsByName) - Builds %s does not exists for test plan %s" % (buildName, testPlanName))

    def getTestCaseByExtID(self, testCaseExternalID):
        """Return test case by its external ID
        Error are managed by getTestCase method"""
        return self.getTestCase(testcaseexternalid=testCaseExternalID)

class TestEngine(object):
    """This class must be derived to implement an automatic test engine"""

    def __init__(self, arg=None):
        """ 'arg' is a tuple of test function name to execute
        (execution order in order the same as the tuple order)
        If arg is not set, all test are executed in alphabetical order
        """
        self.arg = arg

    def setUp(self):
        """Method called before all tests to pass
        Can be implemented is the derived class
        """
        pass

    def TearDown(self):
        """Method called after all tests are ran
        Can be implemented is the derived class
        """
        pass

    def BeforeEachTest(self, fctName):
        """Method called before each test
        Can be implemented is the derived class
        'fctName' is the test function that will be called
        just after
        """
        pass

    def AfterEachTest(self, fctName):
        """Method called after each test
        Can be implemented is the derived class
        'fctName' is the test function that has been called
        just before
        """
        pass

    def test_1(self):
        """docstring for test_1"""
        pass

    def test_2(self):
        """docstring for test_2"""
        pass

    def run(self):
        """Run test
        If 'arg' is empty, execute all methods of this class starting with 'test_'
        Otherwise, 'arg' must be a list of test function name to execute
        tests method of this class must start with 'test_' and SHALL return: 
            - the test result: string 'p', 'b' or 'f' if there no notes
            - the tuple (string test result, string test notes)
        """


        if self.arg is None:
            # No test list specified, run all tests
            testlist = filter(filter_fct, self.__class__.__dict__)
        else:
            testlist = self.arg


        self.setUp()

        for fct in testlist:
            try:
                self.BeforeEachTest(fctName)
                ret = self.fctName()

                if type(ret) == str:
                    if not ret in "pfb":
                        #TODO: gerer l'erreur
                        pass
                    else:
                        #TODO: save results
                        pass
                elif type(ret) == tuple:
                    # First element is test result
                    if not ret[0] in "pbf":
                        #TODO: gerer l'erreur
                        pass
                    # Second element is a string for test notes
                    elif not ret[1] == str:
                        #TODO: gerer l'erreur
                        pass
                    else:
                        #TODO Save results
                        pass

                self.AfterEachTest(fctName)

            except Exception, e:
                raise e

        self.TearDown()

def filter_fct(element):
    """Search in class memeber test functions"""
    return element.startswith("test_")

            
