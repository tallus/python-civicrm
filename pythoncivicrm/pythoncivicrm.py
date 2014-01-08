"""
.. module::pythoncivicrm 
    :synopis:Python module to access the CiviCRM v3 API. 

Python CiviCRM
==============

This is a module for interacting with the CiviCRM REST API Version 3.

It's use should be fairly straight forward, at least if you have basic 
familiarity with the API documentation.

Everything is implemented in the CiviCRM class. You need, at a minimum
to pass a URL, and the your site and API keys when instantiating your 
object.

This class has methods that correspond to nearly all the underlying 
actions provided by the REST API, as well as implementing a few more of 
its own. Some of these are more convenient and/or simpler versions 
of the actions. Others provide for more complex or specific tasks e.g. 
adding a contact. The eventual aim is to match the functionality provided
in the PHP API. 

There are some differences in how things are implemented, in particular 
with how things are returned. See :ref:`things-to-note`.

A CivicrmError will be raised for anything other than a 200 respose e.g. 404

Usage
-----
Use example for a basic search::

    url = 'www.example.org/path/to/civi/codebase/civicrm/extern/rest.php'
    site_key ='your site key'
    api_key ='your api key'
    civicrm = CiviCRM(url, site_key, api_key)


    search_terms = {'city' : 'Gotham City', 'contact_type' : 'Individual'}
    search results = civicrm.get('Contact', search_terms)
    first_10_search results = civicrm.get('Contact', search_terms, limit=10)

.. _things-to-note:

Things to note
--------------

* Unless otherwise specified methods expect to take a dictionary of values, rather than kwargs**, this is params in the parameters, when used. 
* Except for options as defined in the CiviCRM API <a href=http://wiki.civicrm.org/confluence/display/CRMDOC/Using+the+API#UsingtheAPI-Parameters">here</a>.
* Entity and Action must always be specified explicitly. They are removed if found in params, along with references to site/api keys.
* The CiviCRM API typically returns JSON (that would decode to a dictionary) with the actual results you want stored in values(or result if a single value is expected). Additional info is typically API version and count. If results are returned successfully we only return the results themselves -- typically a list of dictionaries, as this API version is always 3 with this module, and count can easily be derived using len().
* Returned values are generally sequential (i.e. a list (of dictionaries) rather than a dictionary (of dictionaries) with numbers for keys) except in the case of getfields & getoptions that return  a dictionary with real keys.
* Results are unicode
* Most actions returns the (updated) record in question, others a count e.g. delete
* the  replace API call is undocumented ,AFAIK, so not implemented, use getaction if you must.
"""


from __future__ import absolute_import, print_function, unicode_literals

import re
import requests
import json

class CivicrmError(Exception):
    pass

