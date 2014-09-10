"""
.. module::pythoncivicrm
:synopis:Python module to access the CiviCRM v3 API.

Python CiviCRM
==============

This is a module for interacting with the CiviCRM REST API Version 3.

It's use should be fairly straight forward, at least if you have basic
familiarity with the API documentation.

Everything is implemented in the CiviCRM class. You need, at a minimum to pass a
URL, and the your site and API keys when instantiating your object.

This class has methods that correspond to nearly all the underlying actions
provided by the REST API, as well as implementing a few more of its own. Some of
these are more convenient and/or simpler versions of the actions. Others provide
for more complex or specific tasks e.g. adding a contact. The eventual aim is to
match the functionality provided in the PHP API.

There are some differences in how things are implemented, in particular with how
things are returned. See :ref:`things-to-note`.

A CivicrmError will be raised for anything other than a 200 respose e.g. a 404.

Usage
-----
Usage example for a basic search::

    url = 'www.example.org/path/to/civi/codebase/civicrm/extern/rest.php'
    site_key ='your site key'
    api_key ='your api key'
    civicrm = CiviCRM(url, site_key, api_key)

    search_results = civicrm.get('Contact', city='Gotham City')
    first_10_search_results = civicrm.get('Contact',
            city='Gotham City', limit=10)

It can be easier to construct a dict and feed them to methods using ** to
expand it to key value pairs::

    my_dict =   {
                country      = 'United States',
                city         ='Gotham City',
                contact_type ='Individual
                }
    civicrm.get('Contact', **my_dict)


.. _things-to-note:

Things to note
--------------

* Of the options defined in the CiviCRM API
http://wiki.civicrm.org/confluence/display/CRMDOC/Using+ the+API#UsingtheAPI-
Parameters only limit, offset (& sequential) are currently supported,
sequential is set to 1 (true) by default and should not generally be changed.

* Entity and Action must always be specified explicitly. They are removed if
found in params, along with references to site/api keys.

* The CiviCRM API typically returns JSON (that would decode to a dictionary)
with the actual results you want stored in values(or result if a single  value
is expected). Additional info is typically API version and count. If  results
are returned successfully we only return the results themselves --  typically a
list of dictionaries, as this API version is always 3 with this  module, and
count can easily be derived using len().

* Returned values are generally sequential (i.e. a list (of dictionaries) rather
than a dictionary (of dictionaries) with numbers for keys) except in the case of
getfields & getoptions that return  a dictionary with real keys.

* Results are unicode

* Most actions returns the (updated) record in question, others a count e.g.
* delete

* The is_valid_method uses getoptions() to both checks an option is valid and
returns the corresponding id (where this is valid). It does this for both an id
supplied as an int and a label supplied as a string. This is convinient as it
allows methods to take a descriptive label as well as a numeric id, rather than
being limited to this. When methods do this they don't use this method if a
numeric id is supplied, so that id is not checked for validity (though a Civicrm
will still be raised if its not) as it is assumed you know what you are doing in
this case, and we can save an extra API call for speed.

* The  replace API call is undocumented, AFAIK, so not implemented, use
getaction if you must.
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

    def __init__(self, url, site_key, api_key, use_ssl=True):
        """Set url,api keys, ssl usage."""

        # strip http(s):// off url
        regex = re.compile('^https?://')
        # handwavey email regex
        self.eml = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")
        self.urlstring = regex.sub('', url)
        self.site_key = site_key
        self.api_key = api_key
        self.use_ssl = use_ssl
        if self.use_ssl:
            start = 'https://'
        else:
            start = 'http://'
        self.url = "%s%s/extern/rest.php" % (start, self.urlstring)

    def _get(self, action, entity, parameters=None):
        """Internal method to make api calls"""

        if not parameters:
            parameters = {}
        payload = self._construct_payload(action, entity, parameters)
        api_call = requests.get(self.url, params=payload)
        if api_call.status_code != 200:
            raise CivicrmError('request to %s failed with status code %s'
                               % (self.url, api_call.status_code))
        results = json.loads(api_call.content)
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
        results = json.loads(api_call.content)
        # Some entities return things in the values field
        # that don't conform to the normal use elsewhere
        # Here we check for this and just return straight results
        funny_values = ['GroupContact']
        if entity in funny_values:
            return results
        else:
            return self._check_results(results)

    def _construct_payload(self, action, entity, parameters):
        """Takes action, entity, parameters
        returns  payload(sanitized parameters)."""

        payload = {
            'key': self.site_key,
            'api_key': self.api_key,
            'json': 1,
            'entity': entity,
            'action': action
            # 'fnName': "civicrm/%s/%s" % (entity, action)
        }
        # these should all be set explicitly so remove from parameters
        for badparam in ['site_key', 'api_key', 'entity', 'action', 'json']:
            parameters.pop(badparam, None)
        # add in parameters
        payload.update(parameters)
        # add (not) sequential if not set
        if 'sequential' not in payload:
            payload['sequential'] = 1
        return payload

    def _add_options(self, params, **kwargs):
        """Adds limit and offset etc in form required by REST API
        Takes key=value pairs and/or a dictionary(kwlist)
        in addition to a parameter dictionary to extend."""

        for key, value in kwargs.items():
            if value:
                option = "options[%s]" % key
                params.update({option: value})
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

    def is_valid_option(self, entity, field, value):
        """Takes a value which can be an id or its corresponding
        label, Returns the (corresponding) id if valid, otherwise
        raises a CivicrmError."""

        # keys are id's
        try:
            options = self.getoptions(entity, field)
        except CivicrmError:
            raise CivicrmError("%s has no defined options for %s"
                               % (entity, field))
        # swap keys & values for lookup keys are labels
        labels = dict((value, key) for key, value
                      in options.items())
        if type(value) is int and str(value) in options:
            return value
        elif value in labels:
            return labels[value]
        else:
            raise CivicrmError("invalid option %s" % value)
            # return(labels)

    def get(self, entity, **kwargs):
        """Simple implementation of get action.
        Supply search terms in a dictionary called params
        Pass limit and offset for a subset of the results
        (or pass them in  params). Other options can also be passed
        as key=value pairs (options as defined here:
        http://wiki.civicrm.org/confluence/display/CRMDOC/Using+the+API
        #UsingtheAPI-Parameters e.g. match, match mandatory.
        Returns a list of dictionaries or an empty list."""

        limit = kwargs.pop('limit', None)
        offset = kwargs.pop('offset', None)
        params = self._add_options(kwargs, limit=limit, offset=offset)
        return self._get('get', entity, params)

    def getsingle(self, entity, **kwargs):
        """Simple implementation of getsingle action.
        Returns a dictionary.
        Raises a CiviCRM  error if no or multiple results are found."""

        # TODO OPTIONS?
        return self._get('getsingle', entity, kwargs)

    def getvalue(self, entity, returnfield, **kwargs):
        """Simple implementation of getvalue action.
        Will only return one field as unicodestring
        and expects only one result, as per get single.
        Raises a CiviCRM  error if no or multiple results are found."""

        # TODO OPTIONS?
        kwargs.update({'return': returnfield})
        return self._get('getvalue', entity, kwargs)

    def create(self, entity, **kwargs):
        """Simple implementation of create action.
        Returns a list of dictionaries of created entries."""

        # TODO OPTIONS?
        return self._post('create', entity, kwargs)

    def update(self, entity, db_id, **kwargs):
        """Update a record. An id must be supplied.
        Returns a list of dictionaries of updated  entries."""

        # TODO OPTIONS?
        return self.create(entity, id=db_id, **kwargs)

    def setvalue(self, entity, db_id, field, value):
        """Updates a single field. This is not well documented, use at own risk.
        Takes an id and single field and value,
        returns a dictionary with the updated field and record."""
        # TODO OPTIONS?
        return self._post('setvalue', entity,
                          parameters={'id': db_id, 'field': field, 'value': value})

    def delete(self, entity, db_id, skip_undelete=False):
        """Delete a record. Set skip_undelete to True, to permanently
        delete a record for cases  where there is a 'recycle bin'
        e.g. contacts.
        In some cases, e.g. entity_tags entries entries can be deleted
        without the id (get on entity tags doesn't return the id). In these
        cases use getaction with delete and the appropriate key-value pairs.
        Returns the number of deleted records."""

        # TODO OPTIONS?
        if skip_undelete is True:
            params = {'id': db_id, 'skip_undelete': 1}
        else:
            params = {'id': db_id}
        return self._post('delete', entity, params)

    def getcount(self, entity, **kwargs):
        """Returns the number of qualifying records. Expects a dictionary.
        Mayt not be accurate for values > 25. (will return 25)."""

        return self._get('getcount', entity, kwargs)

    def getfields(self, entity):
        """Returns a dictionary of fields for entity, where
        keys (and key['name']) are names of field and the value
        is a dictionary describing that field."""

        return self._get('getfields', entity, parameters={'sequential': 0})

    def getoptions(self, entity, field):
        """Returns a dictionary of options for fields
        as key/value pairs. Typically identical to each other.
        (though sometimes appear to be synonyms? e.g. 1: Yes)
        Raises CivicrmError if a field has no associated options
        or is not present etc."""

        parameters = {'field': field, 'sequential': 0}
        return self._get('getoptions', entity, parameters)

    def doaction(self, action, entity, **kwargs):
        """There are other actions for some entities, but
        these are undocumented?. This allows you to utilise
        these. Use with caution."""

        return self._post(action, entity, kwargs)

    def add_contact(self, contact_type, **kwargs):
        """Creates a contact from supplied dictionary params.
        Raises a CivicrmError if a required field is not supplied:
        contact_type and/or one of  first_name, last_name,
        email, display_name. Returns a dictionary of the contact created"""

        required = ['first_name', 'last_name', 'email', 'display_name']
        missing_fields = matches_required(required, kwargs)
        if missing_fields:
            raise CivicrmError('One of the following fields must exist:%s'
                               % ", ".join(missing_fields))
        return self.create('Contact', contact_type=contact_type, **kwargs)[0]

    def add_relationship(self, contact_a, contact_b, relationship,
                         **kwargs):
        """Adds a relationship between contact_a and contact_b.
        Contacts must be supplied as id's (int).
        If the relationship is supplied as an int it is assumend to be an id,
        otherwise name_a_b, label_a_b, name_b_a, label_b_a  and description
        are searched for a match.
        A CivicrmError is raised if no match is found.
        N.B. 'Alice', 'Bob', 'Employer of' means Bob is the employer of Alice.
        Non compulsory fields may be passed in a keyword pairs.
        Searching for a match will hit the API and may do so multiple times,
        you may find it beneficial to check the result for
        'relationship_type_id' and cache this result.
        Returns a dictionary of the contact created."""

        relationship_id = None
        if type(relationship) is int:
            relationship_id = relationship
        else:
            for field in ['name_a_b', 'label_a_b',
                          'name_b_a', 'label_b_a',
                          'description']:

                result = self.get('RelationshipType',
                                  **{field: relationship, 'return': ['id']})
                if result:
                    relationship_id = result[0]['id']
                    break
        if not relationship_id:
            raise CivicrmError('invalid relationship %s' % relationship)

        kwargs.update({
            'relationship_type_id': relationship_id,
            'contact_id_a': contact_a,
            'contact_id_b': contact_b
        })
        return self.create('Relationship', **kwargs)[0]

    def add_activity_type(self, label, weight=5, is_active=0, **kwargs):
        """Creates an Activity Type. Label is a string describing the activity
        spaces are allowed.  Weight is any postive or negative integer. It
        affects the order in which things are displayed in the web interface.
        It defaults to 5, this puts things just after the basic types such
        as Phone Call. is_active defaults to 0: disabled (as per CiviCRM.
        Set to 1 to make the Activity Type active"""
        kwargs.update({
            'label': label,
            'weight': weight,
            'is_active': is_active
        })
        return self.create('ActivityType', **kwargs)[0]

    def add_activity(self, activity_type, sourceid,
                     subject=None, date_time=None, activity_status=None,
                     activity_medium=None, priority=None, **kwargs):
        """Creates an activity.
        activity_type, activity_status, activity_medium and priority
        can all be supplied as a label or id (int). The label
        wil be automatically coverted into the corresponding id
        so activity_type becomes  activity_type_id. Valid values
        can be obtained with  the getoptions method e.g.
        getoptions('Activity', 'status_id')
        (This method doesn't take activity_type_name
        -- its identical for predefined types.
        use  the create method  if you insist on using it).
        sourceid is an int, typically the contact_id for
        the person creating the activity, loosely defined.
        There is also a target_contact_id for person contacted etc.
        Subject is a string, typically a summary of the activity.
        date_time should be string not a datetime object.
        It's short hand for 'activity_date_time'."""

        if type(activity_type) is not int:
            activity_type = self.is_valid_option(
                'Activity', 'activity_type_id', activity_type)
        kwargs['activity_type_id'] = activity_type
        # get corresponding id
        largs = locals()
        for option in ['activity_status', 'activity_medium', 'priority']:
            if largs[option]:
                val = largs[option]
                name = option + '_id'
                if type(val) is not int:
                    val = self.is_valid_option('Activity', name, val)
                kwargs[name] = val
        kwargs.update({
            'source_contact_id': sourceid,
            'subject': subject,
            'activity_date_time': date_time
        })
        return self.create('Activity', **kwargs)[0]

    def add_contribution(self, contact_id, total_amount,
                         financial_type, **kwargs):
        """Add a contribution of amount credited to contact_id.
        financial_type can be an integer or a string corresponding to a
        financial types id or value respectively.
        This can be obtained with
        self.getoptions('Contribution', 'financial_type_id')."""

        if type(financial_type) is not int:
            financial_type = self.is_valid_option('Contribution',
                                                  'financial_type_id', financial_type)
        # kwargs['financial_type_id'] = financial_type
        kwargs.update({
            'financial_type_id': financial_type,
            'contact_id': contact_id,
            'total_amount': total_amount,
        })
        return self.create('Contribution', **kwargs)[0]

    def add_email(self, contact_id, email, email_like=False, **kwargs):
        """Add an email to civicrm. If email_like is True it checks
        to see whether the supplied email looks something like a real email,
        using a typical handwavey regex (specifically  something like
        something@something.something so local emails will fail).
        A CivicrmError is raised if it fails this "test".
        No claim is made that this actually is or isn't a valid email,
        never mind that you can actually send email to it.
        Civicrm doesn't care and will take anything in the field apparently."""

        if email_like and not re.match(self.eml, email):
            raise CivicrmError("Might not be an email address")
        return self.create('Email', contact_id=contact_id, email=email,
                           **kwargs)[0]

    def add_note(self, entity_id, note, **kwargs):
        """Add a note . Note if entity_table is not defined,
        it defaults to civicrm_contact. entity_table refers to the
        table name in civicrm database. Other fields are  subject
        contact_id (note creator), modified_date and privacy."""

        return self.create('Note', entity_id=entity_id, note=note,
                           **kwargs)[0]

    def add_tag(self, name, **kwargs):
        """Add a tag."""

        return self.create('Tag', name=name, **kwargs)[0]

    def add_entity_tag(self, entity_id, tag_id,
                       entity_table="civicrm_contact"):
        """Tag an entity_id (a contact id by default) by tag id.
        Note returns a dict with "is_error,not_added, added, total_count
        It's not an error to tag an entity with a tag, it just won't
        get added Iand added and not_added will reflect this.
        See also notes under delete."""

        return self.create('EntityTag', entity_id=entity_id,
                           tag_id=tag_id, entity_table=entity_table)

    def add_group(self, title, **kwargs):
        """Add a group to CiviCRM."""

        return self.create('Group', title=title, **kwargs)[0]

    def add_group_contact(self, contact_id, group_id, **kwargs):
        """Add a link between a group and a contact. See entity_tag
        for a description of return values (and deleting)."""

        return self.create('GroupContact', contact_id=contact_id,
                           group_id=group_id)

    def add_phone(self, contact_id, phone, **kwargs):
        """Add a phone number to CiviCRM. phone_type is an int,
        is_primary defaults to 1(true). phone_numeric is phone number
        as digits only (no spaces, dashes etc)."""

        return self.create('Phone', contact_id=contact_id,
                           phone=phone, **kwargs)[0]

    def add_address(self, contact_id, location_type, **kwargs):
        """Add an address to civicrm. location_type can be supplied as
        numeric id or its equivalent value."""

        if type(location_type) is not int:
            location_type = self.is_valid_option('Address',
                                                 'location_type_id', location_type)
        kwargs.update({
            'contact_id': contact_id,
            'location_type_id': location_type,
        })
        return self.create('Address', **kwargs)[0]


def matches_required(required, params):
    """if none of the fields in the list required are in params,
    returns a list of missing fields, or None"""
    missing = []
    for key in required:
        # there is a required field so return right away
        if key in params:
            return None
        else:
            missing.append(key)
    return missing

# TODO:
# write functions to take Search parameters, get matching id's,
# then calling setvalue or update,
# allowing the code to refuse to update more than one record
# or not sort_name=com.com
# unit test with test db/ mock
