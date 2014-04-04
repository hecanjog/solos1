from pippi import dsp
from pippic import settings as s
import solo1 as bot

shortname   = 'ch'
name        = 'chirp'

def play(voice_id):
    tel = bot.getTel()

    bpm = s.config('bpm')

    #if 'gentle' in tel['name'] or 'upbeat' in tel['name'] or 'full' in tel['name']:
        #dsp.log('')
        #dsp.log(voice_id + ' chirps silent')
        #return dsp.pad('', 0, dsp.stf(dsp.rand(1, 10)))

    length = int((1.0 / (tel['pace'] / 10.0)) * dsp.stf(3))

    def makecurve(length):
        # freq, length, pulsewidth, waveform, window, mod, modRange, modFreq, amp

        wf = dsp.breakpoint([0] + [ dsp.rand(-1, 1) for i in range(int(dsp.rand(5, 30))) ] + [0], 1024)
        win = dsp.breakpoint([0] + [ dsp.rand(0, 1) for i in range(4) ] + [0], 1024)
        mod = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(4, 8))) ], 1024)

        smaxamp = dsp.rand(0.65, 0.95)
        amp = dsp.rand(0.01, smaxamp)

        pw = dsp.rand(0.1, 1.0)

        if 'upbeat' in tel['name']:
            wf = dsp.breakpoint([0] + [ dsp.rand(-1, 1) for i in range(int(dsp.rand(5, 30))) ] + [0], 1024)
            win = dsp.breakpoint([0] + [ dsp.rand(0, 1) for i in range(4) ] + [0], 1024)
            mod = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(5, 80))) ], 1024)


            pw = 1.0

        if 'ballsout' in tel['name']:
            wf = dsp.breakpoint([0] + [ dsp.rand(-1, 1) for i in range(int(dsp.rand(10, 40))) ] + [0], 1024)
            win = dsp.breakpoint([0] + [ dsp.rand(0, 1) for i in range(10) ] + [0], 1024)
            mod = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(20, 100))) ], 1024)


        if 'sparse' in tel['name']:
            amp = dsp.rand(0.7, 3)

        freq = tel['register'] * tel['roughness'] * (tel['density'] * tel['pace'] * 0.25)
        #if dsp.rand(0, 100) > 50:
            #freq = dsp.rand(2, 20)

        modR = tel['harmonicity']
        modF= tel['pace'] / 10.0

        c = dsp.pulsar(freq, length, pw, wf, win, mod, modR, modF, amp)

        ngrains = len(c)
        pans = dsp.breakpoint([ dsp.rand(0,1) for i in range(100) ], ngrains)

        maxPad = dsp.randint(2000, 4000)

        if 'sparse' in tel['name']:
            c = dsp.vsplit(c, dsp.mstf(0.5), dsp.mstf(tel['density'] * tel['harmonicity'] * tel['roughness'] * tel['pace']))
            c = [ dsp.randchoose(c) for i in range(int(dsp.rand(3, 10))) ]

        elif 'ballsout' in tel['name']:
            c = dsp.vsplit(c, dsp.mstf(0.1), dsp.mstf(400))
            c = dsp.packet_shuffle(c, dsp.randint(5, 10))

            speeds = dsp.breakpoint([ dsp.rand(tel['register'] * 0.1 + 0.2, tel['register'] + 0.2) for i in range(100) ], ngrains)

            c = [ dsp.transpose(cg, speeds[i]) for i, cg in enumerate(c) ]
            #c = [ dsp.amp(cg, dsp.rand(0.25, 1.25)) for i, cg in enumerate(c) ]

            for ic, cc in enumerate(c):
                if dsp.rand(0, 100) > 70:
                    c[ic] = dsp.tone(dsp.flen(cc), 11000, amp=0.5)

        elif 'upbeat' in tel['name']:
            beat = dsp.bpm2frames(bpm)
            c = dsp.split(c, beat)

            maxPad = 0

            c = [ dsp.pad(cg, 0, dsp.mstf(dsp.rand(10, beat / 4))) for i, cg in enumerate(c) ]

        else:
            c = dsp.vsplit(c, dsp.mstf(10), dsp.mstf(tel['density'] * tel['harmonicity'] * tel['roughness'] * tel['pace'] * dsp.rand(1, 10)))

        c = [ dsp.pan(cg, pans[i]) for i, cg in enumerate(c) ]
        c = [ dsp.env(cg, 'sine') for i, cg in enumerate(c) ]

        if 'sparse' in tel['name'] or 'ballsout' in tel['name']:
            speeds = dsp.breakpoint([ dsp.rand(0.5, 1.99) for i in range(100) ], ngrains)
            
            for ic, cc in enumerate(c):
                if dsp.flen(cc) < dsp.mstf(100):
                    c[ic] = cc + ''.join([ dsp.amp(cc, dsp.rand(0.1, 1.0)) for buh in range(dsp.randint(1, int(tel['density']))) ])

            c = [ dsp.transpose(cg, speeds[i]) for i, cg in enumerate(c) ]
            c = [ dsp.pan(cg, dsp.rand(0.0, 1.0)) for i, cg in enumerate(c) ]

        if 'ballsout' not in tel['name']:
            c = [ dsp.pad(cg, 0, dsp.mstf(dsp.rand(10, maxPad))) for i, cg in enumerate(c) ]

        out = ''.join(c)

        return out

    out = makecurve(length)

    if dsp.flen(out) > dsp.mstf(100) and dsp.rand(0, 100) > 30:
        out = dsp.drift(out, (tel['harmonicity'] - 10.0) * -1 * 0.5, dsp.randint(41, 441))

    if dsp.flen(out) > dsp.stf(10):
        out = dsp.fill(out, dsp.stf(10))

    if dsp.rand(0, 100) > 50:
        out = dsp.vsplit(out, 41, 441)
        for ii, o in enumerate(out):
            if dsp.rand(0, 100) > 50:
                out[ii] = dsp.pad('', 0, dsp.flen(o))
            elif dsp.rand(0, 100) > 50:
                out[ii] = dsp.amp(o, dsp.rand(0.75, 3))

        out = [ dsp.pan(o, dsp.rand()) for o in out ]

        out = ''.join(out)

    dsp.log('')
    dsp.log('chirp')
    dsp.log('%s length: %.2f' % (voice_id, dsp.fts(dsp.flen(out))))
    bot.show_telemetry(tel)

    return out
