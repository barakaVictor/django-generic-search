=======================
Django Generic Search
=======================

Django Generic Search is a Django app to conduct generic search on your site's pages. Visitors on your site can search for any
available pages on your side given they new or can guess accurately keywords or search queries related to thos pages.

The app uses the page title and meta name and meta description html tags to generate search results so be sure to include
this tags in your html page templates.

The application is currently not optimized for sites that result in large amounts of data upon crawling.

For a better experience, this app can be used together with ``django-robots`` and the django sitemaps framework.

Quick start
-----------

Install the package using ``pip``.

.. code-block:: sh

	$ pip install django-generic-search

Add ``generic-search`` to your ``INSTALLED_APPS`` setting like this

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'generic-search',
    ]

Include the ``generic-search`` URLconf in your project urls.py like this

.. code-block:: python

    path('search/', include('generic-search.urls')),

Create a html form and point its action attribute to the above url as below

.. code-block:: HTML

    <form method="GET" action="{% url 'search:general_search' %}">
        <input type="text" name="q" placeholder="Search...">
        <button type="submit" class="btn btn-outline-primary custom-inline-button">Go</button>
    </form>

include settings below in project ``settings.py``

.. code-block:: python

    ALLOWED_HOSTS = [
        'localhost',
    ]
    SPYDER_START_URLS = {
        'gammaspider': ['https://localhost:8000/']
    }

When in production, update the settings above appropriately to reflect your production environment.

Override the default template used to display the search index and search results page to reflect the theme of
your site by creating a templates directory in your project root directory. In the created templates directory,
create a directory with the name ``generic_search`` and place index.html in it. You can copy the template provided in the
package to the path created above to get a full picture of the available blocks that can be overriden.

Start the development server and visit http://127.0.0.1:8000/

On a new terminal, run the commands below.

Run ``python manage.py crawlsite`` to generate data about available pages on your site.
Run ``python manage.py cleancrawlresults`` to prepare the data for indexing.
Run ``python manage.py indexsite`` to generate an index file for the data.

Visit http://127.0.0.1:8000/<url as apecified in your url conf>/?q=<search-query> to search.
