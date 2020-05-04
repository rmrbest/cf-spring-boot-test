import unittest

from cfprovision import cfprovision


class MyTestCase(unittest.TestCase):

    def test_parse_config(self):
        cfprovision.parse_config('test/config_fake.yml')
        self.assertEqual('my-key-fake', cfprovision.key_name)
        self.assertEqual('rmrbest.test.fake', cfprovision.s3_template_bucket_name)
        self.assertEqual('test', cfprovision.environment)
        self.assertEqual('test-app', cfprovision.stack_name)


if __name__ == '__main__':
    unittest.main()
