"""REA native capture: pepflash CSPRNG draws (network key) + game TCP frames.
Usage:  py frida_capture.py --prng <pid> [<pid>...] --net <pid> [--seconds N]
Writes JSONL -> data/frida_capture.jsonl   (Frida 17 module API, robust resolver)
"""
import frida, json, time, argparse, sys

LOG = r"C:\Users\vip19\PycharmProjects\DofusCokpit\data\frida_capture.jsonl"

RESOLVER = r"""
function expAddr(mod,name){try{
  var m=null;
  try{ m=Process.findModuleByName(mod); }catch(e){}
  if(!m){ try{ m=Process.getModuleByName(mod); }catch(e){} }
  if(m){ try{ var a=m.findExportByName(name); if(a) return a; }catch(e){}
         try{ var b=m.getExportByName(name); if(b) return b; }catch(e){} }
  try{ if(Module.findGlobalExportByName) return Module.findGlobalExportByName(name); }catch(e){}
  return null;
}catch(e){return null;}}
function abHex(ab){var u=new Uint8Array(ab),s='';for(var i=0;i<u.length;i++){var h=u[i].toString(16);if(h.length<2)h='0'+h;s+=h;}return s;}
"""

PRNG_JS = RESOLVER + r"""
function modoff(a){var m=Process.findModuleByAddress(a);return m?(m.name+'+0x'+a.sub(m.base).toString(16)):String(a);}
function hookRng(mod,name,bufArg,lenArg){
  var addr=expAddr(mod,name);
  if(!addr){send({t:'nohook',fn:mod+'!'+name});return;}
  Interceptor.attach(addr,{
    onEnter:function(args){this.buf=args[bufArg];this.len=args[lenArg].toInt32();},
    onLeave:function(ret){try{var n=this.len;if(n>0&&n<=256){
      var ab=this.buf.readByteArray(n);
      var bt=Thread.backtrace(this.context,Backtracer.FUZZY).slice(0,6).map(modoff);
      var flash=bt.some(function(x){return x.indexOf('pepflash')>=0;});
      send({t:'prng',fn:name,size:n,hex:abHex(ab),flash:flash,bt:bt});
    }}catch(e){send({t:'err',where:name,e:String(e)});}}
  });
  send({t:'hooked',fn:mod+'!'+name});
}
hookRng('bcryptprimitives.dll','ProcessPrng',0,1);
hookRng('cryptbase.dll','SystemFunction036',0,1);
hookRng('bcrypt.dll','BCryptGenRandom',1,2);
"""

NET_JS = RESOLVER + r"""
function logbuf(ptr,len,where){
  if(len<=0||len>65536)return;
  var ab=ptr.readByteArray(Math.min(len,4096));var u=new Uint8Array(ab);
  if(u.length>=2&&u[0]==0xc3&&u[1]==0xb9){send({t:'frame',where:where,len:len,hex:abHex(ab)});}
}
var s=expAddr('ws2_32.dll','send');
if(s){Interceptor.attach(s,{onEnter:function(a){try{logbuf(a[1],a[2].toInt32(),'send');}catch(e){}}});send({t:'hooked',fn:'ws2_32!send'});}else{send({t:'nohook',fn:'ws2_32!send'});}
var ws=expAddr('ws2_32.dll','WSASend');
if(ws){Interceptor.attach(ws,{onEnter:function(a){try{
  var cnt=a[2].toInt32();var bufs=a[1];
  for(var i=0;i<cnt&&i<4;i++){var wb=bufs.add(i*Process.pointerSize*2);var l=wb.readU32();var p=wb.add(Process.pointerSize).readPointer();logbuf(p,l,'WSASend');}
}catch(e){}}});send({t:'hooked',fn:'ws2_32!WSASend'});}else{send({t:'nohook',fn:'ws2_32!WSASend'});}
"""

def w(o):
    o['ts']=time.time()
    with open(LOG,'a',encoding='utf-8') as f:
        f.write(json.dumps(o)+'\n')
    t=o.get('t')
    if t=='prng': print("PRNG %s size=%d flash=%s %s" % (o['fn'],o['size'],o.get('flash'),o['hex']))
    elif t=='frame': print("FRAME %s len=%d %s" % (o['where'],o['len'],o['hex'][:48]))
    elif t in ('hooked','nohook','err','fridaerr'): print(o)
    sys.stdout.flush()

def on_msg_factory(pid,role):
    def on_message(message,data):
        if message['type']=='send':
            p=message['payload']; p['pid']=pid; p['role']=role; w(p)
        else:
            w({'t':'fridaerr','pid':pid,'role':role,'message':str(message)})
    return on_message

def attach(pid,js,role):
    ses=frida.attach(pid)
    scr=ses.create_script(js)
    scr.on('message',on_msg_factory(pid,role))
    scr.load()
    return ses,scr

ap=argparse.ArgumentParser()
ap.add_argument('--prng',nargs='*',type=int,default=[])
ap.add_argument('--net',nargs='*',type=int,default=[])
ap.add_argument('--seconds',type=int,default=0)
a=ap.parse_args()
w({'t':'session-start','prng':a.prng,'net':a.net})
hold=[]
for pid in a.prng:
    try: hold.append(attach(pid,PRNG_JS,'prng')); print('attached prng',pid)
    except Exception as e: print('PRNG attach FAIL',pid,e)
    sys.stdout.flush()
for pid in a.net:
    try: hold.append(attach(pid,NET_JS,'net')); print('attached net',pid)
    except Exception as e: print('NET attach FAIL',pid,e)
    sys.stdout.flush()
print('=== CAPTURING (reconnect an account + do a trade; Ctrl-C to stop) ==='); sys.stdout.flush()
try:
    if a.seconds>0: time.sleep(a.seconds)
    else:
        while True: time.sleep(1)
except KeyboardInterrupt: pass
print('=== stopped ===')
