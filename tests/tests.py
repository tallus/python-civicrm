import unittest
from pythoncivicrm.pythoncivicrm import _add_options
from pythoncivicrm.pythoncivicrm import CiviCRM
from pythoncivicrm.pythoncivicrm import CivicrmError


class MyTests(unittest.TestCase):
        # pylint: disable=R0904

    def setUp(self):
        ip='192.168.56.101' # was '192.168.1.124'
        url = "%s/drupal7/sites/all/modules/civicrm/extern/rest.php" % ip
        site_key = '371cfadc834d2784a35e4f4ab20c1316'
        api_key = 'b734df56706432bb514ed737465424c3'
        self.cc = CiviCRM(url, site_key, api_key, use_ssl=False)

    def tearDown(self):
        pass

    def test_example(self):
        pass
         
    def test_add_options(self):
        results = _add_options({}, limit=1,offset=0)
        expected = {u'options[limit]' : 1, u'options[offset]' : 0}
        self.assertEquals(expected['options[limit]'], 1)
    
    def test_add_single_option(self):
        results = _add_options({}, limit=1)
        self.assertEquals(len(results), 1)

    def test__construct_request(self):
        url, payload = self.cc._construct_request('get', 'Contact', 
                {'json' : 0, 'contact_id': 2})
        self.assertEquals(payload['json'], 1)
        self.assertEquals(payload['contact_id'], 2)

    def test__check_results(self):
        results = self.cc._check_results({'is_error' : 0, 'result' : 1})
        self.assertEquals(results, 1)

    def test__check_results_raises_exception(self):
        self.assertRaises(CivicrmError, self.cc._check_results,
                {'is_error' : 1, 'error_message' : 'test', 'result' : 1})

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
        results = self.cc.get('Contact', {'contact_id': 2})
        result = results[0]
        self.assertEquals(result['sort_name'], 'Terry, Brittney')

    def test_get_with__multiple_params(self):
        results = self.cc.get('Contact', {'contact_type': 'Individual',
            'Country' : 'United States'})
        self.assertGreater(len(results), 1)

    def test_get_with_limit_offset(self):
        results = self.cc.get('Contact', {'contact_type': 'Individual',
            'Country' : 'United States'}, limit=2,offset=0)
        result = results[0]
        self.assertEquals(result['sort_name'], 'Terry, Brittney')
        self.assertEquals(len(results), 2)

    def test_get_null_set(self):
        results = self.cc.get('Contact', {'contact_id': 100000})
        self.assertEquals(results, [])

    def test_get_invalid_option(self):
        self.assertRaises(CivicrmError,self.cc.get, 
                'Contact', {'contact_id': 'a'})

    def test_getsingle(self):
        results = self.cc.getsingle('Contact', {'contact_id': 2})
        self.assertEquals(results['sort_name'], 'Terry, Brittney')

    def test_getsingle_multiple_results(self):
        self.assertRaises(CivicrmError, self.cc.getsingle, 
            'Contact', {'Country' : 'United States'})

    def test_getvalue(self):
        results = self.cc.getvalue('Contact', 'sort_name', {'contact_id': 2})
        self.assertEquals(type(results), unicode)
        self.assertEquals(results, 'Terry, Brittney')
        
    def test_getvalue_multiple_results(self):
        self.assertRaises(CivicrmError, self.cc.getvalue, 
            'Contact', 'sort_name', {'Country' : 'United States'})
    
    def test_search(self):
        results = self.cc.search('Contact', contact_id=2)
        result = results[0]
        self.assertEquals(result['sort_name'], 'Terry, Brittney')

    def test_searchsingle(self):
        results = self.cc.searchsingle('Contact', contact_id=2)
        self.assertEquals(results['sort_name'], 'Terry, Brittney')

    def test_searchvalue(self):
        results = self.cc.searchvalue('Contact', 'sort_name', contact_id=2)
        self.assertEquals(type(results), unicode)
        self.assertEquals(results, 'Terry, Brittney')

    def test_create(self):
        results = self.cc.create('Contact', 
                {'contact_type' : 'individual', 'display_name' : 'bar, foo'})
        self.cc.delete('Contact', results[0]['id'], True)
        self.assertEquals(results[0]['display_name'], 'bar, foo')
    
    def test_delete(self):
        cresults = self.cc.create('Contact', 
                {'contact_type' : 'individual', 'display_name' : 'bar, foo'})
        results = self.cc.delete('Contact', cresults[0]['id'], True)
        self.assertEquals(results, 1)

    def test_update(self):
        cresults = self.cc.create('Contact', 
                {'contact_type' : 'individual', 
                 'display_name' : 'bar, foo'})
        myid = cresults[0]['id']
        results = self.cc.update('Contact', myid,
                {'display_name' : 'foo, bar'})
        self.cc.delete('Contact', myid, True)
        self.assertEquals(results[0]['display_name'], 'foo, bar')

    def test_setvalue(self):
        cresults = self.cc.create('Contact', 
                {'contact_type' : 'individual', 
                 'display_name' : 'bar, foo'})
        myid = cresults[0]['id']
        results = self.cc.setvalue('Contact', myid, 
                'display_name', 'foo, bar')
        self.cc.delete('Contact', myid, True)
        self.assertEquals(results['display_name'], 'foo, bar')

    def test_updatevalues(self):
        cresults = self.cc.create('Contact', 
                {'contact_type' : 'individual', 
                 'display_name' : 'bar, foo'})
        myid = cresults[0]['id']
        results = self.cc.updatevalues('Contact', myid,
                display_name = 'foo, bar')
        self.cc.delete('Contact', myid, True)
        self.assertEquals(results[0]['display_name'], 'foo, bar')


if __name__ == '__main__':
    pass
    
