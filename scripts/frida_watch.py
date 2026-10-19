"""REA watcher: auto-attach PRNG + net(send/recv) hooks to EVERY Dofus Retro.exe
process the instant it appears, so we catch key-gen from process birth.
Usage:  py frida_watch.py           (Ctrl-C to stop)
Writes -> data/frida_capture.jsonl
Then: fully CLOSE one account and REOPEN it (fresh launch) -> caught from start.
"""
import frida, json, time, sys

LOG = r"C:\Users\vip19\PycharmProjects\DofusCokpit\data\frida_capture.jsonl"

JS = r"""
function expAddr(mod,name){try{
  var m=null; try{m=Process.findModuleByName(mod);}catch(e){}
  if(!m){try{m=Process.getModuleByName(mod);}catch(e){}}
  if(m){try{var a=m.findExportByName(name);if(a)return a;}catch(e){}
        try{var b=m.getExportByName(name);if(b)return b;}catch(e){}}
  try{if(Module.findGlobalExportByName)return Module.findGlobalExportByName(name);}catch(e){}
  return null;
}catch(e){return null;}}
function abHex(ab){var u=new Uint8Array(ab),s='';for(var i=0;i<u.length;i++){var h=u[i].toString(16);if(h.length<2)h='0'+h;s+=h;}return s;}
function printable(ab){var u=new Uint8Array(ab),n=0;for(var i=0;i<u.length;i++){if(u[i]>=0x20&&u[i]<0x7f)n++;}return u.length?n/u.length:0;}
function modoff(a){var m=Process.findModuleByAddress(a);return m?(m.name+'+0x'+a.sub(m.base).toString(16)):String(a);}

// --- CSPRNG (key candidates) ---
function hookRng(mod,name,bufArg,lenArg){
  var addr=expAddr(mod,name); if(!addr){return;}
  Interceptor.attach(addr,{
    onEnter:function(args){this.buf=args[bufArg];this.len=args[lenArg].toInt32();},
    onLeave:function(ret){try{var n=this.len;if(n>0&&n<=256){
      var ab=this.buf.readByteArray(n);
      var bt=Thread.backtrace(this.context,Backtracer.FUZZY).slice(0,6).map(modoff);
      var flash=bt.some(function(x){return x.indexOf('pepflash')>=0;});
      send({t:'prng',fn:name,size:n,hex:abHex(ab),flash:flash,bt:bt});
    }}catch(e){}}
  });
  send({t:'hooked',fn:name});
}
hookRng('bcryptprimitives.dll','ProcessPrng',0,1);
hookRng('cryptbase.dll','SystemFunction036',0,1);
hookRng('bcrypt.dll','BCryptGenRandom',1,2);

// --- outbound frames (ù) ---
function logsend(ptr,len){ if(len<=0||len>65536)return; var ab=ptr.readByteArray(Math.min(len,4096));var u=new Uint8Array(ab);
  if(u.length>=2&&u[0]==0xc3&&u[1]==0xb9){send({t:'frame',len:len,hex:abHex(ab)});} }
var S=expAddr('ws2_32.dll','send'); if(S)Interceptor.attach(S,{onEnter:function(a){try{logsend(a[1],a[2].toInt32());}catch(e){}}});
var WS=expAddr('ws2_32.dll','WSASend'); if(WS)Interceptor.attach(WS,{onEnter:function(a){try{var c=a[2].toInt32();var b=a[1];for(var i=0;i<c&&i<4;i++){var wb=b.add(i*Process.pointerSize*2);logsend(wb.add(Process.pointerSize).readPointer(),wb.readU32());}}catch(e){}}});

// --- inbound (clear S->C handshake: connexionKey etc.) ---
var R=expAddr('ws2_32.dll','recv');
if(R)Interceptor.attach(R,{onEnter:function(a){this.b=a[1];},onLeave:function(ret){try{var n=ret.toInt32();if(n>0&&n<=400){var ab=this.b.readByteArray(n);if(printable(ab)>0.7)send({t:'recv',len:n,hex:abHex(ab)});}}catch(e){}}});
send({t:'ready'});
"""

def w(o):
    o['ts']=time.time()
    with open(LOG,'a',encoding='utf-8') as f: f.write(json.dumps(o)+'\n')
    t=o.get('t')
    if t=='prng': print("  PRNG %s size=%d flash=%s %s" % (o['fn'],o['size'],o.get('flash'),o['hex'])); sys.stdout.flush()
    elif t=='frame': print("  FRAME len=%d %s" % (o['len'],o['hex'][:48])); sys.stdout.flush()
    elif t=='recv': print("  RECV len=%d %s" % (o['len'],bytes.fromhex(o['hex'])[:60])); sys.stdout.flush()

def on_msg(pid):
    def f(message,data):
        if message['type']=='send': p=message['payload']; p['pid']=pid; w(p)
        else: w({'t':'fridaerr','pid':pid,'message':str(message)})
    return f

dev=frida.get_local_device()
attached={}
w({'t':'watch-start'})
print("=== WATCHING for Dofus Retro.exe processes. CLOSE+REOPEN one account. Ctrl-C to stop ==="); sys.stdout.flush()
try:
  while True:
    try:
      pids=[p.pid for p in dev.enumerate_processes() if p.name=='Dofus Retro.exe']
    except Exception as e:
      pids=[]
    for pid in pids:
      if pid in attached: continue
      try:
        ses=dev.attach(pid); scr=ses.create_script(JS); scr.on('message',on_msg(pid)); scr.load()
        attached[pid]=(ses,scr); print("  + attached",pid); sys.stdout.flush()
      except Exception as e:
        attached[pid]=None  # don't retry failed ones every loop
    time.sleep(0.15)
except KeyboardInterrupt:
  print("=== stopped ===")
