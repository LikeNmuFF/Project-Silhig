import tkinter as tk
import urllib.request
import urllib.parse
import json
import threading
from datetime import datetime
import ctypes, sys

# ── Windows DPI fix ───────────────────────────────────────────────────────────
if sys.platform == "win32":
    try:    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try: ctypes.windll.user32.SetProcessDPIAware()
        except Exception: pass

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search?name={}&count=1&language=en&format=json"
WX_URL  = ("https://api.open-meteo.com/v1/forecast?"
           "latitude={lat}&longitude={lon}"
           "&current=temperature_2m,apparent_temperature,weathercode,windspeed_10m,relativehumidity_2m"
           "&hourly=temperature_2m,weathercode"
           "&temperature_unit=celsius&wind_speed_unit=kmh"
           "&forecast_days=1&timezone=auto")

WX_CODES = {
    0:"Clear Sky", 1:"Mainly Clear", 2:"Partly Cloudy", 3:"Overcast",
    45:"Foggy", 48:"Icy Fog", 51:"Light Drizzle", 53:"Drizzle",
    55:"Heavy Drizzle", 61:"Light Rain", 63:"Rain", 65:"Heavy Rain",
    71:"Light Snow", 73:"Snow", 75:"Heavy Snow", 80:"Showers",
    81:"Heavy Showers", 82:"Violent Showers", 95:"Thunderstorm",
    96:"Thunderstorm + Hail", 99:"Severe Thunderstorm",
}
WX_ICONS = {
    0:"☀", 1:"🌤", 2:"⛅", 3:"☁", 45:"🌫", 48:"🌫",
    51:"🌦", 53:"🌦", 55:"🌧", 61:"🌧", 63:"🌧", 65:"🌧",
    71:"❄", 73:"❄", 75:"❄", 80:"🌦", 81:"🌧", 82:"⛈",
    95:"⛈", 96:"⛈", 99:"⛈",
}

BG      = "#0b0f18"
CARD    = "#111827"
CARD2   = "#1a2234"
ACCENT  = "#4f9eff"
ACCENTD = "#1a3a6e"
TEXT_HI = "#f0f6ff"
TEXT_MID= "#8899bb"
TEXT_DIM= "#3d4f6e"
BORDER  = "#1e2d45"
RED     = "#f87171"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "WeatherWidget/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def get_coords(city):
    data = fetch_json(GEO_URL.format(urllib.parse.quote(city)))
    if not data.get("results"): return None
    r = data["results"][0]
    return r["latitude"], r["longitude"], r.get("name", city), r.get("country_code", "")

def get_weather(lat, lon):
    return fetch_json(WX_URL.format(lat=lat, lon=lon))


