
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

from flask import Blueprint, render_template, request, abort, redirect, session, flash
from flask.ext.login import login_required

import os
import stripe
stripe_keys = {'secret_key': os.environ['SECRET_KEY'],
               'publishable_key': os.environ['PUBLISHABLE_KEY']
              }
stripe.api_key = stripe_keys['secret_key']

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
    return redirect("/greetings")

@root.route('/greetings')
def do_onboarding():
    if session.get('user_id', False):
        # If logged in, redirect to dashboard
        return redirect("/list")
    else:
        # If not logged in, redirect to onboarding
        return render_template('onboarding.html')

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/list')
@login_required
def do_list():
    import os
    quizzes = {}
    for test in os.listdir('data'):
        print test
        questions, params = parse_quiz(test)
        print questions, params
        quizzes[test] = params
        quizzes[test]['num_questions'] = len(questions)

    from .db import db
    from .models import Result
    results = Result.query.filter_by(user=session["user_id"])\
                          .order_by(Result.percentage.asc())\
                          .all()
    test_results = {}
    for result in results:
        try:
            # If this is higher than anything we've seen before, store it.
            if result.percentage > test_results[result.testname]:
                test_results[result.testname] = result.percentage
        except KeyError:
            pass
        test_results[result.testname] = result

    # TODO: Show what class percentile they achieved

    # Pester them about setting their full name.
    from .db import get_user_by_id
    if not get_user_by_id(session["user_id"]).full_name:
        flash('You should <a href="/account">set your full name.</a> We print it on your Certificates!', 'info')

    return render_template('list.html', quizzes=quizzes, results=test_results)

@dashboard.route('/account', methods=['GET', 'POST'])
@login_required
def do_account():
    from .db import db, get_user_by_id
    user = get_user_by_id(session["user_id"])
    if hasattr(request, 'form'):
        if 'full_name' in request.form:
            full_name = request.form['full_name']
            user.full_name = full_name
            db.session.commit()
            flash('Full Name set to {}. Thanks! <a href="/">'.format(user.full_name))

    return render_template('account.html', user=user)


@dashboard.errorhandler(401)
@dashboard.errorhandler(403)
def gohome(e):
    return redirect("/")

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
@login_required
def do_quiz(quizname):
    questions, addtl = parse_quiz(quizname)
    return render_template('quiz.html', questions=questions, **addtl)

@quiz.route('/check/', methods=['POST'])
@login_required
def do_check():
    quiz_id = request.form['quiz_id']
    questions, addtl = parse_quiz(quiz_id)

    results = dict()
    for idnum, question in enumerate(questions):
        their_answer = request.form[str(idnum + 1)]
        right_answer = questions[question]['correct']
        if their_answer == right_answer:
            results[idnum + 1] = True
        else:
            results[idnum + 1] = False

    percentage = (float(len([i for i in results if results[i] is True])) / float(len(results)))

    from .db import db, get_user_by_id
    from .models import Result
    result = Result(user=get_user_by_id(session["user_id"]),
                    testname=quiz_id,
                    percentage=percentage)
    db.session.add(result)
    db.session.commit()

    # TODO: Add a link back to the dashboard.
    return render_template('check.html', results=results,
                                         questions=questions,
                                         quiz_name=addtl['quiz_name'],
                                         percentage=percentage,
                                         result=result)

certificate = Blueprint('certificate', __name__)

@certificate.route('/certificate/<int:resultid>')
@login_required
def do_certificate(resultid):
    from .db import db, get_user_by_id
    from .models import Result, Certificate

    result = Result.query.filter_by(id=resultid).first()

    user = get_user_by_id(session['user_id'])
    if result.user != user.id:
        # This user doesn't own this certificate.
        return redirect("/")

    if not result.certificate:
        # If cert doesn't exist, insert row into certificates with relevant info
        cert = Certificate(result=result)
        db.session.add(cert)
        db.session.commit()
    else:
        cert = result.certificate

    # Generate certificate.
    cert_html = render_template('certificate.html', cert_name="Certificate of Completion",
                                                    course_name="Monty Python Studies",
                                                    student_name=user.full_name or user.email,
                                                    site_name="Monty Python Academy",
                                                    sub_site_name="Online Campus",
                                                    verbose_date="Thirtieth day of June, Two-Thousand and Thirteen",
                                                    important_people={"John T Johnson": "Headmaster",
                                                                        "Susan Q Winklebottom": "Directress of Student Affairs"},
                                                    cert_id=cert.gid)

    if not cert.purchased:
        # If not purchased yet, redirect to purchase form.
        session['cert_id'] = cert.id
        return render_template('purchase.html', key=stripe_keys['publishable_key'],
                                                desc="Certificate of Completion: Monty Python Studies",
                                                amount=500,
                                                teaser_img="/generated/asdoifjawoiejfasodifja.png")
    elif cert.purchased:
        # If purchased, redirect to page for PDF and high-res PNG download.
        return cert_html


@certificate.route('/charge', methods=['POST'])
@login_required
def charge():
    from .db import db, get_user_by_id
    from .models import Certificate
    if not session.get('cert_id'):
        flash("Something went wrong. Your card was not charged.")
        return redirect("/")

    # Amount in cents
    amount = 500

    try:
        customer = stripe.Customer.create(
            email=get_user_by_id(session["user_id"]).email,
            card=request.form['stripeToken']
        )
    except (stripe.InvalidRequestError):
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect("/")

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Certificate of Completion',
    )

    # Set certificate status to purchased.
    cert_id = session['cert_id']
    cert = Certificate.query.filter_by(id=cert_id).first()
    cert.purchased = True
    db.session.add(cert)
    db.session.commit()

    return render_template('charge.html', amount=amount, result_id=cert.result_id)
