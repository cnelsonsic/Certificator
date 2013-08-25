import os
import unittest
import tempfile
import httpretty

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

    def login(self):
        # Mock the response from persona.org for success.
        persona = ('{"audience":"http://localhost/",'
                   '"expires":9377394697781,'
                   '"issuer":"gmail.login.persona.org",'
                   '"email":"example@gmail.com",'
                   '"status":"okay"}')
        httpretty.register_uri(httpretty.POST,
                               "https://verifier.login.persona.org/verify",
                               body=persona,
                               content_type="application/json")

        rv = self.app.post('/api/login', data=dict(assertion="asdf"))

    def test_not_logged_in_redirect(self):
        '''When a user is not logged in, redirect to the landing page.'''
        rv = self.app.get('/')
        print repr(rv.headers)
        assert rv.status_code == 302
        assert rv.headers['Location'] == 'http://localhost/greetings'

    @httpretty.activate
    def test_log_in(self):
        '''A user has clicked the login button.'''

        # Shouldn't be able to see the available quizzes without logging in
        rv = self.app.get('/list')
        assert "Available Quizzes" not in rv.data

        self.login()

        # Should be able to see the available quizzes now.
        rv = self.app.get('/list')
        assert "Available Quizzes" in rv.data


if __name__ == '__main__':
    unittest.main()
