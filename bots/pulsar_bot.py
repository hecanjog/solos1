from pippi import dsp
from pippic import settings
from termcolor import colored

"""
register: low - high
density: thin - thick
harmonicity: aharmonic - harmonic
roughness: smooth - rough
pace: slow - fast
"""

numpoints = 48
numlands  = 5

dsp.log('loaded pulsar bot')

def mc(r):
    return dsp.breakpoint([ int(dsp.rand(r[0], r[1])) for i in range(numlands) ], numpoints)

zones = [
    {
        'name': 'sparse',
        'register': (7, 10),
        'density': (1, 2),
        'harmonicity': (1, 10),
        'roughness': (1, 5),
        'pace': (1, 3)
    }, {
        'name': 'gentle',
        'register': (3, 7),
        'density': (3, 6),
        'harmonicity': (8, 10),
        'roughness': (1, 2),
        'pace': (1, 3)
    }, {
        'name': 'ballsout',
        'register': (1, 10),
        'density': (8, 10),
        'harmonicity': (1, 10),
        'roughness': (8, 10),
        'pace': (3, 10)
    }, {
        'name': 'upbeat',
        'register': (5, 8),
        'density': (5, 8),
        'harmonicity': (8, 10),
        'roughness': (2, 4),
        'pace': (4, 7)
    },
]

def make_section(zone):
    zone['register'] = mc(zone['register'])
    zone['density'] = mc(zone['density'])
    zone['harmonicity'] = mc(zone['harmonicity'])
    zone['roughness'] = mc(zone['roughness'])
    zone['pace'] = mc(zone['pace'])

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

def make_telemetry(zones):
    sections = []

    zones *= 4
    zones = dsp.randshuffle(zones)

    for zone in zones:
        sections += make_section(zone)

    return sections 

tel = make_telemetry(zones)

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
            output += [ colored(v.upper(), color) ]
        else:
            output += [ colored('%s: %.2f' % (k[:3], v), color) ]

    output = ' | '.join(output)
    dsp.log(output)
def zone(register, density, harmonicity, roughness, pace):
    matched_zones = []

    for zone in zones:
        if register >= zone['register'][0] and register <= zone['register'][1] and density >= zone['density'][0] and density <= zone['density'][1] and harmonicity >= zone['harmonicity'][0] and harmonicity <= zone['harmonicity'][1] and roughness >= zone['roughness'][0] and roughness <= zone['roughness'][1] and pace >= zone['pace'][0] and pace <= zone['pace'][1]:
            matched_zones += [ zone['name'] ]

    return matched_zones

def getTel():
    count = int(settings.shared('count'))
    return tel[count % len(tel)]
