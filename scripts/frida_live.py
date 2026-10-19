"""REA LIVE feed: real-time clear Dofus Retro protocol (both directions) via a
Frida hook on the Flash/Chromium socket, decoded with the project's own
app/network/protocol.py, and PUSHED into the running API (POST /live/stream) so
the RepopMonitor + bank/HDV auto-sync work live WITHOUT pcap. No crypto key.

Usage:  py scripts/frida_live.py
Env:    LIVE_API (default http://127.0.0.1:8000/live/stream) ; set to "" to disable push.
Writes  data/live_feed.jsonl and prints a concise live view.
"""
import frida, json, time, sys, os, collections, urllib.request

ROOT = r"C:\Users\vip19\PycharmProjects\DofusCokpit"
sys.path.insert(0, ROOT)
from app.network import protocol as P

LOG = os.path.join(ROOT, "data", "live_feed.jsonl")
API_URL = os.getenv("LIVE_API", "http://127.0.0.1:8000/live/stream")
DELIM = b"\x00"
UU = b"\xc3\xb9"

JS = r"""
function expAddr(mod,name){try{
  var m=null; try{m=Process.findModuleByName(mod);}catch(e){}
  if(!m){try{m=Process.getModuleByName(mod);}catch(e){}}
  if(m){try{var a=m.findExportByName(name);if(a)return a;}catch(e){}
        try{var b=m.getExportByName(name);if(b)return b;}catch(e){}}
  try{if(Module.findGlobalExportByName)return Module.findGlobalExportByName(name);}catch(e){}
  return null;}catch(e){return null;}}
function keep(ab){var u=new Uint8Array(ab),L=Math.min(u.length,64),p=0;
  for(var i=0;i<L;i++){var c=u[i];if((c>=0x20&&c<0x7f)||c==0||c==10)p++;}
  var frame=(u.length>=2&&u[0]==0xc3&&u[1]==0xb9);
  return frame||(L>0&&p/L>0.6);}
var R=expAddr('ws2_32.dll','recv');
if(R)Interceptor.attach(R,{onEnter:function(a){this.s=a[0];this.b=a[1];},onLeave:function(ret){
  try{var n=ret.toInt32();if(n>0){var ab=this.b.readByteArray(Math.min(n,65536));if(keep(ab))send({d:'r',s:this.s.toString()},ab);}}catch(e){}}});
function onsend(sock,ptr,len){ if(len<=0)return; var ab=ptr.readByteArray(Math.min(len,65536)); if(keep(ab))send({d:'s',s:sock.toString()},ab); }
var S=expAddr('ws2_32.dll','send'); if(S)Interceptor.attach(S,{onEnter:function(a){try{onsend(a[0],a[1],a[2].toInt32());}catch(e){}}});
var WS=expAddr('ws2_32.dll','WSASend'); if(WS)Interceptor.attach(WS,{onEnter:function(a){try{var c=a[2].toInt32();var bu=a[1];for(var i=0;i<c&&i<4;i++){var wb=bu.add(i*Process.pointerSize*2);onsend(a[0],wb.add(Process.pointerSize).readPointer(),wb.readU32());}}catch(e){}}});
send({d:'ready'});
"""

GAME_PREFIXES = ("GDM","GM","EL","ASK","ALK","EHP","EHl","EHL","GTS","PM~","HC","HG","AY","AT","Ad","Ac","GC","Bp","Ir","GA","GV","ERK","EMK","ECK","BN","Af")
inbuf = collections.defaultdict(bytes)
game_socks = set()
pending = collections.defaultdict(list)   # streamkey -> [raw S->C msg]
tally = collections.Counter()
stats = {"posted": 0, "post_err": 0}

def jlog(o):
    o["ts"] = time.time()
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")

