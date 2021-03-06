import datetime

import requests
from flask import abort, Blueprint, request

from weber_utils import Optional, takes_schema_args

from .api_utils import auto_commit, get_api_decorator, API_SUCCESS
from .utils import get_current_time
from .models import Session, Test, TestMetadata, SessionMetadata, Error, db
from sqlalchemy.orm.exc import NoResultFound

blueprint = Blueprint('api', __name__, url_prefix='/api')

api_func = get_api_decorator(blueprint)

##########################################################################

@api_func
@auto_commit
@takes_schema_args(id=int,
                   name=str,
                   version=Optional(str),
                   revision=Optional(str))
def set_product(id, name, version=None, revision=None):
    update = {'product_name': name, 'product_version': version, 'product_revision': revision}
    if not Session.query.filter(Session.id == id).update(update):
        abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int,
                   user_name=str)
def set_session_user(id, user_name):
    update = {'user_name': user_name}
    if not Session.query.filter(Session.id == id).update(update):
        abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(logical_id=Optional(str),
                   hostname=Optional(str),
                   product_name=Optional(str),
                   product_version=Optional(str),
                   product_revision=Optional(str))
def report_session_start(logical_id=None, hostname=None,
                         product_name=None,
                         product_version=None,
                         product_revision=None):
    if hostname is None:
        hostname = request.remote_addr
    return Session(logical_id=logical_id, hostname=hostname,
                   product_name=product_name, product_version=product_version, product_revision=product_revision)


@api_func
@auto_commit
@takes_schema_args(id=int, duration=Optional((float, int)))
def report_session_end(id, duration=None):
    update = {'end_time': get_current_time() if duration is None else Session.start_time + duration}
    if not Session.query.filter(Session.id == id, Session.end_time == None).update(update):
        if Session.query.filter(Session.id == id).count():
            # we have a session, but it already ended
            abort(requests.codes.conflict)
        else:
            abort(requests.codes.not_found)


@api_func
@auto_commit
@takes_schema_args(session_id=int, name=Optional(str), test_logical_id=Optional(str))
def report_test_start(session_id, name=None, test_logical_id=None):
    try:
        session = Session.query.filter(Session.id == session_id).one()
    except NoResultFound:
        abort(requests.codes.not_found)
    if session.end_time is not None:
        abort(requests.codes.conflict)
    return Test(session_id=session.id, logical_id=test_logical_id, name=name)


@api_func
@auto_commit
@takes_schema_args(id=int, duration=Optional((float, int)))
def report_test_end(id, duration=None):
    update = {'end_time': get_current_time() if duration is None else Test.start_time + duration}
    test = Test.query.get(id)
    if test is None:
        abort(requests.codes.not_found)
    if test.end_time is not None:
        # we have a test, but it already ended
        abort(requests.codes.conflict)

    test.end_time = get_current_time() if duration is None else test.start_time + duration

    session_update = {'num_finished_tests': Session.num_finished_tests + 1}
    if test.num_failures:
        session_update['num_failed_tests'] = Session.num_failed_tests + 1
    elif test.num_errors:
        session_update['num_error_tests'] = Session.num_error_tests + 1
    elif test.skipped:
        session_update['num_skipped_tests'] = Session.num_skipped_tests + 1

    Session.query.filter(Session.id == test.session_id).update(session_update)


@api_func
@auto_commit
@takes_schema_args(id=int)
def report_test_skipped(id):
    update = {'skipped': True}
    if not Test.query.filter(Test.id == id).update(update):
        if Test.query.filter(Test.id == id).count():
            # we have a test, but it already ended
            abort(requests.codes.conflict)
        else:
            abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int)
def report_test_interrupted(id):
    update = {'interrupted': True}
    if not Test.query.filter(Test.id == id).update(update):
        if Test.query.filter(Test.id == id).count():
            # we have a test, but it already ended
            abort(requests.codes.conflict)
        else:
            abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int)
def add_test_error(id):
    try:
        test = Test.query.filter(Test.id == id).one()
        test.num_errors = Test.num_errors + 1
    except NoResultFound:
        abort(requests.codes.not_found)


@api_func
@auto_commit
@takes_schema_args(id=int)
def add_test_failure(id):

    try:
        test = Test.query.filter(Test.id == id).one()
        test.num_failures = Test.num_failures + 1
    except NoResultFound:
        abort(requests.codes.not_found)


@api_func
@auto_commit
@takes_schema_args(id=int, metadata=dict)
def add_test_metadata(id, metadata):

    try:
        test = Test.query.filter(Test.id == id).one()
        test.metadata_objects.append(TestMetadata(metadata_item=metadata))
    except NoResultFound:
        abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int, metadata=dict)
def add_session_metadata(id, metadata):

    try:
        session = Session.query.filter(Session.id == id).one()
        session.metadata_objects.append(SessionMetadata(metadata_item=metadata))
    except NoResultFound:
        abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int, exception=str, exception_type=str, traceback=list, timestamp=Optional((float, int, long)))
def add_test_error_data(id, exception, exception_type, traceback, timestamp=None):
    if timestamp is None:
        timestamp = get_current_time()
    try:
        test = Test.query.filter(Test.id == id).one()
        test.errors.append(Error(exception=exception,
                      exception_type=exception_type,
                      traceback=traceback,
                      timestamp=timestamp))
        test.num_errors = Test.num_errors + 1

    except NoResultFound:
        abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int, exception=str, exception_type=str, traceback=list, timestamp=Optional((float, int, long)))
def add_session_error_data(id, exception, exception_type, traceback, timestamp=None):
    if timestamp is None:
        timestamp = get_current_time()
    try:
        session = Session.query.filter(Session.id == id).one()
        session.errors.append(Error(exception=exception,
                      exception_type=exception_type,
                      traceback=traceback,
                      timestamp=timestamp))

    except NoResultFound:
        abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int,
                   conclusion=str)
def set_test_conclusion(id, conclusion):
    update = {'test_conclusion': conclusion}
    if not Test.query.filter(Test.id == id).update(update):
        abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int,
                   status=str)
def edit_session_status(id, status):
    if status not in ['', 'RUNNING', 'FAILURE', 'SUCCESS']:
        abort(requests.codes.bad_request)
    update = {'edited_status': status}
    if not Session.query.filter(Session.id == id).update(update):
        abort(requests.codes.not_found)

@api_func
@auto_commit
@takes_schema_args(id=int,
                   status=str)
def edit_test_status(id, status):
    if status not in ['', 'RUNNING', 'SUCCESS', 'SKIPPED', 'FAILURE', 'ERROR', 'INTERRUPTED']:
        abort(requests.codes.bad_request)
    update = {'edited_status': status}
    if not Test.query.filter(Test.id == id).update(update):
        abort(requests.codes.not_found)
