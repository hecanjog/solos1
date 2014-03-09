from pippi import dsp
from pippi import tune
from pippic.settings import get_param as p
from pippic.settings import voice as vp
from pippic.settings import shared
import pulsar_bot as bot

shortname   = 'pp'
name        = 'pulsar'

def play(voice_id):
    tel = bot.getTel()
    if tel['name'] == 'sparse':
        dsp.log('pulsar silent')
        bot.show_telemetry(tel)
        return dsp.pad('', 0, dsp.stf(dsp.rand(1, 10)))

    #####################
    # PARAMS 
    ##################### 
    if tel['name'] == 'gentle':
        volume = dsp.rand(0.2, 0.6)
    elif tel['name'] == 'upbeat':
        volume = dsp.rand(0.4, 0.6)
    else:
        volume = dsp.rand(0.3, 0.6)

    melodies = [dsp.randchoose(['c', 'e', 'g', 'a'])]

    if tel['density'] >= 4:
        melodies += [ [ dsp.randchoose(['c', 'e', 'g', 'a']) for i in range(2) ] for m in range(dsp.randint(2, 4)) ]

    if tel['density'] >= 6:
        melodies += [ [ dsp.randchoose(['c', 'd', 'e', 'f', 'g', 'a']) for i in range(dsp.randint(3, 6)) ] for m in range(dsp.randint(2, 5)) ]

    notes = dsp.randchoose(melodies)

    octave = (tel['register'] / 10.0) * 4 + 1

    root        = p(voice_id, 'root', 27.5)
    bpm         = p(voice_id, 'bpm', 80.0)

    length = int((1.0 / (tel['pace'] / 10.0)) * dsp.stf(5))
    # Cap voice length at 60 secs
    if length > dsp.stf(60):
        length = dsp.stf(60)

    env         = 'sine'

    mod         = p(voice_id, 'mod', 'random')
    modFreq     = p(voice_id, 'modfreq', dsp.rand(1.0, 2.5) / dsp.fts(length))

    modRange    = p(voice_id, 'speed', 0.02)
    modRange    = dsp.rand(0, modRange)

    pulsewidth = 1.0 / (tel['roughness'] / 10.0)
    pulsewidth -= dsp.rand(0, 0.09)

    beat = dsp.bpm2frames(bpm)

    tune.a0 = float(root)
    freqs   = [ tune.ntf(note, octave) for note in notes ]

    #####################
    # SIREN
    ##################### 
    if tel['roughness'] >= 8: 
        waveform = dsp.wavetable([0] + [ dsp.rand(-1, 1) for w in range(10) ] + [0], 512)
        window = dsp.wavetable([0] + [ dsp.rand(0, 1) for w in range(10) ] + [0], 512)
        senv = 'tri'

        if tel['roughness'] >= 9:
            waveform = dsp.wavetable([0] + [ dsp.rand(-1, 1) for w in range(50) ] + [0], 512)
            window = dsp.wavetable([0] + [ dsp.rand(0, 1) for w in range(50) ] + [0], 512)
            senv = 'vary'

        modRange = tel['harmonicity'] * 30
        modFreq = tel['pace'] / 5.0

        out = dsp.pulsar(2, length, pulsewidth, waveform, window, mod, modRange, modFreq, volume)
        out = dsp.env(out, senv)
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
        minplen     = dsp.ftms(length / 2)
        maxplen     = dsp.ftms(length)

    elif tel['roughness'] <= 4:
        window      = 'sine'
        waveform    = 'sine2pi'
        minplen     = 10
        maxplen     = 80

    elif tel['roughness'] > 4:
        window      = 'tri'
        waveform    = 'tri'
        minplen     = 20
        maxplen     = 60

    elif tel['roughness'] >= 7:
        window      = 'vary'
        waveform    = 'vary'
        minplen     = 1
        maxplen     = 40

    mod = dsp.wavetable(mod, 512)
    window = dsp.wavetable(window, 512)
    waveform = dsp.wavetable(waveform, 512)

    ffc = []
    for freq in freqs:
        fffF = freq * dsp.rand(0.98, 1.03)
        ffc += [ dsp.breakpoint([ dsp.rand(freq, fffF) for i in range(50) ], numgrains) ]

    pc = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(5, numgrains))) ], numgrains)

    out = ''
    outlen = 0
    count = 0
    while outlen < length:
        layers = []

        plen = dsp.mstf(dsp.rand(minplen, maxplen))

        if tel['register'] >= 6 and tel['density'] >= 6:
            maxo = int(dsp.rand(2, 6))
        else:
            maxo = 1

        for iff, freq in enumerate(freqs):
            if tel['name'] == 'gentle':
                volume = dsp.rand(0.1, 0.4)
            elif tel['name'] == 'upbeat':
                volume = dsp.rand(0.5, 0.75)
            else:
                volume = dsp.rand(0.3, 0.6)

            f = ffc[iff][count % len(ffc[iff])] * 2**int(dsp.rand(0, maxo))
            layer = dsp.pulsar(f, plen, pulsewidth, waveform, window, mod, modRange, modFreq, volume)

            layer = dsp.env(layer, 'sine')
            layer = dsp.pan(layer, dsp.rand())

            layers += [ layer ]

        layer = dsp.mix(layers)
        out += layer

        outlen += dsp.flen(layer)
        count += 1

    out = dsp.env(out, 'sine')

    dsp.log('%s length: %.2f' % (voice_id, dsp.fts(dsp.flen(out))))

    bot.show_telemetry(tel)

    return out

