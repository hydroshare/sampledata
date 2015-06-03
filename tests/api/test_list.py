__author__ = 'valentin'
import os

import unittest
from hs_restclient import HydroShare

class TestGetResourceList(unittest.TestCase):
    def setUp(self):
        self.url = os.environ['HYDROSHARE'] if os.environ.get('HYDROSHARE') is not None else "http://dev.hydroshare.org"
        # need to have some generic titles. Not sure how we can pass them
        self.a_Title = os.environ['ResourceTitle'] if  os.environ.get('ResourceTitle') is not None else 'Logan DEM'
        self.a_resource_id = os.environ['ResourceId'] if os.environ.get('ResourceId') is not None else 'e327f29ff92b4871a4a94556db7b7635'

    def test_get_resource_list(self):
        success_title = False
        success_id = False
        hs = HydroShare()
        res_list = hs.getResourceList()

        for (i, r) in enumerate(res_list):
            if (r['resource_title'] == self.a_Title):
                success_title= True
            if r['resource_id']== self.a_resource_id :
                success_id=True


        self.assertTrue( success_title, "title not found")
        self.assertTrue( success_id, "id not found")