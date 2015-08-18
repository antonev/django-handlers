.. _tutorial:

Getting Started with Django Handlers
====================================


Introduction
------------

Let's imagine that we have a django application and we want
to create REST API for it.

Our API should have two urls:

- /records/ for GET and POST requests
- /records/{record_id}/ for GET, PUT, and DELETE requests


Installation
------------

Firstly, we need to install django-handlers:

.. code-block:: bash
    
    $ pip install django-handlers


Creating Handler
----------------

It is very simple to create a handler.
The best place for it is our views file::

    from django_handlers import Handler
    
    handler = Handler()


Adding Endpoints
----------------

Let's add a view for handling of GET requests::

    @handler.get('records')
    def view_records(request):
        records = Record.objects.all()
        return JsonResponse({
            'records': [record.data for record in records]
        })


'records' is an endpoint name. Endpoint is a simple callable that delegates
request handling to a view associated with an HTTP method.

Let's add to the same endpoint a view for handling of POST requests::

    @handler.post('records')
    def add_record(request):
        form = RecordForm(json.loads(request.body))

        if form.is_valid():
            record = form.save()
            return JsonResponse(record.data)

        return JsonResponse(form.errors, status_code=422)


Now we have endpoint 'records' with two views.
We can associate the endpoint with an url::

    from .views import handler

    urlpatterns = [
        url(r'^records/$', handler.records),
    ]


Now view_records handles GET requests and add_record handles POST requests
to url '/records/'. Let's add views to another endpoint::

    @handler.get('record')
    def view_record(request, record_id):
        record = get_object_or_404(Record, id=record_id)
        return JsonResponse(record.data)


    @handler.put('record')
    def change_record(request, record_id):
        record = get_object_or_404(Record, id=record_id)
        form = RecordForm(json.loads(request.body), instance=record)

        if not form.is_valid():
            return JsonResponse(form.errors, status_code=422)

        form.save()
        return JsonResponse({})


    @handler.delete('record')
    def delete_record(request, record_id):
        record = get_object_or_404(Record, id=record_id)
        record.delete()
        return JsonResponse({})


    # Note that also views can be added via add_view method:

    # handler.add_view('get', 'record', view_record)
    # handler.add_view('put', 'record', change_record)
    # handler.add_view('delete', 'record', delete_record)


We should add new url and associate endpoint 'record' with it:

.. code-block:: python
    :emphasize-lines: 3

    urlapatterns = [
        url(r'^records/$', handler.records),
        url(r'^records/(\d+)/$', handler.record),
    ]


Adding Hooks
------------

You might notice that our views have some code duplication.
We can decrease it by using hooks::

    @handler.before('record')
    def before_record(request, record_id):
        request.record = get_object_or_404(Record, id=record_id)


    @handler.get('record')
    def view_record(request, record_id):
        return JsonResponse(request.record.data)


    @handler.put('record')
    def change_record(request, record_id):
        form = RecordForm(json.loads(request.body), instance=request.record)

        if not form.is_valid():
            return JsonResponse(form.errors, status_code=422)

        form.save()
        return JsonResponse({})


    @handler.delete('record')
    def delete_record(request, record_id):
        request.record.delete()
        return JsonResponse({})


Now before_record will be called before each view of endpoint 'record'.
Also you can add hook to be called after each view of specified endpoint::

    @handler.after('record')
    def after_record(request, record_id):
        do_something()


Using Decorators
----------------

Of course, you can decorate you views but sometimes it is not enough
(for example, in case of csrf_exempt) and you want to decorate your endpoints.

To decorate all handler endpoints you can pass decorators
via argument for \_\_init\_\_ method::

    handler = Handler(decorators=[csrf_exempt, my_decorator])


To decorate specific endpoint you can use decorate method::

    handler.decorate('something', my_decorator)
    handler.decorate('something', [csrf_exempt, my_decorator])
