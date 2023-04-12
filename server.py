#############
# server.py #
#############

import datetime
import logging

import asyncio

import aiocoap.resource as resource
import aiocoap

import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

class SeparateLargeResource(resource.Resource):
    def get_link_description(self):
        #Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="Temperature")

    async def render_get(self, request):
        global sensor
        temperature = (sensor.get_temperature() * (9/5)) + 32
        temperature = "%0.2f" % temperature
        payload = ("Temperature: " + temperature + " F").encode('ascii')
        return aiocoap.Message(payload=payload)

class LargeResource(resource.Resource):
    def get_link_description(self):
        #Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="Hello World")

    async def render_get(self, request):
        
        payload = "Hello World".encode('ascii')
        return aiocoap.Message(payload=payload)
        
#Logging Setup

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

async def main():
    #GPIO Setup
    GPIO_setup()
    
    #Resource tree creation
    root = resource.Site()

    root.add_resource(['.well-known', 'core'], resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['temperature'], SeparateLargeResource())
    root.add_resource(['hello'], LargeResource())
    
    await aiocoap.Context.create_server_context(root)
    
    #run forever
    await asyncio.get_running_loop().create_future()


def GPIO_setup():
    GPIO.setmode(GPIO.BOARD)
    global sensor
    TEMP_SENSOR = 7
    sensor = W1ThermSensor()
    GPIO.setup(TEMP_SENSOR, GPIO.IN)

if __name__ == "__main__":
    asyncio.run(main())


