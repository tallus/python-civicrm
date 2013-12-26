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

Things to note
--------------

* Unless otherwise specified methods expect to take a dictionary of values, rather than kwargs**, this is params in the parameters, when used. 
* Except for options as defined in the CiviCRM API <a href=http://wiki.civicrm.org/confluence/display/CRMDOC/Using+the+API#UsingtheAPI-Parameters">here</a>.
* Entity and Action must always be specified explicitly. They are removed if found in params, along with references to site/api keys.
* The CiviCRM API typically returns JSON (that would decode to a dictionary) with the actual results you want stored in values(or result if a single value is expected). Additional info is typically API version and count. If results are returned successfully we only return the results themselves -- typically a list of dictionaries, as this API version is always 3 with this module, and count can easily be derived using len().
* Returned values are generally sequential (i.e. a list (of dictionaries) rather than a dictionary (of dictionaries) with numbers for keys) except in the case of getfields & getoptions that return  a dictionary with real keys.
* Results are unicode
* the  replace API call is undocumented ,AFAIK, so not implemented, use getaction if you must.

