#!/usr/bin/python
# -*- coding: utf-8 -*-

from domogik.xpl.common.plugin import XplPlugin
from domogik.tests.common.plugintestcase import PluginTestCase
from domogik.tests.common.testplugin import TestPlugin
from domogik.tests.common.testdevice import TestDevice
from domogik.tests.common.testsensor import TestSensor
from domogik.common.utils import get_sanitized_hostname
from datetime import datetime
import unittest
import sys
import os
import traceback
import time

try:
    # python3
    from urllib.request import urlopen
except ImportError:
    # python2
    from urllib import urlopen
from threading import Thread

class GeolocTestCase(PluginTestCase):

    def test_0100_position(self):
        """ check if the xpl messages about total space are OK
            Sample message : 
            xpl-stat
            {
            hop=1
            source=domogik-geoloc.darkstar
            target=*
            }
            sensor.basic
            {
            device=test_device_geoloc
            type=position_degrees
            current=3,3
            }
        """
        global device_name
        global device_id
        global cfg

        # call he plugin url in a thread
        url = "http://{0}:{1}/position/{2}/{3}".format(cfg['host'], cfg['port'], device_name, "3,3")
        thr_url = Thread(None,
                         call_url,
                         "url",
                         (url,),
                         {})
        thr_url.start()

        # do the test
        # the 60s interval allows to launch the url call to geoloc plugin in a thread
        print(u"Check that a message about position is sent in less than 60 seconds")
        
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-stat",
                                          xplschema = "sensor.basic",
                                          xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                          data = {"type" : "position_degrees", 
                                                  "device" : device_name,
                                                  "current" : "3,3"},
                                          timeout = 60))
        print(u"Check that the value of the xPL message has been inserted in database")
        sensor = TestSensor(device_id, "position_degrees")
        print(sensor.get_last_value())
        self.assertTrue(sensor.get_last_value()[1] == self.xpl_data.data['current'])

def call_url(url):
    time.sleep(10)
    # call an url
    print("Calling {0}".format(url))
    html = urlopen(url)
    print(html.read())
    
        


if __name__ == "__main__":
    ### global variables
    device_name = "test_device_geoloc"

    ### configuration

    # set up the xpl features
    xpl_plugin = XplPlugin(name = 'test', 
                           daemonize = False, 
                           parser = None, 
                           nohub = True,
                           test  = True)

    # set up the plugin name
    name = "geoloc"

    # set up the configuration of the plugin
    # configuration is done in test_0010_configure_the_plugin with the cfg content
    # notice that the old configuration is deleted before
    cfg = { 'configured' : True,
            'host' : '0.0.0.0',
            'port' : '40445' }
   

    ### start tests

    # load the test devices class
    td = TestDevice()

    # delete existing devices for this plugin on this host
    client_id = "{0}-{1}.{2}".format("plugin", name, get_sanitized_hostname())
    try:
        td.del_devices_by_client(client_id)
    except: 
        print(u"Error while deleting all the test device for the client id '{0}' : {1}".format(client_id, traceback.format_exc()))
        sys.exit(1)

    # create a test device
    try:
        params = td.get_params(client_id, "geoloc.position_degrees")

        # fill in the params
        params["device_type"] = "geoloc.position_degrees"
        params["name"] = "test_device_geoloc"
        params["reference"] = "reference"
        params["description"] = "description"
        # global params
        # xpl params
        for the_param in params['xpl']:
            if the_param['key'] == "device":
                the_param['value'] = device_name
        print("PARAMS={0}".format(params))
        # create
        device_id = td.create_device(params)['id']

    except:
        print(u"Error while creating the test devices : {0}".format(traceback.format_exc()))
        sys.exit(1)

    
    ### prepare and run the test suite
    suite = unittest.TestSuite()
    # check domogik is running, configure the plugin
    suite.addTest(GeolocTestCase("test_0001_domogik_is_running", xpl_plugin, name, cfg))
    suite.addTest(GeolocTestCase("test_0010_configure_the_plugin", xpl_plugin, name, cfg))
    
    # start the plugin
    suite.addTest(GeolocTestCase("test_0050_start_the_plugin", xpl_plugin, name, cfg))

    # do the specific plugin tests
    suite.addTest(GeolocTestCase("test_0100_position", xpl_plugin, name, cfg))
    
    # wait for 2 seconds... why ? well... this is quite embarrasing to explain!
    # on my laptop, when the "stop the plugin" test is launched, an "active" 
    # plugin.status message is sent just before the "stopped" plugin.status 
    # message... and so, the plugin is seen as still active and the test fails
    # yeah, this need to be fixed in the testplugin.py file, but this will be 
    # done later so...
    time.sleep(2)

    # do some tests comon to all the plugins
    #suite.addTest(GeolocTestCase("test_9900_hbeat", xpl_plugin, name, cfg))
    suite.addTest(GeolocTestCase("test_9990_stop_the_plugin", xpl_plugin, name, cfg))
    
    # quit
    res = unittest.TextTestRunner().run(suite)
    if res.wasSuccessful() == True:
        rc = 0   # tests are ok so the shell return code is 0
    else:
        rc = 1   # tests are ok so the shell return code is != 0
    xpl_plugin.force_leave(return_code = rc)
     
    
