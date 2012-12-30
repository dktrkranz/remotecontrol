#!/usr/bin/python
#Copyright (c) 2012 Luca Falavigna

#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.

import dbus
from os import environ
from subprocess import check_output, CalledProcessError
from sys import argv

options = ('play', 'pause', 'stop', 'volume', 'volumeup', 'volumedown')

T_SERVICE_NAME = 'org.mpris.Totem'
T_OBJECT_PATH = '/Player'
T_INTERFACE = 'org.freedesktop.MediaPlayer'

try:
    option = argv[1]
except IndexError:
    pass
else:
    if option in options:
        if 'DISPLAY' not in environ:
            environ['DISPLAY'] = ':0'
        if 'DBUS_SESSION_BUS_ADDRESS' not in environ:
            try:
                pid = check_output(['pidof', '-c', 'totem']).strip()
            except CalledProcessError:
                exit()
            with open('/proc/%s/environ' % pid, 'r') as fd:
                environment = fd.read().split('\x00')
            for env in environment:
                if env.startswith('DBUS_SESSION_BUS_ADDRESS'):
                    dbusenv = '='.join(env.split('=')[1:])
                    environ['DBUS_SESSION_BUS_ADDRESS'] = dbusenv
            if 'DBUS_SESSION_BUS_ADDRESS' not in environ:
                exit()
        session_bus = dbus.SessionBus()
        totem = session_bus.get_object(T_SERVICE_NAME, T_OBJECT_PATH)
        totem_mediaplayer = dbus.Interface(totem, dbus_interface=T_INTERFACE)
        if option == 'play':
            if totem_mediaplayer.GetStatus()[0] != 0:
                totem_mediaplayer.Play()
                print('Playback started')
        elif option == 'pause':
            if totem_mediaplayer.GetStatus()[0] != 1:
                totem_mediaplayer.Pause()
                print('Playback paused')
        elif option == 'stop':
            if totem_mediaplayer.GetStatus()[0] != 2:
                totem_mediaplayer.Stop()
                print('Playback stopped')
        elif option == 'volume':
            try:
                volume = int(argv[2])
            except (IndexError, ValueError):
                pass
            else:
                totem_mediaplayer.VolumeSet(volume)
                print(('Volume set to %d' % totem_mediaplayer.VolumeGet()))
        elif option == 'volumeup':
            volume = totem_mediaplayer.VolumeGet() * 110 / 100
            totem_mediaplayer.VolumeSet(volume)
            print(('Volume set to %d' % totem_mediaplayer.VolumeGet()))
        elif option == 'volumedown':
            volume = totem_mediaplayer.VolumeGet() * 100 / 110
            totem_mediaplayer.VolumeSet(volume)
            print(('Volume set to %d' % totem_mediaplayer.VolumeGet()))
