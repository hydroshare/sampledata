__author__ = 'valentin'
import os, sys
import StringIO, zipfile
import tempfile
import shutil

import unittest
from datetime import date, datetime
import requests

from hs_restclient import HydroShare, HydroShareAuthBasic
from hs_restclient import  HydroShareNotFound,HydroShareNotAuthorized, HydroShareException,HydroShareHTTPException


class TestGetResourceList(unittest.TestCase):

    # these will need to be replaced with some form of properties reader.

    def setUp(self):
        self.resources_to_delete = []
        self.url = os.environ['HYDROSHARE'] if os.environ.get('HYDROSHARE') is not None else "dev.hydroshare.org"
        self.use_https = os.getenv('USE_HTTPS', 'False')
        if self.use_https == 'True':
            self.use_https = True
        else:
            self.use_https = False

        self.port = os.environ.get('PORT', None)

        # need to have some generic titles. Not sure how we can pass them
        self.creator = os.environ['Creator'] if os.environ.get('Creator') is not None else 'admin'
        self.creatorPassword = os.environ.get('CreatorPassword') # if it's empty, fail the auth tests
        self.auth = None
        if self.creatorPassword:
            self.auth = HydroShareAuthBasic(username=self.creator,password=self.creatorPassword)
        # items to look up. Present info from dev.hydroshare.org
        self.a_Title = os.environ['ResourceTitle'] if  os.environ.get('ResourceTitle') is not None else 'Logan DEM'
        self.a_resource_id = os.environ['ResourceId'] if os.environ.get('ResourceId') is not None else 'e327f29ff92b4871a4a94556db7b7635'
        self.a_resource_type = os.environ['ResourceType'] if os.environ.get('ResourceType') is not None else 'RasterResource'
        self.a_resource_filename = os.environ['ResourceName'] if os.environ.get('ResourceName') is not None else 'logan.tif'
        # create
        self.test_genericResource_path = '../../raw/document/pdf/HIC2014-1566.pdf'
        self.test_netcdfResource_path = '../../raw/netcdf_rapid_compliant/-nfiehydroZone-home-public-usgs-national-2015-08-19-national_2015-08-19.nc'

        if self.url.startswith('www'):
            raise unittest.SkipTest("No Live Tests on www")
        expected_testpath = os.getcwd().endswith('api')
        if not expected_testpath:
            self.fail( "tests need to run from 'tests/api' current path is:" + os.getcwd())

    def tearDown(self):
        # Try to make sure all created resources are cleaned up from iRODS
        # by calling delete on them through the REST API.
        hs = self.get_hs_auth()
        for res_id in self.resources_to_delete:
            try:
                del_res_id = hs.deleteResource(res_id)
                assert(del_res_id == res_id)
            except HydroShareNotFound:
                # The resource was probably already deleted.
                pass

    # def test_get_resource_list(self):
    #     success_title = False
    #     success_id = False
    #     hs = HydroShare(hostname=self.url)
    #
    #     res_list = hs.getResourceList()
    #
    #     for (i, r) in enumerate(res_list):
    #         if (r['resource_title'] == self.a_Title):
    #             success_title= True
    #         if r['resource_id']== self.a_resource_id :
    #             success_id=True
    #         if (success_id and success_title):
    #             break
    #
    #
    #     self.assertTrue( success_title, "title not found")
    #     self.assertTrue( success_id, "id not found")
    #
    # def test_get_resource_list_filter_creator(self):
    #     hs = HydroShare(hostname=self.url)
    #     res_list = hs.getResourceList(creator=self.creator)
    #     for (i, r) in enumerate(res_list):
    #         self.assertEquals(r['creator'], self.creator)
    #
    #
    #
    #
    # def test_get_resource_list_filter_date(self):
    #     hs = HydroShare(hostname=self.url)
    #     from_date = date(2015, 5, 20)
    #     res_list = hs.getResourceList(from_date=from_date)
    #     for (i, r) in enumerate(res_list):
    #         self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() >= from_date)
    #
    #     to_date = date(2015, 5, 21) # up to and including 5/21/2015
    #     res_list = hs.getResourceList(to_date=to_date)
    #     for (i, r) in enumerate(res_list):
    #         self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() < to_date)
    #
    #     from_date = date(2015, 5, 19)
    #     to_date = date(2015, 5, 22) # up to and including 5/21/2015
    #     res_list = hs.getResourceList(from_date=from_date, to_date=to_date)
    #     for (i, r) in enumerate(res_list):
    #         self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() >= from_date)
    #         self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() < to_date)
    #
    # def test_get_resource_list_filter_date(self):
    #     hs = HydroShare(hostname=self.url)
    #     from_date = date(2015, 5, 20)
    #     res_list = hs.getResourceList(from_date=from_date)
    #     for (i, r) in enumerate(res_list):
    #         self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() >= from_date)
    #
    #     to_date = date(2015, 5, 21) # up to and including 5/21/2015
    #     res_list = hs.getResourceList(to_date=to_date)
    #     for (i, r) in enumerate(res_list):
    #         self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() < to_date)
    #
    #     from_date = date(2015, 5, 19)
    #     to_date = date(2015, 5, 22) # up to and including 5/21/2015
    #     res_list = hs.getResourceList(from_date=from_date, to_date=to_date)
    #     for (i, r) in enumerate(res_list):
    #         self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() >= from_date)
    #         self.assertTrue(datetime.strptime(r['date_created'], '%m-%d-%Y').date() < to_date)
    #
    # def test_get_resource(self):
    #     hs = HydroShare(hostname=self.url)
    #     # ideally, look a system metadata, and if file is small, then load it into memory.
    #
    #     sysmeta = hs.getSystemMetadata(self.a_resource_id)
    #     self.assertEqual(sysmeta['resource_id'], self.a_resource_id)
    #     self.assertEqual(sysmeta['resource_type'], self.a_resource_type)
    #     self.assertTrue(sysmeta['public'])
    #
    #     # if (sysmeta['size']) < 1000000:
    #     stream = hs.getResource(self.a_resource_id)
    #     in_memory = StringIO.StringIO()
    #     for chunk in stream:
    #         in_memory.write(chunk)
    #     self.assertTrue( zipfile.is_zipfile(in_memory) )
    #     with zipfile.ZipFile(in_memory, 'r') as myzip:
    #         filelist = myzip.infolist()
    #         success = False
    #         for f in filelist:
    #             if self.a_resource_filename in f.filename:
    #                 success = True
    #                 break
    #         self.assertTrue(success, "did not find file")

    def _create_resource_without_file(self, hs, abstract, title, keywords, rtype='GenericResource', is_public=False):
        newres = hs.createResource(rtype, title, keywords=keywords, abstract=abstract)
        assert(newres is not None)
        self.resources_to_delete.append(newres)
        if is_public:
            hs.setAccessRules(newres, public=True)
        return newres

    def get_hs_auth(self):
        self.assertIsNotNone(self.auth, "Auth not provided")
        hs = None
        try:
            hs = HydroShare(hostname=self.url, auth=self.auth, use_https=self.use_https, port=self.port)
        except:
            self.fail("Authorized Connection Failed" + sys.exc_info()[0])
        return hs

    def get_hs_noauth(self):
        hs = None
        try:
            hs = HydroShare(hostname=self.url, use_https=self.use_https, port=self.port)
        except:
            self.fail("Anonymous Connection Failed" + sys.exc_info()[0])
        return hs

    def test_get_public_resource_noauth(self):
        hs = self.get_hs_auth()

         # Create a public resource
        newres_id = self._create_resource_without_file(hs, abstract='This is a public resource to be fetched noauth',
                                                       title='My public resource noauth', keywords=('this is public', 'a resource', 'no auth'),
                                                       is_public=True)

        hs_noauth = self.get_hs_noauth()
        # Get public resource as anonymous user
        try:
            tmp_dir = tempfile.mkdtemp()
            hs_noauth.getResource(newres_id, destination=tmp_dir)
            for f in os.listdir(tmp_dir):
                if f.endswith('.zip'):
                    fpath = os.path.join(tmp_dir, f)
                    self.assertGreater(os.stat(fpath).st_size, 0)
        finally:
            shutil.rmtree(tmp_dir)



