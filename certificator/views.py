
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

from flask import Blueprint, jsonify, render_template

root = Blueprint('root', __name__)

@root.route('/favicon.ico')
def do_serve_favicon():
    import os
    from flask import send_from_directory, current_app, request

    ua = request.headers.get('User-Agent')
    if ua and ("Chrome" in ua or "Opera" in ua):
        # favicon = "triops.svg"
        favicon = "favicon.png"
    elif ua and "Firefox" in ua:
        favicon = "favicon.png"
    else:
        favicon = "favicon.ico"

    return send_from_directory(os.path.join(current_app.root_path, 'static'),
                               favicon)

quiz = Blueprint('quiz', __name__)
@quiz.route('/quiz/<quizname>')
def do_quiz(quizname):
    # Populate the page with questions and answers, and a button to submit it.
    questions = {"What is tha airspeed veolicty of an unladen swallow?": dict(answers=["44mph", "88mph", "24mph", "32mph"], id='q1')}
    params = dict(quiz_name=quizname, questions=questions)

    return render_template('quiz.html', quiz_name=quizname, questions=questions)

@quiz.route('/quiz/<quizname>/check')
def do_check(quizname, methods=['POST']):
    # answers = request.form.get('_method', '').upper()

    return render_template('check.html', params=params, alerts=alerts)

