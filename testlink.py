# -*- coding: utf-8 -*-
"""

TestLinkAPI - v0.20
Created on 5 nov. 2011
@author: Olivier Renault (admin@sqaopen.net)
@author: kereval.com
Initialy based on the James Stock testlink-api-python-client R7.

Update by pade to provide a user friendly library, 
with more robustness and error management
"""
import xmlrpclib
from datetime import datetime


class TestLinkErrors(Exception):
    """ Basic error handler
    Return message pass as argument
    """
    def __init__(self, msg):
        self.__msg = msg

    def __str__(self):
        return self.__msg

class TestLinkAPIClient(object):        
    """
    Low level access
    """

    def __init__(self, server_url, devKey):
        self.server = xmlrpclib.Server(server_url)
        self.devKey = devKey
        self.stepsList = []

    #
    #  BUILT-IN API CALLS
    #
    
    def checkDevKey(self):
        """ checkDevKey :
        check if Developer Key exists   
        """
        argsAPI = {'devKey': self.devKey}     
        return self.server.tl.checkDevKey(argsAPI)

    def about(self):
        """ about :
        Gives basic information about the API
        """
        return self.server.tl.about()
  
    def ping(self):
        """ ping :   
        """
        return self.server.tl.ping()

    def echo(self, message):
        return self.server.tl.repeat({'str': message})

    def doesUserExist(self, user):
        """ doesUserExist :
        Checks if a user name exists 
        """
        argsAPI = {'devKey' : self.devKey,
                'user':str(user)}   
        return self.server.tl.doesUserExist(argsAPI)
        
    def getBuildsForTestPlan(self, testplanid):
        """ getBuildsForTestPlan :
        Gets a list of builds within a test plan 
        """
        argsAPI = {'devKey' : self.devKey,
                'testplanid':str(testplanid)}   
        return self.server.tl.getBuildsForTestPlan(argsAPI)

    def getFirstLevelTestSuitesForTestProject(self, testprojectid):
        """ getFirstLevelTestSuitesForTestProject :
        Get set of test suites AT TOP LEVEL of tree on a Test Project 
        """  
        argsAPI = {'devKey' : self.devKey,
                'testprojectid':str(testprojectid)}   
        return self.server.tl.getFirstLevelTestSuitesForTestProject(argsAPI)
        
    def getFullPath(self,nodeid):
        """ getFullPath :
        Gets full path from the given node till the top using 
        nodes_hierarchy_table 
        """
        argsAPI = {'devKey' : self.devKey,
                'nodeid':str(nodeid)}    
        return self.server.tl.getFullPath(argsAPI)

    def getLastExecutionResult(self, testplanid, testcaseid):
        """ getLastExecutionResult :
        Gets the result of LAST EXECUTION for a particular testcase on a 
        test plan, but WITHOUT checking for a particular build 
        """
        argsAPI = {'devKey' : self.devKey,
                'testplanid' : str(testplanid),
                'testcaseid' : str(testcaseid)}     
        return self.server.tl.getLastExecutionResult(argsAPI)

    def getLatestBuildForTestPlan(self, testplanid):
        """ getLastExecutionResult :
        Gets the latest build by choosing the maximum build id for a 
        specific test plan  
        """  
        argsAPI = {'devKey' : self.devKey,
                'testplanid':str(testplanid)}  
        return self.server.tl.getLatestBuildForTestPlan(argsAPI)

    def getProjects(self):
        """ getProjects: 
        Gets a list of all projects 
        """
        argsAPI = {'devKey' : self.devKey} 
        return self.server.tl.getProjects(argsAPI)

    def getProjectTestPlans(self, testprojectid):
        """ getLastExecutionResult :
        Gets a list of test plans within a project 
        """ 
        argsAPI = {'devKey' : self.devKey,
                'testprojectid':str(testprojectid)}  
        return self.server.tl.getProjectTestPlans(argsAPI)

    def getTestCase(self, testcaseid=None, testcaseexternalid=None, version=None):
        """ getTestCase :
        Gets test case specification using external or internal id and its verion
        (if version is not specified, the higher version is used)
        """

        argsAPI = {'devKey' : self.devKey}
        if testcaseexternalid is not None:
            argsAPI.update({'testcaseexternalid': str(testcaseexternalid)})
        elif testcaseid is not None:
            argsAPI.update({'testcaseid': str(testcaseid)})
        if  version is not None:
            argsAPI.update({'version': str(version)})

        return self.server.tl.getTestCase(argsAPI)          

    def getTestCaseAttachments(self, testcaseid):
        """ getTestCaseAttachments :
        Gets attachments for specified test case  
        """
        argsAPI = {'devKey' : self.devKey,
                'testcaseid':str(testcaseid)}  
        return self.server.tl.getTestCaseAttachments(argsAPI)    

    def getTestCaseCustomFieldDesignValue(self, testcaseexternalid, version, 
                                     testprojectid, customfieldname, details='value'):
        """ getTestCaseCustomFieldDesignValue :
        Gets value of a Custom Field with scope='design' for a given Test case  
        """
        argsAPI = {'devKey' : self.devKey,
                'testcaseexternalid' : str(testcaseexternalid),
                'version' : int(version),
                'testprojectid' : str(testprojectid),
                'customfieldname' : str(customfieldname),
                'details' : str(details)}
        return self.server.tl.getTestCaseCustomFieldDesignValue(argsAPI)                                                

    def getTestCaseIDByName(self, testCaseName, testSuiteName=None, testProjectName=None):
        """ 
        Find a test case by its name
        testSuiteName and testProjectName are optionals arguments
        This function return a list of tests cases
        """
        argsAPI = {'devKey' : self.devKey,
                'testcasename':str(testCaseName)}

        if testSuiteName is not None:
            argsAPI.update({'testsuitename':str(testSuiteName)})
    
        if testProjectName is not None:
            argsAPI.update({'testprojectname':str(testProjectName)})

        # Server return can be a list or a dictionnary !
        # This function always return a list
        ret_srv = self.server.tl.getTestCaseIDByName(argsAPI)
        if type(ret_srv) == dict:
            retval = []
            for value in ret_srv.values():
                retval.append(value)
            return retval
        else:
            return ret_srv

    def getTestCasesForTestPlan(self, *args):
        """ getTestCasesForTestPlan :
        List test cases linked to a test plan    
            Mandatory parameters : testplanid
            Optional parameters : testcaseid, buildid, keywordid, keywords,
                executed, assignedto, executestatus, executiontype, getstepinfo 
        """        
        testplanid = args[0]
        argsAPI = {'devKey' : self.devKey,
                'testplanid' : str(testplanid)}
        if len(args) > 1:
            params = args[1:] 
            for param in params:
                paramlist = param.split("=")                     
                argsAPI[paramlist[0]] = paramlist[1]  
        return self.server.tl.getTestCasesForTestPlan(argsAPI)   
            
    def getTestCasesForTestSuite(self, testsuiteid, deep, details):
        """ getTestCasesForTestSuite :
        List test cases within a test suite    
        """        
        argsAPI = {'devKey' : self.devKey,
                'testsuiteid' : str(testsuiteid),
                'deep' : str(deep),
                'details' : str(details)}                  
        return self.server.tl.getTestCasesForTestSuite(argsAPI)
  
    def getTestPlanByName(self, testprojectname, testplanname):
        """ getTestPlanByName :
        Gets info about target test project   
        """
        argsAPI = {'devKey' : self.devKey,
                'testprojectname' : str(testprojectname),
                'testplanname' : str(testplanname)}    
        return self.server.tl.getTestPlanByName(argsAPI)

    def getTestPlanPlatforms(self, testplanid):
        """ getTestPlanPlatforms :
        Returns the list of platforms associated to a given test plan    
        """
        argsAPI = {'devKey' : self.devKey,
                'testplanid' : str(testplanid)}    
        return self.server.tl.getTestPlanPlatforms(argsAPI)  

    def getTestProjectByName(self, testprojectname):
        """ getTestProjectByName :
        Gets info about target test project    
        """
        argsAPI = {'devKey' : self.devKey,
                'testprojectname' : str(testprojectname)}    
        return self.server.tl.getTestProjectByName(argsAPI)    
  
    def getTestSuiteByID(self, testsuiteid):
        """ getTestSuiteByID :
        Return a TestSuite by ID    
        """
        argsAPI = {'devKey' : self.devKey,
                'testsuiteid' : str(testsuiteid)}    
        return self.server.tl.getTestSuiteByID(argsAPI)   
  
    def getTestSuitesForTestPlan(self, testplanid):
        """ getTestSuitesForTestPlan :
        List test suites within a test plan alphabetically     
        """
        argsAPI = {'devKey' : self.devKey,
                'testplanid' : str(testplanid)}    
        return self.server.tl.getTestSuitesForTestPlan(argsAPI)  
        
    def getTestSuitesForTestSuite(self, testsuiteid):
        """ getTestSuitesForTestSuite :
        get list of TestSuites which are DIRECT children of a given TestSuite     
        """
        argsAPI = {'devKey' : self.devKey,
                'testsuiteid' : str(testsuiteid)}    
        return self.server.tl.getTestSuitesForTestSuite(argsAPI)        
        
    def getTotalsForTestPlan(self, testplanid):
        """ getTotalsForTestPlan :
        Gets the summarized results grouped by platform    
        """
        argsAPI = {'devKey' : self.devKey,
                'testplanid' : str(testplanid)}    
        return self.server.tl.getTotalsForTestPlan(argsAPI)  

    def createTestProject(self, *args):
        """ createTestProject :
        Create a test project  
            Mandatory parameters : testprojectname, testcaseprefix
            Optional parameters : notes, options, active, public
            Options: map of requirementsEnabled, testPriorityEnabled, 
                            automationEnabled, inventoryEnabled 
        """        
        testprojectname = args[0]
        testcaseprefix = args[1]
        options={}
        argsAPI = {'devKey' : self.devKey,
                   'testprojectname' : str(testprojectname), 
                   'testcaseprefix' : str(testcaseprefix)}
        if len(args)>2:
            params = args[2:] 
            for param in params:
              paramlist = param.split("=")
              if paramlist[0] == "options":
                  optionlist = paramlist[1].split(",")
                  for option in optionlist:
                      optiontuple = option.split(":")
                      options[optiontuple[0]] = optiontuple[1]  
                  argsAPI[paramlist[0]] = options   
              else:
                  argsAPI[paramlist[0]] = paramlist[1]  
        return self.server.tl.createTestProject(argsAPI)
        
    def createBuild(self, testplanid, buildname, buildnotes):
        """ createBuild :
        Creates a new build for a specific test plan     
        """
        argsAPI = {'devKey' : self.devKey,
                'testplanid' : str(testplanid),
                'buildname' : str(buildname),
                'buildnotes' : str(buildnotes)}                  
        return self.server.tl.createBuild(argsAPI)        
    
    def createTestPlan(self, *args):
        """ createTestPlan :
        Create a test plan 
            Mandatory parameters : testplanname, testprojectname
            Optional parameters : notes, active, public   
        """        
        testplanname = args[0]
        testprojectname = args[1]
        argsAPI = {'devKey' : self.devKey,
                'testplanname' : str(testplanname),
                'testprojectname' : str(testprojectname)}
        if len(args)>2:
            params = args[2:] 
            for param in params:
              paramlist = param.split("=")       
              argsAPI[paramlist[0]] = paramlist[1]  
        return self.server.tl.createTestPlan(argsAPI)    
 
    def createTestSuite(self, *args):
        """ createTestSuite :
        Create a test suite  
          Mandatory parameters : testprojectid, testsuitename, details
          Optional parameters : parentid, order, checkduplicatedname, 
                                actiononduplicatedname   
        """        
        argsAPI = {'devKey' : self.devKey,
                'testprojectid' : str(args[0]),
                'testsuitename' : str(args[1]),
                'details' : str(args[2])}
        if len(args)>3:
            params = args[3:] 
            for param in params:
              paramlist = param.split("=")       
              argsAPI[paramlist[0]] = paramlist[1]  
        return self.server.tl.createTestSuite(argsAPI)       

    def createTestCase(self, *args):
        """ createTestCase :
        Create a test case  
          Mandatory parameters : testcasename, testsuiteid, testprojectid, 
                                 authorlogin, summary, steps 
          Optional parameters : preconditions, importance, execution, order, 
                       internalid, checkduplicatedname, actiononduplicatedname   
        """
        argsAPI = {'devKey' : self.devKey,
                'testcasename' : str(args[0]),
                'testsuiteid' : str(args[1]),
                'testprojectid' : str(args[2]),
                'authorlogin' : str(args[3]),
                'summary' : str(args[4]),
                'steps' : self.stepsList}
        if len(args)>5:
            params = args[5:] 
            for param in params:
              paramlist = param.split("=")       
              argsAPI[paramlist[0]] = paramlist[1]
        ret = self.server.tl.createTestCase(argsAPI) 
        self.stepsList = []                    
        return ret 

    def reportTCResult(self, testcaseid, testplanid, buildname, status, notes ):
    	"""
        Report execution result
        testcaseid: internal testlink id of the test case
        testplanid: testplan associated with the test case
        buildname: build name of the test case
        status: test verdict ('p': pass,'f': fail,'b': blocked)

        Return : [{'status': True, 'operation': 'reportTCResult', 'message': 'Success!', 'overwrite': False, 'id': '37'}]
        id correspond to the executionID needed to attach files to a test execution
        """
        argsAPI = {'devKey' : self.devKey,
                'testcaseid' : testcaseid,
                'testplanid' : testplanid,
                'status': status,
                'buildname': buildname,
                'notes': str(notes)
                }
        return self.server.tl.reportTCResult(argsAPI)


        
    def uploadExecutionAttachment(self,attachmentfile,executionid,title,description):
        """
        Attach a file to a test execution
        attachmentfile: python file descriptor pointing to the file
        name : name of the file
        title : title of the attachment
        description : description of the attachment
        content type : mimetype of the file
        """
        import mimetypes
        import base64
        import os.path
        argsAPI={'devKey' : self.devKey,
                 'executionid':executionid,
                 'title':title,
                 'filename':os.path.basename(attachmentfile.name),
                 'description':description,
                 'filetype':mimetypes.guess_type(attachmentfile.name)[0],
                 'content':base64.encodestring(attachmentfile.read())
                 }
        return self.server.tl.uploadExecutionAttachment(argsAPI)
                        
    #
    #  ADDITIONNAL FUNCTIONS
    #                                   

    def countProjects(self):
        """ countProjects :
        Count all the test project   
        """
        projects=TestlinkAPIClient.getProjects(self)
        return len(projects)
    
    def countTestPlans(self):
        """ countProjects :
        Count all the test plans   
        """
        projects=TestlinkAPIClient.getProjects(self)
        nbTP = 0
        for project in projects:
            ret = TestlinkAPIClient.getProjectTestPlans(self,project['id'])
            nbTP += len(ret)
        return nbTP

    def countTestSuites(self):
        """ countProjects :
        Count all the test suites   
        """
        projects=TestlinkAPIClient.getProjects(self)
        nbTS = 0
        for project in projects:
            TestPlans = TestlinkAPIClient.getProjectTestPlans(self,
                                                                 project['id'])
            for TestPlan in TestPlans:
                TestSuites = TestlinkAPIClient.getTestSuitesForTestPlan(self, 
                                                                TestPlan['id'])
                nbTS += len(TestSuites)
        return nbTS
               
    def countTestCasesTP(self):
        """ countProjects :
        Count all the test cases linked to a Test Plan   
        """
        projects=TestlinkAPIClient.getProjects(self)
        nbTC = 0
        for project in projects:
            TestPlans = TestlinkAPIClient.getProjectTestPlans(self, 
                                                                 project['id'])
            for TestPlan in TestPlans:
                TestCases = TestlinkAPIClient.getTestCasesForTestPlan(self,
                                                                TestPlan['id'])
                nbTC += len(TestCases)
        return nbTC
        
    def countTestCasesTS(self):
        """ countProjects :
        Count all the test cases linked to a Test Suite   
        """
        projects=TestlinkAPIClient.getProjects(self)
        nbTC = 0
        for project in projects:
            TestPlans = TestlinkAPIClient.getProjectTestPlans(self,
                                                                 project['id'])
            for TestPlan in TestPlans:
                TestSuites = TestlinkAPIClient.getTestSuitesForTestPlan(self,
                                                                TestPlan['id'])
                for TestSuite in TestSuites:
                    TestCases = TestlinkAPIClient.getTestCasesForTestSuite(self,
                                                 TestSuite['id'],'true','full')
                    for TestCase in TestCases:
                        nbTC += len(TestCases)
        return nbTC

    def countPlatforms(self):
        """ countPlatforms :
        Count all the Platforms  
        """
        projects=TestlinkAPIClient.getProjects(self)
        nbPlatforms = 0
        for project in projects:
            TestPlans = TestlinkAPIClient.getProjectTestPlans(self,
                                                                 project['id'])
            for TestPlan in TestPlans:
                Platforms = TestlinkAPIClient.getTestPlanPlatforms(self,
                                                                TestPlan['id'])
                nbPlatforms += len(Platforms)
        return nbPlatforms
        
    def countBuilds(self):
        """ countBuilds :
        Count all the Builds  
        """
        projects=TestlinkAPIClient.getProjects(self)
        nbBuilds = 0
        for project in projects:
            TestPlans = TestlinkAPIClient.getProjectTestPlans(self,
                                                                 project['id'])
            for TestPlan in TestPlans:
                Builds = TestlinkAPIClient.getBuildsForTestPlan(self,
                                                                TestPlan['id'])
                nbBuilds += len(Builds)
        return nbBuilds
        
    def listProjects(self):
        """ listProjects :
        Lists the Projects (display Name & ID)  
        """
        projects=TestlinkAPIClient.getProjects(self)
        for project in projects:
          print "Name: %s ID: %s " % (project['name'], project['id'])
  

    def initStep(self, actions, expected_results, execution_type):
        """ initStep :
        Initializes the list which stores the Steps of a Test Case to create  
        """
        self.stepsList = []
        lst = {}
        lst['step_number'] = '1'
        lst['actions'] = actions
        lst['expected_results'] = expected_results
        lst['execution_type'] = str(execution_type)
        self.stepsList.append(lst)
        return True
        
    def appendStep(self, actions, expected_results, execution_type):
        """ appendStep :
        Appends a step to the steps list  
        """
        lst = {}
        lst['step_number'] = str(len(self.stepsList)+1)
        lst['actions'] = actions
        lst['expected_results'] = expected_results
        lst['execution_type'] = str(execution_type)
        self.stepsList.append(lst)
        return True                
                                        
    def getProjectIDByName(self, projectName):   
        projects=self.server.tl.getProjects({'devKey' : self.devKey})
        for project in projects:
            if (project['name'] == projectName): 
                result = project['id']
                break
            else:
                result = -1
        return result

    def __str__(self):
        message = "TestLinkAPIClient - version %s"
        return message % self.__VERSION__

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

            