# auth tests
    def test_get_resource_list_filter_creator_private(self):
        hs = self.get_hs_auth()

        # Create a public resource
        self._create_resource_without_file(hs, abstract='This is a public resource',
                                           title='My public resource', keywords=('this is public', 'a resource'),
                                           is_public=True)

        # Create two private resources
        self._create_resource_without_file(hs, abstract='This is private resource 1',
                                           title='My public resource, no. 1', keywords=('this is private', 'resource1'))
        self._create_resource_without_file(hs, abstract='This is private resource 2',
                                           title='My public resource, no. 2', keywords=('this is private', 'resource2'))

        # Count public and private resources
        public_count = 0
        private_count = 0
        res_list = hs.getResourceList(creator=self.creator)
        for res in res_list:
            if res['public'] is True:
                public_count += 1
            else:
                private_count += 1

        self.assertGreater(private_count,public_count, "Private("+str(private_count)+") not greater than public("+str(public_count)+") ")

# Create and delete
# need to setup with a set list
    #NOTE: If some assertion fails, then you can end up with a created resource.
    # may need to do a separate set of cases where setUpModule creates, and tearDownModule.
    # @unittest.skipUnless( os.getcwd().endswith('tests/api') ,
    #                  "current path needs end with 'tests/api' path is" + os.getcwd() )
    def test_create_get_delete_resource(self):
        hs = self.get_hs_auth()

        abstract = 'Abstract for hello world resource'
        title = 'Minimal hello world resource'
        keywords = ('hello', 'world')
        rtype = 'GenericResource'
        fname = self.test_genericResource_path
        success = False
        errorMessage = []

        self.assertTrue(os.path.isfile(self.test_genericResource_path), "cannot find "+ self.test_genericResource_path + " at cwd: "+ os.getcwd() + " directory should be tests/api" )

        with  open(os.path.relpath(self.test_genericResource_path), 'r') as original:
        # Create
            newres = hs.createResource(rtype, title, resource_filename=original, keywords=keywords, abstract=abstract)
            self.resources_to_delete.append(newres)
            self.assertIsNotNone(newres)


        sysmeta = hs.getSystemMetadata(newres)
        self.assertEqual(sysmeta['resource_id'], newres)
        self.assertEqual(sysmeta['resource_type'], rtype)
        self.assertFalse(sysmeta['public'])


        # Make resource public
        hs.setAccessRules(newres, public=True)
        sysmeta = hs.getSystemMetadata(newres)
        self.assertTrue(sysmeta['public'])

        stream = hs.getResource(newres)
        in_memory = StringIO.StringIO()
        for chunk in stream:
            in_memory.write(chunk)
        self.assertTrue( zipfile.is_zipfile(in_memory) )
        with zipfile.ZipFile(in_memory, 'r') as myzip:
            filelist = myzip.infolist()

            for f in filelist:
                if self.a_resource_filename in f.filename:
                    downloaded = myzip.open(f.filename, 'r')
                    downloaded_in_memory = StringIO.StringIO()
                    for chunk in downloaded:
                        downloaded_in_memory.write(chunk)
                    with  open(os.path.relpath(self.test_genericResource_path), 'r') as original:
                        self.assertEqual(downloaded.read(), original.read())

        # Delete
        delres = hs.deleteResource(newres)
        self.assertEqual(delres, newres)
        self.assertRaises(HydroShareNotFound, hs.getSystemMetadata, (newres,))

    def test_netcdf_resource_create(self):
        hs = self.get_hs_auth()

        abstract = 'Abstract for rapid-compliant netcdf resource'
        title = 'Minimal rapid-compliant netcdf resource'
        keywords = ('rapid', 'NFIE', 'test')
        rtype = 'NetcdfResource'
        fname = self.test_netcdfResource_path

        self.assertTrue(os.path.isfile(fname), "cannot find "+ fname + " at cwd: "+ os.getcwd() + " directory should be tests/api" )

        newres = hs.createResource(rtype, title, resource_filename=fname, keywords=keywords, abstract=abstract)
        self.assertIsNotNone(newres)
        self.resources_to_delete.append(newres)

#     @with_httmock(mocks.hydroshare.resourceFileCRUD)
#     def test_create_get_delete_resource_file(self):
#         hs = HydroShare()
#         # Add
#         res_id = '0b047b77767e46c6b6f525a2f386b9fe'
#         fpath = 'mocks/data/another_resource_file.txt'
#         fname = os.path.basename(fpath)
#         resp = hs.addResourceFile(res_id, fpath)
#         self.assertEqual(resp, res_id)
#
#         # Get
#         tmpdir = tempfile.mkdtemp()
#         res_file = hs.getResourceFile(res_id, fname, destination=tmpdir)
#         self.assertTrue(filecmp.cmp(res_file, fpath, shallow=False))
#         shutil.rmtree(tmpdir)
#
#         # Delete
#         delres = hs.deleteResourceFile(res_id, fname)
#         self.assertEqual(delres, res_id)

if __name__ == '__main__':
    unittest.main()