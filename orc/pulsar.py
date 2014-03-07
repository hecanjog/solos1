from pippi import dsp
from pippi import tune
from pippic.settings import get_param as p
from pippic.settings import voice as vp

shortname   = 'pp'
name        = 'pulsar'
device      = 'T6_pair1'
#device      = 'default'
loop        = True

def play(voice_id):
    if dsp.rand(0, 100) > 50:
        dsp.log('pulsar silent')
        return dsp.pad('', 0, dsp.stf(dsp.rand(1, 10)))

    volume      = p(voice_id, 'volume', dsp.rand(70.0, 100.0)) / 100.0

    nplays = vp(voice_id, 'plays')
    sectioni = vp(voice_id, 'sections')

    if nplays == 1:
        dsp.log('1!')

    if nplays >= 6:
        vp(voice_id, 'plays', 0)
        dsp.log("%s: p %s s %s" % (voice_id, nplays, sectioni))

        if sectioni > 10:
            vp(voice_id, 'sections', 0)
        else:
            vp(voice_id, 'sections', int(sectioni) + 1)

    melodies = [dsp.randchoose(['c', 'e', 'g', 'a'])]

    if sectioni % 2 == 0:
        melodies += [
                ['c', 'a'],
                ['c', 'g'],
        ]

    if sectioni % 3 == 0 and nplays % 5 == 0:
        #print 'more notes'
        melodies += [
            ['c', 'd', 'e', 'f'],
            ['c', 'g', 'e'],
            ['c', 'e', 'g', 'a'],
        ]

    notes = melodies[nplays % len(melodies)]

    octaves = dsp.breakpoint([ dsp.rand(1, 3) for o in range(100) ], 1000)
    octave = int(octaves[nplays % len(octaves)])

    root        = p(voice_id, 'root', 27.5)
    bpm         = p(voice_id, 'bpm', 80.0)

    lengths = dsp.breakpoint([ dsp.rand(0.5, 4) for o in range(20) ], 200)
    length = dsp.stf(lengths[nplays % len(lengths)])

    env         = p(voice_id, 'envelope', 'hann')

    mod         = p(voice_id, 'mod', 'random')
    modFreq     = p(voice_id, 'modfreq', dsp.rand(1.0, 2.5) / dsp.fts(length))

    modRange    = p(voice_id, 'speed', 0.02)
    modRange    = dsp.rand(0, modRange)

    pws = [0.1, 0.5, 0.05, 0.6, 1.0, 0.9, 0.2, 0.001]
    pulsewidth = pws[ nplays % len(pws) ]

    window      = p(voice_id, 'window', 'sine')
    waveform    = p(voice_id, 'waveform', 'sine2pi')

    glitch    = p(voice_id, 'glitch', False)

    beat = dsp.bpm2frames(bpm)

    tune.a0 = float(root)
    freqs   = [ tune.ntf(note, octave) for note in notes ]

    mod = dsp.wavetable(mod, 512)
    window = dsp.wavetable(window, 512)
    waveform = dsp.wavetable(waveform, 512)

    numgrains = int(dsp.rand(50, 500))

    pwc = dsp.breakpoint([ dsp.rand() for i in range(10) ], numgrains)

    ffc = []

    for freq in freqs:
        fffF = freq * dsp.rand(0.98, 1.03)
        ffc += [ dsp.breakpoint([ dsp.rand(freq, fffF) for i in range(50) ], numgrains) ]

    pc = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(5, numgrains))) ], numgrains)

    out = ''

    plens = dsp.breakpoint([ dsp.rand(1, 80) for o in range(int(dsp.rand(10, numgrains))) ], numgrains)

    if nplays == 1 or nplays == 5:
        dsp.log('siren!')
        sirenlen = dsp.mstf(dsp.rand(170, 2000))
        waveform = dsp.wavetable('vary', 512)
        window = dsp.wavetable('vary', 512)
        out = dsp.pan(dsp.env(dsp.amp(dsp.pulsar(2, sirenlen, 1.0, waveform, window, mod, dsp.rand(10, 200), dsp.rand(0.4, 0.6), volume), dsp.rand(0.8, 0.95)), 'sine'), dsp.rand())

        out = dsp.amp(out, 0.3)

        return out


    outlen = 0
    count = 0
    while outlen < length:
        layers = []

        plen = dsp.mstf(plens[nplays % len(plens)])

        if sectioni % 2 == 0:
            maxo = int(dsp.rand(2, 6))
        else:
            maxo = 1

        for iff, freq in enumerate(freqs):
            layers += [ dsp.pan(dsp.env(dsp.amp(dsp.pulsar(ffc[iff][count % len(ffc[iff])] * 2**int(dsp.rand(0, maxo)), plen, pwc[count % len(pwc)], waveform, window, mod, modRange, modFreq, volume), dsp.rand(0.2, 0.3)), 'sine'), pc[count % len(pc)]) ]

        layer = dsp.mix(layers)
        out += layer

        outlen += dsp.flen(layer)
        count += 1

    out = dsp.env(out, 'sine')

    return out

