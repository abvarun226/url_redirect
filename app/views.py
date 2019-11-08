from flask import render_template, redirect, request, url_for, session, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, login_required, login_user, \
    logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from app import app, db, models, login_manager
from config import Auth
from .models import User, im_data
import os, datetime, json


@app.route('/status')
def status():
    return 'Status OK'


""" OAuth Session creation """
def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)


@app.route('/gCallback')
def callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            email_domain = email.split('@')[1]
            if app.config['OAUTH_EMAIL_DOMAIN'] != email_domain:
                return 'Email domain does not have access!'
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            print(token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            user.is_active = True
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
""" OAuth Session creation """


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'myname': current_user.name}
    return render_template('index.html', title='Home', user=user)


@app.route('/getEntries', methods=['GET'])
@login_required
def get_entries():
    user_type = request.args.get('type')
    user_email = current_user.email
    user_name = user_email.split('@')[0]
    if user_type == 'all':
        db_result = models.im_data.query.all()
    else:
        db_result = models.im_data.query.filter_by(user_id=user_name).all()
    result = []
    for rows in db_result:
        if rows.share == False and user_name != rows.user_id:
            continue
        temp = {
            "url_name": rows.url_name,
            "full_url": rows.url,
            "user_id": rows.user_id,
            "share": rows.share
        }
        result.append(temp)
    return jsonify(result), 200


@app.route('/getEntriesSSP', methods=['GET'])
@login_required
def get_entries_ssp():
    user_type = request.args.get('type')
    dt_draw = request.args.get('draw', 0)
    dt_start = request.args.get('start', 0)
    dt_length = request.args.get('length', 10)
    dt_search = request.args.get('search[value]', '')
    dt_search_regex = request.args.get('search[regex]', False)
    dt_order_col = request.args.get('order[0][column]', 0)
    dt_order_dir = request.args.get('order[0][dir]', 'asc')
    user_email = current_user.email
    user_name = user_email.split('@')[0]
    dt_length = int(dt_length)
    dt_start = int(dt_start)
    dt_order_col = int(dt_order_col)
    if dt_search != '':
        dt_search = "%" + dt_search + "%"
    column_list = [models.im_data.url_name, models.im_data.user_id, models.im_data.url]
    filtered_count = 0
    if user_type == 'all':
        total_count = models.im_data.query.count()
        if dt_search == '':
            if dt_order_dir == 'asc':
                db_result = models.im_data.query.order_by(column_list[dt_order_col]
                    ).limit(dt_length
                    ).offset(dt_start).all()
            else:
                db_result = models.im_data.query.order_by(column_list[dt_order_col].desc()
                    ).limit(dt_length
                    ).offset(dt_start
                    ).all()
            filtered_count = total_count
        else:
            filtered_count = models.im_data.query.filter(or_(models.im_data.url_name == dt_search, models.im_data.url == dt_search, models.im_data.user_id == dt_search)).count()
            if dt_order_dir == 'asc':
                db_result = models.im_data.query.filter(
                    or_(
                        models.im_data.url_name.like(dt_search),
                        models.im_data.url.like(dt_search),
                        models.im_data.user_id.like(dt_search))
                    ).order_by(column_list[dt_order_col]
                    ).limit(dt_length
                    ).offset(dt_start
                    ).all()
            else:
                db_result = models.im_data.query.filter(
                    or_(
                        models.im_data.url_name.like(dt_search),
                        models.im_data.url.like(dt_search),
                        models.im_data.user_id.like(dt_search))
                    ).order_by(column_list[dt_order_col].desc()
                    ).limit(dt_length
                    ).offset(dt_start
                    ).all()
    result = {'data' : []}
    for rows in db_result:
        if rows.share == False and user_name != rows.user_id:
            continue
        temp = {
            'DT_RowId': rows.id,
            'url_name': '<a href="/' + str(rows.url_name) + '" target="_blank" id="dtrow_' + str(rows.id) + '">' + str(rows.url_name) + '</a>',
            'user_id': rows.user_id,
            'full_url': rows.url,
            'share': rows.share
        }
        result['data'].append(temp)
    result['recordsFiltered'] = filtered_count
    result['recordsTotal'] = total_count
    result['draw'] = dt_draw
    return jsonify(result), 200


@app.route('/postEntry', methods=['POST'])
@login_required
def post_entry():
    user_email = current_user.email
    content = request.form
    if 'urlname' not in content or 'fullurl' not in content or 'share' not in content or 'action' not in content:
        return jsonify(status=400, message='Parameters missing'), 400
    url_name = content['urlname']
    full_url = content['fullurl']
    share = content['share']
    action = content['action']
    if url_name == '' or full_url == '' or share == '' or action == '':
        return jsonify(status=400, message='Parameters missing'), 400
    if share == 'true' or share == True:
        share = True
    else:
        share = False
    user_name = user_email.split('@')[0]
    check_url_name = models.im_data.query.filter_by(url_name=url_name).first()
    req_status = 500
    req_msg = 'Something went wrong'
    if check_url_name is None:
        new_data = models.im_data(
            url_name=url_name,
            url=full_url,
            create_time=datetime.datetime.now(),
            update_time=datetime.datetime.now(),
            user_id=user_name,
            share=share,
            hits=0
        )
        db.session.add(new_data)
        db.session.commit()
        req_status = 200
        req_msg = 'Success'
    elif action == 'update':
        if user_name == check_url_name.user_id:
            check_url_name.url = full_url
            check_url_name.update_time=datetime.datetime.now()
            check_url_name.share=share
            db.session.commit()
            req_status = 201
            req_msg = 'Updated'
        else:
            req_status = 403
            req_msg = 'You do not have permission to update this entry'
    elif action == 'create':
        req_status = 400
        req_msg = 'URL Name already exists'
    return jsonify(status=req_status, message=req_msg), req_status


@app.route('/delEntry', methods=['GET'])
@login_required
def delete_entry():
    user_email = current_user.email
    user_name = user_email.split('@')[0]
    url_name = request.args.get('name', '')
    if url_name == '':
        return jsonify(status=400, message='Parameters missing'), 400
    row = models.im_data.query.filter_by(url_name=url_name).first()
    if row.user_id == user_name:
        db.session.delete(row)
        db.session.commit()
        req_msg = "Deleted"
        req_status = 200
    else:
        req_msg = "You do not have permission to delete this entry"
        req_status = 403
    return jsonify(status=req_status, message=req_msg), req_status


@app.route('/getEntry', methods=['GET'])
@login_required
def get_entry():
    url_name = request.args.get('name', '')
    if url_name == '':
        return jsonify(status=400, message='Parameters missing'), 400
    row = models.im_data.query.filter_by(url_name=url_name).first()
    temp = {
        'url_name': row.url_name,
        'full_url': row.url,
        'share': row.share
    }
    result = [temp]
    return jsonify(result), 200


def hit_metrics(url_name):
    row = models.im_data.query.filter_by(url_name=url_name).first()
    row.hits += 1
    db.session.commit()


@app.route('/<url_name>', methods=['GET'])
def router(url_name):
    if url_name == 'favicon.ico':
        return 'Not Found', 404
    url_list = models.im_data.query.filter_by(url_name=url_name).first()
    if url_list is None:
        return redirect(url_for('index'))
    url_redirect = url_list.url
    if url_redirect == '':
        return redirect(url_for('index'))
    try:
        hit_metrics(url_name)
    except:
        print('Error storing HIT metric')
        pass
    return redirect(url_redirect)
