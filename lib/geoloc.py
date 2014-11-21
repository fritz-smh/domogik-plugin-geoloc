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

from flask import Flask, g, send_from_directory, request
from domogik_packages.plugin_geoloc.bin.geoloc import app
import traceback
import os
import re

ok = 200
error = 500

# to activate for debug only
debug = True

@app.route('/')
def root():
    return send_from_directory("/media/stock/domotique/git/domogik-plugin-geoloc/data/", 'index.html')

@app.route('/position/<string:device>/', methods = ["POST"])
def position_post(device):
    """ Used for POST on /position/<device>/

        Sample for Android app Trip Tracker :
        data = ImmutableMultiDict([('locations[1][longitude]', u'-1.3015050539275859'), ('locations[0][time]', u'1414950119346'), ('locations[1][speed]', u'1.5556983'), ('locations[1][time]', u'1414958966722'), ('locations[1][latitude]', u'47.08956470569191'), ('locations[0][longitude]', u'-1.3015941102186852'), ('locations[0][latitude]', u'47.08935763509281'), ('locations[0][speed]', u'0.3824184')])
    """
    try:
        # check if the device exists
        found = False
        for a_device in g.devices:
            if device == g.get_parameter_for_feature(a_device, "xpl_stats", "position", "device"):
                found = True
            break
        # device not found
        if not found:
            if debug:
                return "No device '{0}' exists. Existing devices : {1}".format(device, g.devices), error
            else:
                return "No device '{0}' exists".format(device), error
        
        #print("Raw data = {0}".format(request.form))
        data = request.form
        # find the last index
        idx = 0
        for key in data:
            if idx < int(key[10:11]):
                idx = int(key[10:11])
        longitude = data["locations[{0}][longitude]".format(idx)]
        latitude = data["locations[{0}][latitude]".format(idx)]
        if longitude is None:
            return "Data not valid!", error
            
        #print("latitude = {0}".format(latitude))
        #print("longitude = {0}".format(longitude))
        position_format = "trip tracker android application"
        g.send_xpl_position_degree(device, "{0},{1}".format(longitude, latitude))

    except:
        if debug:
            return "Error while processing received position : {0}. <br/>Error is : {1}".format(data, traceback.format_exc()), error
        else:
            return "Error while processing received position : {0}".format(data), error
    return "Position successfully processed ({0}): {1}".format(position_format, data), ok



@app.route('/position/<string:device>/<string:data>', methods = ["GET"])
def position_get(device, data):
    """ Used for GET on /position/<device>/<value>
    
        Sample for use with :
        * plugin user interface
        * tasker

        wget -qO- http://192.168.1.10:40445/position/fritz/-1.9781616210925,46.790657811998
    """
    try:
        # check if the device exists
        found = False
        for a_device in g.devices:
            if device == g.get_parameter_for_feature(a_device, "xpl_stats", "position", "device"):
                found = True
            break
        # device not found
        if not found:
            if debug:
                return "No device '{0}' exists. Existing devices : {1}".format(device, g.devices), error
            else:
                return "No device '{0}' exists".format(device), error
        
        ### check the position format

        # TODO : use the same xpl function for all (and give the type as a param)

        # degrees
        re_degrees = re.compile('^-?\d+\.?\d*,-?\d+\.?\d*$')
        if re_degrees.match(data):
            position_format = "degrees"
            g.send_xpl_position_degree(device, data)
        else:
            return "Unrecognize position type!", error

        # degrees minutes
        #TODO


        # degrees minutes seconds
        #TODO

    except:
        if debug:
            return "Error while processing received position : {0}. <br/>Error is : {1}".format(data, traceback.format_exc()), error
        else:
            return "Error while processing received position : {0}".format(data), error
    return "Position successfully processed ({0}): {1}".format(position_format, data), ok


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

