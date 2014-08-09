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

- Geoloc

@author: Fritz <fritz.smh@gmail.com>
@copyright: (C) 2007-2014 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from flask import Flask, g, send_from_directory
from domogik_packages.plugin_geoloc.bin.geoloc import app
import traceback
import os

ok = 200
error = 500

# to activate for debug only
debug = True



@app.route('/')
def root():
    return send_from_directory("/media/stock/domotique/git/domogik-plugin-geoloc/data/", 'index.html')

@app.route('/position_degrees/<string:device>/<string:data>', methods = ["GET"])
def position_degrees(device, data):
    debug_info = ""
    try:
        # check if the device exists
        found = False
        for a_device in g.devices:
            if device == g.get_parameter_for_feature(a_device, "xpl_stats", "position", "device"):
                found = True
            break
        # device not found
        if not found:
            return "No device '{0}' exists".format(device), error
        
        # check the position format
        # TODO

        # send position over xpl
        g.send_xpl_position_degree(device, data)
    except:
        if debug:
            return "Error while processing received position : {0}. <br/>Error is : {1}".format(data, traceback.format_exc()), error
        else:
            return "Error while processing received position : {0}".format(data), error
    if debug:
        return "Position successfully processed : {0}.<br/>{1}".format(data, debug_info), ok
    else:
        return "Position successfully processed : {0}".format(data), ok


@app.route('/static/css/<string:file>', methods = ["GET"])
def static_css(file):
    """ we override /static which is already handles by flask because when we create the app = Flask(...) 
        we are not yet able to know the static directory and so set it...
    """
    return send_from_directory("{0}/".format(os.path.join(g.get_data_files_directory(), "static/css")), file)


@app.route('/static/js/<string:file>', methods = ["GET"])
def static_js(file):
    """ we override /static which is already handles by flask because when we create the app = Flask(...) 
        we are not yet able to know the static directory and so set it...
    """
    return send_from_directory("{0}/".format(os.path.join(g.get_data_files_directory(), "static/js")), file)

