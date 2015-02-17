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

**Documentation can be found at: http://python-civicrm.readthedocs.org/**


Usage
-----
Use example for a basic search::

    url = 'www.example.org/path/to/civi/codebase/civicrm/extern/rest.php'
    site_key ='your site key'
    api_key ='your api key'
    civicrm = CiviCRM(url, site_key, api_key)


    search_results = civicrm.get('Contact', city='Gotham City')
    first_10_search_results = civicrm.get('Contact',
            city='Gotham City', limit=10)

The following optional values can be supplied when intializing:
    use_ssl=True/False      Connect over https not http, defaults to True.
    timeout=N               Connection will time out in N seconds, i.e if
                            no response is sent by the server in N seconds.
                            requests.exceptions.Timeout will be raised if
                            the connection timesout.
                            Defaults to None, this means the connection will
                            hang until closed.

e.g.
    url = 'www.example.org/path/to/civi/codebase/civicrm/extern/rest.php'
    site_key ='your site key'
    api_key ='your api key'
    civicrm = CiviCRM(url, site_key, api_key, timeout=5)

    Connections will timeout after 5 seconds, and raise an error.


Things to note
--------------

* Though methods typically expect to take key=values pairs, it can be easier 
to feed them a dict and expand it with the ** notatation like so:
    my_dict =   {
                country' : 'United States', 
                city='Gotham City', 
                contact_type='Individual
                }
    civicrm.get('Contact', **my_dict)
* Of the options defined in the CiviCRM API <a href=http://wiki.civicrm.org/confluence/display/CRMDOC/Using+the+API#UsingtheAPI-Parameters">here</a> only limit, offset (& sequential) are currently supported, sequential is set to 1 (true) by default and should not generally be changed .
* Entity and Action must always be specified explicitly. They are removed if found in params, along with references to site/api keys.
* The CiviCRM API typically returns JSON (that would decode to a dictionary) with the actual results you want stored in values(or result if a single value is expected). Additional info is typically API version and count. If results are returned successfully we only return the results themselves -- typically a list of dictionaries, as this API version is always 3 with this module, and count can easily be derived using len().
* Returned values are generally sequential (i.e. a list (of dictionaries) rather than a dictionary (of dictionaries) with numbers for keys) except in the case of getfields & getoptions that return  a dictionary with real keys.
* Results are unicode
* The  replace API call is undocumented, AFAIK, so not implemented, use getaction if you must.
* Mock is required to run the unit-tests, however it is not listed in requirements.txt, you will need to install it yourself with pip install mock on Python 2.7 or use pip install -r requirements-dev.txt (it is part of the standard library with recent releases of Python 3).
* There are also integration tests which should be run against a clean install of Civicrm with the sample data loaded. You will need to create a file called config.py in tests with IP_ADDR etc set correctly as per your installation. N.B. Do not run these against a production server.
