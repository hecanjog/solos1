from pippi import dsp
from pippic import settings as s
import pulsar_bot as bot

shortname   = 'ch'
name        = 'chirp'

def play(voice_id):
    tel = bot.getTel()
    section = tel['name']

    bpm = s.config('bpm')

    if section == 'gentle' or section == 'upbeat' or section == 'full':
        dsp.log('')
        dsp.log(voice_id + ' chirps silent')
        return dsp.pad('', 0, dsp.stf(dsp.rand(1, 10)))

    length = int((1.0 / (tel['pace'] / 10.0)) * dsp.stf(3))

    def makecurve(length):
        # freq, length, pulsewidth, waveform, window, mod, modRange, modFreq, amp

        if section == 'sparse':
            wf = dsp.breakpoint([0] + [ dsp.rand(-1, 1) for i in range(int(dsp.rand(5, 10))) ] + [0], 1024)
            win = dsp.breakpoint([0] + [ dsp.rand(0, 1) for i in range(4) ] + [0], 1024)
            mod = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(4, 8))) ], 1024)

            freq = dsp.rand(5000, 8000)
            freq = tel['register'] * 1000 * dsp.rand(0.9, 1.1) 

            modR = dsp.rand(0.5, 1.5)
            modF = 1.0 / dsp.fts(length)
            modR = tel['harmonicity'] * 30
            modF= tel['pace'] / 5.0

            smaxamp = dsp.rand(3, 5)
            amp = dsp.rand(0.75, smaxamp)

            pw = dsp.rand(0.1, 1.0)

        if section == 'upbeat':
            wf = dsp.breakpoint([0] + [ dsp.rand(-1, 1) for i in range(int(dsp.rand(5, 10))) ] + [0], 1024)
            win = dsp.breakpoint([0] + [ dsp.rand(0, 1) for i in range(4) ] + [0], 1024)
            mod = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(5, 80))) ], 1024)

            freq = tel['register'] * 1000 * dsp.rand(0.9, 1.1) 

            modR = tel['harmonicity'] * 30
            modF= tel['pace'] / 5.0

            amp = dsp.rand(0.3, 0.5)

            pw = 1.0

        if section == 'ballsout':
            wf = dsp.breakpoint([0] + [ dsp.rand(-1, 1) for i in range(int(dsp.rand(10, 30))) ] + [0], 1024)
            win = dsp.breakpoint([0] + [ dsp.rand(0, 1) for i in range(10) ] + [0], 1024)
            mod = dsp.breakpoint([ dsp.rand(0, 1) for i in range(int(dsp.rand(20, 100))) ], 1024)

            freq = tel['register'] * 1000 * dsp.rand(0.9, 1.1) 

            modR = tel['harmonicity'] * 30
            modF= tel['pace'] / 5.0

            #modR = dsp.rand(0.5, 1.5)
            #modF = 1.0 / dsp.fts(length)

            amp = dsp.rand(0.3, 0.8)

            pw = 1.0

        c = dsp.pulsar(freq, length, pw, wf, win, mod, modR, modF, amp)

        ngrains = len(c)
        pans = dsp.breakpoint([ dsp.rand(0,1) for i in range(100) ], ngrains)

        if section == 'sparse':
            c = dsp.vsplit(c, dsp.mstf(0.5), dsp.mstf(6))
            c = [ dsp.randchoose(c) for i in range(int(dsp.rand(3, 10))) ]

            maxPad = dsp.randint(2000, 4000)

        if section == 'ballsout':
            c = dsp.vsplit(c, dsp.mstf(0.1), dsp.mstf(30))
            c = dsp.packet_shuffle(c, 10)
            maxPad = dsp.randint(0, 100)

            speeds = dsp.breakpoint([ dsp.rand(0.5, 1.99) for i in range(100) ], ngrains)

            c = [ dsp.transpose(cg, speeds[i]) for i, cg in enumerate(c) ]
            c = [ dsp.amp(cg, dsp.rand(0.25, 5.0)) for i, cg in enumerate(c) ]

            for ic, cc in enumerate(c):
                if dsp.rand(0, 100) > 70:
                    c[ic] = dsp.tone(dsp.flen(cc), 11000, amp=0.5)

            for ic, cc in enumerate(c):
                if dsp.rand(0, 100) > 50:
                    c[ic] = dsp.pad('', 0, dsp.flen(cc))


        if section == 'upbeat':
            beat = dsp.bpm2frames(bpm)
            c = dsp.split(c, beat)

            maxPad = 0

            c = [ dsp.pad(cg, 0, dsp.mstf(dsp.rand(10, beat / 4))) for i, cg in enumerate(c) ]

        c = [ dsp.pan(cg, pans[i]) for i, cg in enumerate(c) ]
        c = [ dsp.env(cg, 'sine') for i, cg in enumerate(c) ]

        if section == 'sparse' or section == 'ballsout':
            speeds = dsp.breakpoint([ dsp.rand(0.5, 1.99) for i in range(100) ], ngrains)
            c = [ cg * dsp.randint(1, int(tel['density'])) for cg in c ]
            c = [ dsp.transpose(cg, speeds[i]) for i, cg in enumerate(c) ]
            c = [ dsp.pan(cg, dsp.rand(0.0, 1.0)) for i, cg in enumerate(c) ]

        c = [ dsp.pad(cg, 0, dsp.mstf(dsp.rand(10, maxPad))) for i, cg in enumerate(c) ]

        out = ''.join(c)

        return out

    out = makecurve(length)

    dsp.log('')
    dsp.log('chirp')
    dsp.log('%s length: %.2f' % (voice_id, dsp.fts(dsp.flen(out))))
    bot.show_telemetry(tel)

    return out
