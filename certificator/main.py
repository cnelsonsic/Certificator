
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

from flask import Flask
from .models import *

def create_app(config_filename=None):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename or 'config.py')

    from .db import db
    db.init_app(app)
    db.app = app

    db.create_all()

    # from .views import dashboard
    # app.register_blueprint(dashboard)

    return app

def main():
    app = create_app()
    app.run()

if __name__ == '__main__':
    main()