class CiviCRM:
    """
    .. class::CiviCRM(self, url, site_key, api_key, [use_ssl=True])
    make calls against the civicrm api
    """
    def __init__(self, url, site_key, api_key, 
            use_ssl=True):
        """Set url,api keys, ssl usage."""
        # strip http(s):// off url 
        regex = re.compile('^https?://')
        self.urlstring = regex.sub('', url)
        self.site_key = site_key
        self.api_key = api_key
        self.use_ssl = use_ssl
        if self.use_ssl:
            start = 'https://'
        else:
            start = 'http://'
        self.url =  "%s%s/extern/rest.php" % (start, self.urlstring)

    def _get(self, action, entity, parameters=None):
        """Internal method to make api calls"""
        if not parameters:
            parameters = {}
        payload = self._construct_payload(action, entity, parameters)
        api_call = requests.get(self.url, params=payload)
        if api_call.status_code != 200:
                raise CivicrmError('request to %s failed with status code %s'
                        % (self.url, api_call.status_code))
        results =  json.loads(api_call.content)
        return self._check_results(results)

    def _post(self, action, entity, parameters=None):
        """Internal method to make api calls"""
        if not parameters:
            parameters = {}
        payload = self._construct_payload(action, entity, parameters)
        api_call = requests.post(self.url, params=payload)
        if api_call.status_code != 200:
                raise CivicrmError('request to %s failed with status code %s'
                        % (self.url, api_call.status_code))
        results =  json.loads(api_call.content)
        return self._check_results(results)

        
    def _construct_payload(self, action, entity, parameters):
        """Takes action, entity, parameters
        returns  payload(sanitized parameters)"""
        payload = {
                'key' : self.site_key,
                'api_key' : self.api_key, 
                'json' : 1,
                'entity' : entity,
                'action' : action
                }
        # these should all be set explicitly so remove from parameters
        for badparam in ['site_key', 'api_key', 'entity', 'action', 
                'json']:
            parameters.pop(badparam, None)
        # add in parameters
        payload.update(parameters)
        # add (not) sequential of not set
        if not 'sequential' in payload:
                payload['sequential'] = 1
        return payload
    
    def _add_options(self, params, kwlist=None, **kwargs):
        """adds limit and offset etc in form required by REST API
        Takes key=value pairs and/or a dictionary(kwlist) 
        in addition to a parameter dictionary to extend"""
        if kwlist:
            for key, value in kwlist.iteritems():
                if value:
                    option = "options[%s]" % key
                    params.update({option : value})
            return params
        for key, value in kwargs.iteritems():
            if value:
                option = "options[%s]" % key
                params.update({option : value})
        return params

    def _check_results(self, results):
        """returns relevant part of results or raise error"""
        if 'is_error' in results and results['is_error'] == 1:
            raise CivicrmError(results['error_message'])
        if 'values' in results:
            return results['values']
        elif 'result' in results:
            return results['result']
        else:
            return results

   
    def get(self, entity, params=None, **kwargs):
        """Simple implementation of get action.
        Supply search terms in a dictionary called params
        Pass limit and offset for a subset of the results
        (or pass them in  params). Other options can also be passed
        as key=value pairs (options as defined here:
        http://wiki.civicrm.org/confluence/display/CRMDOC/Using+the+API#UsingtheAPI-Parameters e.g. match, match mandatory.
        Returns a list of dictionaries or an empty list.
        """
        params = self._add_options(params, kwargs)
        return self._get('get', entity, params)

    def getsingle(self, entity, params):
        """Simple implementation of getsingle action.
        Returns a dictionary. 
        Raises a CiviCRM  error if no or multiple results are found."""
        # TODO OPTIONS?
        return self._get('getsingle', entity, params)
        

    def getvalue(self, entity, returnfield, params):
        """Simple implementation of getvalue action.
        Will only return one field as unicodestring  
        and expects only one result, as per get single.
        Raises a CiviCRM  error if no or multiple results are found."""
        # TODO OPTIONS?
        params.update({'return' : returnfield})
        return self._get('getvalue', entity, params)
        

    def search(self, entity, limit=None, offset=None, **kwargs):
        """Like get but using key=value rather than passing a dictionary.
        Pass limit and offset for a subset of the results.
        Returns in the same way as the get method"""
        #TODO support passing of option in Dict
        params = kwargs
        params = self._add_options(params, limit=limit, offset=offset)
        return self._get('get', entity, params)

    def searchsingle(self, entity, **kwargs):
        """Search entity for field=value, Returns a dictionary. 
        Raises a CiviCRM  error if no or multiple results are found."""
        # TODO OPTIONS?
        return self._get('getsingle', entity, kwargs)
        

    def searchvalue(self, entity, returnfield, **kwargs):
        """Search entity for field = value, 
        return single result with single field as unicode string
        Raises a CiviCRM  error if no or multiple results are found."""
        # TODO OPTIONS?
        kwargs.update({'return' : returnfield})
        return self._get('getvalue', entity, kwargs)

    def create(self, entity, params):
        """Simple implementation of create action.
        Returns a list of dictionaries of created entries."""
        # TODO OPTIONS?
        return self._post('create', entity, params)
        
    def update(self, entity, db_id, params):
        """Update a record. An id must be supplied.
        Returns a list of dictionaries of updated  entries."""
        # TODO OPTIONS?
        params.update({'id' : db_id})
        return self.create(entity, params)

    def updatevalues(self, entity, db_id, **kwargs):
        """update a record using key=value pairs. An id must be supplied.
        Returns a list of dictionaries of updated  entries."""
        params = kwargs
        params.update({'id' : db_id})
        return self.create(entity, params)
                
    def setvalue(self, entity, db_id, field, value):
        """Updates a single field.
        This is not well documented, use at own risk.
        Takes an id and single field and value, 
        returns a dictionary with the updated field and record."""
        # TODO OPTIONS?
        return self._post('setvalue', entity, 
                parameters={'id' :db_id, 'field' : field, 'value' : value})
        
    def delete(self, entity, db_id, skip_undelete = False):
        """Delete a record. Set skip_undelete to True, to 
        permanently delete a record for cases  where there
        is a 'recycle bin' e.g. contacts
        Returns number of deleted records"""
        # TODO OPTIONS?
        if skip_undelete is True:
            params = {'id' : db_id, 'skip_undelete': 1}
        else:
            params = {'id' : db_id}
        return self._post('delete', entity, params)

    def getcount(self, entity, params):
        """Returns the number of qualifying records. Expects a dictionary.
        Mayt not be accurate for values > 25. (will return 25)"""
        return self._get('getcount', entity, params)

    def getcountkw(self,entity, **kwargs):
        """Returns the number of qualifying records. Takes key=value pairs.
        May not be accurate for values > 25. (will return 25)"""
        return self._get('getcount', entity, kwargs)
        
    
    def getfields(self, entity):
        """Returns a dictionary of fields for entity, where
        keys (and key['name']) are names of field and the value
        is a dictionary describing that field"""
        return self._get('getfields', entity, parameters = {'sequential' : 0})

    def getoptions(self, entity, field):
        """Returns a dictionary of options for fields
        as key/value pairs. Typically identical to each other.
        (though sometimes appear to be synonyms? e.g. 1: Yes)
        Raises CivicrmError if a field has no associated options 
        or is not present etc"""
        parameters = {'field' : field, 'sequential' : 0}
        return self._get('getoptions', entity, parameters)

    def doaction(self,action ,entity, params=None):
        """There are other actions for some entities, but
        these are undocumented?. This allows you to utilise
        these. Use with caution."""
        return self._post(action, entity, params)

        # TODO
        # write functions to take Search parameters, get matching id's,
        # then calling setvalue or update,
        #allowing for refusing to update more than  one record
        # or not sort_name=com.com
        # unit test with test db/ mock
      
