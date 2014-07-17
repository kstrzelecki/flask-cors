# -*- coding: utf-8 -*-
"""
    test
    ~~~~
    Flask-CORS is a simple extension to Flask allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2014 by Cory Dolphin.
    :license: MIT, see LICENSE for more details.
"""

from tests.base_test import FlaskCorsTestCase
from flask import Flask

try:
    # this is how you would normally import
    from flask.ext.cors import *
except:
    # support local usage without installed package
    from flask_cors import *

class OriginsTestCase(FlaskCorsTestCase):
    def setUp(self):
        self.example_origin = 'http://example.com'
        self.app = Flask(__name__)

        @self.app.route('/')
        @cross_origin()
        def wildcard():
            return 'Welcome!'

        @self.app.route('/test_list')
        @cross_origin(origins=["Foo", "Bar"])
        def test_list():
            return 'Welcome!'

        @self.app.route('/test_string')
        @cross_origin(origins="Foo")
        def test_string():
            return 'Welcome!'

        @self.app.route('/test_set')
        @cross_origin(origins=set(["Foo", "Bar"]))
        def test_set():
            return 'Welcome!'

        @self.app.route('/test_origins_single')
        @cross_origin(origins=["Foo", "Bar", self.example_origin],
                      origins_single=True)
        def test_origins_single():
            return 'Welcome!'

    def test_wildcard_defaults_no_origin(self):
        ''' If there is no Origin header in the request, the
            Access-Control-Allow-Origin header should not be included,
            according to the w3 spec.
        '''
        with self.app.test_client() as c:
            for verb in self.iter_verbs(c):
                result = verb('/')
                self.assertEqual(result.headers.get(ACL_ORIGIN),'*')

    def test_app_configured_origins(self):
        ''' If the application contains a list of origins in the
            `CORS_ORIGINS` config value, then origins should default to them
            instead of '*'
        '''
        app = Flask(__name__)
        app.config['CORS_ORIGINS'] = ['Foo', 'Bar']

        @app.route('/')
        @cross_origin(methods=['GET', 'OPTIONS', 'HEAD', 'PUT', 'POST'])
        def wildcard():
            return 'Welcome!'

        with app.test_client() as c:
            for verb in self.iter_verbs(c):
                result = verb('/')
                self.assertEqual(result.headers.get(ACL_ORIGIN), 'Foo, Bar')

    def test_wildcard_defaults_origin(self):
        ''' If there is no Origin header in the request, the
            Access-Control-Allow-Origin header should be included, if and only
            if the always_send parameter is `True`, which is the default value.
        '''
        with self.app.test_client() as c:
            for verb in self.iter_verbs(c):
                result = verb('/', headers={'Origin': self.example_origin})
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.headers.get(ACL_ORIGIN), '*')

    def test_list_serialized(self):
        ''' If there is an Origin header in the request, the
            Access-Control-Allow-Origin header should be echoed.
        '''
        with self.app.test_client() as c:
            result = c.get('/test_list')
            self.assertEqual(result.headers.get(ACL_ORIGIN), 'Foo, Bar')

    def test_string_serialized(self):
        ''' If there is an Origin header in the request,
            the Access-Control-Allow-Origin header should be echoed back.
        '''
        with self.app.test_client() as c:
            result = c.get('/test_string')
            self.assertEqual(result.headers.get(ACL_ORIGIN), 'Foo')

    def test_set_serialized(self):
        ''' If there is an Origin header in the request,
            the Access-Control-Allow-Origin header should be echoed back.
        '''
        with self.app.test_client() as c:
            result = c.get('/test_set')

            allowed = result.headers.get(ACL_ORIGIN)
            # Order is not garaunteed
            self.assertTrue(allowed == 'Foo, Bar' or allowed == 'Bar, Foo')

    def test_list_single_origin(self):
        ''' If there is an Origin header in the request that fits the allowed
            origins list and origins_single is set, the
            Access-Control-Allow-Origin should be set to the request's Origin
            value.
        '''
        with self.app.test_client() as c:
            result = c.get('/test_origins_single',
                           headers={'Origin': self.example_origin})
            self.assertEqual(result.headers.get(ACL_ORIGIN),
                             self.example_origin)

    def test_app_configured_origins_single(self):
        ''' If `CORS_ORIGINS_SINGLE` config value is set, then origins_single
        option should default to them.
        '''
        app = Flask(__name__)
        app.config['CORS_ORIGINS_SINGLE'] = True

        @app.route('/')
        @cross_origin(origins=[self.example_origin, 'Foo'])
        def wildcard():
            return 'Welcome!'

        with app.test_client() as c:
            result = c.get('/', headers={'Origin': self.example_origin})
            self.assertEqual(result.headers.get(ACL_ORIGIN),
                             self.example_origin)


if __name__ == "__main__":
    unittest.main()
