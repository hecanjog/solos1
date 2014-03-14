from pippi import dsp
from pippic import settings
from pippic import rt
from termcolor import colored
import multiprocessing as mp
import pulsar
import chirps
import json
import time

"""
register: low - high
density: thin - thick
harmonicity: aharmonic - harmonic
roughness: smooth - rough
pace: slow - fast
"""

numpoints = 48
numlands  = 5

dsp.log('loaded geodes bot')

def mc(r, numpoints):
    return dsp.breakpoint([ dsp.rand(r[0], r[1]) for i in range(numlands) ], numpoints)

def make_section(zone):
    numpoints = dsp.randint(20, 30)

    zone['register'] = mc(zone['register'], numpoints)
    zone['density'] = mc(zone['density'], numpoints)
    zone['harmonicity'] = mc(zone['harmonicity'], numpoints)
    zone['roughness'] = mc(zone['roughness'], numpoints)
    zone['pace'] = mc(zone['pace'], numpoints)

    return [ make_point(zone, i) for i in range(numpoints) ]

def make_point(zone, i):
    return {
            'name': zone['name'],
            'register': zone['register'][i],
            'density': zone['density'][i],
            'harmonicity': zone['harmonicity'][i],
            'roughness': zone['roughness'][i],
            'pace': zone['pace'][i],
    }

def make_telemetry():
    zones = [
        {
            'name': ['sparse'],
            'register': (7, 10),
            'density': (1, 2),
            'harmonicity': (1, 10),
            'roughness': (1, 5),
            'pace': (1, 3)
        }, {
            'name': ['gentle'],
            'register': (3, 7),
            'density': (3, 8),
            'harmonicity': (8, 10),
            'roughness': (1, 2),
            'pace': (1, 3)
        }, {
            'name': ['ballsout'],
            'register': (1, 10),
            'density': (2, 10),
            'harmonicity': (1, 10),
            'roughness': (4, 10),
            'pace': (3, 10)
        }, {
            'name': ['upbeat'],
            'register': (5, 8),
            'density': (1, 8),
            'harmonicity': (8, 10),
            'roughness': (2, 4),
            'pace': (4, 7)
        }, {
            'name': ['upbeat'],
            'register': (5, 8),
            'density': (1, 8),
            'harmonicity': (8, 10),
            'roughness': (2, 4),
            'pace': (4, 7)
        },
    ]

    dsp.log('generating telemetry...')

    numsections = dsp.randint(10, 20)
    sections = []

    for s in range(numsections):
        zone = dsp.randchoose(zones)
        section = make_section(zone)
        sections += section

        # Transition
        if dsp.rand(0, 100) > 20:
            next_zone = dsp.randchoose(zones)

            if next_zone['name'] != zone['name']:
                next_section = make_section(next_zone)

                transition_zone = {
                    'name': ['transition', section[-1]['name'][0], next_section[0]['name'][0]],
                    'register': (section[-1]['register'], next_section[0]['register']),
                    'density': (section[-1]['density'], next_section[0]['density']),
                    'harmonicity': (section[-1]['harmonicity'], next_section[0]['harmonicity']),
                    'roughness': (section[-1]['roughness'], next_section[0]['roughness']),
                    'pace': (section[-1]['pace'], next_section[0]['pace']),
                }

                transition_section = make_section(transition_zone)

                sections += transition_section
                sections += next_section


    dsp.log('telemetry generated')
    settings.shared('tel', sections)

def run(gens, tick):
    dsp.log('telemetry up!')
    started = time.time()

    def worker(gens, tick):
        while time.time() < started + (60 * 15):
            dsp.delay(dsp.stf(dsp.rand(2, 20)))

            if dsp.rand(0, 100) > 50:
                if dsp.rand(0, 100) > 35:
                    voice_id, generator_name = settings.add_voice('pp re qu')
                    dsp.log('starting pulsar voice %s' % voice_id)
                else:
                    if dsp.rand(0, 100) > 50:
                        voice_id, generator_name = settings.add_voice('ch re qu')
                    else:
                        voice_id, generator_name = settings.add_voice('ch qu')

                    dsp.log('starting chirp voice %s' % voice_id)

                playback_process = mp.Process(name=voice_id, target=rt.out, args=(gens[generator_name], tick))
                playback_process.start()

                dsp.delay(dsp.stf(dsp.rand(6, 35)))

                dsp.log('stopping voice %s' % voice_id)
                settings.voice(voice_id, 'loop', 0)

    for w in range(10):
        # Spawn worker
        worker_process = mp.Process(name='worker', target=worker, args=(gens, tick))
        worker_process.start()

def show_telemetry(tel):
    output = [] 

    for k, v in tel.iteritems():
        if k == 'register':
            color = 'blue'

        elif k == 'density':
            color = 'red'

        elif k == 'harmonicity':
            color = 'green'

        elif k == 'roughness':
            color = 'cyan'

        elif k == 'pace':
            color = 'yellow'

        else:
            color = 'white'

        if k == 'name':
            output += [ colored(' '.join(v), color) ]
        else:
            output += [ colored('%s: %.2f' % (k[:3], v), color) ]

    output = ' | '.join(output)
    dsp.log(output)

def getTel():
    tel = json.loads(settings.shared('tel'))
    count = int(settings.shared('count'))
    tel = tel[count % len(tel)]

    return tel