# ── Location Prompt ───────────────────────────────────────────────────────────
class LocationPrompt(tk.Tk):
    def __init__(self):
        super().__init__()
        self.chosen_city = None
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=BG)
        self.resizable(False, False)
        self._dx = self._dy = 0
        self._build()
        self._place()

    def _build(self):
        bar = tk.Frame(self, bg=CARD, height=32)
        bar.pack(fill="x"); bar.pack_propagate(False)
        bar.bind("<ButtonPress-1>", self._ds)
        bar.bind("<B1-Motion>",     self._dm)
        tk.Label(bar, text="Weather Widget", bg=CARD, fg=TEXT_MID,
                 font=("Segoe UI", 9)).pack(side="left", padx=12, pady=7)
        tk.Button(bar, text="✕", bg=CARD, fg=TEXT_MID, bd=0,
                  activebackground=RED, activeforeground=TEXT_HI,
                  font=("Segoe UI", 10), cursor="hand2",
                  command=self.destroy).pack(side="right", padx=8)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(self, bg=BG, padx=28, pady=28); body.pack()
        tk.Label(body, text="⛅", bg=BG, font=("Segoe UI Emoji", 38)).pack()
        tk.Label(body, text="Where are you?", bg=BG, fg=TEXT_HI,
                 font=("Segoe UI", 16, "bold")).pack(pady=(8, 4))
        tk.Label(body, text="Enter your city, Get the local forecast.",
                 bg=BG, fg=TEXT_MID, font=("Segoe UI", 10)).pack(pady=(0, 18))

        self._var = tk.StringVar()
        ef = tk.Frame(body, bg=ACCENT, padx=1, pady=1); ef.pack(fill="x")
        self._entry = tk.Entry(ef, textvariable=self._var,
            bg=CARD2, fg=TEXT_HI, insertbackground=ACCENT,
            relief="flat", font=("Segoe UI", 13), highlightthickness=0)
        self._entry.pack(fill="x", ipady=9, ipadx=10)
        self._entry.bind("<Return>", lambda e: self._go())
        self._entry.focus_set()

        self._err = tk.Label(body, text="", bg=BG, fg=RED, font=("Segoe UI", 9))
        self._err.pack(pady=(4, 0))

        self._btn = tk.Button(body, text="Get Weather  →",
            bg=ACCENT, fg=BG, bd=0,
            activebackground="#2563eb", activeforeground=TEXT_HI,
            font=("Segoe UI", 11, "bold"), cursor="hand2", pady=10,
            command=self._go)
        self._btn.pack(fill="x", pady=(14, 0))

    def _place(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = 340, self.winfo_reqheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _go(self):
        city = self._var.get().strip()
        if not city:
            self._err.config(text="Please enter a city name."); return
        self._btn.config(state="disabled", text="Searching…")
        self._err.config(text="")
        threading.Thread(target=self._validate, args=(city,), daemon=True).start()

    def _validate(self, city):
        try:
            result = get_coords(city)
            if result:
                self.chosen_city = city
                self.after(0, self.destroy)
            else:
                self.after(0, self._fail)
        except Exception:
            self.after(0, self._fail)

    def _fail(self):
        self._btn.config(state="normal", text="Get Weather  →")
        self._err.config(text="City not found. Try a different name.")

    def _ds(self, e): self._dx, self._dy = e.x, e.y
    def _dm(self, e):
        self.geometry(f"+{self.winfo_x()+e.x-self._dx}+{self.winfo_y()+e.y-self._dy}")


# ── Main Weather Widget ───────────────────────────────────────────────────────
class WeatherWidget(tk.Tk):
    W = 400   # wider so all content fits without scrolling

    def __init__(self, city):
        super().__init__()
        self.title("Weather")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.city_name    = tk.StringVar(value=city)
        self.weather_data = None
        self.loc_info     = None
        self._dx = self._dy = 0
        self._build_ui()
        self._place()
        self.after(100, self._refresh)

    def _build_ui(self):
        # title bar
        bar = tk.Frame(self, bg=CARD, height=36)
        bar.pack(fill="x"); bar.pack_propagate(False)
        bar.bind("<ButtonPress-1>", self._ds)
        bar.bind("<B1-Motion>",     self._dm)
        tk.Label(bar, text="⛅  WEATHER", bg=CARD, fg=ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=14, pady=9)
        for txt, cmd, hov in [("✕", self.destroy, RED), ("↺", self._refresh, ACCENT)]:
            tk.Button(bar, text=txt, bg=CARD, fg=TEXT_MID, bd=0,
                      activebackground=CARD2, activeforeground=hov,
                      font=("Segoe UI", 11), cursor="hand2",
                      command=cmd).pack(side="right", padx=(0, 8))
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # search bar
        sf = tk.Frame(self, bg=BG, pady=10, padx=14); sf.pack(fill="x")
        ef = tk.Frame(sf, bg=BORDER, padx=1, pady=1)
        ef.pack(side="left", fill="x", expand=True)
        self._entry = tk.Entry(ef, textvariable=self.city_name,
            bg=CARD2, fg=TEXT_HI, insertbackground=ACCENT,
            relief="flat", font=("Segoe UI", 11), highlightthickness=0)
        self._entry.pack(fill="x", ipady=6, ipadx=8)
        self._entry.bind("<Return>", lambda e: self._refresh())
        tk.Button(sf, text="Go", bg=ACCENT, fg=BG, bd=0,
                  activebackground="#2563eb", activeforeground=TEXT_HI,
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  padx=14, pady=7, command=self._refresh).pack(side="left", padx=(8, 0))

        # scrollable content area
        self._canvas = tk.Canvas(self, bg=BG, highlightthickness=0,
                                  width=self.W, height=500)
        self._vsb = tk.Scrollbar(self, orient="vertical",
                                  command=self._canvas.yview,
                                  bg=CARD, troughcolor=BG, width=6)
        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._content = tk.Frame(self._canvas, bg=BG)
        self._win_id = self._canvas.create_window((0, 0), window=self._content, anchor="nw")

        self._content.bind("<Configure>", self._on_content_resize)
        self._canvas.bind("<Configure>",  self._on_canvas_resize)
        self._canvas.bind("<MouseWheel>",  lambda e: self._canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._status = tk.Label(self._content, text="", bg=BG, fg=TEXT_MID,
                                font=("Segoe UI", 10))

    def _on_content_resize(self, e):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        # auto-fit window height (cap at 90% screen height)
        sh = self.winfo_screenheight()
        h  = min(self._content.winfo_reqheight() + 90, int(sh * 0.9))
        x, y = self.winfo_x(), self.winfo_y()
        self.geometry(f"{self.W}x{h}+{x}+{y}")

    def _on_canvas_resize(self, e):
        self._canvas.itemconfig(self._win_id, width=e.width)

    # ── Current card ─────────────────────────────────────────────────────────
    def _build_current(self, parent, cur, loc_label):
        code  = cur["weathercode"]
        temp  = cur["temperature_2m"]
        feels = cur["apparent_temperature"]
        wind  = cur["windspeed_10m"]
        humid = cur["relativehumidity_2m"]
        icon  = WX_ICONS.get(code, "🌡")
        desc  = WX_CODES.get(code, "Unknown")

        pad = tk.Frame(parent, bg=BG); pad.pack(fill="x", padx=14, pady=(6, 0))

        tk.Label(pad, text=f"📍 {loc_label}", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))

        hero = tk.Frame(pad, bg=BG); hero.pack(fill="x", pady=(0, 10))
        tk.Label(hero, text=icon, bg=BG,
                 font=("Segoe UI Emoji", 48)).pack(side="left")
        right = tk.Frame(hero, bg=BG)
        right.pack(side="left", padx=10, anchor="center")
        tk.Label(right, text=f"{temp:.0f}°C", bg=BG, fg=TEXT_HI,
                 font=("Segoe UI", 36, "bold")).pack(anchor="w")
        tk.Label(right, text=desc, bg=BG, fg=TEXT_MID,
                 font=("Segoe UI", 11)).pack(anchor="w")

        # stats strip
        strip = tk.Frame(parent, bg=CARD); strip.pack(fill="x", pady=(0, 10))
        for emoji, label, val in [
            ("🌡", "Feels like", f"{feels:.0f}°C"),
            ("💨", "Wind",       f"{wind:.0f} km/h"),
            ("💧", "Humidity",   f"{humid:.0f}%"),
        ]:
            col = tk.Frame(strip, bg=CARD)
            col.pack(side="left", expand=True, pady=12)
            tk.Label(col, text=emoji, bg=CARD,
                     font=("Segoe UI Emoji", 14)).pack()
            tk.Label(col, text=val, bg=CARD, fg=TEXT_HI,
                     font=("Segoe UI", 12, "bold")).pack()
            tk.Label(col, text=label, bg=CARD, fg=TEXT_DIM,
                     font=("Segoe UI", 8)).pack()

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(0, 8))

    # ── Hourly grid ───────────────────────────────────────────────────────────
    def _build_hourly(self, parent, hourly):
        pad = tk.Frame(parent, bg=BG); pad.pack(fill="x", padx=14)
        tk.Label(pad, text="NEXT 12 HOURS", bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 8))

        times = hourly["time"]
        temps = hourly["temperature_2m"]
        codes = hourly["weathercode"]
        now_h = datetime.now().hour
        slots = [(t, tp, c) for t, tp, c in zip(times, temps, codes)
                 if int(t[11:13]) >= now_h][:12]

        # 4 columns x 3 rows grid
        grid = tk.Frame(pad, bg=BG); grid.pack(fill="x")
        COLS = 4
        for i, (t, tp, c) in enumerate(slots):
            h      = int(t[11:13])
            ampm   = f"{h % 12 or 12}{'am' if h < 12 else 'pm'}"
            is_now = (i == 0)
            box_bg = ACCENTD if is_now else CARD
            lbl_fg = ACCENT  if is_now else TEXT_DIM

            col_i = i % COLS
            row_i = i // COLS

            box = tk.Frame(grid, bg=box_bg, padx=8, pady=10)
            box.grid(row=row_i, column=col_i, padx=3, pady=3, sticky="nsew")
            grid.columnconfigure(col_i, weight=1)

            tk.Label(box, text="NOW" if is_now else ampm,
                     bg=box_bg, fg=lbl_fg,
                     font=("Segoe UI", 8, "bold" if is_now else "normal")).pack()
            tk.Label(box, text=WX_ICONS.get(c, "🌡"), bg=box_bg,
                     font=("Segoe UI Emoji", 20)).pack(pady=3)
            tk.Label(box, text=f"{tp:.0f}°C", bg=box_bg, fg=TEXT_HI,
                     font=("Segoe UI", 10, "bold")).pack()

        # bottom padding
        tk.Frame(parent, bg=BG, height=10).pack()

    # ── Fetch / render ────────────────────────────────────────────────────────
    def _refresh(self):
        city = self.city_name.get().strip()
        if not city: return
        self._clear()
        self._status.config(text=f"Fetching weather for {city}…")
        self._status.pack(pady=60)
        threading.Thread(target=self._fetch, args=(city,), daemon=True).start()

    def _fetch(self, city):
        try:
            coords = get_coords(city)
            if not coords:
                self.after(0, lambda: self._error(f'City "{city}" not found.')); return
            lat, lon, name, cc = coords
            data = get_weather(lat, lon)
            self.weather_data = data
            self.loc_info = (name, cc)
            self.after(0, self._render)
        except Exception as e:
            self.after(0, lambda: self._error(str(e)))

    def _render(self):
        self._clear()
        d   = self.weather_data
        loc = f"{self.loc_info[0]}, {self.loc_info[1].upper()}"
        self._build_current(self._content, d["current"], loc)
        self._build_hourly(self._content, d["hourly"])

    def _error(self, msg):
        self._clear()
        self._status.config(text=f"⚠  {msg}", fg=RED)
        self._status.pack(pady=60)

    def _clear(self):
        for w in self._content.winfo_children(): w.destroy()
        self._status = tk.Label(self._content, bg=BG, fg=TEXT_MID,
                                font=("Segoe UI", 10))

    # ── Drag ─────────────────────────────────────────────────────────────────
    def _ds(self, e): self._dx, self._dy = e.x, e.y
    def _dm(self, e):
        self.geometry(f"+{self.winfo_x()+e.x-self._dx}+{self.winfo_y()+e.y-self._dy}")

    def _place(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.W}x600+{sw - self.W - 40}+{sh // 2 - 300}")


if __name__ == "__main__":
    prompt = LocationPrompt()
    prompt.mainloop()
    city = prompt.chosen_city
    if not city: sys.exit(0)
    widget = WeatherWidget(city)
    widget.mainloop()
