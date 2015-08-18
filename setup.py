try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='django-handlers',
    version=__import__('django_handlers').__version__,
    url='https://github.com/antonev/django-handlers',
    license='MIT',
    description='Simple library for creation '
                'of REST APIs with Django',
    author='Anton Evdokimov',
    author_email='antonevv@gmail.com',
    long_description='This library makes it possible to have many views '
                     'associated with one URL (separate view for each '
                     'HTTP method). It can be used for creation of REST APIs '
                     'or just for simplification of views in Django app.',
    py_modules=['django_handlers'],
    install_requires=[],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)
