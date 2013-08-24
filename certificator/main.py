
#    Certificator: Certificates that a person has the skills to pay the bills.
#    Copyright (C) 2013 C Nelson <cnelsonsic@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.browserid import BrowserID
from flask.ext.bootstrap import Bootstrap

import db

from .models import *

def create_app(config_filename=None):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename or 'config.py')
    if 'CERTIFICATOR_SETTINGS' in os.environ:
        # Only try to load a config from it if set.
        app.config.from_envvar('CERTIFICATOR_SETTINGS')

    from .db import get_user_by_id, get_user
    login_manager = LoginManager()
    login_manager.user_loader(get_user_by_id)
    login_manager.init_app(app)

    browser_id = BrowserID()
    browser_id.user_loader(get_user)
    browser_id.init_app(app)

    Bootstrap(app)

    from .db import db as sqla
    from .db import create_tables
    sqla.init_app(app)
    sqla.app = app

    sqla.create_all()

    import stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    from .views import root, quiz, dashboard, certificate
    app.register_blueprint(root)
    app.register_blueprint(quiz)
    app.register_blueprint(dashboard)
    app.register_blueprint(certificate)

    return app

def main():
    app = create_app()
    app.run(host='0.0.0.0', port=5012, debug=True)

if __name__ == '__main__':
    main()