def push_api():
    if not API_URL:
        return
    for sk, msgs in list(pending.items()):
        if not msgs:
            continue
        pending[sk] = []
        try:
            body = json.dumps({"stream": sk, "messages": msgs}).encode("utf-8")
            req = urllib.request.Request(API_URL, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                resp.read()
            stats["posted"] += len(msgs)
        except Exception as e:
            stats["post_err"] += 1
            # on ne perd pas tout : remets en file (borné) si l'API est down
            if len(pending[sk]) < 500:
                pending[sk] = msgs + pending[sk]

def decode_s2c(msg):
    if msg.startswith(P.MAP_DATA_PREFIX):
        m = P.parse_map_change(msg)
        if m is not None:
            z = P.MAP_ZONES.get(m, ""); xy = P.MAP_COORDS.get(m)
            return "map", f"map {m}" + (f" [{xy[0]},{xy[1]}]" if xy else "") + (f" {z}" if z else "")
    if msg.startswith(P.MAP_ACTORS_PREFIX):
        acts = P.parse_map_actors(msg)
        grp = [a for a in acts if a.get("op") == "add" and a.get("monsters")]
        if grp:
            names = []
            for a in grp:
                for mid, lv in zip(a.get("monsters", []), a.get("levels", []) or []):
                    names.append(f"{P.MONSTER_NAMES.get(mid, '#'+str(mid))} lv{lv}")
            if names: return "mobs", "groupe: " + ", ".join(names[:6])
    if msg.startswith(P.HDV_AVG_PRICE_PREFIX):
        r = P.parse_hdv_avg_price(msg[len(P.HDV_AVG_PRICE_PREFIX):])
        if r: return "price_avg", f"HDV moy gid={r[0]} = {r[1]}"
    if msg.startswith(P.HDV_ITEM_PRICE_PREFIX):
        r = P.parse_hdv_item_prices(msg[len(P.HDV_ITEM_PRICE_PREFIX):])
        if r and r.get("price") is not None: return "price", f"HDV gid={r['item_id']} = {r['price']}"
    if msg.startswith(P.BANK_MESSAGE_PREFIX) and not msg.startswith("ELK"):
        inv = P.parse_bank_storage(msg[len(P.BANK_MESSAGE_PREFIX):])
        if inv: return "bank", f"banque: {len(inv)} items"
    if msg.startswith(P.INVENTORY_PREFIX):
        c = P.parse_character_inventory(msg)
        if c: return "inv", f"inv {c['name']} lv{c['level']} ({len(c['equipment'])} equip)"
    if msg.startswith(P.FIGHTER_PM_PREFIX):
        r = P.parse_fighter_name(msg)
        if r: return "fighter", f"combattant {r[0]} = {r[1]}"
    if msg.startswith(P.TURN_START_PREFIX):
        r = P.parse_turn_start(msg)
        if r is not None: return "turn", f"tour de {r}"
    if msg.startswith("HC"): return "handshake", f"HC {msg[2:][:16]}..."
    return None

def handle_s2c(key, data):
    buf = inbuf[key] + data
    *done, rem = buf.split(DELIM)
    inbuf[key] = rem
    sk = f"{key[0]}:{key[1]}"
    for raw in done:
        if not raw: continue
        try: msg = raw.decode("utf-8", "ignore").strip()
        except Exception: continue
        if not msg: continue
        if key not in game_socks and msg[:3] not in GAME_PREFIXES and msg[:2] not in GAME_PREFIXES:
            continue
        game_socks.add(key)
        pending[sk].append(msg)            # -> API (feed_messages)
        dec = decode_s2c(msg)
        kind = dec[0] if dec else "s2c"
        tally[kind] += 1
        jlog({"dir": "S->C", "stream": sk, "kind": kind, "raw": msg[:300]})
        if dec:
            print(f"  [S<-C] {dec[1]}"); sys.stdout.flush()

def handle_c2s(key, data):
    for chunk in data.split(DELIM):
        if UU not in chunk: continue
        parts = chunk.split(UU)
        if len(parts) < 3: continue
        cmd = parts[2].rstrip(b"\n").decode("utf-8", "ignore").strip()
        if not cmd: continue
        game_socks.add(key)
        tally["c2s"] += 1
        jlog({"dir": "C->S", "stream": f"{key[0]}:{key[1]}", "kind": "cmd", "cmd": cmd[:200]})
        print(f"  [C->S] {cmd[:120]}"); sys.stdout.flush()

def on_msg_factory(pid):
    def on_message(message, data):
        if message.get("type") != "send": return
        p = message["payload"]; d = p.get("d")
        if d == "ready" or data is None: return
        key = (pid, p.get("s"))
        if d == "r": handle_s2c(key, bytes(data))
        elif d == "s": handle_c2s(key, bytes(data))
    return on_message

dev = frida.get_local_device()
attached = {}
print(f"=== LIVE FEED -> {API_URL or '(push off)'} . Joue normalement. Ctrl-C pour stopper ==="); sys.stdout.flush()
last_push = last_tally = time.time()
try:
    while True:
        try: pids = [p.pid for p in dev.enumerate_processes() if p.name == "Dofus Retro.exe"]
        except Exception: pids = []
        for pid in pids:
            if pid in attached: continue
            try:
                ses = dev.attach(pid); scr = ses.create_script(JS)
                scr.on("message", on_msg_factory(pid)); scr.load()
                attached[pid] = (ses, scr)
            except Exception:
                attached[pid] = None
        now = time.time()
        if now - last_push > 1.5:
            last_push = now; push_api()
        if now - last_tally > 15:
            last_tally = now
            print("  -- tally:", dict(tally), "| api posted:", stats["posted"], "err:", stats["post_err"]); sys.stdout.flush()
        time.sleep(0.2)
except KeyboardInterrupt:
    push_api()
    print("=== stopped. tally:", dict(tally), "| api posted:", stats["posted"], "===")
