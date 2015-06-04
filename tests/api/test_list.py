__author__ = 'valentin'
import os, sys

import unittest
from datetime import date, datetime
import requests

from hs_restclient import HydroShare, HydroShareAuthBasic


class TestGetResourceList(unittest.TestCase):

    # these will need to be replaced with some form of properties reader.

    def setUp(self):
        self.url = os.environ['HYDROSHARE'] if os.environ.get('HYDROSHARE') is not None else "dev.hydroshare.org"
        # need to have some generic titles. Not sure how we can pass them
        self.a_Title = os.environ['ResourceTitle'] if  os.environ.get('ResourceTitle') is not None else 'Logan DEM'
        self.a_resource_id = os.environ['ResourceId'] if os.environ.get('ResourceId') is not None else 'e327f29ff92b4871a4a94556db7b7635'
        self.creator = os.environ['Creator'] if os.environ.get('Creator') is not None else 'admin'
        self.creatorPassword = os.environ.get('CreatorPassword') # if it's empty, fail the auth tests
        self.auth = None
        if self.creatorPassword:
            self.auth = HydroShareAuthBasic(username=self.creator,password=self.creatorPassword)




    def test_get_resource_list(self):
        success_title = False
        success_id = False
        hs = HydroShare(hostname=self.url)

        res_list = hs.getResourceList()

        for (i, r) in enumerate(res_list):
            if (r['resource_title'] == self.a_Title):
                success_title= True
            if r['resource_id']== self.a_resource_id :
                success_id=True
            if (success_id and success_title):
                break


        self.assertTrue( success_title, "title not found")
        self.assertTrue( success_id, "id not found")

    def test_get_resource_list_filter_creator(self):
        hs = HydroShare(hostname=self.url)
        res_list = hs.getResourceList(creator=self.creator)
        for (i, r) in enumerate(res_list):
            self.assertEquals(r['creator'], self.creator)




    def test_get_resource_list_filter_date(self):
        hs = HydroShare(hostname=self.url)
        from_date = date(2015, 5, 20)
        res_list = hs.getResourceList(from_date=from_date)
        for (i, r) in enumerate(res_list):
            self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() >= from_date)

        to_date = date(2015, 5, 21) # up to and including 5/21/2015
        res_list = hs.getResourceList(to_date=to_date)
        for (i, r) in enumerate(res_list):
            self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() < to_date)

        from_date = date(2015, 5, 19)
        to_date = date(2015, 5, 22) # up to and including 5/21/2015
        res_list = hs.getResourceList(from_date=from_date, to_date=to_date)
        for (i, r) in enumerate(res_list):
            self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() >= from_date)
            self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() < to_date)

# auth tests
    def test_auth(self):
        self.assertIsNotNone(self.auth, "Auth not provided")
        hs = None
        try:
            hs= HydroShare(hostname=self.url, auth=self.auth)
        except:
            self.fail("Authorized Connection Failed" + sys.exc_info()[0])
        return hs

    def test_get_resource_list_filter_creator_private(self):
        hs = self.test_auth()
        res_list = hs.getResourceList(creator=self.creator)
        # should be a lambda to to this
        public_count = sum(1 for x in res_list)
        hs_auth = HydroShare(hostname=self.url, auth=self.auth)
        res_list_auth = hs_auth.getResourceList(creator=self.creator)
        private_count = sum(1 for x in res_list_auth)
        self.assertGreater(private_count,public_count, "Private("+str(private_count)+") not greater than puhlic("+str(public_count)+") ")