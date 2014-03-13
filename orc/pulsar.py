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

    melodies = [dsp.randchoose(['c', 'g', 'a'])]

    if tel['density'] >= 4:
        melodies += [ [ dsp.randchoose(['c', 'g', 'a']) for i in range(2) ] for m in range(dsp.randint(2, 4)) ]

    if tel['density'] >= 6:
        melodies += [ [ dsp.randchoose(['c', 'd', 'e', 'g', 'a']) for i in range(dsp.randint(3, 6)) ] for m in range(dsp.randint(2, 5)) ]

    notes = dsp.randchoose(melodies)

    octave = (tel['register'] / 10.0) * 4 + 1

    root        = p(voice_id, 'root', 27.5)
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

    modRange    = p(voice_id, 'speed', 0.01)
    modRange    = dsp.rand(0, modRange)

    pulsewidth = 1.0 / (tel['roughness'] / 10.0)
    pulsewidth -= dsp.rand(0, 0.09)

    beat = dsp.bpm2frames(bpm)

    tune.a0 = float(root)
    freqs   = [ tune.ntf(note, octave, ratios=tune.just) for note in notes ]


    #####################
    # SIREN
    ##################### 
    if 'ballsout' in tel['name']: 
        waveform = dsp.wavetable([0] + [ dsp.rand(-1, 1) for w in range(10) ] + [0], 512)
        window = dsp.wavetable([0] + [ dsp.rand(0, 1) for w in range(10) ] + [0], 512)

        if tel['roughness'] >= 9:
            waveform = dsp.wavetable([0] + [ dsp.rand(-1, 1) for w in range(50) ] + [0], 512)
            window = dsp.wavetable([0] + [ dsp.rand(0, 1) for w in range(50) ] + [0], 512)

        modRange = tel['harmonicity'] * 30
        modFreq = tel['pace'] / 5.0

        out = dsp.pulsar(2, length, pulsewidth, waveform, window, mod, modRange, modFreq, volume)
        out = dsp.pan(out, dsp.rand())
        out = dsp.amp(out, dsp.rand(0.3, 0.5))

        dsp.log('siren!')
        bot.show_telemetry(tel)
        return out

    #####################
    # NORMAL 
    ##################### 
    numgrains = int(dsp.rand(50, 500))

    if tel['roughness'] <= 2:
        window      = 'sine'
        waveform    = 'sine2pi'
        if dsp.rand(0, 100) > 50:
            minplen     = dsp.ftms(length / 4)
            maxplen     = 30000
        else:
            minplen     = 5
            maxplen     = 80

    elif tel['roughness'] <= 4:
        window      = 'sine'
        waveform    = 'sine2pi'
        minplen     = 10
        maxplen     = 80

    elif tel['roughness'] > 4:
        window      = 'tri'
        waveform    = 'tri'
        minplen     = 5 
        maxplen     = 60

    elif tel['roughness'] >= 7:
        window      = 'vary'
        waveform    = 'vary'
        minplen     = 1
        maxplen     = 40

    mod = dsp.wavetable(mod, 512)
    window = dsp.wavetable(window, 512)
    waveform = dsp.wavetable(waveform, 512)

    pc = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(5, numgrains))) ], numgrains)

    out = ''
    outlen = 0
    count = 0

    bar = dsp.randint(4, 8)

    if tel['density'] > 6:
        numbeats = bar * dsp.randint(4, 8)

    while outlen < length:
        layers = []

        if tel['density'] > 6:
            plen = beat / dsp.randint(1, 8)
        else:
            plen = dsp.mstf(dsp.rand(minplen, maxplen))

        if tel['register'] >= 6 and tel['density'] >= 6:
            maxo = int(dsp.rand(2, 6))
        else:
            maxo = 1

        if tel['density'] > 6:
            freqs = dsp.randshuffle(freqs)
            for b in range(numbeats):
                f = freqs[b % len(freqs)] 
                if dsp.rand(0, 100) > 70:
                    f *= 2**int(dsp.rand(0, maxo))

                b = dsp.pulsar(f, plen, pulsewidth, waveform, window, mod, modRange, modFreq, volume)
                b = dsp.pan(b, dsp.rand())

                out += b
                outlen += dsp.flen(b)

        else:
            for iff, freq in enumerate(freqs):
                if 'gentle' in tel['name']:
                    volume = dsp.rand(0.5, 0.7)
                elif 'upbeat' in tel['name']:
                    volume = dsp.rand(0.5, 0.75)
                else:
                    volume = dsp.rand(0.4, 0.6)

                if dsp.rand(0, 100) > 70:
                    freq *= 2**int(dsp.rand(0, maxo))

                layer = dsp.pulsar(freq, plen, pulsewidth, waveform, window, mod, modRange, modFreq, volume)

                layer = dsp.env(layer, 'sine')
                layer = dsp.pan(layer, dsp.rand())

                layers += [ layer ]

            layer = dsp.mix(layers)
            out += layer
            outlen += dsp.flen(layer)

            count += 1

    out = dsp.env(out, 'sine')

    dsp.log((tel['harmonicity'] - 10) * -0.5)
    #if dsp.flen(out) > dsp.mstf(100):
        #out = dsp.drift(out, (tel['harmonicity'] - 10.0) * -1 * 0.02)

    dsp.log('')
    dsp.log('pulsar')
    dsp.log('%s length: %.2f' % (voice_id, dsp.fts(dsp.flen(out))))
    bot.show_telemetry(tel)

    return out

