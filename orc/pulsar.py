from pippi import dsp
from pippi import tune
from pippic.settings import get_param as p
from pippic.settings import voice as vp
from pippic.settings import shared
import geodes as bot

shortname   = 'pp'
name        = 'pulsar'

def play(voice_id):
    tel = bot.getTel()

    if 'sparse' in tel['name'] or 'ballsout' in tel['name']:
        dsp.log('')
        dsp.log(voice_id + ' pulsar silent')
        bot.show_telemetry(tel)
        return dsp.pad('', 0, dsp.stf(dsp.rand(1, 10)))

    #####################
    # PARAMS 
    ##################### 
    volume = dsp.rand(0.4, 0.7)

    melodies = [[dsp.randchoose([1, 5, 6])]]

    if tel['density'] >= 4:
        melodies += [ [ dsp.randchoose([1, 5, 6]) for i in range(2) ] for m in range(dsp.randint(2, 4)) ]

    if tel['density'] >= 6:
        melodies += [ [ dsp.randchoose([1, 2, 3, 5, 6]) for i in range(dsp.randint(3, 6)) ] for m in range(dsp.randint(2, 5)) ]

    try:
        notes = dsp.randchoose(melodies)
    except IndexError:
        dsp.log(melodies)
        notes = [1]

    octave = int(round((tel['register'] / 10.0) * 4 + 1))

    bpm         = p(voice_id, 'bpm', 80.0)

    if 'ballsout' in tel['name']:
        length = int((1.0 / (tel['pace'] / 10.0)) * dsp.stf(3))
    else:
        length = int((1.0 / (tel['pace'] / 10.0)) * dsp.stf(4)) + dsp.stf(dsp.rand(0.25, 1))

    # Cap voice length at 60 secs
    if length > dsp.stf(60):
        length = dsp.stf(60)

    env         = 'sine'

    mod         = p(voice_id, 'mod', 'random')
    modFreq     = p(voice_id, 'modfreq', dsp.rand(1.0, 2.5) / dsp.fts(length))

    modRange    = dsp.rand(0.01, 0.04)
    modRange    = dsp.rand(0, modRange)

    pulsewidth = 1.0 / (tel['roughness'] / 10.0)
    pulsewidth -= dsp.rand(0, 0.09)
    if pulsewidth < 0.1:
        pulsewidth = 0.1

    beat = dsp.bpm2frames(bpm)
 
    try:
        freqs   = tune.fromdegrees(notes, octave=octave, ratios=tune.just, root='c')
    except TypeError:
        print 'hm', notes, octave
        freqs = tune.fromdegrees([1,5], octave=octave, ratios=tune.just, root='c')

    #####################
    # NORMAL 
    ##################### 
    numgrains = int(dsp.rand(50, 500))

    if tel['roughness'] <= 2:
        window      = 'sine'
        waveform    = 'sine2pi'
        minplen     = dsp.ftms(length / 4)
        maxplen     = 30000

    elif tel['roughness'] <= 4:
        window      = 'sine'
        waveform    = 'sine2pi'
        minplen     = 10
        maxplen     = 350

    elif tel['roughness'] > 4:
        window      = 'tri'
        waveform    = 'tri'
        minplen     = 10 
        maxplen     = 120

    elif tel['roughness'] >= 7:
        window      = 'vary'
        waveform    = 'tri'
        minplen     = 5
        maxplen     = 80

    mod = dsp.wavetable(mod, 512)
    window = dsp.wavetable(window, 512)
    waveform = dsp.wavetable(waveform, 512)

    pc = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(5, numgrains))) ], numgrains)

    out = ''
    outlen = 0
    count = 0

    bar = dsp.randint(4, 8)

    dobeats = dsp.rand(0, 100) > 10

    if tel['density'] > 4 and dobeats:
        numbeats = bar * dsp.randint(4, 8)

    while outlen < length:
        layers = []

        if tel['density'] > 4 and dobeats:
            plen = beat / dsp.randint(2, 8)
        else:
            plen = dsp.mstf(dsp.rand(minplen, maxplen))

        if tel['register'] >= 6 and tel['density'] >= 4:
            maxo = dsp.randint(2, 6)
        else:
            maxo = 1

        if tel['density'] > 4 and dobeats:
            freqs = dsp.randshuffle(freqs)
            for b in range(numbeats):
                f = freqs[b % len(freqs)] 
                if dsp.rand(0, 100) > 70:
                    f *= 2**dsp.randint(0, maxo)

                b = dsp.pulsar(f, plen, pulsewidth, waveform, window, mod, modRange, modFreq, volume)
                b = dsp.pan(b, dsp.rand())

                out += b
                outlen += dsp.flen(b)

        else:
            for iff, freq in enumerate(freqs):
                if 'gentle' in tel['name']:
                    volume = dsp.rand(0.5, 1)
                elif 'upbeat' in tel['name']:
                    volume = dsp.rand(0.5, 0.9)
                else:
                    volume = dsp.rand(0.4, 0.8)

                if dsp.rand(0, 100) > 60:
                    freq *= 2**dsp.randint(0, maxo)

                layer = dsp.pulsar(freq, plen, pulsewidth, waveform, window, mod, modRange, modFreq, volume)

                layer = dsp.env(layer, 'sine')
                layer = dsp.pan(layer, dsp.rand())

                layers += [ layer ]

            layer = dsp.mix(layers)
            out += layer
            outlen += dsp.flen(layer)

            count += 1

    out = dsp.env(out, 'sine')

    if dsp.flen(out) > dsp.mstf(100) and dsp.rand(0, 100) > 50:
        out = dsp.drift(out, (tel['harmonicity'] - 10.0) * -1 * 0.03, dsp.randint(41, 441))

    dsp.log('')
    dsp.log('pulsar')
    dsp.log('%s length: %.2f' % (voice_id, dsp.fts(dsp.flen(out))))
    bot.show_telemetry(tel)

    return out

