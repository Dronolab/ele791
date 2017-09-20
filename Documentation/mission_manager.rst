Mission Manager
===============
The main goal of the mission manager is to provide a unified interface between
the ground control station (GCS) and the different UAVs.

Ideally, we plan on having 2 different 'buses'. The first one allows for high
level communication between remote entities while the second one manages
inter-application communications.

For now, we are set on `ZMQ <http://zeromq.org/>` which provides python
bindings.


Inter-node communications
-------------------------
For this kind of communication, we use a publisher/subscriber architecture.
Every message and its content shall be described here. Each UAV is subscribed to
the GCS topic. This is the main communication bus, it is used mainly to start
the whole mission. In the futur, each UAV could also subscribe to other UAVs,
this could be used for Dynamic Obstacle Avoidance and more fun stuff.


Inter-process communications
----------------------------
For this kind of communication, we use a request/reply architecture. This allows
us to make sure everything is in sync. Also, if an application does not reply in
a given timeframe, we can resend the request. All requests and expected replies
shall be documented here.

TODO:
        replace these with real name

        +---------------------+----------------------+-----------------+
        |                     | REQ                  | REP             |
        +=====================+======================+=================+
        | **01-capture**      |                                        |
        +---------------------+----------------------+-----------------+
        |                     | CAPTURE:[FREQ]       | CAPTURE:DONE    |
        +---------------------+----------------------+-----------------+
        |                     | CAPTURE:STOP         | CAPTURE:STOPPED |
        +---------------------+----------------------+-----------------+
        |                                                              |
        +---------------------+----------------------+-----------------+
        | **02-preproc**      |                                        |
        +---------------------+----------------------+-----------------+
        |                                                              |
        +---------------------+----------------------+-----------------+
        | **03-geo**          |                                        |
        +---------------------+----------------------+-----------------+
        |                     | GEO:POS:[FREQ]       | GEO:STARTED     |
        +---------------------+----------------------+-----------------+
        |                     | GEO:STOP             | GEO:STOPPED     |
        +---------------------+----------------------+-----------------+
        |                                                              |
        +---------------------+----------------------+-----------------+
        | **04-targetdetect** |                                        |
        +---------------------+----------------------+-----------------+
        |                                                              |
        +---------------------+----------------------+-----------------+
        | **05-transfer**     |                                        |
        +---------------------+----------------------+-----------------+

``CAPTURE:[FREQ]``
        Trigger the ``capture`` application to take a picture at ``[FREQ]``. If
        no ``[FREQ]`` is given, trigger a single picture.

``CAPTURE:DONE``
        Signal the manager that the picture was taken.

``CAPTURE:STOP``
        Signal the manager that ``capture`` is stopped.
