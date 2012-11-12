#! /usr/bin/python
# -*- coding: UTF-8 -*-

#  Copyright 2012 Paul Dassier, Luiko Czub, TestLink-API-Python-client developers
#
#  Licensed under ???
#  see https://github.com/orenault/TestLink-API-Python-client/issues/4


class TestLinkObject(object):
    """ generic class with general behaviour of TestLink objects
    should not be used directly
    """
    
    __slots__ = ['_api'  '_attributes']
    
    # Name API getMethod for class data 
    APIGETMETHOD = 'getMethodMustDefinedOnSubclass'
    # Name API fieldname for id
    APIIDFNAME = 'testobjidMustDefinedOnSubclass'

    def __init__(self, api, **attributes):
        """ New instance of a TestLink object
        
        API is an api client object as connection to the TestLink Server
        ARGS are key value pairs defining for self attributes
        """

        self._attributes = {}
        self._api  = api
        self._storeAttributes(attributes)
        
    def __getattr__(self, name):
        """ if name is key in ._attributes, returns that values """
        if self._attributes.has_key(name):
            return self._attributes[name]
        else:
            return super(TestLinkObject, self).__getattr__(name) 
        
    def _storeAttributes(self, attributes):
        """ Store key value pairs from dictionary ATTRIBUTES as own attributes 
        """
        self._attributes.update(attributes)
      
    def _getAttributesFromAPI(self, keys):
        """ Calls the API getMethod for and returns the result
        
        KEYS is a dictionary with key value pairs
        """
        # FIXME LC 10.11.12: API needs public method .callServerWithCheck()
        # FIXME LC 11.11.12: .callServerWithCheck() should add Args like devKey
        # FIXME LC 11.11.12: .callServerWithCheck() should check Data Error
        api_keys = {'devKey' : self._api.devKey}
        api_keys.update(keys)
        return self._api._callServer(self.APIGETMETHOD, keys)[0]
                
    def setAttributesFromAPI(self,  primary_key, **other_keys):
        """ calls the API getMethod and stores the return values as attributes 
        
        PRIMARY_KEY is the value for the self.APIIDFNAME argument
        OTHER_KEYS are optional key value pairs 
        """
        
        keys = {self.APIIDFNAME : primary_key}
        keys.update(other_keys)
        api_args = self._getAttributesFromAPI(keys)
        self._storeAttributes(api_args)
    
class TLTestCase(TestLinkObject):
    """ TestCase class - stores testcase data from TestLink """
    
    # Name API getMethod for class data 
    APIGETMETHOD = 'getTestCase'
    # Name API fieldname for id
    APIIDFNAME = 'testcaseid'

    
            
        