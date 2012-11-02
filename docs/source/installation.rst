Installation
============

1. Create a local\_settings.py that contains any values you want to
   override from settings.py.

2. Install your dependencies:

   $ pip install -r pip-requirements

3. $ ./manage.py syncdb --migrate

4. Go nuts.

The default settings use sqlite3 as the database, with
/path/to/spiff/spiff.sqlite3 as the file.

Apache
------

This section is included as an example to get Spiff and Apache to work
together in harmony. It is more or less exactly how we run things at
synhak.org

First, decide where you're going to serve up spiff. Keep in mind: this
URL should probably never ever ever change in your space's lifetime. QR
codes, hardware sensors, door swipes, and whatever else you have talking
to Spiff will need reconfigured if things ever move. We run our instance
at http://synhak.org/auth/

Our git clone of Spiff is located in /usr/share/spiff/.

$ git clone git://github.com/SYNHAK/spiff.git /usr/share/spiff/ $ cd
/usr/share/spiff/ *Configure your local\_settings.py here* $ ./manage.py
syncdb --migrate

In /etc/httpd/conf.d/synhak.org.conf:

::

    <VirtualHost *:80>
      LoadModule wsgi_module modules/mod_wsgi.so
      WSGIScriptAliasMatch ^/auth(/([^~].*)?)$ /usr/share/spiff/spiff/wsgi.py$1
      Alias /auth/static /usr/share/spiff/spiff/static
      WSGIPassAuthorization On
      WSGIDaemonProcess spiff-1 user=apache group=apache threads=25
      WSGIProcessGroup spiff-1
    </VirtualHost>

That is all you need. You may then access spiff at
http://your-space.org/auth/


