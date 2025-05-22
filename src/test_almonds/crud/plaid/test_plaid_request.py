from uuid import uuid4

from almonds.crud.plaid.request import create_request, get_requests_by_user_id
from almonds.schemas.plaid.request import RequestBase


def test_create_and_get_requests_by_user(sessionmaker_test):
    user_id = uuid4()
    other_user_id = uuid4()

    req1 = RequestBase(
        request_id="req_1",
        user_id=user_id,
        call="endpoint1",
    )
    req2 = RequestBase(
        request_id="req_2",
        user_id=user_id,
        call="endpoint2",
    )
    req3 = RequestBase(
        request_id="req_3",
        user_id=other_user_id,
        call="endpoint3",
    )

    create_request(req1, sessionmaker=sessionmaker_test)
    create_request(req2, sessionmaker=sessionmaker_test)
    create_request(req3, sessionmaker=sessionmaker_test)

    # Get requests for user_id
    requests = get_requests_by_user_id(user_id, sessionmaker=sessionmaker_test)
    assert len(requests) == 2
    ids = {request.request_id for request in requests}
    assert ids == {"req_1", "req_2"}
    assert all(request.user_id == user_id for request in requests)
    assert all(request.created_at is not None for request in requests)

    # Get requests for other_user_id
    requests_other = get_requests_by_user_id(
        other_user_id, sessionmaker=sessionmaker_test
    )
    assert len(requests_other) == 1
    assert requests_other[0].request_id == "req_3"
    assert requests_other[0].user_id == other_user_id


def test_get_requests_by_user_id_empty(sessionmaker_test):
    user_id = uuid4()
    requests = get_requests_by_user_id(user_id, sessionmaker=sessionmaker_test)
    assert requests == []
