"""Unit tests require running cicicrm instance loaded with sample data
(only) do not test against production machine."""
import unittest
from pythoncivicrm.pythoncivicrm import CiviCRM
from pythoncivicrm.pythoncivicrm import CivicrmError
from pythoncivicrm.pythoncivicrm import matches_required

class MyTests(unittest.TestCase):
        # pylint: disable=R0904

    def setUp(self):
        ip = '192.168.56.101' # was '192.168.1.124'
        url = "%s/drupal7/sites/all/modules/civicrm/" % ip
        site_key = '371cfadc834d2784a35e4f4ab20c1316'
        api_key = 'b734df56706432bb514ed737465424c3'
        self.cc = CiviCRM(url, site_key, api_key, use_ssl=False)
        self.contact_id = 202 # id for a valid civicrm user

    def tearDown(self):
        pass

    def test_example(self):
        pass
         
    def test_add_options(self):
        results = self.cc._add_options({}, limit=1,offset=0)
        expected = {u'options[limit]' : 1, u'options[offset]' : 0}
        self.assertEquals(expected['options[limit]'], 1)
    
    def test_add_single_option(self):
        results = self.cc._add_options({}, limit=1)
        self.assertEquals(len(results), 1)

    def test__construct_payload(self):
        payload = self.cc._construct_payload('get', 'Contact', 
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
    
    def test__get(self):
        results = self.cc._get('get', 'Contact')
        self.assertGreater(len(results), 1)

    def test__post(self):
        results = self.cc._post('get', 'Contact')
        self.assertGreater(len(results), 1)
    
    def test_get(self):
        results = self.cc.get('Contact')
        self.assertGreater(len(results), 1)
    
    def test_get_with_params(self):
        results = self.cc.get('Contact', contact_id=2)
        result = results[0]
        self.assertEquals(result['sort_name'], 'Terry, Brittney')

    def test_get_with__multiple_params(self):
        results = self.cc.get('Contact', **{'contact_type': 'Individual',
            'Country' : 'United States'})
        self.assertGreater(len(results), 1)

    def test_get_with_limit_offset(self):
        results = self.cc.get('Contact', **{'contact_type': 'Individual','Country' : 'United States', 'limit': 2, 'offset': 0})
        result = results[0]
        self.assertEquals(result['sort_name'], 'Terry, Brittney')
        self.assertEquals(len(results), 2)

    def test_get_null_set(self):
        results = self.cc.get('Contact', contact_id=100000)
        self.assertEquals(results, [])

    def test_get_invalid_option(self):
        self.assertRaises(CivicrmError,self.cc.get, 
                'Contact', contact_id='a')

    def test_getsingle(self):
        results = self.cc.getsingle('Contact',contact_id=2)
        self.assertEquals(results['sort_name'], 'Terry, Brittney')

    def test_getsingle_multiple_results(self):
        self.assertRaises(CivicrmError, self.cc.getsingle, 
            'Contact', country='United States')

    def test_getvalue(self):
        results = self.cc.getvalue('Contact', 'sort_name', contact_id=2)
        self.assertEquals(type(results), unicode)
        self.assertEquals(results, 'Terry, Brittney')
        
    def test_getvalue_multiple_results(self):
        self.assertRaises(CivicrmError, self.cc.getvalue, 
            'Contact', 'sort_name', country='United States')
    
    def test_create(self):
        results = self.cc.create('Contact', 
                contact_type='individual', display_name='bar, foo')
        self.cc.delete('Contact', results[0]['id'], True)
        self.assertEquals(results[0]['display_name'], 'bar, foo')
    
    def test_delete(self):
        cresults = self.cc.create('Contact', 
                contact_type='individual', display_name='bar, foo')
        results = self.cc.delete('Contact', cresults[0]['id'], True)
        self.assertEquals(results, 1)

    def test_update(self):
        cresults = self.cc.create('Contact', 
                contact_type='individual', display_name='bar, foo')
        myid = cresults[0]['id']
        results = self.cc.update('Contact', myid, display_name='foo, bar')
        self.cc.delete('Contact', myid, True)
        self.assertEquals(results[0]['display_name'], 'foo, bar')

    def test_setvalue(self):
        cresults = self.cc.create('Contact', 
                contact_type='individual', display_name='bar, foo')
        myid = cresults[0]['id']
        results = self.cc.setvalue('Contact', myid, 
                'display_name', 'foo, bar')
        self.cc.delete('Contact', myid, True)
        self.assertEquals(results['display_name'], 'foo, bar')


    def test_getcount(self):
        count = self.cc.getcount('Contact', contact_id=2)
        self.assertEquals(count, 1)

    def test_getfields(self):
        results = self.cc.getfields('Contact')
        self.assertIn('id', results)

    def test_getoptions(self):
        results = self.cc.getoptions('Contact', 'contact_type')
        self.assertIn('Organization', results)
    
    def test_getoptions_raises_error(self):
        self.assertRaises(CivicrmError, self.cc.getoptions, 'Contact', 'city')

    def test_doaction(self):
        results = self.cc.doaction('get', 'Contact')
        self.assertGreater(len(results), 1)

    def test_create_contact(self):
        results =  self.cc.create_contact(
                contact_type='Individual', display_name='test')
        self.cc.delete('Contact', results['id'], True)
        self.assertEquals(results['display_name'], 'test')

    def test_create_contact_required_field_missing(self):
        self.assertRaisesRegexp(CivicrmError, 'fields must exist',
                self.cc.create_contact, contact_type='Individual')
    
    def test_create_contact_wrong_type(self):
        self.assertRaisesRegexp(CivicrmError,' not a valid option',
                self.cc.create_contact, 'not a contact type', 
                display_name='test')

    def test_add_relationship_by_id(self):
        result = self.cc.add_relationship(101, 102, 1)
        self.cc.delete('Relationship', result['id'], True)
        self.assertEquals(result['relationship_type_id'], '1')

    def test_add_relationship_by_type(self):
        result = self.cc.add_relationship(101, 102, 'Partner of')
        self.cc.delete('Relationship', result['id'], True)
        self.assertEquals(result['relationship_type_id'], '3')

    def test_add_relationship_type_not_found(self):
        self.assertRaises(CivicrmError, 
                self.cc.add_relationship, 101, 102, 'Aunt of')
    
    def test_add_activity_type(self):
        result = self.cc.add_activity_type('test_activity_type', 
                is_active=1)
        atypes  = self.cc.get('ActivityType')
        self.cc.delete('ActivityType', result['id'], True)
        self.assertIn('test_activity_type', atypes)

    def test_add_activity_by_status_id(self):
        result = self.cc.add_activity("Meeting", self.contact_id, 
                subject = "test", status = 2,  is_test=1)
        self.cc.delete('Activity', result['id'], True)
        self.assertEquals(result['activity_type_id'], '1')
    
    def test_add_activity_by_status_type(self):
        result = self.cc.add_activity("Meeting", self.contact_id,
                subject = "test", activity_status = "completed", 
                status = "Cancelled",  is_test=1)
        self.cc.delete('Activity', result['id'], True)
        self.assertEquals(result['activity_type_id'], '1')

    def test_add_activity_invalid_label(self):
        self.assertRaises(CivicrmError,
            self.cc.add_activity,"Not A Meeting", self.contact_id,  
            "test", "0000", 2)

    def test_add_activity_invalid_status_id(self):
        self.assertRaises(CivicrmError,
            self.cc.add_activity,"Meeting", self.contact_id, 
            "test", "0000", 10)

    def test_add_activity_invalid_status_type(self):
        self.assertRaises(CivicrmError,
            self.cc.add_activity,"Meeting", self.contact_id,
            "test", "0000", "test")

    def test_add_contribution(self):
        result = self.cc.add_contribution(self.contact_id, 100, 1, is_test=1)
        self.cc.delete('Contribution', result['id'], True)
        self.assertEquals(result['total_amount'], '100')

    def test_add_email(self):
        result = self.cc.add_email(self.contact_id, 'test@example.org')
        self.cc.delete('Email', result['id'], True)
        self.assertEquals(result['email'], 'test@example.org')

    def test_add_email_is_not_email_like(self):
        self.assertRaises(CivicrmError, self.cc.add_email, 
            self.contact_id, 'invalid.address', True)

    def test_add_note(self):
        result = self.cc.add_note(self.contact_id, 'test')
        self.cc.delete('Note', result['id'], True)
        self.assertEquals(result['note'], 'test')

    def test_add_tag(self):
        result = self.cc.add_tag('test')
        self.cc.delete('Tag', result['id'], True)
        self.assertEquals(result['name'], 'test')

    def test_add_entity_tag(self):
        result = self.cc.add_entity_tag(self.contact_id, 1)
        self.cc.doaction('delete', 'EntityTag', tag_id=1,
                entity_id=202)
        self.assertEquals(result['added'], 1)

    def test_add_group(self):
        result = self.cc.add_group(title='test')
        self.cc.delete('Group', result['id'], True)
        self.assertEquals(result['title'], 'test')
    
    def test_add_group_contact(self):
        result = self.cc.add_group_contact(self.contact_id, 5)
        self.cc.doaction('delete', 'GroupContact', group_id=5,
                contact_id=self.contact_id)
        self.assertEquals(result['added'], 1)

    def test_add_phone(self):
        result = self.cc.add_phone(self.contact_id, '111-111-1111')
        self.cc.delete('Phone', result['id'], True)
        self.assertEquals(result['phone'], '111-111-1111')

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

    
if __name__ == '__main__':
    pass
