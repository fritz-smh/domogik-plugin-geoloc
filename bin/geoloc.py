#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Geoloc

Implements
==========

- GeolocManager

@author: Fritz <fritz.smh@gmail.com>
@copyright: (C) 2007-2014 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.xpl.common.xplmessage import XplMessage
from domogik.xpl.common.plugin import XplPlugin

import threading
import traceback
import re
from flask import Flask, g
from flask_bootstrap import Bootstrap




### flask

app = Flask(__name__)
# the import is made here because these are the url related functions
from domogik_packages.plugin_geoloc.lib.geoloc import *





### plugin
class GeolocManager(XplPlugin):
    """ Handle a REST service to retrieve geoloc informations
    """

    def __init__(self, app):
        """ Init plugin
            @param app : flask app
        """
        XplPlugin.__init__(self, name='geoloc')
        self.app = app

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        #if not self.check_configured():
        #    return

        # get the plugin configuration
        self.rest_host = self.get_config("host")
        self.rest_port = self.get_config("port")

        # get the devices list
        self.devices = self.get_device_list(quit_if_no_device = False)


    def run(self):
        """ Start the rest service in a thread
            and set the plugin as ready
        """

        thr_name = "geoloc_rest_service"
        # more informations about parameters here : http://werkzeug.pocoo.org/docs/serving/#werkzeug.serving.run_simple
        thr = threading.Thread(None,
                               self.app.run,
                               thr_name,
                               (),
                               { 'debug' : True, \
                                 'host'  :  self.rest_host, \
                                 'port' : self.rest_port, \
                                 'use_reloader'  :  False, \
                                 'threaded'  :  True
                               })
        thr.start()
        self.register_thread(thr)

        self.ready()
        self.log.info(u"Plugin ready :)")


    def send_xpl_position_degree(self, device, value):
        """ Send xPL message on network
        """
        self.log.debug(u"Position received for '{0}' : {1}".format(device, value))
        msg = XplMessage()
        msg.set_type("xpl-stat")
        msg.set_schema("sensor.basic")
        msg.add_data({"device" : device})
        msg.add_data({"type" : "position_degrees"})
        msg.add_data({"current" : value})
        self.myxpl.send(msg)


### main
if __name__ == "__main__":
    ### Instantiate the plugin manager
    Bootstrap(app)
    geoloc = GeolocManager(app)

    ### decorators for flask
    @app.before_request
    def before_request():
        g.send_xpl_position_degree = geoloc.send_xpl_position_degree
        g.devices = geoloc.devices
        g.get_parameter_for_feature = geoloc.get_parameter_for_feature
        g.get_data_files_directory = geoloc.get_data_files_directory

    ### launch the rest service
    geoloc.run()
