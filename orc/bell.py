from pippi import dsp
from pippic import settings

shortname   = 'be'
name        = 'bell'
#device      = 'T6_pair2'
device      = 'default'
loop        = True

guitar = dsp.read('sounds/bellarp.wav').data
guitar = dsp.transpose(guitar, 0.5)

scale = [1.0, 1.25, 1.5]

gamut = [ dsp.transpose(guitar, s * 0.25) for s in scale ]

def play(voice_id):
    bpm = float(settings.param(voice_id, 'bpm'))

    # Choose sound from gamut
    s = dsp.randchoose(gamut)

    beat = dsp.mstf(dsp.bpm2ms(bpm * 2))

    # Choose num beats
    numbeats = dsp.randint(1, 7)

    out = ''

    # for each beat:
    for b in range(numbeats):
        b = dsp.transpose(s, 2**dsp.randint(0, 6))

        # Cut to beat length
        b = dsp.fill(b, beat)

        # Envelope it
        b = dsp.env(b, 'phasor')

        # Pan it
        b = dsp.pan(b, dsp.rand())

        # Alias it
        #if dsp.randint(0,1) == 0:
            #b = dsp.alias(b)

        # Amp it
        b = dsp.amp(b, dsp.rand(0.5, 1.0))

        # Pinecone it
        #b = dsp.pine(b, dsp.flen(b) * 4, 245.27 * (2**dsp.randint(0,4)))

        out += b

    return out

