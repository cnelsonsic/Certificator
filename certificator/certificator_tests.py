import os
import unittest
import tempfile

import certificator
from certificator.main import create_app

class CertificatorTestCase(unittest.TestCase):

    def setUp(self):
        self.application = create_app()
        self.db_fd, self.application.config['DATABASE'] = tempfile.mkstemp()
        self.application.config['TESTING'] = True
        self.app = self.application.test_client()
        from certificator.db import db as sqla
        sqla.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.application.config['DATABASE'])

    def test_not_logged_in_redirect(self):
        '''When a user is not logged in, redirect to the landing page.'''
        rv = self.app.get('/')
        print repr(rv.headers)
        assert rv.status_code == 302
        assert rv.headers['Location'] == 'http://localhost/greetings'

if __name__ == '__main__':
    unittest.main()
