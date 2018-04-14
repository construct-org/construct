=====
casts
=====


Record CLI demos using spielbash/asciinema
==========================================

Build it...

.. code-block:: console

    docker build -f record.Dockerfile -t record_casts .


Run it...

.. code-block:: console

    docker run --rm -it -v $PWD:/data record_casts --width 120 --height 40


Convert asciicasts to gif using asciicast2gif
=============================================

Build it...

.. code-block:: console

    docker build -f convert.Dockerfile -t convert_casts .


Run it...

.. code-block:: console

    docker run --rm -it -v %cd%:/data convert_casts


Run em back to back on Windows
==============================

Build both the record and convert Dockerfiles. Then run...

.. code-block:: console

    build
