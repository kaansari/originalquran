# app.py
from flask import Flask, render_template, abort, request, redirect
import json

app = Flask(__name__)

# ----------------------
# Load data
# ----------------------
with open("pagination_map.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("verses.json", encoding="utf-8") as f:
    verses = json.load(f)

with open("sura.json", encoding="utf-8") as f:
    suras = json.load(f)

# ----------------------
# Helper functions
# ----------------------

def parse_ref(ref):
    s, a = ref.split(":")
    return int(s), int(a)


def get_page_data(page_number):
    for p in pages:
        if p["page"] == page_number:
            start_s, start_a = parse_ref(p["from"])
            end_s, end_a = parse_ref(p["to"])

            ayat = []
            current_s = start_s
            current_a = start_a

            while True:
                # Find global ayah id via sura.json
                sura_meta = suras[str(current_s)]
                global_id = sura_meta["start"] + current_a - 1
                ayah = verses[str(global_id)]
                ayat.append({
                    "surah": current_s,
                    "ayah": current_a,
                    "arabic": ayah.get("arabic"),
                    "en": ayah.get("en")
                })

                if current_s == end_s and current_a == end_a:
                    break

                current_a += 1
                if current_a > suras[str(current_s)]["nAyah"]:
                    current_s += 1
                    current_a = 1

            return p, ayat
    return None, None

# ----------------------
# Routes

# Home page with surah/ayah navigation (RTL)
@app.route("/")
def index():
    return render_template(
        "index.html",
        suras=suras,
        total_pages=len(pages)
    )


@app.route("/goto", methods=["GET"])
def goto():
    surah = int(request.args.get("surah"))
    ayah = int(request.args.get("ayah"))

    # find page containing this ayah
    for p in pages:
        start_s, start_a = parse_ref(p["from"])
        end_s, end_a = parse_ref(p["to"])

        if (surah > start_s or (surah == start_s and ayah >= start_a)) and \
           (surah < end_s or (surah == end_s and ayah <= end_a)):
            return redirect(f"/page/{p['page']}")

    abort(404)


@app.route("/page/<int:page_number>")
def show_page(page_number):
    page, ayat = get_page_data(page_number)
    if not page:
        abort(404)
    return render_template(
        "page.html",
        page=page,
        ayat=ayat,
        page_number=page_number,
        total_pages=len(pages),
        suras=suras  # Add this line to pass surah data to template
    )

# ----------------------

if __name__ == "__main__":
    app.run(debug=True)