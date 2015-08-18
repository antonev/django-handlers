from functools import wraps

import pytest
from django.http import HttpResponse


@pytest.mark.parametrize('method', [
    'get',
    'head',
    'options',
    'post',
    'put',
    'patch',
    'delete',
])
def test_method(rf, method):
    from django_handlers import Handler

    handler = Handler()

    @handler.get('something')
    def get(request):
        return HttpResponse('get')

    @handler.head('something')
    def head(request):
        return HttpResponse('head')

    @handler.options('something')
    def options(request):
        return HttpResponse('options')

    @handler.post('something')
    def post(request):
        return HttpResponse('post')

    @handler.put('something')
    def put(request):
        return HttpResponse('put')

    @handler.patch('something')
    def patch(request):
        return HttpResponse('patch')

    @handler.delete('something')
    def delete(request):
        return HttpResponse('delete')

    request = getattr(rf, method)('/something')
    response = handler.something(request)
    assert response.content.decode('utf-8') == method


@pytest.mark.parametrize('method, status_code', [
    ('get', 200),
    ('post', 405),
    ('put', 200),
    ('delete', 405),
])
def test_method_not_allowed(rf, method, status_code):
    from django_handlers import Handler

    handler = Handler()

    @handler.get('something')
    def get_something(request):
        return HttpResponse()

    @handler.put('something')
    def post_something(request):
        return HttpResponse()

    request = getattr(rf, method)('/something')
    response = handler.something(request)
    assert response.status_code == status_code


def test_arguments(rf):
    from django_handlers import Handler

    handler = Handler()

    @handler.get('add')
    def add(request, x, y):
        return HttpResponse(str(int(x) + int(y)))

    request = rf.get('/add/5/2')
    response = handler.add(request, '5', '2')
    assert response.content.decode('utf-8') == '7'


@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize('endpoint_name, expected_calls', [
    ('hooked', ['hook', 'view']),
    ('skipped', ['view']),
])
def test_before(rf, method, endpoint_name, expected_calls):
    from django_handlers import Handler

    handler = Handler()
    calls = []

    @handler.before('hooked')
    def hook(request):
        calls.append('hook')

    @handler.get('hooked')
    def get_hooked(request):
        calls.append('view')
        return HttpResponse()

    @handler.post('hooked')
    def post_hooked(request):
        calls.append('view')
        return HttpResponse()

    @handler.get('skipped')
    def get_skipped(request):
        calls.append('view')
        return HttpResponse()

    @handler.post('skipped')
    def post_skipped(request):
        calls.append('view')
        return HttpResponse()

    request = getattr(rf, method)('/something')
    getattr(handler, endpoint_name)(request)
    assert calls == expected_calls


@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize('endpoint_name', ['endpoint1', 'endpoint2'])
def test_before_all(rf, method, endpoint_name):
    from django_handlers import Handler

    handler = Handler()
    calls = []

    @handler.before
    def hook(request):
        calls.append('hook')

    @handler.get('endpoint1')
    def get1(request):
        calls.append('view')
        return HttpResponse()

    @handler.post('endpoint1')
    def post1(request):
        calls.append('view')
        return HttpResponse()

    @handler.get('endpoint2')
    def get2(request):
        calls.append('view')
        return HttpResponse()

    @handler.post('endpoint2')
    def post2(request):
        calls.append('view')
        return HttpResponse()

    request = getattr(rf, method)('/something')
    getattr(handler, endpoint_name)(request)
    assert calls == ['hook', 'view']


@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize('endpoint_name, expected_calls', [
    ('hooked', ['view', 'hook']),
    ('skipped', ['view']),
])
def test_after(rf, method, endpoint_name, expected_calls):
    from django_handlers import Handler

    handler = Handler()
    calls = []

    @handler.after('hooked')
    def hook(endpoint_name):
        calls.append('hook')

    @handler.get('hooked')
    def get_hooked(request):
        calls.append('view')
        return HttpResponse()

    @handler.post('hooked')
    def post_hooked(request):
        calls.append('view')
        return HttpResponse()

    @handler.get('skipped')
    def get_skipped(request):
        calls.append('view')
        return HttpResponse()

    @handler.post('skipped')
    def post_skipped(request):
        calls.append('view')
        return HttpResponse()

    request = getattr(rf, method)('/something')
    getattr(handler, endpoint_name)(request)
    assert calls == expected_calls


