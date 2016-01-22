# Live tests of hs_restclient
#
# How to run locally:
# USE_HTTPS=True HYDROSHARE=mill24.cep.unc.edu Creator=admin CreatorPassword=default CLIENT_ID=... CLIENT_SECRET=... VERIFY_CERTS=False nosetests test_live
#
import os, sys
import StringIO, zipfile
import tempfile
import shutil
import unittest
import json

import requests

from hs_restclient import HydroShare, HydroShareAuthBasic, HydroShareAuthOAuth2
from hs_restclient import  HydroShareNotFound,HydroShareNotAuthorized, HydroShareException,HydroShareHTTPException


class HydroShareTestCase(unittest.TestCase):

    _TOKEN_URL_PROTO_WITHOUT_PORT = "{scheme}://{hostname}/o/token/"
    _TOKEN_URL_PROTO_WITH_PORT = "{scheme}://{hostname}:{port}/o/token/"

    # these will need to be replaced with some form of properties reader.

    def setUp(self):
        self.resources_to_delete = []
        self.url = os.environ['HYDROSHARE'] if os.environ.get('HYDROSHARE') is not None else "dev.hydroshare.org"
        self.use_https = os.getenv('USE_HTTPS', 'True')
        if self.use_https == 'True':
            self.use_https = True
        else:
            self.use_https = False

        self.verify = os.getenv('VERIFY_CERTS', 'True')
        if self.verify == 'True':
            self.verify = True
        else:
            self.verify = False

        self.port = os.environ.get('PORT', None)

        # OAuth2
        self.client_id = os.environ.get('CLIENT_ID', None)
        self.client_secret = os.environ.get('CLIENT_SECRET', None)

        # need to have some generic titles. Not sure how we can pass them
        self.creator = os.environ['Creator'] if os.environ.get('Creator') is not None else 'admin'
        self.creatorPassword = os.environ.get('CreatorPassword') # if it's empty, fail the auth tests
        self.auth = None
        self.oauth = None
        if self.creatorPassword:
            self.auth = HydroShareAuthBasic(username=self.creator,password=self.creatorPassword)
            if self.client_id and self.client_secret:
                self.oauth = HydroShareAuthOAuth2(self.client_id, self.client_secret,
                                                  self.url, use_https=self.use_https, port=self.port,
                                                  username=self.creator, password=self.creatorPassword)
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

        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):

        shutil.rmtree(self.tmp_dir)
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
            hs = HydroShare(hostname=self.url, auth=self.auth, use_https=self.use_https, verify=self.verify,
                            port=self.port)
        except:
            self.fail("Authorized Connection Failed" + sys.exc_info()[0])
        return hs

    def get_hs_noauth(self):
        hs = None
        try:
            hs = HydroShare(hostname=self.url, use_https=self.use_https, verify=self.verify,
                            port=self.port)
        except:
            self.fail("Anonymous Connection Failed" + sys.exc_info()[0])
        return hs

    def get_hs_oauth2(self):
        hs = None
        try:
            hs = HydroShare(hostname=self.url, auth=self.oauth, use_https=self.use_https, verify=self.verify,
                            port=self.port)
        except:
            self.fail("OAuth2 Connection Failed" + str(sys.exc_info()[0]))
        return hs

    def get_hs_oauth2_token(self):
        hs = None
        # Get token ourselves (i.e. without using oauthlib, etc.)
        try:
            if self.use_https:
                scheme = 'https'
            else:
                scheme = 'http'
            data = {'grant_type': 'password',
                    'username': self.creator, 'password': self.creatorPassword}
            if self.port:
                token_url = self._TOKEN_URL_PROTO_WITH_PORT.format(scheme=scheme,
                                                                   hostname=self.url,
                                                                   port=self.port)
            else:
                token_url = self._TOKEN_URL_PROTO_WITHOUT_PORT.format(scheme=scheme,
                                                                      hostname=self.url)
            r = requests.post(token_url, data=data, auth=(self.client_id, self.client_secret),
                              verify=self.verify)
            token = json.loads(r.text)
            oauth_token = HydroShareAuthOAuth2(self.client_id, self.client_secret,
                                               self.url, use_https=self.use_https, port=self.port,
                                               token=token)
            hs = HydroShare(hostname=self.url, auth=oauth_token, use_https=self.use_https, verify=self.verify,
                            port=self.port)
        except:
            self.fail("OAuth2 Connection Failed" + str(sys.exc_info()[0]))
        return hs


class TestGetResourceList(HydroShareTestCase):

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

        # Test resource type in system metadata
        sysmeta = hs.getSystemMetadata(newres)
        self.assertEqual(sysmeta['resource_type'], rtype)

        # Test resource type in resource list
        for resource in hs.getResourceList():
            if resource['resource_id'] == newres:
                self.assertEqual(resource['resource_type'], rtype)

    def test_oauth2_authentication(self):
        if self.client_id is None or self.client_secret is None:
            self.skipTest("OAuth2 client ID/secret not specified.")

        hs = self.get_hs_oauth2()

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

    def test_oauth2_authentication_token(self):
        if self.client_id is None or self.client_secret is None:
            self.skipTest("OAuth2 client ID/secret not specified.")

        hs = self.get_hs_oauth2_token()

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


class TestGetResource(HydroShareTestCase):

    def test_get_public_resource_noauth(self):
        hs = self.get_hs_auth()

        # Create a public resource
        res_id = self._create_resource_without_file(hs, abstract='This is a public resource to be fetched noauth',
                                                    title='My public resource noauth',
                                                    keywords=('this is public', 'a resource', 'no auth'),
                                                    is_public=True)
        # Download without authentication
        hs_noauth = self.get_hs_noauth()
        hs_noauth.getResource(res_id, destination=self.tmp_dir)
        res_file_path = os.path.join(self.tmp_dir, "{res_id}.zip".format(res_id=res_id))
        self.assertTrue(os.path.exists(res_file_path))
        self.assertGreater(os.stat(res_file_path).st_size, 0)

    def test_get_private_resource_oauth(self):
        if self.client_id is None or self.client_secret is None:
            self.skipTest("OAuth2 client ID/secret not specified.")

        hs = self.get_hs_oauth2()

        # Create a private resource
        res_id = self._create_resource_without_file(hs, abstract='This is a private resource',
                                                    title='My private resource',
                                                    keywords=('this is private', 'a resource'),
                                                    is_public=False)
        hs.getResource(res_id, destination=self.tmp_dir)
        res_file_path = os.path.join(self.tmp_dir, "{res_id}.zip".format(res_id=res_id))
        self.assertTrue(os.path.exists(res_file_path))
        self.assertGreater(os.stat(res_file_path).st_size, 0)


if __name__ == '__main__':
    unittest.main()
