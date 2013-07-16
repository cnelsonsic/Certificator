
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

from flask import Blueprint, render_template, request, abort, redirect

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

@root.route('/')
def do_index():
    # If logged in, redirect to dashboard
    # If not logged in, redirect to onboarding
    return redirect("/signup")


@root.route('/signup')
def do_signup():
    return render_template('signup.html')

quiz = Blueprint('quiz', __name__)

def parse_quiz(quizname):
    try:
        with open('data/'+quizname) as f:
            quiz_data = f.readlines()
    except (IOError):
        abort(404)

    questions = dict()
    params = dict(quiz_id=quizname)
    current_question = None
    for line in quiz_data:
        if line.startswith("Title:"):
            params['quiz_name'] = line.replace("Title:", "").strip()
        elif line.startswith("Description:"):
            params['description'] = line.replace("Description:", "").strip()
        elif line.startswith("Q:"):
            current_question = line.replace("Q:", "").strip()
            questions[current_question] = dict()
            questions[current_question]['answers'] = list()
            questions[current_question]['id'] = len(questions)

        elif line.startswith("A:") or line.startswith("A*:"):
            answer = line.replace("A:", "").replace("A*:", "").strip()
            questions[current_question]['answers'].append(answer)
            if line.startswith("A*:"):
                questions[current_question]['correct'] = answer

    return questions, params


@quiz.route('/quiz/<quizname>')
def do_quiz(quizname):
    questions, addtl = parse_quiz(quizname)
    return render_template('quiz.html', questions=questions, **addtl)

@quiz.route('/check/', methods=['POST'])
def do_check():
    questions, addtl = parse_quiz(request.form['quiz_id'])

    results = dict()
    for idnum, question in enumerate(questions):
        their_answer = request.form[str(idnum + 1)]
        right_answer = questions[question]['correct']
        if their_answer == right_answer:
            results[idnum + 1] = True
        else:
            results[idnum + 1] = False

    percentage = (float(len([i for i in results if results[i] is True])) / float(len(results)))

    return render_template('check.html', results=results,
                                         questions=questions,
                                         quiz_name=addtl['quiz_name'],
                                         percentage=percentage)