@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize('endpoint_name', ['endpoint1', 'endpoint2'])
def test_after_all(rf, method, endpoint_name):
    from django_handlers import Handler

    handler = Handler()
    calls = []

    @handler.after
    def hook(endpoint_name):
        calls.append('hook')

    @handler.get('endpoint1')
    def get1(request):
        calls.append('view')
        return HttpResponse()

    @handler.post('endpoint1')
    def post1(request):
        calls.append('view')
        return HttpResponse()

    @handler.get('endpoint2')
    def get2(request):
        calls.append('view')
        return HttpResponse()

    @handler.post('endpoint2')
    def post2(request):
        calls.append('view')
        return HttpResponse()

    request = getattr(rf, method)('/something')
    getattr(handler, endpoint_name)(request)
    assert calls == ['view', 'hook']


@pytest.mark.parametrize('endpoint_name', ['endpoint1', 'endpoint2'])
def test_decorators(rf, endpoint_name):
    from django_handlers import Handler

    calls = []

    def decorator1(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            calls.append('decorator1')
            return view(*args, **kwargs)
        return wrapper

    def decorator2(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            calls.append('decorator2')
            return view(*args, **kwargs)
        return wrapper

    decorators = [decorator1, decorator2]
    handler = Handler(decorators=decorators)

    @handler.get('endpoint1')
    def get1(request):
        return HttpResponse()

    @handler.get('endpoint2')
    def get2(request):
        return HttpResponse()

    request = rf.get('/something')
    getattr(handler, endpoint_name)(request)

    assert calls == ['decorator1', 'decorator2']


@pytest.mark.parametrize('endpoint_name, decorated, decorator_called', [
    ('endpoint1', 'endpoint1', True),
    ('endpoint1', 'endpoint2', False),
    ('endpoint2', 'endpoint2', True),
    ('endpoint2', 'endpoint1', False),
])
def test_decorate(rf, endpoint_name, decorated, decorator_called):
    from django_handlers import Handler

    handler = Handler()

    @handler.get('endpoint1')
    def get1(request):
        return HttpResponse()

    @handler.get('endpoint2')
    def get2(request):
        return HttpResponse()

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            decorator.is_called = True
            return view(*args, **kwargs)
        return wrapper

    decorator.is_called = False

    handler.decorate(decorated, decorator)
    request = rf.get('/something')
    getattr(handler, endpoint_name)(request)
    assert decorator.is_called is decorator_called


@pytest.mark.parametrize('endpoint_name, decorated, expected_calls', [
    ('endpoint1', 'endpoint1', ['decorator1', 'decorator2']),
    ('endpoint1', 'endpoint2', []),
    ('endpoint2', 'endpoint2', ['decorator1', 'decorator2']),
    ('endpoint2', 'endpoint1', []),
])
def test_decorate_with_many(rf, endpoint_name, decorated, expected_calls):
    from django_handlers import Handler

    handler = Handler()
    calls = []

    @handler.get('endpoint1')
    def get1(request):
        return HttpResponse()

    @handler.get('endpoint2')
    def get2(request):
        return HttpResponse()

    def decorator1(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            calls.append('decorator1')
            return view(*args, **kwargs)
        return wrapper

    def decorator2(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            calls.append('decorator2')
            return view(*args, **kwargs)
        return wrapper

    handler.decorate(decorated, [decorator1, decorator2])
    request = rf.get('/something')
    getattr(handler, endpoint_name)(request)
    assert calls == expected_calls


@pytest.mark.parametrize('endpoint_name', [
    'add_view',
    'head',
    'get',
    'post',
    'put',
    'delete',
    'before',
    'add_pre_hook',
    'after',
    'add_post_hook',
    'decorate'
])
def test_invalid_endpoint(endpoint_name):
    from django_handlers import Handler

    handler = Handler()

    with pytest.raises(ValueError):
        @handler.get(endpoint_name)
        def view(request):
            return HttpResponse()
