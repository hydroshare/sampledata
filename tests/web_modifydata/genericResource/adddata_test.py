# -*- coding: utf-8 -*-
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
import time, unittest
import os

def is_alert_present(wd):
    try:
        wd.switch_to_alert().text
        return True
    except:
        return False

class adddata(unittest.TestCase):
    def setUp(self):

        desired_capabilities = {}
        desired_capabilities['browserName'] = os.environ['SELENIUM_BROWSER']
        desired_capabilities['version'] = os.getenv('SELENIUM_VERSION', '')
        desired_capabilities['platform'] = os.environ['SELENIUM_PLATFORM']
        command_executor = "http://%s:%s@%s:%s/wd/hub" % (os.environ['SAUCE_USER_NAME'], os.environ['SAUCE_API_KEY'], os.environ['SELENIUM_HOST'], os.environ['SELENIUM_PORT'])
        self.wd  = webdriver.Remote(desired_capabilities=desired_capabilities, command_executor=command_executor)
        self.wd.implicitly_wait(60)
        self.url = os.environ['HYDROSHARE']
        self.user_viewer =  os.environ['HS_VIEWER_USER']
        self.password_viewer =  os.environ['HS_VIEWER_PASSWORD']
        self.user_creator =  os.environ['HS_CREATOR_USER']
        self.password_creator =  os.environ['HS_CREATOR_PASSWORD']
        self.user_superuser = os.environ['SUPERUSER_NAME']
        self.password_superuser = os.environ['SUPERUSER_PASSWORD']

    def test_adddata(self):
        success = True
        wd = self.wd
        wd.get("http://sandbox.hydroshare.org/")
        wd.find_element_by_css_selector("#signin-menu > a").click()
        wd.find_element_by_id("id_username").click()
        wd.find_element_by_id("id_username").clear()
        wd.find_element_by_id("id_username").send_keys("creator")
        wd.find_element_by_id("id_password").click()
        wd.find_element_by_id("id_password").clear()
        wd.find_element_by_id("id_password").send_keys("creator")
        wd.find_element_by_css_selector("input.hl-btn.hl-btn-green").click()
        wd.find_element_by_link_text("RESOURCES").click()
        wd.find_element_by_link_text("Create new").click()
        wd.find_element_by_id("title").click()
        wd.find_element_by_id("title").clear()
        wd.find_element_by_id("title").send_keys("test_private")
        wd.find_element_by_id("select-file").click()
        wd.find_element_by_xpath("//form[@class='form-horizontal']//button[.='Create Resource']").click()
        if not ("Congratulations!" in wd.find_element_by_tag_name("html").text):
            success = False
            print("verifyTextPresent failed")
        if not ("test_private" in wd.find_element_by_tag_name("html").text):
            success = False
            print("verifyTextPresent failed")
        ActionChains(wd).double_click(wd.find_element_by_css_selector("span.label-file-name")).perform()
        wd.find_element_by_css_selector("span.label-file-name").click()
        if not ("logan.tif" in wd.find_element_by_tag_name("html").text):
            success = False
            print("verifyTextPresent failed")
        wd.find_element_by_id("edit-metadata").click()
        wd.find_element_by_id("id_abstract").click()
        wd.find_element_by_id("id_abstract").clear()
        wd.find_element_by_id("id_abstract").send_keys("test abstract")
        wd.find_element_by_xpath("//form[@id='id-description']/fieldset/div[2]/button").click()
        wd.find_element_by_id("txt-keyword").click()
        wd.find_element_by_id("txt-keyword").clear()
        wd.find_element_by_id("txt-keyword").send_keys("geotiff")
        wd.find_element_by_id("btn-add-keyword").click()
        wd.find_element_by_xpath("//form[@id='id-subject']/fieldset/div[2]/button").click()
        wd.find_element_by_link_text("Manage access").click()
        wd.find_element_by_xpath("//div[@class='custom-btn-toolbar']/a/span").click()
        wd.find_element_by_link_text("RESOURCES").click()
        wd.find_element_by_link_text("Create new").click()
        wd.find_element_by_id("title").click()
        wd.find_element_by_id("title").clear()
        wd.find_element_by_id("title").send_keys("test public")
        wd.find_element_by_id("title").click()
        wd.find_element_by_id("title").clear()
        wd.find_element_by_id("title").send_keys("test_public")
        wd.find_element_by_id("select-file").click()
        wd.find_element_by_xpath("//form[@class='form-horizontal']//button[.='Create Resource']").click()
        wd.find_element_by_id("edit-metadata").click()
        wd.find_element_by_id("id_abstract").click()
        wd.find_element_by_id("id_abstract").clear()
        wd.find_element_by_id("id_abstract").send_keys("test public file")
        wd.find_element_by_xpath("//form[@id='id-description']/fieldset/div[2]/button").click()
        wd.find_element_by_id("txt-keyword").click()
        wd.find_element_by_id("txt-keyword").clear()
        wd.find_element_by_id("txt-keyword").send_keys("report")
        wd.find_element_by_id("btn-add-keyword").click()
        wd.find_element_by_xpath("//form[@id='id-subject']/fieldset/div[2]/button").click()
        wd.find_element_by_id("body").click()
        wd.find_element_by_xpath("//div[@class='custom-btn-toolbar']/a/span").click()
        wd.find_element_by_id("btn-public").click()
        if not ("Public" in wd.find_element_by_tag_name("html").text):
            success = False
            print("verifyTextPresent failed")
        wd.find_element_by_link_text("RESOURCES").click()
        if not ("test_private" in wd.find_element_by_tag_name("html").text):
            success = False
            print("verifyTextPresent failed")
        if not ("test_public" in wd.find_element_by_tag_name("html").text):
            success = False
            print("verifyTextPresent failed")
        self.assertTrue(success)
    
    def tearDown(self):
        self.wd.quit()

if __name__ == '__main__':
    unittest.main()
