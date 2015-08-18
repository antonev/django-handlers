.. Django Handlers documentation master file, created by
   sphinx-quickstart on Sun Aug 16 18:51:24 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Handlers documentation!
=========================================

This library makes it possible to have many views
associated with one URL (separate view for each
HTTP method). It can be used for creation of REST APIs
or just for simplification of views in a Django application.

So, instead of writing this::
    
    # views.py

    def records_view(request):
        if request.method == 'GET':
            records = Record.objects.all()
            return JsonResponse({
                'records': [record.data for record in records]
            })

        if request.method == 'POST':
            form = RecordForm(json.loads(request.body))

            if form.is_valid():
                record = form.save()
                return JsonResponse(record.data)
            else:
                return JsonResponse(form.errors, status_code=422)

        return HttpResponseNotAllowed(['GET', 'POST'])


    # urls.py

    from .views import records_view

    urlpatterns = [''
        (r'^records/$', records_view),
    ]


you can write this::
    
    # views.py

    from django_handlers import Handler

    handler = Handler()


    @handler.get('records')
    def view_records(request):
        records = Record.objects.all()
        return JsonResponse({
            'records': [record.data for record in records]
        })


    @handler.post('records')
    def add_record(request):
        form = RecordForm(json.loads(request.body))

        if form.is_valid():
            record = form.save()
            return JsonResponse(record.data)
        
        return JsonResponse(form.errors, status_code=422)


    # urls.py

    from .views import handler

    urlpatterns = [''
        (r'^records/$', handler.records),
    ]



Contents
========

.. toctree::
    :maxdepth: 2

    tutorial
    api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

