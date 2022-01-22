=====
Django Generic Search
=====

Django Generic Search is a Django app to conduct generic search on your site's pages. Visitors on your site can search for any
available pages on your side given they new or can guess accurately keywords or search queries related to thos pages.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "django-generic-search" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'generic-search',
    ]

2. Include the django-generic-search URLconf in your project urls.py like this::

    path('search/', include('generic-search.urls')),

3. include settings below in project settings.py

    ALLOWED_HOSTS = [
        'localhost',
    ]

    SPYDER_START_URLS = {
        'gammaspider': ['https://localhost:8000/']
    }

    When in production, update the settings above appropriately to reflect your production environment.

4. Run ``python manage.py crawlsite`` to create an index of the available pages on your site.

5. Start the development server and visit http://127.0.0.1:8000/

6. Visit http://127.0.0.1:8000/search/?q=<search-query> to retrieve search results.