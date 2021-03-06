.. _web-deps:

================
Web dependencies
================

Our site need many depends files - for javascript and css. To make loading faster and at the
same time - not inhibit our work web-depends code was prepared. Most of it you can found in
"*projectksi.core.deps*" module. It is responsible for:

 - `compile less files to css`_
 - `compile coffee files to js`_
 - `minifying, combining and gzip’ing`_ css
 - `minifying, combining and gzip’ing`_ js


Compile less files to css
=========================

Like `LESS official website`_ say - less files can be compile in one of two way:

  - client side (by LESS javascript compiler)
  - server side (by *lessc* tool)

Both are diffrent and both are useful. You can choose way than projectksi LESS is compiling by
set *projectksi.web_deps.less_compiler.side* to *client* or *server* value. To compile LESS
files in server side you need have *lessc* installed. You can found instruction how to do this
on LESS website. On Ubuntu it will:

    sudo apt-get install node-less

.. _`LESS official website`: http://lesscss.org/#-client-side-usage

LESS client side compiling (DEV)
--------------------------------

At client side compiling mode *less* files are directly included in html layout:

.. code-block:: html

    <link rel="stylesheet/less" type="text/css" href="http://localhost/develop-css/test.less">

Add and of the file "*less.min.js*" library will be included. That one will compile all less files
in page load time. In this way after LESS file change server restart is not required - simple refresh
you page and results will be show.

More, when you turn on LESS "*watch mode*" page reloads won't be needed - page will be automatically
fit to new look one second after less file saving. You should notice that browser sometimes cache
less files to and in this case *watch mode* won't work. You must find a way to disable caching on your
test site - in Google Chrome you can do it through "Development Tools" -> "Settings" -> "Disable Cache".

This mode will be useful in development time - should not be used in production.

LESS server side compiling (PRODUCTION)
---------------------------------------

At server side compiling mode *less* files are compiled to css files and later treated like normal
css. To use this mode you need *leesc* tool installed in your system - from LESS website.

This mode will be useful in production - should not be used in development time.

Compile coffee files to js
==========================

To compile *.coffee* files we use CoffeeScriptRedux_ compiler. It give us possibility to automate
generate js to coffee `source maps`_ files. You can control source coffee directory and output coffee
directory by modify configuration in `Main config.yaml`_ file. You should remember, that output directory
should be source subdirectory - because *.coffee* files need be served by this same static subdomain.

Compiling process can be configured by two ways.
 First you can set *projectksi.web_deps.coffee_compiler.sourcemaps* configuration
directive to *false* or *true*. When sourcemaps mode is on compiling process will generate not
only *js* files, but source maps files to. It will have name like *js* generated files, but with *.map* extension. Code will
automatically add needed comment line to js files.
 Next by changing *projectksi.web_deps.coffee_compiler.autorecompile* directive you can control than
*coffee* files should be automatically recompiled after changes. It create another thread and observe
files, shoudn't be used on production server.

.. _CoffeeScriptRedux: https://github.com/michaelficarra/CoffeeScriptRedux/
.. _`source maps`: http://www.html5rocks.com/en/tutorials/developertools/sourcemaps/


CoffeeScriptRedux installation
------------------------------

You should install CoffeeScriptRedux_ fallowing their page instructions. Next, you should
set *projectksi.web_deps.coffee_compiler.path* configuration directive to show you own pathes.

Minifying, combining and gzip’ing
=================================

We use *squezeeit* to minifying, combining and gzip’ing our css and js files. If you want understand
how squezeeit is integrated with *projectksi* - first read https://github.com/psychowico/Squeezeit
to know how this tool work.

Main config.yaml
----------------

Location of our main *config.yaml* file is get from *projectksi.web_deps.squeezeit.config* configuration
directive. By default it will be "sqeezeit-config.yaml" in project main directory.
There default pathes are configured:

.. code-block:: yaml

    bundles: ./projectksi/static/

    #Where to output the bundles and bundle info file
    output: ./projectksi/static/publish

    #Source files
    css: ./projectksi/static/css/
    javascript: ./projectksi/static/js/
    coffee: ./projectksi/static/coffee/
    lessCompileOutput: ./projectksi/static/css/compiled_less/
    coffeeCompileOutput: ./projectksi/static/coffee/compiled/

    #Bundle names include MD5 hash of contents (E.G. [bundlename]-[md5 hash].js - See bundle info file)
    hashfilenames: true

This pathes is not likely to change. You just need remember to add all new *js*, *css*, *less* and
*coffee* files to yaml bundle files - or they won't be included in pages layout.

Another configuration
---------------------

To turn off *squeezeit* you need set *projectksi.web_deps.squeezeit.enabled* configuration
directive to *false*. Files will be serve single, in original, not minifying state. You should
avoid this at production server.

You can set *projectksi.web_deps.squeezeit.prefered_version* configuration directive to one of three
states:

 - raw (to include in layout combined files )
 - mini (to include in layout combined and minified files )
 - gz (to include in layout combined, minified and gzip'ed files )


Problems
--------

Sometimes after minifying *js* files some errors will be occur on the page, that won't happen before.
Probably it is because some library was minifying before - and somebody did it too good.
In most case you just need found lines with bugs and add semicolon at end.