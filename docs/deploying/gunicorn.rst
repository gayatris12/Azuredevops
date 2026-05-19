Gunicorn
========

`Gunicorn`_ is a pure Python WSGI server with simple configuration and
multiple worker implementations for performance tuning.

*   It tends to integrate easily with hosting platforms.
*   It does not support Windows (but does run on WSL).
*   It is easy to install as it does not require additional dependencies
    or compilation.
*   It has built-in async worker support using gevent.

This page outlines the basics of running Gunicorn. Be sure to read its
`documentation`_ and use ``gunicorn --help`` to understand what features
are available.

.. _Gunicorn: https://gunicorn.org/
.. _documentation: https://docs.gunicorn.org/


Installing
----------

Gunicorn is easy to install, as it does not require external
dependencies or compilation. It runs on Windows only under WSL.

Create a virtualenv, install your application, then install
``gunicorn``.

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # install your application
    $ pip install gunicorn


Running
-------

The only required argument to Gunicorn tells it how to load your Flask
application. The syntax is ``{module_import}:{app_variable}``.
``module_import`` is the dotted import name to the module with your
application. ``app_variable`` is the variable with the application. It
can also be a function call (with any arguments) if you're using the
app factory pattern.

.. code-block:: text

    # equivalent to 'from hello import app'
    $ gunicorn -w 4 'hello:app'

    # equivalent to 'from hello import create_app; create_app()'
    $ gunicorn -w 4 'hello:create_app()'

    Starting gunicorn 20.1.0
    Listening at: http://127.0.0.1:8000 (x)
    Using worker: sync
    Booting worker with pid: x
    Booting worker with pid: x
    Booting worker with pid: x
    Booting worker with pid: x

The ``-w`` option specifies the number of processes to run; a starting
value could be ``CPU * 2``. The default is only 1 worker, which is
probably not what you want for the default worker type.

Logs for each request aren't shown by default, only worker info and
errors are shown. To show access logs on stdout, use the
``--access-logfile=-`` option.


Configuration File
------------------

While passing arguments to Gunicorn via the command line is useful for simple 
setups, production deployments usually rely on a configuration file. 

Create a file named ``gunicorn.conf.py`` in your project directory:

.. code-block:: python

    # gunicorn.conf.py
    bind = "127.0.0.1:8000"
    workers = 4
    accesslog = "-"

You can then run Gunicorn by pointing it to your configuration file using 
the ``-c`` option:

.. code-block:: text

    $ gunicorn -c gunicorn.conf.py 'example:app'


Running in the Background
-------------------------

Running Gunicorn from the command line blocks the terminal. For production 
deployments, you should use a process manager like ``systemd`` or ``supervisor`` 
to run Gunicorn in the background, start it automatically on boot and restart 
it if it crashes. 

See the Gunicorn documentation on `Deploying Gunicorn <https://docs.gunicorn.org/en/latest/deploy.html>`_ 
for examples of systemd service files.


Binding Externally
------------------

Gunicorn should not be run as root because it would cause your
application code to run as root, which is not secure. However, this
means it will not be possible to bind to port 80 or 443. Instead, a
reverse proxy such as :doc:`nginx` or :doc:`apache-httpd` should be used
in front of Gunicorn.

You can bind to all external IPs on a non-privileged port using the
``-b 0.0.0.0`` option. Don't do this when using a reverse proxy setup,
otherwise it will be possible to bypass the proxy.

.. code-block:: text

    $ gunicorn -w 4 -b 0.0.0.0 'hello:create_app()'
    Listening at: http://0.0.0.0:8000 (x)

``0.0.0.0`` is not a valid address to navigate to, you'd use a specific
IP address in your browser.

.. note::
    When running Gunicorn behind a reverse proxy, the proxy will intercept the 
    client's IP address. To ensure your Flask application correctly reads the 
    forwarded headers (like ``X-Forwarded-For``), you must apply the 
    :class:`~werkzeug.middleware.proxy_fix.ProxyFix` middleware. See 
    :doc:`proxy_fix` for more information.


Async with gevent
-----------------

The default sync worker is appropriate for most use cases. If you need numerous,
long running, concurrent connections, Gunicorn provides an asynchronous worker
using `gevent`_. This is not the same as Python's ``async/await``, or the ASGI
server spec. See :doc:`/gevent` for more information about enabling it in your
application.

.. _gevent: https://www.gevent.org/

When using gevent, greenlet>=1.0 is required. When using PyPy, PyPy>=7.3.7 is
required.

.. code-block:: text

    $ gunicorn -k gevent 'hello:create_app()'
    Starting gunicorn 20.1.0
    Listening at: http://127.0.0.1:8000 (x)
    Using worker: gevent
    Booting worker with pid: x