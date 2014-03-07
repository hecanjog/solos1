from pippi import dsp
from pippic import settings as s

shortname   = 'ch'
name        = 'chirp'

def play(voice_id):
    if dsp.rand(0, 100) > 50:
        dsp.log('chirps silent')
        return dsp.pad('', 0, dsp.stf(dsp.rand(1, 10)))

    length = dsp.stf(dsp.rand(0.5, 1))

    nplays = s.voice(voice_id, 'plays')
    nsection = s.voice(voice_id, 'sections')

    dsp.log("%s: s %s p %s" % (voice_id, nsection, nplays))

    if nplays % 30 == 0:
        s.voice(voice_id, 'plays', 0)

    if nplays % 15 == 0:
        nsection += 1
        s.voice(voice_id, 'sections', nsection)

    if nplays % 3 == 0:
        section = 'busy'
    else:
        section = 'calm'

    def makecurve(length):
        # freq, length, pulsewidth, waveform, window, mod, modRange, modFreq, amp

        if section == 'calm':
            wf = dsp.breakpoint([0] + [ dsp.rand(-1, 1) for i in range(int(dsp.rand(5, 10))) ] + [0], 1024)
            win = dsp.breakpoint([0] + [ dsp.rand(0, 1) for i in range(4) ] + [0], 1024)
            mod = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(4, 8))) ], 1024)

            freq = dsp.rand(5000, 8000)

            modR = dsp.rand(0.5, 1.5)
            modF = 1.0 / dsp.fts(length)

            amp = dsp.rand(0.5, 0.9)

            pw = dsp.rand(0.1, 1.0)


        if section == 'busy':
            wf = dsp.breakpoint([0] + [ dsp.rand(-1, 1) for i in range(int(dsp.rand(5, 10))) ] + [0], 1024)
            win = dsp.breakpoint([0] + [ dsp.rand(0, 1) for i in range(4) ] + [0], 1024)
            mod = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(5, 80))) ], 1024)

            freq = dsp.rand(10000, 18000)

            modR = dsp.rand(0.5, 1.5)
            modF = 1.0 / dsp.fts(length)

            amp = dsp.rand(0.3, 0.8)

            pw = 1.0

        c = dsp.pulsar(freq, length, pw, wf, win, mod, modR, modF, amp)

        ngrains = len(c)
        pans = dsp.breakpoint([ dsp.rand(0,1) for i in range(100) ], ngrains)

        if section == 'calm':
            c = dsp.vsplit(c, dsp.mstf(1), dsp.mstf(30))
            c = [ dsp.randchoose(c) for i in range(int(dsp.rand(3, 10))) ]

            maxPad = 2000

        if section == 'busy':
            c = dsp.vsplit(c, dsp.mstf(1), dsp.mstf(100))
            c = dsp.packet_shuffle(c, 10)
            maxPad = 35

            speeds = dsp.breakpoint([ dsp.rand(0.25, 0.99) for i in range(100) ], ngrains)

            c = [ dsp.transpose(cg, speeds[i]) for i, cg in enumerate(c) ]


        c = [ dsp.pan(cg, pans[i]) for i, cg in enumerate(c) ]
        c = [ dsp.env(cg, 'sine') for i, cg in enumerate(c) ]
        c = [ dsp.pad(cg, 0, dsp.mstf(dsp.rand(10, maxPad))) for i, cg in enumerate(c) ]

        out = ''.join(c)

        #out = c

        return out

    out = makecurve(length)

    return out
