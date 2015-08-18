from itertools import chain

from collections import (
    defaultdict,
    Iterable,
)

from django.http import HttpResponseNotAllowed


__version__ = '0.1.0'


class Handler(object):
    """Container for views.

    :param decorators: (optional) list of decorators that will be applied
        to each endpoint.
    """

    def __init__(self, decorators=None):
        self._decorators = decorators or []
        self._views = defaultdict(dict)
        self._pre_hooks = defaultdict(list)
        self._post_hooks = defaultdict(list)
        self._invalid_endpoint_names = dir(self)

    def add_view(self, method, endpoint_name, view):
        """Adds a view to handler.

        :param method: HTTP method to be handled by the view
        :param endpoint_name: name of endpoint to associate the view with
        :param view: function to be used for requests handling
        """

        self._ensure_endpoint_exists(endpoint_name)
        self._views[endpoint_name][method.upper()] = view

    def _ensure_endpoint_exists(self, endpoint_name):
        self._validate_endpoint_name(endpoint_name)

        if endpoint_name not in self._views:
            self._add_endpoint(endpoint_name)

    def _validate_endpoint_name(self, endpoint_name):
        if endpoint_name in self._invalid_endpoint_names:
            raise ValueError('Invalid endpoint name {}'.format(endpoint_name))

    def _add_endpoint(self, endpoint_name):
        def endpoint(request, *args, **kwargs):
            for hook in self._get_pre_hooks(endpoint_name):
                hook(request, *args, **kwargs)

            try:
                view = self._views[endpoint_name][request.method]
            except KeyError:
                allowed_methods = self._views[endpoint_name].keys()
                response = HttpResponseNotAllowed(allowed_methods)
            else:
                response = view(request, *args, **kwargs)

            for hook in self._get_post_hooks(endpoint_name):
                hook(request, *args, **kwargs)

            return response

        for decorator in reversed(self._decorators):
            endpoint = decorator(endpoint)

        setattr(self, endpoint_name, endpoint)

    def _get_pre_hooks(self, endpoint_name):
        return chain(self._pre_hooks[None], self._pre_hooks[endpoint_name])

    def _get_post_hooks(self, endpoint_name):
        return chain(self._post_hooks[None], self._post_hooks[endpoint_name])

    def _register(self, method, endpoint_name):
        def decorator(view):
            self.add_view(method, endpoint_name, view)
            return view
        return decorator

    def get(self, endpoint_name):
        """Decorates a view to use it for handling of GET requests.

        :param endpoint_name: name of endpoint for given view.
        """
        return self._register('GET', endpoint_name)

    def head(self, endpoint_name):
        """Decorates a view to use it for handling of HEAD requests.

        :param endpoint_name: name of endpoint for given view.
        """

        return self._register('HEAD', endpoint_name)

    def options(self, endpoint_name):
        """Decorates a view to use it for handling of OPTIONS requests.

        :param endpoint_name: name of endpoint for given view.
        """

        return self._register('OPTIONS', endpoint_name)

    def post(self, endpoint_name):
        """Decorates a view to use it for handling of POST requests.

        :param endpoint_name: name of endpoint`.
        """

        return self._register('POST', endpoint_name)

    def put(self, endpoint_name):
        """Decorates a view to use it for handling of PUT requests.

        :param endpoint_name: name of endpoint.
        """

        return self._register('PUT', endpoint_name)

    def patch(self, endpoint_name):
        """Decorates a view to use it for handling of PATCH requests.

        :param endpoint_name: name of endpoint.
        """

        return self._register('PATCH', endpoint_name)

    def delete(self, endpoint_name):
        """Decorates a view to use it for handling of DELETE requests.

        :param endpoint_name: name of endpoint.
        """

        return self._register('DELETE', endpoint_name)

    def before(self, target):
        """Decorates a function to call it before views.

        :param target: (optional) name of endpoint. Without it the
            hook will be added for all endpoints.
        """
        if callable(target):
            endpoint_name = None
        else:
            endpoint_name = target

        def decorator(view):
            self.add_pre_hook(endpoint_name, view)
            return view

        if endpoint_name is None:
            return decorator(target)

        return decorator

    def add_pre_hook(self, endpoint_name, hook):
        """Adds a function to call it before endpoint's views.

        :param endpoint_name: name of handler endpoint
        :param hook: function that should be called after endpoint's views
        """
        self._pre_hooks[endpoint_name].append(hook)

    def after(self, target):
        """Decorates a function to call it after views.

        :param target: (optional) name of endpoint. Without it the
            hook will be added for all endpoints.
        """
        if callable(target):
            endpoint_name = None
        else:
            endpoint_name = target

        def decorator(view):
            self.add_post_hook(endpoint_name, view)
            return view

        if endpoint_name is None:
            return decorator(target)

        return decorator

    def add_post_hook(self, endpoint_name, hook):
        """Adds a function to call it after endpoint's views.

        :param endpoint_name: name of handler endpoint
        :param hook: function that should be called after endpoint's views
        """
        self._post_hooks[endpoint_name].append(hook)

    def decorate(self, endpoint_name, decorator):
        """Decorates an endpoint.

        :param endpoint_name: an endpoint to decorate.
        :param decorator: one decorator or iterable with decorators.
        """
        endpoint = getattr(self, endpoint_name)

        if isinstance(decorator, Iterable):
            for dec in reversed(decorator):
                endpoint = dec(endpoint)
        else:
            endpoint = decorator(endpoint)

        setattr(self, endpoint_name, endpoint)
