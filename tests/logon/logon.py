# https://github.com/rossrowe/sauce-ci-python-demo/blob/master/simple_test.py
from selenium import webdriver
import unittest
import os


"""
Python unittest class which demonstrates creating a webdriver instance using environment variables
populated by the Sauce CI plugins.
"""

class testLogon(unittest.TestCase):

    def setUp(self):
        desired_capabilities = {}
        desired_capabilities['browserName'] = os.environ['SELENIUM_BROWSER']
        desired_capabilities['version'] = os.getenv('SELENIUM_VERSION', '')
        desired_capabilities['platform'] = os.environ['SELENIUM_PLATFORM']
        command_executor = "http://%s:%s@%s:%s/wd/hub" % (os.environ['SAUCE_USER_NAME'], os.environ['SAUCE_API_KEY'], os.environ['SELENIUM_HOST'], os.environ['SELENIUM_PORT'])
        self.wd = webdriver.Remote(desired_capabilities=desired_capabilities, command_executor=command_executor)
        self.url = os.environ['HYDROSHARE']
        self.user_viewer =  os.environ['HS_VIEWER_USER']
        self.password_viewer =  os.environ['HS_VIEWER_PASSWORD']
        self.user_creator =  os.environ['HS_CREATOR_USER']
        self.password_creator =  os.environ['HS_CREATOR_PASSWORD']
        self.user_superuser = os.environ['SUPERUSER_NAME']
        self.password_superuser = os.environ['SUPERUSER_PASSWORD']


    def test_viewerlogin(self):
        success = True
        wd  = self.wd
        wd.get(str(self.url))
        wd.find_element_by_css_selector("#signin-menu > a").click()
        wd.find_element_by_id("id_username").click()
        wd.find_element_by_id("id_username").clear()
        wd.find_element_by_id("id_username").send_keys(str(self.user_viewer))
        wd.find_element_by_id("id_password").click()
        wd.find_element_by_id("id_password").clear()
        wd.find_element_by_id("id_password").send_keys(str(self.password_viewer))
        wd.find_element_by_css_selector("input.hl-btn.hl-btn-green").click()
        print "\rSauceOnDemandSessionID=%s job-name=%s" % (self.wd.session_id, "test_viewerlogin")
        assert u'Home | Hydroshare' in wd.title
        if not ("Successfully logged in" in wd.find_element_by_tag_name("html").text):
            success = False
            print("Successfully logged in failed")
        self.assertTrue(success)

    def tearDown(self):
        self.wd.quit()

if __name__ == '__main__':
    unittest.main()
