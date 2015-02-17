"""Unit tests.

These mock the return values from the API, so no running instance is needed.
Note, for convenience, mock returns values omit some things returned by
the API.
"""
import unittest
import mock

from pythoncivicrm.pythoncivicrm import CiviCRM
from pythoncivicrm.pythoncivicrm import CivicrmError
from pythoncivicrm.pythoncivicrm import matches_required

class CiviCRMTests(unittest.TestCase):
        # pylint: disable=R0904

    def setUp(self):
        #ip = '192.168.56.101' # was '192.168.1.124'
        ip = '192.168.1.107'
        url = "%s/drupal7/sites/all/modules/civicrm/" % ip
        site_key = '371cfadc834d2784a35e4f4ab20c1316'
        api_key = 'b734df56706432bb514ed737465424c3'
        self.cc = CiviCRM(url, site_key, api_key, timeout=1, use_ssl=False)
        self.contact_id = 202 # id for a valid civicrm user
        self.contact_json = '''{
            "address_id": "1",
            "country_id": "1228",
            "contact_id": "1",
            "id": "1",
            "world_region": "America South, Central, North and Caribbean",
            "city": "Portland",
            "preferred_mail_format": "Both",
            "display_name": "Test Test",
            "do_not_sms": "0",
            "email_id": "1",
            "organization_name": "org.org",
            "is_opt_out": "0",
            "do_not_email": "0",
            "do_not_mail": "0",
            "state_province_id": "1036",
            "email": "email@example.org",
            "worldregion_id": "2",
            "do_not_phone": "0",
            "is_deceased": "0", "state_province": "OR",
            "contact_type": "Individual",
            "contact_is_deleted": "0",
            "street_address": "PO Box 28228"
        }'''
        self.contacts = '{"values":[' + self.contact_json + ']}'
        self.results =  """
            {
            "is_error":0,
            "version":3,
            "count":1,"id":2,
            "values":[
                {"id":"2",
                "contact_type":"Individual",
                "contact_sub_type":"",
                "do_not_email":"0",
                "do_not_phone":"0",
                "do_not_mail":"0",
                "do_not_sms":"0",
                "do_not_trade":"0",
                "is_opt_out":"0",
                "display_name":"bar, foo",
                "created_date":"2014-10-05 13:05:13",
                "modified_date":"2014-10-05 13:05:13"}
                ]
            }
        """


    def tearDown(self):
        pass

    # methods and fuctions without network calls

    def test_add_options(self):
        results = self.cc._add_options({}, limit=1,offset=0)
        expected = {u'options[limit]' : 1, u'options[offset]' : 0}
        self.assertEquals(expected['options[limit]'], 1)

    def test_add_single_option(self):
        results = self.cc._add_options({}, limit=1)
        self.assertEquals(len(results), 1)

    def test__construct_payload_get(self):
        payload = self.cc._construct_payload('get', 'get', 'Contact',
                {'json' : 0, 'contact_id': 2})
        self.assertEquals(payload['json'], 1)
        self.assertEquals(payload['contact_id'], 2)

    def test__construct_payload_post(self):
        payload = self.cc._construct_payload('post', 'create', 'Contact',
                {'json' : 0, 'contact_id': 2})
        self.assertEquals(payload['json'], 1)
        self.assertEquals(payload['contact_id'], 2)

    def test__check_results(self):
        results = self.cc._check_results({'is_error' : 0, 'result' : 1})
        self.assertEquals(results, 1)

    def test__check_results_raises_exception(self):
        self.assertRaises(CivicrmError, self.cc._check_results,
                {'is_error' : 1, 'error_message' : 'test', 'result' : 1})

    def test_is_valid_option_id_is_valid(self):
        result = self.cc.is_valid_option(
                'Activity', 'activity_is_test', 0)
        self.assertEquals(result, 0)

    def test_is_valid_option_id_is_not_valid(self):
        self.assertRaises(CivicrmError, self.cc.is_valid_option,
            'Activity', 'activity_is_test', 2)

    def test_is_valid_option_label_is_valid(self):
        result = self.cc.is_valid_option(
                'Activity', 'activity_is_test', 'Yes')
        self.assertEquals(result, '1')

    def test_is_valid_option_label_is_not_valid(self):
        self.assertRaises(CivicrmError, self.cc.is_valid_option,
            'Activity', 'activity_is_test', 'Not Valid')

    def test_is_valid_option_label_is_none(self):
        self.assertRaises(CivicrmError, self.cc.is_valid_option,
            'Activity', 'activity_is_test', None)

    def test_matches_required_no_match(self):
        required = ['exists']
        params = {'does not exist' : True}
        results = matches_required(required, params)
        self.assertEquals(results, ['exists'])

    def test_matches_required_matches(self):
        required = ['exists']
        params = {'exists' : True}
        results = matches_required(required, params)
        self.assertEquals(results, None)

    # Methods calling requests

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test__get(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = self.contacts
        results = self.cc._get('get', 'Contact')
        self.assertEqual(results[0]['id'], '1')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test__post(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = self.contacts
        results = self.cc._post('get', 'Contact')
        self.assertEqual(results[0]['id'], '1')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_get(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = self.contacts
        results = self.cc.get('Contact')
        self.assertEqual(results[0]['id'], '1')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_get_invalid_option(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = """
            {
                "is_error": 1,
                "error_code": 2001,
                "error_message": "id is not a valid integer",
                "entity": "Contact",
                "action": "get",
                "error_field": "id",
                "type": "integer"
            }
        """
        self.assertRaises(CivicrmError,self.cc.get,
                "Contact", contact_id="a")

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_getsingle(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = self.contact_json
        results = self.cc.getsingle('Contact',contact_id=1)
        self.assertEqual(results['id'], '1')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_getsingle_multiple_results(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = """
            {
                "count":25,
                "is_error":1,
                "error_message":"Expected one Contact but found 25"
            }"""
        self.assertRaises(CivicrmError, self.cc.getsingle,
            'Contact', country='United States')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_getvalue(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = \
            """{"is_error":0,"result":"Test, Test"}"""
        results = self.cc.getvalue('Contact', 'sort_name', contact_id=1)
        self.assertEquals(type(results), unicode)
        self.assertEquals(results, 'Test, Test')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_getvalue_multiple_results(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = """
            {
                "count":25,
                "is_error":1,
                "error_message":"Expected one Contact but found 25"
            }"""
        self.assertRaises(CivicrmError, self.cc.getvalue,
            'Contact', 'sort_name', country='United States')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_create(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = self.results
        results = self.cc.create('Contact',
                contact_type='individual', display_name='bar, foo')
        self.assertEquals(results[0]['display_name'], 'bar, foo')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_delete(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content =\
            """{"is_error":0,"version":3,"count":1,"values":1}"""
        results = self.cc.delete('Contact', 2, True)
        self.assertEquals(results, 1)

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_update(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = self.results
        results = self.cc.update('Contact', 2, display_name='bar, foo')
        self.assertEquals(results[0]['display_name'], 'bar, foo')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_setvalue(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":2,
            "values":{"id":"2","display_name":"foo,bar"}
        }"""
        results = self.cc.setvalue('Contact', 2, 'display_name', 'foo, bar')
        self.assertEquals(results['display_name'], 'foo,bar')


    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_getcount(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content =\
                """{"is_error":0,"result":1}"""
        count = self.cc.getcount('Contact', contact_id=1)
        self.assertEquals(count, 1)


    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_getoptions(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = """
            {
            "is_error":0,
            "version":3,
            "count":3,
            "values":{
                "Household":"Household",
                "Individual":"Individual",
                "Organization":"Organization"
                }
            }"""
        results = self.cc.getoptions('Contact', 'contact_type')
        self.assertIn('Organization', results)

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_getoptions_raises_error(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = """
            {"is_error":1,"error_message":"The field 'city' doesn't exist."}
            """
        self.assertRaises(CivicrmError, self.cc.getoptions, 'Contact', 'city')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_doaction(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = self.contacts
        results = self.cc.doaction('get', 'Contact')
        self.assertEqual(results[0]['id'], '1')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_contact(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = self.results
        results =  self.cc.add_contact(
                contact_type='Individual', display_name='bar, foo')
        self.assertEquals(results['display_name'], 'bar, foo')

    def test_add_contact_required_field_missing(self):
        self.assertRaisesRegexp(CivicrmError, 'fields must exist',
                self.cc.add_contact, contact_type='Individual')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_contact_wrong_type(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
        {
            "error_field":"contact_type",
            "error_code":2001,
            "entity":"Contact",
            "action":"create",
            "is_error":1,
            "error_message":"'not a contact type' is not a valid option for field contact_type"
        }"""
        self.assertRaisesRegexp(CivicrmError,' not a valid option',
                self.cc.add_contact, 'not a contact type',
                display_name='test')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_relationship_by_id(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":382,
            "values":[{
            "id":"382",
            "contact_id_a":"101",
            "contact_id_b":"102",
            "relationship_type_id":"1",
            "start_date":"NULL",
            "end_date":"NULL",
            "is_active":"1",
            "description":"",
            "is_permission_a_b":"0",
            "is_permission_b_a":"0",
            "case_id":""}]
        }"""
        result = self.cc.add_relationship(101, 102, 1)
        self.assertEquals(result['relationship_type_id'], '1')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_relationship_by_type(self, mock_requests):
        result1 = """{
        "is_error":0,"version":3,"count":1,"id":3,
        "values":[{"id":"3","name_a_b":"Partnerof"}]
        }"""
        result2 = """
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":382,
            "values":[{
            "id":"382",
            "contact_id_a":"101",
            "contact_id_b":"102",
            "relationship_type_id":"3",
            "start_date":"NULL",
            "end_date":"NULL",
            "is_active":"1",
            "description":"",
            "is_permission_a_b":"0",
            "is_permission_b_a":"0",
            "case_id":""}]
        }"""
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = result1
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = result2
        result = self.cc.add_relationship(101, 102, 'Partner of')
        call = mock_requests.post.call_args[1]['data']['relationship_type_id']
        self.assertEquals(call, '3')
        self.assertEquals(result['relationship_type_id'], '3')


    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_relationship_type_not_found(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content =\
            """{"is_error":0,"version":3,"count":0,"values":[]}"""
        self.assertRaises(CivicrmError,
                self.cc.add_relationship, 101, 102, 'Aunt of')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_activity_type(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
            {
                "is_error":0,
                "version":3,
                "count":1,
                "id":772,
                "values":[{
                "id":"772",
                "option_group_id":"2",
                "label":"test_activity_type",
                "value":"64",
                "name":"test_activity_type",
                "is_active":"1"}]
            }"""
        result = self.cc.add_activity_type('test_activity_type', is_active=1)
        self.assertEqual(result['name'], 'test_activity_type')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_activity_by_status_id(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content ="""
            {
                "is_error":0,
                "version":3,
                "count":1,
                "id":3,
                "values":[{
                    "id":"3",
                    "activity_type_id":"1",
                    "subject":"test",
                    "status_id":"2",
                    "priority_id":"2"}]
            }"""
        result = self.cc.add_activity(1, self.contact_id,
                subject = "test", status = 2,  is_test=1)
        self.assertEquals(result['activity_type_id'], '1')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    @mock.patch.object(CiviCRM, "is_valid_option")
    def test_add_activity_by_status_type(self, mock_is_valid, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content ="""
            {
                "is_error":0,
                "version":3,
                "count":1,
                "id":3,
                "values":[{
                    "id":"3",
                    "activity_type_id":"1",
                    "subject":"test",
                    "status_id":"2",
                    "priority_id":"2"}]
            }"""
        results = [1, 2]
        def side_effect(*args, **kwargs):
            return results.pop(0)
        mock_is_valid.side_effect = side_effect
        result = self.cc.add_activity("Meeting", self.contact_id,
                subject = "test", activity_status = "Completed",
                status = "Cancelled",  is_test=1)
        self.assertEquals(result['activity_type_id'], '1')

    @mock.patch.object(CiviCRM, "is_valid_option")
    def test_add_activity_invalid_label(self, mock_is_valid):
        def side_effect(*args, **kwargs):
            raise CivicrmError
        mock_is_valid.side_effect = side_effect
        self.assertRaises(CivicrmError,
            self.cc.add_activity,"Not A Meeting", self.contact_id,
            "test", "0000", 2)

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_activity_invalid_status_id(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":3,
            "values":{"1":"Meeting","2":"Phone Call","3":"Email"}
        }
        """
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
            {
                "error_field":"status_id",
                "error_code":2001,
                "entity":"Activity",
                "action":"create",
                "is_error":1,
                "error_message":"'10'is not a valid option for field status_id"
            }"""
        self.assertRaises(CivicrmError,
            self.cc.add_activity,"Meeting", self.contact_id,
            "test", "0000", 10)

    @mock.patch.object(CiviCRM, "is_valid_option")
    def test_add_activity_invalid_status_type(self, mock_valid):
        returns = [1, CivicrmError('error')]
        def side_effect(*args, **kwargs):
            result = returns.pop(0)
            if isinstance(result, Exception):
                raise result
            return result
        mock_valid.side_effect = side_effect
        self.assertRaises(CivicrmError,
            self.cc.add_activity,"Meeting", self.contact_id,
            "test", "0000", "test")

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_contribution_by_id(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":130,
            "values":[
                {"id":"130",
                "contact_id":"202",
                "financial_type_id":"1",
                "payment_instrument_id":"4",
                "total_amount":"100",
                "currency":"USD",
                "contribution_status_id":"1",
                "contribution_type_id":"1"}
            ]
        }
        """
        self.cc.is_valid_option = mock.MagicMock()
        result = self.cc.add_contribution(self.contact_id, 100, 1, is_test=1)
        self.assertEquals(result['total_amount'], '100')
        assert not self.cc.is_valid_option.called

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_contribution_by_type(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content ="""
        {
            "is_error":0,
            "version":3,
            "count":4,
            "values":{
            "3":"Campaign Contribution",
            "1":"Donation",
            "4":"Event Fee",
            "2":"Member Dues"}
        }"""
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content ="""
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":130,
            "values":[
                {"id":"130",
                "contact_id":"202",
                "financial_type_id":"1",
                "payment_instrument_id":"4",
                "total_amount":"100",
                "currency":"USD",
                "contribution_status_id":"1",
                "contribution_type_id":"1"}
            ]
        }"""
        self.cc.is_valid_option = mock.MagicMock()
        result = self.cc.add_contribution(self.contact_id,
                100, 'Donation', is_test=1)
        self.assertEquals(result['total_amount'], '100')
        self.cc.is_valid_option.assert_called_with(
            'Contribution', 'financial_type_id', 'Donation')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_contribution_invalid_financial_type(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content ="""
        {
            "is_error":0,
            "version":3,
            "count":4,
            "values":{
            "3":"Campaign Contribution",
            "1":"Donation",
            "4":"Event Fee",
            "2":"Member Dues"}
        }"""
        self.assertRaises(CivicrmError,
                self.cc.add_contribution,self.contact_id,
                100, 'Not Valid', is_test=1)

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_email(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content ="""
        {
            "is_error":0,
            "version":3,"count":1,
            "id":220,
            "values":[{
                "id":"220",
                "contact_id":"202",
                "email":"test@example.org",
                "is_primary":"0"
            }]
        }
        """
        result = self.cc.add_email(self.contact_id, 'test@example.org')
        self.assertEquals(result['email'], 'test@example.org')

    def test_add_email_is_not_email_like(self):
        self.assertRaises(CivicrmError, self.cc.add_email,
            self.contact_id, 'invalid.address', True)

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_note(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content ="""
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":41,
            "values":[{
                "id":"41",
                "entity_table":"civicrm_contact",
                "entity_id":"202",
                "note":"test",
                "contact_id":"202",
                "privacy":"0"}]
        }
        """
        result = self.cc.add_note(self.contact_id, 'test')
        self.assertEquals(result['note'], 'test')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_tag(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content ="""
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":22,
            "values":[{
                "id":"22",
                "name":"test",
                "description":"",
                "used_for":"civicrm_contact"
            }]
        }
        """
        result = self.cc.add_tag('test')
        self.assertEquals(result['name'], 'test')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_entity_tag(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content =\
            """{"is_error":0,"not_added":0,"added":1,"total_count":1}"""
        result = self.cc.add_entity_tag(self.contact_id, 1)
        self.assertEquals(result['added'], 1)

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_group(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":22,
            "values":[{
            "id":"22",
            "name":"test_22",
            "title":"test"
            }]
        }
        """
        result = self.cc.add_group(title='test')
        self.assertEquals(result['title'], 'test')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_group_contact(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content =\
            """{"is_error":0,"not_added":0,"added":1,"total_count":1}"""
        result = self.cc.add_group_contact(self.contact_id, 5)
        self.assertEquals(result['added'], 1)

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_phone(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":179,
            "values":[{
                "id":"179",
                "contact_id":"202",
                "is_primary":"0",
                "mobile_provider_id":"",
                "phone":"111-111-1111",
                "phone_ext":"",
                "phone_numeric":"",
                "phone_type_id":""
            }]
        }
        """
        result = self.cc.add_phone(self.contact_id, '111-111-1111')
        self.assertEquals(result['phone'], '111-111-1111')

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_address_by_location_type_id(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":214,
            "values":[{
                "id":"214",
                "contact_id":"202",
                "location_type_id":"1",
                "is_primary":"0",
                "is_billing":"0",
                "manual_geo_code":"0"
            }]
        }
        """
        self.cc.is_valid_option = mock.MagicMock()
        result = self.cc.add_address(self.contact_id, 1)
        self.assertEquals(result['location_type_id'], '1')
        assert not self.cc.is_valid_option.called

    @mock.patch("pythoncivicrm.pythoncivicrm.requests")
    def test_add_address_by_location_type(self, mock_requests):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":5,
            "values":{
                "5":"Billing",
                "1":"Home",
                "3":"Main",
                "4":"Other",
                "2":"Work"
            }
        }
        """
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = """
        {
            "is_error":0,
            "version":3,
            "count":1,
            "id":214,
            "values":[{
                "id":"214",
                "contact_id":"202",
                "location_type_id":"1",
                "is_primary":"0",
                "is_billing":"0",
                "manual_geo_code":"0"
            }]
        }
        """
        self.cc.is_valid_option = mock.MagicMock()
        result = self.cc.add_address(self.contact_id, 'Home')
        self.assertEquals(result['location_type_id'], '1')
        self.cc.is_valid_option.assert_called_with(
            'Address', 'location_type_id', 'Home')


if __name__ == '__main__':
    pass
