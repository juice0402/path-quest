/* ---------- sound (11/5): everything is made right here with Web Audio, no sound files.
   a toy-box band (xylophone, music box, glockenspiel, bells, a melodica, a toy drum) plays one tune per land,
   the captain's march when he is near, a short tune on the result paper; every move has its own little sound.
   build: tools/audio/build_sound.py puts this file between the SND markers of the game ---------- */
var AUD=(()=>{
  const AC=window.AudioContext||window.webkitAudioContext;
  let bouncing=false,ctx=null,master=null,mBus=null,sBus=null,rv=null,nb=null,on=true,ok=false,players=[],cur=null,jing=null,last={},stepK=0;
  try{on=localStorage.getItem('pq.snd')!=='0'}catch(err){}
  const NT={C:0,D:2,E:4,F:5,G:7,A:9,B:11};
  const nm=s=>{const m=/^([A-G])([#b]?)(-?\d)$/.exec(s);return m?12*(+m[3]+1)+NT[m[1]]+(m[2]==='#'?1:m[2]==='b'?-1:0):null};
  const hz=m=>440*Math.pow(2,(m-69)/12);

  function boot(){
    if(ctx||!AC)return ctx;
    try{if(navigator.audioSession)navigator.audioSession.type='ambient'}catch(err){}
    try{ctx=new AC()}catch(err){ctx=null;return null}
    graph();setInterval(tick,25);setInterval(sync,400);
    return ctx;
  }
  function graph(){ /* the mixing desk: music and sounds, a little room echo, a soft limiter */
    const comp=ctx.createDynamicsCompressor();
    comp.threshold.value=-16;comp.knee.value=12;comp.ratio.value=3.5;comp.attack.value=.005;comp.release.value=.25;
    master=ctx.createGain();master.gain.value=on?.9:0;
    mBus=ctx.createGain();mBus.gain.value=.25;
    sBus=ctx.createGain();sBus.gain.value=.8;
    rv=ctx.createConvolver();
    const L=Math.floor(ctx.sampleRate*1.5),ir=ctx.createBuffer(2,L,ctx.sampleRate);
    for(let c=0;c<2;c++){const d=ir.getChannelData(c);for(let i=0;i<L;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/L,3.2)}
    rv.buffer=ir;
    const rg=ctx.createGain();rg.gain.value=.5;rv.connect(rg);rg.connect(comp);
    const mw=ctx.createGain();mw.gain.value=.3;mBus.connect(mw);mw.connect(rv);
    const sw=ctx.createGain();sw.gain.value=.12;sBus.connect(sw);sw.connect(rv);
    mBus.connect(comp);sBus.connect(comp);comp.connect(master);master.connect(ctx.destination);
    nb=ctx.createBuffer(1,ctx.sampleRate,ctx.sampleRate);
    const nd=nb.getChannelData(0);for(let i=0;i<nd.length;i++)nd[i]=Math.random()*2-1;
  }
  const live=()=>!!(ctx&&ok&&on&&ctx.state==='running');

  /* ---- building blocks ---- */
  function gain(dest,v){const g=ctx.createGain();g.gain.value=v==null?1:v;g.connect(dest);return g}
  function env(g,t,a,peak,dec){g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(Math.max(.0002,peak),t+a);g.gain.exponentialRampToValueAtTime(.0001,t+a+dec)}
  function osc(type,f,t,stop,dest){const o=ctx.createOscillator();o.type=type;o.frequency.setValueAtTime(f,t);o.connect(dest);o.start(t);o.stop(stop);return o}
  function noise(t,dur,dest,type,f,q){
    const s=ctx.createBufferSource();s.buffer=nb;const b=ctx.createBiquadFilter();b.type=type||'bandpass';b.frequency.setValueAtTime(f||2000,t);b.Q.value=q==null?1:q;
    s.connect(b);b.connect(dest);s.start(t,Math.random()*.5,dur+.05);return {s,b};
  }

  /* ---- the toy-box band: each voice plays one note (time, frequency, length, loudness, where to) ---- */
  const V={
    xylo(t,f,d,v,o){const dec=Math.max(.14,.55-f/3600),g=gain(o,0);env(g,t,.002,v,dec);osc('sine',f,t,t+dec+.05,g);
      const g2=gain(o,0);env(g2,t,.001,v*.22,dec*.25);osc('sine',f*4,t,t+dec*.3+.02,g2);
      const g3=gain(o,0);env(g3,t,.001,v*.12,.02);noise(t,.02,g3,'bandpass',3200,1)},
    mbox(t,f,d,v,o){const g=gain(o,0);env(g,t,.003,v*.7,1.5);osc('sine',f,t,t+1.6,g);osc('sine',f*1.004,t,t+1.6,g);
      const g2=gain(o,0);env(g2,t,.002,v*.3,.35);osc('sine',f*3,t,t+.4,g2);
      const g3=gain(o,0);env(g3,t,.001,v*.1,.012);noise(t,.012,g3,'highpass',5000,.7)},
    glock(t,f,d,v,o){const g=gain(o,0);env(g,t,.002,v,1.3);osc('sine',f,t,t+1.4,g);
      const g2=gain(o,0);env(g2,t,.002,v*.32,.45);osc('sine',f*2.76,t,t+.5,g2);
      const g3=gain(o,0);env(g3,t,.001,v*.14,.18);osc('sine',f*5.4,t,t+.2,g3)},
    bell(t,f,d,v,o){const g=gain(o,0);env(g,t,.002,v,2);const c=osc('sine',f,t,t+2.1,g);
      const m=ctx.createOscillator();m.frequency.setValueAtTime(f*1.4,t);const mg=ctx.createGain();
      mg.gain.setValueAtTime(f*2.2,t);mg.gain.exponentialRampToValueAtTime(f*.04,t+1.5);m.connect(mg);mg.connect(c.frequency);m.start(t);m.stop(t+2.1)},
    reed(t,f,d,v,o){const lp=ctx.createBiquadFilter();lp.type='lowpass';lp.frequency.setValueAtTime(Math.min(3800,f*4.5),t);lp.Q.value=.6;
      const g=gain(o,0);lp.connect(g);const e=t+Math.max(.06,d*.92);
      g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(v*.5,t+.025);g.gain.setTargetAtTime(v*.38,t+.03,.08);g.gain.setTargetAtTime(.0001,e,.035);
      const a=osc('sawtooth',f,t,e+.25,lp),b=osc('square',f*1.004,t,e+.25,lp);
      if(d>.25){const vg=ctx.createGain();vg.gain.value=f*.006;osc('sine',5.5,t+.18,e+.25,vg);vg.connect(a.frequency);vg.connect(b.frequency)}},
    bass(t,f,d,v,o){const g=gain(o,0),e=Math.min(d,.7);g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(v,t+.008);
      g.gain.setTargetAtTime(v*.4,t+.012,.09);g.gain.setTargetAtTime(.0001,t+e,.05);osc('triangle',f,t,t+e+.4,g);
      const g2=gain(o,0);env(g2,t,.003,v*.45,.1);osc('sine',f*2,t,t+.14,g2)},
    pluck(t,f,d,v,o){const lp=ctx.createBiquadFilter();lp.type='lowpass';lp.frequency.setValueAtTime(f*6,t);lp.frequency.exponentialRampToValueAtTime(f*1.5,t+.3);
      const g=gain(o,0);lp.connect(g);env(g,t,.002,v,.6);osc('triangle',f,t,t+.7,lp);osc('sine',f*2,t,t+.3,lp)},
    pad(t,f,d,v,o){const g=gain(o,0),e=t+Math.max(.3,d);g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(v,t+.3);
      g.gain.setValueAtTime(v,e);g.gain.exponentialRampToValueAtTime(.0001,e+.5);osc('triangle',f,t,e+.55,g);osc('sine',f*1.006,t,e+.55,g)}
  };
  const DR={
    kick(t,v,o){const g=gain(o,0);env(g,t,.003,v,.22);const x=osc('sine',160,t,t+.26,g);x.frequency.exponentialRampToValueAtTime(52,t+.14)},
    snare(t,v,o){const g=gain(o,0);env(g,t,.002,v,.13);noise(t,.14,g,'bandpass',1900,.8);const g2=gain(o,0);env(g2,t,.002,v*.5,.06);osc('triangle',230,t,t+.08,g2)},
    wood(t,v,o){const g=gain(o,0);env(g,t,.001,v,.05);osc('sine',1250,t,t+.07,g);const g2=gain(o,0);env(g2,t,.001,v*.4,.015);noise(t,.015,g2,'bandpass',2600,1.5)},
    shaker(t,v,o){const g=gain(o,0);env(g,t,.006,v,.05);noise(t,.07,g,'highpass',6500,.7)},
    tamb(t,v,o){for(let k=0;k<3;k++){const g=gain(o,0);env(g,t+k*.016,.002,v*(1-k*.25),.07);noise(t+k*.016,.08,g,'bandpass',8200,2.5)}},
    tri(t,v,o){const g=gain(o,0);env(g,t,.002,v,1.1);osc('sine',2350,t,t+1.2,g);osc('sine',5600,t,t+.5,g)}
  };

  /* ---- the tunes. chords: one bar per "|", a bar can hold two chords. melody: one token per step
     (a note, "-" holds the one before, "." rests). patterns repeat every bar: R 3 5 7 8 = chord tones,
     h H = 3rd and 5th an octave up, c = the chord above the root, C = the whole chord. drums: x hit, X loud ---- */
  const SONGS={
    home:{bpm:100,bpb:3,chords:'C|Em|F|C|Dm|G|Em|G|C|Em|F|Am|Dm|G|C|C',tracks:[
      {ins:'mbox',v:.5,res:2,mel:'E5 - G5 - C6 - | B5 - G5 - E5 - | A5 - C6 - A5 G5 | E5 - - - - - | F5 - A5 - D6 - | B5 - A5 G5 F5 - | E5 - G5 - B5 - | D6 - - - . . | E6 - D6 C6 G5 - | B5 - G5 - E5 - | F5 G5 A5 - C6 - | E6 - - - C6 - | D6 - C6 A5 F5 - | G5 - B5 - D6 - | C6 - G5 - E5 - | C6 - - - . .'},
      {ins:'bass',v:.34,res:2,oct:3,pat:'R - . . . .'},
      {ins:'xylo',v:.11,res:2,oct:4,pat:'. . c . c .'}]},
    grass:{bpm:126,bpb:4,chords:'F|C|Dm|Bb|F|C|Bb C|F|Bb|C|Am|Dm|Bb|C|Bb C|F',tracks:[
      {ins:'xylo',v:.55,res:2,mel:'C5 F5 A5 C6 - A5 G5 F5 | G5 - E5 C5 - . G5 A5 | A5 - F5 D5 - . A5 C6 | D6 - C6 Bb5 A5 - G5 - | C5 F5 A5 C6 - A5 G5 F5 | G5 - C6 Bb5 A5 - G5 - | F5 G5 A5 Bb5 C6 - E5 - | F5 - - - . . C5 . | D5 F5 Bb5 - A5 - G5 - | E5 G5 C6 - Bb5 - A5 - | C6 - A5 - E5 - A5 - | F5 - A5 - D6 - C6 - | Bb5 - A5 G5 F5 - D5 - | E5 - G5 - C6 - Bb5 - | A5 - F5 - G5 - E5 - | F5 - - - . . . .'},
      {ins:'bass',v:.4,res:2,oct:3,pat:'R . 5 . R . 5 .'},
      {ins:'pluck',v:.1,res:2,oct:4,pat:'. c . c . c . c'},
      {drum:'kick',v:.34,res:2,pat:'x . . . x . . .'},
      {drum:'wood',v:.16,res:2,pat:'. . x . . . x .'},
      {drum:'shaker',v:.07,res:2,pat:'x x X x x x X x'}]},
    forest:{bpm:66,bpb:2,chords:'G|Em|C|D|G|Em|Am D|G|C|D|Bm|Em|C|D|G|G',tracks:[
      {ins:'mbox',v:.5,res:3,mel:'D5 - G5 B5 - A5 | G5 - E5 B4 - - | C5 - E5 G5 - E5 | F#5 - - A5 - - | D5 - G5 B5 - D6 | E6 - D6 B5 - G5 | A5 - C6 F#5 - A5 | G5 - - - - - | E5 - G5 C6 - B5 | A5 - F#5 D5 - - | D5 - F#5 B5 - A5 | G5 - - E5 - - | C6 - B5 A5 - G5 | F#5 - A5 D6 - C6 | B5 - A5 G5 - D5 | G5 - - - - -'},
      {ins:'xylo',v:.1,res:3,oct:4,pat:'R 5 8 h 8 5'},
      {ins:'bass',v:.3,res:3,oct:3,pat:'R - - 5 - -'},
      {drum:'wood',v:.08,res:3,pat:'x . . x . .'},
      {drum:'shaker',v:.04,res:3,pat:'. x x . x x'}]},
    lake:{bpm:92,bpb:4,chords:'Dmaj7|Bm7|Gmaj7|A|Dmaj7|F#m7|Gmaj7|A|Bm7|F#m7|Gmaj7|Dmaj7|Em7|A|D|D',tracks:[
      {ins:'glock',v:.38,res:2,mel:'F#5 - A5 - C#6 - - - | B5 - - A5 F#5 - - - | G5 - B5 - D6 - F#6 - | E6 - - - C#6 - - - | F#5 - A5 - D6 - C#6 - | A5 - - F#5 E5 - - - | D5 E5 F#5 G5 A5 - B5 - | C#6 - - - . . . . | D6 - - B5 F#5 - - - | C#6 - - A5 F#5 - - - | B5 - D6 - F#6 - E6 - | D6 - A5 - F#5 - - - | G5 - B5 - E6 - D6 - | C#6 - B5 - A5 - G5 - | F#5 - A5 - D6 - - - | D6 - - - . . . .'},
      {ins:'pluck',v:.1,res:4,oct:4,pat:'R 5 8 3 h 8 5 3 R 5 8 3 h 8 5 3'},
      {ins:'pad',v:.05,res:2,oct:4,pat:'C - - - - - - -'},
      {ins:'bass',v:.3,res:2,oct:3,pat:'R - - - 5 - - -'},
      {drum:'tri',v:.05,res:2,pat:'x . . . . . . .'},
      {drum:'shaker',v:.04,res:2,pat:'. . x . . . x .'}]},
    snow:{bpm:80,bpb:4,chords:'Am|F|C|G|Am|F|Dm E|Am|F|G|Em|Am|Dm|G|C E|Am',tracks:[
      {ins:'bell',v:.55,res:2,mel:'E5 - - - A5 - B5 - | C6 - - - A5 - - - | G5 - - - E5 - G5 - | D5 - - - - - . . | E5 - - - A5 - C6 - | D6 - - - C6 - A5 - | F5 - A5 - G#5 - B5 - | A5 - - - - - . . | A5 - C6 - F6 - E6 - | D6 - - - B5 - G5 - | E6 - D6 - B5 - G5 - | A5 - - - E5 - - - | F5 - A5 - D6 - C6 - | B5 - - - D6 - G5 - | C6 - E6 - B5 - G#5 - | A5 - - - - - . .'},
      {ins:'pad',v:.08,res:2,oct:4,pat:'C - - - - - - -'},
      {ins:'bass',v:.3,res:2,oct:3,pat:'R - - - - - - -'},
      {ins:'mbox',v:.09,res:2,oct:5,pat:'. . 5 . . . 8 .'},
      {drum:'tamb',v:.05,res:2,pat:'x . x . x . x .'}]},
    castle:{bpm:112,bpb:4,chords:'G|D|G|C D|G|Em|A7|D|G|C|G|Em|C|D|G D|G',tracks:[
      {ins:'reed',v:.3,res:2,mel:'G4 - B4 D5 G5 - D5 - | F#5 - A5 - D5 - . . | G5 - B5 - D6 - B5 - | C6 - A5 - F#5 - D5 - | G5 - G5 A5 B5 - G5 - | E5 - G5 B5 E6 - B5 - | C#6 - A5 - E5 - G5 - | F#5 - - - A5 . D5 . | G5 - B5 - D6 - G5 - | E6 - C6 - G5 - E5 - | D5 - G5 - B5 - G5 - | B5 - G5 - E5 - G5 - | C6 - E6 - C6 - A5 - | D6 - A5 - F#5 - A5 - | B5 - G5 - A5 - F#5 - | G5 - - - . . . .'},
      {ins:'xylo',v:.1,res:2,tr:12,mel:'@0'},
      {ins:'bass',v:.36,res:2,oct:3,pat:'R . . . 5 . . .'},
      {ins:'pluck',v:.1,res:2,oct:4,pat:'. . c . . . c .'},
      {drum:'kick',v:.3,res:2,pat:'x . . . x . . .'},
      {drum:'snare',v:.16,res:2,pat:'. . x . . . x .'},
      {drum:'shaker',v:.05,res:2,pat:'x x x x x x x x'}]},
    boss:{bpm:150,bpb:4,chords:'Dm|Dm|Bb|A|Dm|Gm|A|A|Gm|Dm|Bb|A|Gm|Dm|E A|Dm',tracks:[
      {ins:'reed',v:.3,res:2,mel:'D5 . D5 . F5 E5 D5 . | A5 . A5 . G5 F5 E5 . | F5 . F5 . Bb5 A5 G5 . | E5 - - . C#5 - E5 - | D5 F5 A5 D6 C6 A5 F5 D5 | G5 Bb5 D6 Bb5 G5 - D5 - | E5 G5 A5 C#6 E6 - C#6 A5 | A5 - - - . . . . | G5 . G5 . Bb5 A5 G5 . | F5 . F5 . A5 G5 F5 . | Bb5 . A5 . G5 . F5 . | E5 . F5 . G5 . A5 . | D6 . C6 . Bb5 . A5 . | A5 . G5 . F5 . D5 . | E5 - G#5 - A5 - C#6 - | D6 - - . D5 . . .'},
      {ins:'xylo',v:.11,res:2,tr:12,mel:'@0'},
      {ins:'bass',v:.4,res:2,oct:3,pat:'R . R . 5 . R .'},
      {drum:'kick',v:.32,res:2,pat:'x . . . x . x .'},
      {drum:'snare',v:.17,res:2,pat:'. . x . . . x x'},
      {drum:'wood',v:.06,res:2,pat:'. x . x . x . x'},
      {drum:'shaker',v:.05,res:2,pat:'x x x x x x x x'}]},
    win:{bpm:132,bpb:4,once:1,chords:'C|C',tracks:[
      {ins:'reed',v:.32,res:2,mel:'G4 G4 G4 C5 - - E5 G5 | C6 - - - . . . .'},
      {ins:'xylo',v:.14,res:2,tr:12,mel:'@0'},
      {ins:'bass',v:.36,res:2,oct:3,pat:'R . . . 5 . . .'},
      {drum:'kick',v:.3,res:2,pat:'x . . . x . . .'},
      {drum:'tri',v:.05,res:2,pat:'x . . . . . . .'}]},
    quit:{bpm:100,bpb:4,once:1,chords:'C|C',tracks:[
      {ins:'mbox',v:.5,res:2,mel:'E5 G5 C6 - B5 - G5 - | C6 - - - . . . .'},
      {ins:'bass',v:.3,res:2,oct:3,pat:'R - - - - - - -'},
      {ins:'xylo',v:.1,res:2,oct:4,pat:'. . c . . . c .'}]},
    lose:{bpm:92,bpb:4,once:1,chords:'C G|G C',tracks:[
      {ins:'mbox',v:.5,res:2,mel:'G5 - E5 - C5 - D5 - | B4 - - - C5 - - -'},
      {ins:'bass',v:.3,res:2,oct:3,pat:'R - - - R - - -'}]}
  };
  const QL={'':[0,4,7],m:[0,3,7],'7':[0,4,7,10],maj7:[0,4,7,11],m7:[0,3,7,10],dim:[0,3,6],sus4:[0,5,7]};
  function chordOf(s){const m=/^([A-G])([#b]?)(.*)$/.exec(s);return {r:NT[m[1]]+(m[2]==='#'?1:m[2]==='b'?-1:0),iv:QL[m[3]]||QL['']}}
  const toks=s=>s.replace(/\|/g,' ').trim().split(/\s+/);
  for(const k in SONGS){ /* read every tune once */
    const S=SONGS[k];S.bars=S.chords.split('|').map(b=>b.trim().split(/\s+/).map(chordOf));
    S.grid=Math.max(...S.tracks.map(x=>x.res));
    S.tracks.forEach(x=>{if(x.mel)x.tk=x.mel==='@0'?S.tracks[0].tk:toks(x.mel);if(x.pat)x.tk=toks(x.pat)});
  }
  function tone(c,tok,base){ /* a pattern token on a chord → midi notes */
    const r=base+c.r,iv=c.iv;
    switch(tok){case 'R':return [r];case '3':return [r+iv[1]];case '5':return [r+iv[2]];case '7':return [iv[3]!=null?r+iv[3]:r+12];
      case '8':return [r+12];case 'h':return [r+iv[1]+12];case 'H':return [r+iv[2]+12];case 'c':case 'C':{const q=r-(c.r>=7?12:0);return tok==='c'?[q+iv[1],q+iv[2],q+12]:[q,q+iv[1],q+iv[2]]}}
    return [];
  }
  function holdOf(tk,i){let n=1;while(tk[(i+n)%tk.length]==='-'&&n<tk.length)n++;return n}

  /* ---- the player: looks a little ahead and books the notes on the audio clock ---- */
  function start(id,o){
    const S=SONGS[id];if(!S)return null;
    const tr=(o&&o.tr)||0,bpm=S.bpm*((o&&o.fast)||1),t0=ctx.currentTime+.06;
    const g=ctx.createGain();g.gain.setValueAtTime(.0001,t0);g.gain.setTargetAtTime(1,t0,S.once?.02:.35);g.connect(mBus);
    const p={id,key:(o&&o.key)||id,S,g,tr,dt:60/bpm/S.grid,next:t0,step:0,end:0,total:S.once?S.bars.length*S.bpb*S.grid:0};
    players.push(p);return p;
  }
  function fade(p){if(!p||p.end)return;const t=ctx.currentTime;p.g.gain.cancelScheduledValues(t);p.g.gain.setTargetAtTime(.0001,t,.3);p.end=t+1.4}
  function book(p,step,t){
    const S=p.S,G=S.grid,perBar=S.bpb*G,bar=Math.floor(step/perBar)%S.bars.length,inBar=step%perBar;
    const cs=S.bars[bar],c=cs[Math.min(cs.length-1,Math.floor(inBar/(perBar/cs.length)))];
    for(const x of S.tracks){
      const k=G/x.res;if(step%k)continue;
      const idx=step/k,tk=x.tk,i=x.mel?idx%tk.length:idx%(S.bpb*x.res),tok=tk[i];
      if(tok==='.'||tok==='-')continue;
      if(x.drum){DR[x.drum](t,x.v*(tok==='X'?1.4:1),p.g);continue}
      const len=holdOf(tk,i)*k*p.dt,v=x.v;
      if(x.mel){const m=nm(tok);if(m!=null)V[x.ins](t,hz(m+p.tr+(x.tr||0)),len,v,p.g);continue}
      const ns=tone(c,tok,12*((x.oct||4)+1)+p.tr);const vv=ns.length>1?v*.7:v;
      for(const m of ns)V[x.ins](t,hz(m),len,vv,p.g);
    }
  }
  function tick(){
    if(bouncing||!ctx||ctx.state!=='running')return;
    const now=ctx.currentTime;
    for(const p of players){
      if(p.next<now-.25){const n=Math.ceil((now-p.next)/p.dt);p.step+=n;p.next+=n*p.dt} /* woke up late: skip, do not burst */
      while(p.next<now+.14&&!(p.total&&p.step>=p.total)){if(on)book(p,p.step,p.next);p.step++;p.next+=p.dt}
      if(p.total&&p.step>=p.total&&!p.end)p.end=p.next+1.6;
    }
    players=players.filter(p=>{if(p.end&&now>p.end){try{p.g.disconnect()}catch(err){}if(cur===p)cur=null;if(jing===p)jing=null;return false}return true});
  }

  /* ---- which tune now ---- */
  const vis=id=>{const e=document.getElementById(id);return !!e&&!e.hidden};
  function wanted(){
    if(vis('s-over'))return jing?jing.key:'home';
    if(typeof run==='undefined'||!run||vis('s-title')||vis('s-shop'))return 'home';
    const r=rowOf(run.at),s=stepOf(r),dm=dimOf(r);
    if(s>0&&(s%SPAN>=SPAN-3||s%DIM_LEN>=DIM_LEN-3))return 'boss'+(dm?'@'+dm:'');
    return areaOf(r).k+(dm?'@'+dm:'');
  }
  function sync(){
    if(bouncing||!live()||document.hidden)return;
    const w=wanted();if(cur&&cur.key===w&&!cur.end)return;
    if(jing&&w===jing.key)return;
    const [id,dm]=w.split('@'),d=+dm||0;
    fade(cur);cur=start(id,{key:w,tr:[0,2,-3,5][d%4],fast:d?1.05:1});
  }
  function over(kind){ /* the result paper: a short tune, then the home tune */
    if(!live())return;fade(cur);cur=null;if(jing)fade(jing);jing=start(kind,{key:kind});
  }

  /* ---- little sounds ---- */
  const tn=(ins,m,t,d,v)=>V[ins](t,hz(m),d||.2,v,sBus);
  function sweep(type,f1,f2,t,dur,v,lp){
    const g=gain(sBus,0);env(g,t,.006,v,dur);const o=ctx.createOscillator();o.type=type;o.frequency.setValueAtTime(f1,t);o.frequency.exponentialRampToValueAtTime(f2,t+dur);
    let d=g;if(lp){const f=ctx.createBiquadFilter();f.type='lowpass';f.frequency.value=lp;f.connect(g);d=f}o.connect(d);o.start(t);o.stop(t+dur+.1);return o;
  }
  function nz(t,dur,v,type,f,q,f2){const g=gain(sBus,0);env(g,t,.004,v,dur);const n=noise(t,dur,g,type,f,q);if(f2)n.b.frequency.exponentialRampToValueAtTime(f2,t+dur);return n}
  function whistle(f1,f2,t,dur,v){const g=gain(sBus,0);env(g,t,.02,v,dur);const x=ctx.createOscillator();x.frequency.setValueAtTime(f1,t);x.frequency.exponentialRampToValueAtTime(f2,t+dur);
    const l=ctx.createOscillator(),lg=ctx.createGain();l.frequency.value=8.5;lg.gain.value=f1*.02;l.connect(lg);lg.connect(x.frequency);x.connect(g);x.start(t);x.stop(t+dur+.05);l.start(t);l.stop(t+dur+.05)}
  const arp=(ins,ns,t,gap,d,v)=>ns.forEach((n,k)=>tn(ins,nm(n),t+k*gap,d,v));
  const S={
    tap:t=>sweep('sine',1500,1100,t,.035,.1),
    place:t=>{sweep('sine',190,95,t,.12,.32);sweep('triangle',640,520,t,.07,.2);nz(t,.03,.22,'bandpass',2300,1.2)},
    nope:t=>{sweep('square',250,230,t,.07,.07,900);sweep('square',196,186,t+.09,.1,.07,900)},
    step:t=>{stepK^=1;sweep('sine',stepK?1050:880,stepK?900:760,t,.03,.05)},
    swing:t=>nz(t,.13,.5,'bandpass',700,1.4,3200),
    hit:t=>{sweep('sine',320,170,t,.09,.3);nz(t,.05,.2,'bandpass',1500,1)},
    crit:t=>{S.hit(t);tn('glock',nm('E6'),t+.02,.3,.18);tn('glock',nm('B6'),t+.07,.3,.14)},
    tock:t=>sweep('sine',760,420,t,.05,.14),
    clink:t=>[2300,3450,5150].forEach((f,k)=>{const g=gain(sBus,0);env(g,t,.002,.12/(k+1),.35);osc('sine',f,t,t+.4,g)}),
    block:t=>{sweep('sine',420,330,t,.09,.22);nz(t,.06,.13,'bandpass',900,1.5);S.clink(t+.01)},
    hurt:(t,o)=>{const f=o.boss?620:880,g=gain(sBus,0);env(g,t,.01,.28,.2);const x=ctx.createOscillator();x.frequency.setValueAtTime(f,t);
      x.frequency.linearRampToValueAtTime(f*1.25,t+.05);x.frequency.exponentialRampToValueAtTime(f*.6,t+.2);x.connect(g);x.start(t);x.stop(t+.25)},
    kill:t=>{sweep('sine',260,900,t,.07,.24);arp('xylo',['C6','E6','G6'],t+.06,.035,.2,.13)},
    bigkill:t=>{arp('reed',['G4','C5','E5','G5'],t,.09,.12,.17);tn('reed',nm('C6'),t+.36,.45,.2);tn('glock',nm('C7'),t+.36,.6,.12);S.boom(t,{small:1})},
    coin:t=>{tn('glock',nm('B5'),t,.1,.11);tn('glock',nm('E6'),t+.06,.3,.11)},
    eat:t=>{nz(t,.04,.18,'bandpass',1400,2);nz(t+.08,.04,.16,'bandpass',1100,2);arp('xylo',['C6','E6'],t+.16,.05,.2,.13)},
    chest:t=>{arp('glock',['G5','B5','D6','G6'],t,.07,.4,.15);nz(t+.28,.3,.04,'highpass',7000,.7)},
    reward:t=>arp('mbox',['C6','E6','G6','C7'],t,.08,.5,.17),
    level:t=>{arp('xylo',['C5','E5','G5','C6','E6'],t,.05,.2,.18);tn('bell',nm('G6'),t+.27,.6,.07)},
    evolve:t=>{['C5','E5','G5'].forEach(n=>tn('reed',nm(n),t,.35,.11));['F5','A5','C6'].forEach(n=>tn('reed',nm(n),t+.4,.3,.1));arp('glock',['C6','E6','G6','C7','E7','G7'],t+.72,.05,.4,.11)},
    dice:t=>{for(let k=0;k<6;k++)sweep('sine',1200+Math.random()*700,900,t+k*.045+Math.random()*.015,.025,.11)},
    skill:t=>{arp('glock',['E6','G#6','B6','E7'],t,.04,.3,.11);nz(t,.4,.04,'highpass',6000,.7)},
    plane:t=>nz(t,.28,.42,'bandpass',600,2,2600),
    boomer:t=>{const n=nz(t,.38,.5,'bandpass',900,3),l=ctx.createOscillator(),lg=ctx.createGain();l.frequency.value=13;lg.gain.value=500;l.connect(lg);lg.connect(n.b.frequency);l.start(t);l.stop(t+.45)},
    boom:(t,o)=>{sweep('sine',140,38,t,o.small?.25:.4,o.small?.28:.5);nz(t,o.small?.2:.35,o.small?.14:.28,'lowpass',900,.7,200)},
    cannon:t=>{S.boom(t,{});nz(t,.05,.18,'bandpass',2500,1)},
    bubble:t=>sweep('sine',500,1500,t,.09,.13),
    pop:t=>{nz(t,.03,.16,'highpass',3000,.7);sweep('sine',1800,2400,t,.03,.07)},
    pon:t=>{sweep('sine',420,760,t,.06,.1);nz(t,.02,.05,'bandpass',2500,1)},
    t_atk:t=>sweep('triangle',700,480,t,.06,.09),
    t_dodge:t=>nz(t,.12,.36,'bandpass',1200,1.5,3600),
    t_armor:t=>S.clink(t),
    t_revive:t=>{for(let k=0;k<7;k++)sweep('sine',k%2?720:940,k%2?650:860,t+k*.06,.03,.11)},
    t_wind:t=>{for(let k=0;k<9;k++)sweep('square',500+k*60,480+k*60,t+k*.055,.018,.045,2400)},
    t_rage:t=>{tn('reed',nm('E4'),t,.07,.15);tn('reed',nm('E4'),t+.11,.18,.15);tn('reed',nm('G4'),t+.3,.12,.13)},
    t_flee:t=>whistle(600,1700,t,.4,.12),
    t_shoot:t=>sweep('square',1300,380,t,.1,.1,2500),
    t_recoil:t=>S.cannon(t),
    ko:t=>{whistle(1300,260,t,.65,.14);sweep('sine',150,60,t+.7,.2,.36)},
    record:t=>{arp('xylo',['C5','E5','G5'],t,.07,.2,.18);tn('reed',nm('C6'),t+.21,.35,.15);tn('glock',nm('E6'),t+.21,.5,.11)},
    area:t=>arp('glock',['G5','C6','E6','G6'],t,.12,.6,.11),
    thud:t=>{sweep('sine',110,60,t,.15,.32);nz(t,.1,.13,'lowpass',700,.7)},
    splat:t=>{nz(t,.15,.16,'bandpass',600,1.2,250);sweep('sine',220,110,t,.12,.13)},
    buy:t=>{S.coin(t);S.tap(t)}
  };
  const GAP={coin:.05,step:.05,pon:.09,hit:.04,crit:.04,kill:.05,tap:.05,tock:.05,pop:.05,swing:.06,t_atk:.05,bubble:.08,clink:.05,hurt:.06,block:.05,boom:.1,dice:.2};
  function sfx(n,o){
    if(bouncing||!live()||document.hidden)return;const f=S[n];if(!f)return;
    const now=ctx.currentTime;if(last[n]&&now-last[n]<(GAP[n]||.03))return;last[n]=now;
    try{f(now+.005,o||{})}catch(err){}
  }

  /* ---- switching on, the button, waking up ---- */
  function unlock(){
    if(!boot())return;
    if(ctx.state!=='running')ctx.resume().catch(()=>{});
    if(!ok){ok=true;try{const b=ctx.createBuffer(1,1,22050),s=ctx.createBufferSource();s.buffer=b;s.connect(ctx.destination);s.start(0)}catch(err){}}
    setTimeout(sync,60);
  }
  ['pointerdown','touchend','keydown'].forEach(k=>addEventListener(k,unlock,{capture:true,passive:true}));
  document.addEventListener('visibilitychange',()=>{if(!ctx)return;if(document.hidden)ctx.suspend().catch(()=>{});else if(ok)ctx.resume().then(sync).catch(()=>{})});
  function set(v){
    on=!!v;try{localStorage.setItem('pq.snd',on?'1':'0')}catch(err){}
    if(ctx){master.gain.setTargetAtTime(on?.9:0,ctx.currentTime,.05);if(!on){players.forEach(fade);cur=null;jing=null}else{unlock();sync()}}
    paint();
  }
  const ICON_ON='<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M5 12h5l7-6v20l-7-6H5z" fill="currentColor"/><path d="M21 11.5q3 4.5 0 9M24.5 8.5q5.5 7.5 0 15" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>';
  const ICON_OFF='<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M5 12h5l7-6v20l-7-6H5z" fill="currentColor"/><path d="M21.5 12.5l7 7M28.5 12.5l-7 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>';
  function paint(){const b=document.getElementById('t-snd');if(!b)return;b.innerHTML=on?ICON_ON:ICON_OFF;b.classList.toggle('off',!on);b.setAttribute('aria-pressed',on?'true':'false');b.setAttribute('aria-label',on?'音：あり':'音：なし')}
  const tb=document.getElementById('t-snd');if(tb){tb.addEventListener('click',()=>set(!on));paint()}
  document.addEventListener('click',e=>{const b=e.target&&e.target.closest&&e.target.closest('button');if(b&&b.id!=='t-snd')sfx('tap')},true);

  /* ---- hooked to the field's events ---- */
  FXH.add('place',()=>sfx('place'));
  FXH.add('step',()=>sfx('step'));
  FXH.add('strike',d=>sfx(d.crit?'crit':'hit'));
  FXH.add('hurt',d=>sfx('hurt',{boss:d.boss}));
  FXH.add('kill',d=>sfx(d.e&&(d.e.boss||d.e.king)?'bigkill':'kill'));
  FXH.add('toyhit',()=>sfx('tock'));
  FXH.add('cannon',()=>sfx('cannon'));
  FXH.add('land',d=>sfx(d.kind==='wall'?'thud':'splat'));
  FXH.add('boom',()=>sfx('boom',{}));
  FXH.add('skill',()=>sfx('skill'));
  FXH.add('reach',d=>{if(d.s>0&&d.s%SPAN===0)sfx('area')});
  FXH.add('over',()=>sfx('ko'));

  async function bounce(fn,sec){ /* test only: play into a silent recorder and measure how loud it got */
    const O=window.OfflineAudioContext||window.webkitOfflineAudioContext;if(!O)return null;
    const keep=[ctx,master,mBus,sBus,rv,nb,players,on,cur,jing];
    bouncing=true;ctx=new O(2,Math.round(44100*sec),44100);graph();players=[];on=true;let res=null;
    try{fn();for(const p of players)while(p.next<sec&&!(p.total&&p.step>=p.total)){book(p,p.step,p.next);p.step++;p.next+=p.dt}
      const buf=await ctx.startRendering(),d=buf.getChannelData(0);let pk=0,sq=0,clip=0;
      for(let i=0;i<d.length;i++){const a=Math.abs(d[i]);if(a>pk)pk=a;sq+=d[i]*d[i];if(a>.99)clip++}
      res={peak:+pk.toFixed(3),rms:+Math.sqrt(sq/d.length).toFixed(4),clip};
    }finally{[ctx,master,mBus,sBus,rv,nb,players,on,cur,jing]=keep;bouncing=false}
    return res;
  }
  return {sfx,over,set,bounce,songs:()=>Object.keys(SONGS),names:()=>Object.keys(S),
    song1:(id,sec)=>bounce(()=>start(id,{}),sec||8),sfx1:n=>bounce(()=>S[n](.02,{}),1.6),get on(){return on},get song(){return cur?cur.key:jing?jing.key:''},get state(){return ctx?ctx.state:'none'},
    check(){const bad=[];for(const k in SONGS){const S=SONGS[k];S.tracks.forEach((x,n)=>{const want=x.mel?S.bars.length*S.bpb*x.res:S.bpb*x.res;if(x.tk.length!==want)bad.push(`${k}#${n} ${x.tk.length}/${want}`);
      if(x.mel)x.tk.forEach(tok=>{if(tok!=='.'&&tok!=='-'&&nm(tok)==null)bad.push(`${k}#${n} ${tok}`)})})}return bad}};
})();
function SND(n,o){if(AUD)AUD.sfx(n,o)} /* var and function: safe even before this point has run */
