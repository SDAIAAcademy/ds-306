"""Writes the synthetic data of the DS-306 labs: the Sada Citizen Voice Centre case.

Python standard library only, one fixed seed, the same bytes on every run:

    uv run python prepare_data.py

Everything here is invented. Names, phone numbers and identity numbers are random strings in
the right shape; they belong to nobody. The recorded model runs are synthetic too: they imitate
the behaviour the course measures (a dialect gap, unstable answers on two-topic complaints,
invented deadlines) and were not produced by a model. A trainer with a working key can record
real runs with the labs' live cells and compare.

What it writes into data/ (the answer key for trainers is solutions/answer_key.md):

  complaints.csv.gz        20,000 raw complaints (with personal data, as received)
  districts.csv            12 districts with population and names
  codebook.md              the eight categories, as Sada's intake team defines them
  dialect_map.csv          course-provided spelling rules for Gulf dialect
  redaction_audit.csv      500 complaints whose personal data a person marked (Lab 1.4)
  pair40.csv               40 complaints for the partner exercise, with two reference coders (Lab 2.1)
  pool.csv                 3,000 redacted complaints with intake routing labels (Labs 2.2, 2.3)
  gold.csv                 300 redacted complaints: two coders and the adjudicated label
  prompts/                 Fahim's two prompt versions
  model_runs_gold.csv      recorded labels: two prompts x three runs over the gold set
  model_labels_all.csv.gz  recorded labels (prompt 1, run 1) for all 20,000 complaints
  inspections.jsonl        500 inspection reports
  inspections_reference.jsonl  their reference extractions
  inspection_runs.jsonl    a recorded extraction run over the 500 reports
  capstone/<corpus>/       two capstone corpora with gold sets, recorded runs, codebook and brief
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 306
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

CATEGORIES = ["water_sewage", "roads", "waste", "lighting", "noise", "permits", "parks", "staff_service"]
CATEGORY_NAMES = {
    "water_sewage": ("Water and sewage", "المياه والصرف الصحي"),
    "roads": ("Roads and pavements", "الطرق والأرصفة"),
    "waste": ("Waste and cleanliness", "النظافة والنفايات"),
    "lighting": ("Street lighting", "إنارة الشوارع"),
    "noise": ("Noise", "الإزعاج والضوضاء"),
    "permits": ("Permits and licences", "التصاريح والرخص"),
    "parks": ("Parks and public facilities", "الحدائق والمرافق العامة"),
    "staff_service": ("Staff conduct and service", "تعامل الموظفين وجودة الخدمة"),
}
VARIETIES = ["msa", "gulf", "en"]

# key: (English name, Arabic name, population, variety mix msa/gulf/en, share of water and sewage)
DISTRICTS = {
    "al_nuzha": ("Al-Nuzha", "النزهة", 96_000, (0.50, 0.30, 0.20), 0.16),
    "al_rawabi": ("Al-Rawabi", "الروابي", 74_000, (0.45, 0.35, 0.20), 0.17),
    "al_safa": ("Al-Safa", "الصفا", 118_000, (0.50, 0.30, 0.20), 0.15),
    "al_marwa": ("Al-Marwa", "المروة", 61_000, (0.45, 0.35, 0.20), 0.18),
    "al_naseem": ("Al-Naseem", "النسيم", 88_000, (0.25, 0.65, 0.10), 0.27),
    "al_khalij": ("Al-Khalij", "الخليج", 52_000, (0.35, 0.15, 0.50), 0.13),
    "al_wurud": ("Al-Wurud", "الورود", 69_000, (0.50, 0.30, 0.20), 0.16),
    "al_shati": ("Al-Shati", "الشاطئ", 47_000, (0.35, 0.20, 0.45), 0.12),
    "al_jazira": ("Al-Jazira", "الجزيرة", 103_000, (0.30, 0.60, 0.10), 0.25),
    "al_faisaliya": ("Al-Faisaliya", "الفيصلية", 132_000, (0.50, 0.30, 0.20), 0.17),
    "al_aziziya": ("Al-Aziziya", "العزيزية", 79_000, (0.45, 0.35, 0.20), 0.18),
    "al_salam": ("Al-Salam", "السلام", 58_000, (0.30, 0.55, 0.15), 0.23),
}
OTHER_SHARES = {"roads": 0.21, "waste": 0.18, "lighting": 0.09, "noise": 0.08, "permits": 0.10, "parks": 0.07,
                "staff_service": 0.13}
CHANNELS = [("web", 0.35), ("app", 0.30), ("call_centre", 0.15), ("email", 0.10), ("social", 0.10)]

# ---------------------------------------------------------------- phrase banks

CORE = {
    "water_sewage": {
        "msa": ["انقطعت المياه عن منزلنا في {street} منذ {days} أيام دون أي إشعار.",
                "يوجد طفح للصرف الصحي أمام {place} والرائحة لا تحتمل.",
                "ضغط المياه ضعيف جدا في الأدوار العليا منذ بداية الشهر.",
                "تسربت المياه من أنبوب مكسور في {street} وتجمعت في الطريق.",
                "غرف التفتيش في {street} ممتلئة بمياه الصرف بعد كل مطر."],
        "gulf": ["ترى المجاري طافحة عند {place} والريحة وايد قوية.",
                 "الماي مقطوع عندنا من {days} أيام وما أحد رد علينا.",
                 "الشارع غرقان مويه من البيارة اللي عند {place}.",
                 "ضغط الماي ضعيف مره وما يوصل للخزان فوق.",
                 "فيه تسريب مويه من الماسورة في {street} من أسبوع والشارع غرقان."],
        "en": ["Sewage is overflowing in front of {place} and the smell is unbearable.",
               "We have had no water at home on {street} for {days} days.",
               "Water pressure is very low on the upper floors since the start of the month.",
               "A broken pipe on {street} is leaking water onto the road.",
               "The manholes on {street} fill with sewage after every rain."],
    },
    "roads": {
        "msa": ["توجد حفرة كبيرة في {street} تسببت في أضرار للسيارات.",
                "الرصيف في {street} متكسر ولا يستطيع كبار السن المشي عليه.",
                "أعمال الحفر في {street} متوقفة منذ {days} يوما دون إعادة السفلتة.",
                "المطب الجديد أمام {place} بلا لوحات تحذيرية.",
                "ظهرت تشققات خطيرة في الجسر المؤدي إلى {place}."],
        "gulf": ["فيه حفرة كبيرة في {street} خربت كفرات السيارة.",
                 "الرصيف مكسر عند {place} والشيبان ما يقدرون يمشون.",
                 "الحفريات في {street} لها {days} يوم ومحد سفلتها.",
                 "حطوا مطب عند {place} بدون لوحة وكل يوم حادث.",
                 "الشارع كله ترقيع وحفر من بعد الأمطار."],
        "en": ["There is a large pothole on {street} that has damaged several cars.",
               "The pavement near {place} is broken and elderly people cannot walk on it.",
               "Excavation works on {street} stopped {days} days ago and the road was never resurfaced.",
               "A new speed bump near {place} has no warning signs.",
               "Serious cracks have appeared on the bridge leading to {place}."],
    },
    "waste": {
        "msa": ["لم ترفع النفايات من {street} منذ {days} أيام.",
                "حاويات النفايات عند {place} ممتلئة وتنتشر حولها القطط.",
                "ترمى مخلفات البناء بجوار {place} دون رقابة.",
                "سيارة النظافة تترك نصف المخلفات على الطريق.",
                "الحاوية المخصصة لحينا مكسورة منذ شهر."],
        "gulf": ["الزبالة ما انشالت من {days} أيام في {street}.",
                 "الحاويات عند {place} فايضة والقطاوة معفسينها.",
                 "فيه ناس يكبون مخلفات بناء جنب {place} كل ليلة.",
                 "سيارة البلدية تشيل الزبالة وتطيح نصها بالشارع.",
                 "حاوية حارتنا مكسورة من شهر ومحد بدلها."],
        "en": ["Rubbish has not been collected from {street} for {days} days.",
               "The bins near {place} are overflowing and cats are spreading the waste.",
               "Construction waste is being dumped next to {place} every night.",
               "The collection truck spills half of the waste on the street.",
               "Our neighbourhood bin has been broken for a month."],
    },
    "lighting": {
        "msa": ["أعمدة الإنارة في {street} مطفأة منذ {days} أيام.",
                "الطريق المؤدي إلى {place} مظلم تماما في الليل.",
                "عمود إنارة مائل في {street} ويخشى سقوطه.",
                "الإنارة تعمل في النهار وتنطفئ في الليل في {street}."],
        "gulf": ["لمبات الشارع طافية في {street} من {days} أيام.",
                 "الطريق لين {place} ظلمة بالليل ما تشوف شي.",
                 "فيه عمود نور مايل في {street} بيطيح على أحد.",
                 "الأنوار شغالة بالنهار وطافية بالليل، شلون كذا؟"],
        "en": ["The street lights on {street} have been off for {days} days.",
               "The road to {place} is completely dark at night.",
               "A street light pole on {street} is leaning and may fall.",
               "The lights stay on during the day and go off at night on {street}."],
    },
    "noise": {
        "msa": ["ورشة في {street} تعمل طوال الليل بأصوات مزعجة.",
                "أعمال البناء بجوار {place} تبدأ قبل الفجر كل يوم.",
                "مكبرات الصوت في القاعة المجاورة لـ{place} مرتفعة جدا.",
                "مولد كهربائي يعمل باستمرار في {street} ويسبب ضوضاء."],
        "gulf": ["فيه ورشة في {street} تشتغل طول الليل والإزعاج وايد.",
                 "البناء اللي جنب {place} يبدون قبل الفجر ونصحى من الدق.",
                 "القاعة اللي جنب {place} السماعات عندهم عالية مره.",
                 "ماطور كهربا شغال ليل ونهار في {street}."],
        "en": ["A workshop on {street} runs noisy machines all night.",
               "Construction next to {place} starts before dawn every day.",
               "The wedding hall near {place} plays music far too loud.",
               "A generator on {street} runs day and night and the noise is constant."],
    },
    "permits": {
        "msa": ["تقدمت بطلب رخصة بناء منذ {days} يوما ولم يصلني أي رد.",
                "طلب تجديد رخصة المحل معلق في النظام دون سبب واضح.",
                "رفض طلب التصريح دون ذكر المستندات الناقصة.",
                "ألغي موعد المعاينة لطلب الترخيص مرتين."],
        "gulf": ["مقدم على رخصة بناء من {days} يوم وللحين ما ردوا.",
                 "تجديد رخصة المحل معلق بالنظام وما أدري ليش.",
                 "رفضوا التصريح وما قالوا وش الناقص.",
                 "موعد الكشف على الطلب انلغى مرتين."],
        "en": ["I applied for a building permit {days} days ago and have heard nothing.",
               "My shop licence renewal is stuck in the system with no reason given.",
               "My permit application was rejected without saying which documents were missing.",
               "The inspection appointment for my licence was cancelled twice."],
    },
    "parks": {
        "msa": ["ألعاب الأطفال في {place} مكسورة وخطرة.",
                "الحديقة العامة في {street} بلا سقي والعشب جاف.",
                "دورات المياه في الحديقة مغلقة منذ أسابيع.",
                "ممشى الحي بلا مقاعد كافية لكبار السن."],
        "gulf": ["ألعاب الياهل في الحديقة مكسرة وخطيرة.",
                 "الحديقة اللي في {street} محد يسقيها والزرع ميت.",
                 "حمامات الحديقة مسكرة من أسابيع.",
                 "ممشى الحي ما فيه كراسي تكفي."],
        "en": ["The children's play equipment in the park is broken and dangerous.",
               "The public garden on {street} is not watered and the grass is dead.",
               "The toilets in the park have been closed for weeks.",
               "The walking track does not have enough benches for older people."],
    },
    "staff_service": {
        "msa": ["تعامل الموظف في مركز الخدمة كان غير لائق.",
                "اتصلت بالرقم الموحد {days} مرات ولم يرد أحد.",
                "أغلقوا البلاغ السابق دون أي إجراء فعلي.",
                "انتظرت أكثر من ساعتين في الفرع دون خدمة."],
        "gulf": ["الموظف في مركز الخدمة كان أسلوبه مو زين أبد.",
                 "اتصلت على الرقم الموحد {days} مرات ومحد رد.",
                 "سكروا البلاغ اللي قبل وهم ما سووا شي.",
                 "قعدت ساعتين بالفرع ومحد خدمني."],
        "en": ["The employee at the service centre was rude to me.",
               "I called the hotline {days} times and nobody answered.",
               "They closed my previous report without doing anything.",
               "I waited more than two hours at the branch without being served."],
    },
}
OPENERS = {"msa": ["السلام عليكم،", "أود الإبلاغ عن مشكلة:", "تحية طيبة،", "", ""],
           "gulf": ["السلام عليكم", "مرحبا", "لو سمحتوا", "يا جماعة", "", ""],
           "en": ["Hello,", "Dear Sada team,", "Hi,", "", ""]}
CLOSERS = {"msa": ["نرجو سرعة المعالجة.", "وشكرا لكم.", "آمل التواصل معي.", "", ""],
           "gulf": ["الله يعافيكم شوفوا لنا حل.", "تكفون بسرعة.", "وشكرا.", "الحين صار لها وايد ومحد سوا شي.", ""],
           "en": ["Please fix this soon.", "Thank you.", "Please contact me.", "This is the third time I report it.", ""]}
PLACES = {"ar": ["مدرسة الحي", "المسجد", "السوق المركزي", "المستوصف", "مخبز الحي", "الدوار", "مدخل الحي"],
          "en": ["the neighbourhood school", "the mosque", "the central market", "the clinic", "the bakery",
                 "the roundabout", "the entrance of the district"]}
LATIN_WORDS = ["app", "system", "OK", "online", "ticket"]
DETAILS = {"msa": ["والوضع يتكرر كل أسبوع.", "وقد أبلغت عن ذلك سابقا.", "والمشكلة تزداد سوءا.", "ويتضرر منها سكان الحي كلهم.",
                   "وهذا يؤثر على الأطفال وكبار السن.", "ولم يحضر أحد للمعاينة.", "والوضع على هذه الحال منذ مدة."],
           "gulf": ["وكل أسبوع نفس الشي.", "وبلغنا قبل ومحد سوا شي.", "والوضع كل يوم يسوء.", "وكل أهل الحي متضررين.",
                    "والعيال والشيبان يتأذون.", "ومحد جا يشوف.", "وصار له فترة على هالحال."],
           "en": ["It happens every week.", "I reported it before.", "It is getting worse.", "The whole neighbourhood is affected.",
                  "Children and older people are at risk.", "Nobody came to inspect it.", "It has been like this for a while."]}

FIRST_AR = ["محمد", "عبدالله", "سارة", "نورة", "فهد", "ريم", "خالد", "منيرة", "سلطان", "هيفاء", "عبدالرحمن", "أمل",
            "ناصر", "لطيفة", "تركي", "جواهر", "بدر", "دانة", "راشد", "شهد"]
FIRST_EN = ["Mohammed", "Abdullah", "Sara", "Noura", "Fahad", "Reem", "Khalid", "Munira", "Sultan", "Haifa",
            "Abdulrahman", "Amal", "Nasser", "Latifa", "Turki", "Jawaher", "Badr", "Dana", "Rashid", "Shahad"]
FAMILY_AR = ["القحطاني", "الشمري", "الدوسري", "الزهراني", "الغامدي", "العنزي", "المطيري", "الحربي", "السبيعي", "الشهري"]
FAMILY_EN = ["Al-Qahtani", "Al-Shammari", "Al-Dosari", "Al-Zahrani", "Al-Ghamdi", "Al-Enezi", "Al-Mutairi",
             "Al-Harbi", "Al-Subaie", "Al-Shehri"]

DIALECT_MAP = [  # variant, canonical, note
    ("اللحين", "الحين", "now"), ("الحينه", "الحين", "now"), ("ماحد", "محد", "nobody"), ("ما احد", "محد", "nobody"),
    ("مرره", "مره", "very"), ("شنو", "وش", "what"), ("ويش", "وش", "what"), ("ليه", "ليش", "why"),
    ("ميه", "مويه", "water"), ("مويا", "مويه", "water"), ("زباله", "الزباله", "rubbish"),
    ("ماشفنا", "ما شفنا", "we did not see"), ("مافي", "ما فيه", "there is no"), ("مافيه", "ما فيه", "there is no"),
    ("انشاللة", "ان شاء الله", "God willing"), ("انشالله", "ان شاء الله", "God willing"),
]
DIALECT_VARIANTS = {"الحين": ["اللحين", "الحينه"], "محد": ["ماحد"], "مره": ["مرره"], "وش": ["شنو", "ويش"],
                    "ليش": ["ليه"], "مويه": ["ميه", "مويا"]}

# letters and their isolated presentation forms (text pasted from PDF files)
PRESENTATION = {"ا": "ﺍ", "ب": "ﺏ", "ت": "ﺕ", "ر": "ﺭ", "د": "ﺩ", "و": "ﻭ", "ل": "ﻝ", "م": "ﻡ", "ن": "ﻥ", "ي": "ﻱ"}
DIACRITICS = ["َ", "ُ", "ِ", "ّ", "ْ", "ً"]


def rnd(*parts) -> random.Random:
    return random.Random(hashlib.sha256(json.dumps([SEED, *parts], ensure_ascii=False).encode()).hexdigest())


def choice_w(r: random.Random, items: list[tuple]):
    x, acc = r.random(), 0.0
    for item, w in items:
        acc += w
        if x < acc:
            return item
    return items[-1][0]


def phone(r: random.Random, arabic: bool) -> str:
    d = "5" + "".join(str(r.randrange(10)) for _ in range(8))
    fmt = r.randrange(5)
    s = ["0" + d, f"+966 {d[:2]} {d[2:5]} {d[5:]}", "966" + d, f"0{d[:2]}-{d[2:5]}-{d[5:]}", f"0{d[:2]} {d[2:5]} {d[5:]}"][fmt]
    return s.translate(AR_DIGITS) if arabic and r.random() < 0.35 else s


def national_id(r: random.Random, arabic: bool) -> str:
    s = r.choice("12") + "".join(str(r.randrange(10)) for _ in range(9))
    return s.translate(AR_DIGITS) if arabic and r.random() < 0.35 else s


def person(r: random.Random, variety: str) -> str:
    i = r.randrange(len(FIRST_AR))
    j = r.randrange(len(FAMILY_AR))
    return f"{FIRST_EN[i]} {FAMILY_EN[j]}" if variety == "en" else f"{FIRST_AR[i]} {FAMILY_AR[j]}"


def email(r: random.Random) -> str:
    i = r.randrange(len(FIRST_EN))
    return f"{FIRST_EN[i].lower()}.{r.randrange(10, 999)}@{r.choice(['mail.example', 'inbox.example', 'post.example'])}"


def fill(r: random.Random, sentence: str, variety: str) -> str:
    lang = "en" if variety == "en" else "ar"
    n = r.randrange(1, 201)
    street = f"Street {n}" if lang == "en" else f"شارع {n}"
    return sentence.format(street=street, days=r.randrange(2, 31), place=r.choice(PLACES[lang]))


def pii_sentence(r: random.Random, variety: str, district: str) -> tuple[str, list[dict]]:
    """One sentence that carries personal data, and the marked values."""
    arabic = variety != "en"
    kind = choice_w(r, [("phone", 0.42), ("name", 0.24), ("name_phone", 0.12), ("id", 0.10), ("email", 0.07),
                        ("bare_name", 0.05)])
    if kind == "phone":
        p = phone(r, arabic)
        s = r.choice({"msa": ["للتواصل: {p}", "رقم جوالي {p}"], "gulf": ["كلموني على {p}", "جوالي {p}"],
                      "en": ["Call me on {p}.", "My mobile is {p}."]}[variety]).format(p=p)
        return s, [{"type": "phone", "value": p}]
    if kind == "name":
        n = person(r, variety)
        s = r.choice({"msa": ["اسمي {n}.", "أنا المواطن {n}."], "gulf": ["معك {n}.", "انا {n} من سكان الحي."],
                      "en": ["My name is {n}.", "Regards, {n}"]}[variety]).format(n=n)
        return s, [{"type": "name", "value": n}]
    if kind == "name_phone":
        n, p = person(r, variety), phone(r, arabic)
        s = {"msa": "مقدم البلاغ: {n}، جوال {p}", "gulf": "انا {n} وهذا رقمي {p}",
             "en": "{n}, phone {p}"}[variety].format(n=n, p=p)
        return s, [{"type": "name", "value": n}, {"type": "phone", "value": p}]
    if kind == "id":
        i = national_id(r, arabic)
        s = {"msa": "رقم الهوية {i}", "gulf": "رقم هويتي {i}", "en": "ID number {i}"}[variety].format(i=i)
        return s, [{"type": "national_id", "value": i}]
    if kind == "email":
        e = email(r)
        s = {"msa": "بريدي الإلكتروني {e}", "gulf": "ايميلي {e}", "en": "Contact: {e}"}[variety].format(e=e)
        return s, [{"type": "email", "value": e}]
    n = person(r, variety)  # a name with no cue word in front of it
    en_name, ar_name = DISTRICTS[district][0], DISTRICTS[district][1]
    s = f"{n}, resident of {en_name}" if variety == "en" else f"{n} - حي {ar_name}"
    return s, [{"type": "name", "value": n}]


def scriptify(r: random.Random, text: str, channel: str) -> str:
    """The script variation of Arabic text as it reaches the centre."""
    words = text.split(" ")
    out = []
    for w in words:
        if w.startswith(("أ", "إ")) and r.random() < 0.35:
            w = "ا" + w[1:]
        if w.endswith("ة") and r.random() < 0.12:
            w = w[:-1] + "ه"
        if w.endswith("ي") and len(w) > 2 and r.random() < 0.10:
            w = w[:-1] + "ى"
        out.append(w)
    text = " ".join(out)
    if r.random() < 0.15:  # diacritics on a few words
        ws = text.split(" ")
        for k in r.sample(range(len(ws)), k=min(3, len(ws))):
            if ws[k] and "ء" <= ws[k][0] <= "ي":
                ws[k] = ws[k][0] + r.choice(DIACRITICS) + ws[k][1:]
        text = " ".join(ws)
    if r.random() < 0.10:  # tatweel
        ws = text.split(" ")
        k = r.randrange(len(ws))
        if len(ws[k]) > 2 and "ء" <= ws[k][1] <= "ي":
            ws[k] = ws[k][:2] + "ـــ" + ws[k][2:]
        text = " ".join(ws)
    if channel == "app" and r.random() < 0.25:  # a Persian keyboard layout
        text = text.replace("ي", "ی").replace("ك", "ک")
    if channel == "email" and r.random() < 0.30:  # pasted from a PDF
        text = "".join(PRESENTATION.get(c, c) if r.random() < 0.6 else c for c in text)
    return text


def compose(r: random.Random, category: str, variety: str, district: str, ambiguous: bool, channel: str) -> tuple[str, str | None, list[dict]]:
    bank = CORE[category][variety]
    first, other = r.sample(range(len(bank)), k=2)
    parts = [r.choice(OPENERS[variety]), fill(r, bank[first], variety)]
    if r.random() < 0.40:
        parts.append(fill(r, bank[other], variety))
    if r.random() < 0.6:
        parts.append(r.choice(DETAILS[variety]))
    second = None
    if ambiguous:
        second = r.choice([c for c in CATEGORIES if c != category])
        parts.append(fill(r, r.choice(CORE[second][variety]), variety))
    parts.append(r.choice(CLOSERS[variety]))
    text = " ".join(p for p in parts if p)
    pii = []
    if r.random() < 0.62:
        s, pii = pii_sentence(r, variety, district)
    else:
        s = ""
    if variety == "gulf":
        for canon, variants in DIALECT_VARIANTS.items():
            if canon in text and r.random() < 0.35:
                text = text.replace(canon, r.choice(variants), 1)
        if "وايد" in text and r.random() < 0.3:
            text = text.replace("وايد", "واااايد", 1)
        if r.random() < 0.10:
            text = text.replace(" ", f" {r.choice(LATIN_WORDS)} ", 1)
    if variety != "en":
        text = scriptify(r, text, channel)
    if s:  # the personal data is typed by the citizen after the complaint, outside the script noise above
        text = f"{text} {s}"
    if variety != "en":
        if r.random() < 0.25:  # numbers typed in Arabic-Indic digits
            text = text.translate(AR_DIGITS)
            pii = [{**p, "value": p["value"].translate(AR_DIGITS)} for p in pii]
    return text, second, pii


# ---------------------------------------------------------------- the complaints

def make_complaints():
    r = rnd("complaints")
    start = date(2026, 1, 1)
    base_n = 18_476
    weights = [(k, v[2]) for k, v in DISTRICTS.items()]
    total_pop = sum(w for _, w in weights)
    weights = [(k, w / total_pop) for k, w in weights]
    rows = []
    for i in range(base_n):
        d = choice_w(r, weights)
        en, ar, pop, mix, ws = DISTRICTS[d]
        variety = choice_w(r, list(zip(VARIETIES, mix)))
        rest = 1 - ws
        cats = [("water_sewage", ws)] + [(c, rest * s / sum(OTHER_SHARES.values())) for c, s in OTHER_SHARES.items()]
        category = choice_w(r, cats)
        channel = choice_w(r, CHANNELS)
        if variety == "gulf" and r.random() < 0.3:
            channel = "call_centre"
        ambiguous = r.random() < 0.12
        text, second, pii = compose(r, category, variety, d, ambiguous, channel)
        if variety == "en":
            form_lang = "en" if r.random() < 0.97 else "ar"
        else:
            form_lang = "en" if (channel == "app" and r.random() < 0.30) or r.random() < 0.02 else "ar"
        rows.append({"received": start + timedelta(days=r.randrange(273)), "channel": channel, "form_lang": form_lang,
                     "district": d, "text": text, "_variety": variety, "_category": category, "_second": second or "",
                     "_pii": pii, "_dup": "", "_kind": "original"})
    # exact double submissions
    for k in r.sample(range(base_n), k=555):
        src = rows[k]
        rows.append({**src, "received": src["received"] + timedelta(days=r.randrange(3)),
                     "channel": r.choice([src["channel"], "web", "app"]), "_kind": "exact_copy", "_dup": f"x{k}"})
        src["_dup"] = f"x{k}"
    # resubmissions with an edit
    for k in r.sample(range(base_n), k=369):
        src = rows[k]
        add = {"msa": "هذا بلاغي الثاني عن نفس المشكلة.", "gulf": "هذي ثاني مره ابلغ عن نفس الشي.",
               "en": "This is my second report about this."}[src["_variety"]]
        rows.append({**src, "text": add + " " + src["text"], "received": src["received"] + timedelta(days=r.randrange(4, 21)),
                     "_kind": "resubmission", "_dup": src["_dup"] or f"r{k}"})
        src["_dup"] = src["_dup"] or f"r{k}"
    # the campaign: one sewage overflow, 600 copy-and-edit messages from Al-Naseem
    camp = ["ترى المجاري طافحة في شارع 12 عند المدرسة من أسبوعين والريحة وايد",
            "المجاري طافحة في شارع 12 جنب المدرسة من أسبوعين والشارع غرقان والريحة وايد",
            "المجاري في شارع 12 عند المدرسة طافحة من أسبوعين والعيال يمرون من وسط المويه"]
    for k in range(600):
        variety = "gulf" if r.random() < 0.8 else "msa"
        if variety == "gulf":
            core = r.choice(camp)
        else:
            core = "مياه الصرف الصحي طافحة في شارع 12 عند المدرسة منذ أسبوعين والرائحة لا تحتمل"
        extra = r.choice(["", "، نبي حل", "، الله يعافيكم", "، تكفون", "، صار لها وايد"]) if variety == "gulf" else r.choice(["", "، نرجو الحل"])
        text = " ".join(x for x in [r.choice(OPENERS[variety]), core + extra + "."] if x)
        channel = choice_w(r, [("social", 0.4), ("app", 0.35), ("web", 0.25)])
        text = scriptify(r, text, channel)
        pii = []
        if r.random() < 0.7:
            s, pii = pii_sentence(r, variety, "al_naseem")
            text += " " + s
        rows.append({"received": date(2026, 6, 3) + timedelta(days=r.randrange(10)), "channel": channel,
                     "form_lang": "ar" if r.random() < 0.8 else "en", "district": "al_naseem", "text": text,
                     "_variety": variety, "_category": "water_sewage", "_second": "", "_pii": pii, "_dup": "campaign",
                     "_kind": "campaign"})
    r.shuffle(rows)
    rows.sort(key=lambda x: x["received"])
    for i, row in enumerate(rows, 1):
        row["id"] = f"C{i:05d}"
    return rows


# ---------------------------------------------------------------- redaction used to prepare the labelled files

def redact_known(text: str, pii: list[dict]) -> str:
    """The generator knows where the personal data is; the labelled files are redacted with that knowledge."""
    tags = {"phone": "[PHONE]", "national_id": "[ID]", "email": "[EMAIL]", "name": "[NAME]"}
    for p in pii:
        text = text.replace(p["value"], tags[p["type"]])
    return text


# ---------------------------------------------------------------- coders and the model stand-in for recorded runs

def human_label(r: random.Random, row: dict) -> str:
    acc = 0.68 if row["_second"] else 0.95
    if r.random() < acc:
        return row["_category"]
    if row["_second"]:
        return row["_second"]
    return r.choice([c for c in CATEGORIES if c != row["_category"]])


FLOOD_WORDS = ["غرقان", "مويه", "الشارع غرقان"]
CONFUSE = {"permits": "staff_service", "staff_service": "permits", "waste": "parks", "parks": "waste",
           "lighting": "parks", "roads": "water_sewage", "noise": "roads", "water_sewage": "roads"}


def latent_label(doc_id: str, row: dict, prompt: str, categories=CATEGORIES, acc_table=None) -> str:
    """Fahim's answer for a document and a prompt, before run-to-run variation (synthetic)."""
    r = rnd("latent", doc_id, prompt)
    acc = (acc_table or {"P1": {"msa": 0.88, "gulf": 0.72, "en": 0.90}, "P2": {"msa": 0.87, "gulf": 0.75, "en": 0.91}})[prompt][row["_variety"]]
    if row["_second"]:
        acc *= 0.72
    if r.random() < acc:
        return row["_category"]
    if row["_second"] and r.random() < 0.7:
        return row["_second"]
    if (row["_category"] == "water_sewage" and row["_variety"] == "gulf"
            and any(w in row["text"] for w in FLOOD_WORDS) and "roads" in categories):
        return "roads"
    if "staff_service" in categories and r.random() < 0.40 and row["_category"] != "staff_service":
        return "staff_service"
    if CONFUSE.get(row["_category"]) in categories and r.random() < 0.5:
        return CONFUSE[row["_category"]]
    return r.choice([c for c in categories if c != row["_category"]])


def run_label(doc_id: str, row: dict, prompt: str, run: int, categories=CATEGORIES, acc_table=None) -> str:
    base = latent_label(doc_id, row, prompt, categories, acc_table)
    if run == 1:
        return base
    r = rnd("run", doc_id, prompt, run)
    flip = 0.22 if row["_second"] else 0.035
    if r.random() < flip:
        options = [row["_category"], row["_second"]] if row["_second"] else categories
        return r.choice([c for c in options if c and c != base] or [base])
    return base


def tokens(text: str) -> int:
    arabic = sum("؀" <= c <= "ۿ" or "ﭐ" <= c <= "﻿" for c in text)
    return max(1, round(arabic / 2.6 + (len(text) - arabic) / 4.0))


# ---------------------------------------------------------------- inspection reports

DEFECTS = {
    "pothole": ("a deep pothole", "حفرة عميقة"),
    "sewage_overflow": ("sewage overflowing from a manhole", "طفح مياه الصرف من غرفة تفتيش"),
    "broken_light": ("a street light out of service", "عمود إنارة معطل"),
    "illegal_dumping": ("construction waste dumped illegally", "مخلفات بناء مرمية بشكل مخالف"),
    "damaged_pavement": ("a broken section of pavement", "جزء متكسر من الرصيف"),
    "fallen_sign": ("a fallen traffic sign", "لوحة مرورية ساقطة"),
}
SEVERITY = {
    "low": ("The defect is minor.", "الخلل بسيط."),
    "medium": ("The defect is moderate.", "الخلل متوسط."),
    "high": ("The defect is serious.", "الخلل جسيم."),
    "critical": ("The defect is critical and needs immediate action.", "الخلل حرج ويتطلب تدخلا فوريا."),
}
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December"]
MONTHS_AR = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def make_inspections():
    r = rnd("inspections")
    reports, refs, runs = [], [], []
    for i in range(1, 501):
        rid = f"IR-{i:04d}"
        lang = "en" if r.random() < 0.4 else "ar"
        d = r.choice(list(DISTRICTS))
        en_name, ar_name = DISTRICTS[d][0], DISTRICTS[d][1]
        when = date(2026, 1, 5) + timedelta(days=r.randrange(260))
        fmt = r.choice(["iso", "dmy", "words", "words"])
        if fmt == "iso":
            ds = when.isoformat()
        elif fmt == "dmy":
            ds = f"{when.day:02d}/{when.month:02d}/{when.year}"
        else:
            ds = f"{when.day} {MONTHS_EN[when.month - 1]} {when.year}" if lang == "en" else f"{when.day} {MONTHS_AR[when.month - 1]} {when.year}"
        if lang == "ar" and r.random() < 0.3:
            ds = ds.translate(AR_DIGITS)
        defect = r.choice(list(DEFECTS))
        severity = choice_w(r, [("low", 0.3), ("medium", 0.35), ("high", 0.25), ("critical", 0.10)])
        hazard = severity in ("high", "critical") or r.random() < 0.2
        deadline = None if r.random() < 0.3 else {"low": 30, "medium": 14, "high": 7, "critical": 2}[severity] + r.choice([0, 0, 1, 3])
        district_text = r.choice([en_name, en_name.replace("Al-", "Al "), en_name.replace("Al-", "")]) if lang == "en" else r.choice([ar_name, "حي " + ar_name])
        street = r.randrange(1, 61)
        if lang == "en":
            hz = "It poses a risk to pedestrians." if hazard else "There is no risk to the public."
            dl = f"Repair within {deadline} days." if deadline else r.choice(["No deadline was set.", "The repair date will be set later.", ""])
            text = (f"Inspection report {rid}. Date of visit: {ds}. District: {district_text}. The inspector found "
                    f"{DEFECTS[defect][0]} on Street {street}. {SEVERITY[severity][0]} {hz} {dl}").strip()
        else:
            hz = "يشكل خطرا على المارة." if hazard else "لا يوجد خطر على المارة."
            dl = f"يجب الإصلاح خلال {deadline} أيام." if deadline else r.choice(["لم يحدد موعد للإصلاح.", "سيحدد موعد الإصلاح لاحقا.", ""])
            text = (f"تقرير معاينة رقم {rid}. تاريخ الزيارة: {ds}. الحي: {district_text}. لاحظ المفتش {DEFECTS[defect][1]} "
                    f"في شارع {street}. {SEVERITY[severity][1]} {hz} {dl}").strip()
            if r.random() < 0.25:
                text = text.translate(AR_DIGITS)
        ref = {"id": rid, "district": d, "inspection_date": when.isoformat(), "defect_type": defect, "severity": severity,
               "hazard_to_public": hazard, "repair_deadline_days": deadline}
        # the recorded extraction run (synthetic): the error patterns of Lab 4.2
        rr = rnd("extract", rid)
        got = dict(ref)
        if deadline is None and rr.random() < 0.28:
            got["repair_deadline_days"] = {"low": 30, "medium": 14, "high": 7, "critical": 3}[severity]
        if fmt == "dmy" and when.day <= 12 and when.day != when.month and rr.random() < 0.35:
            got["inspection_date"] = date(when.year, when.day, when.month).isoformat()
        if not hazard and rr.random() < 0.15:
            got["hazard_to_public"] = True
        if defect in ("damaged_pavement", "pothole") and rr.random() < 0.12:
            got["defect_type"] = "pothole" if defect == "damaged_pavement" else "damaged_pavement"
        if severity == "medium" and lang == "ar" and rr.random() < 0.15:
            got["severity"] = "low"
        if district_text.startswith("Al ") or district_text.startswith("حي"):
            if rr.random() < 0.10:
                got["district"] = None
        if deadline is not None and rr.random() < 0.04:
            got["repair_deadline_days"] = None
        reports.append({"id": rid, "lang": lang, "text": text})
        refs.append(ref)
        runs.append({**got, "model": "google/gemma-4-31b-it:free", "prompt": "extract_v1", "recorded": "synthetic",
                     "prompt_tokens": tokens(text) + 410, "completion_tokens": 62})
    return reports, refs, runs


# ---------------------------------------------------------------- capstone corpora

CAPSTONE = {
    "nadwa": {
        "org": ("Nadwa Public Libraries Network", "شبكة ندوة للمكتبات العامة"),
        "unit": "branch",
        "places": ["central", "north", "east", "west", "harbour", "university"],
        "categories": {
            "opening_hours": {"msa": ["المكتبة تغلق مبكرا في نهاية الأسبوع.", "لا تتوافق ساعات العمل مع أوقات الطلاب."],
                              "gulf": ["المكتبة تسكر بدري بالويكند.", "الدوام ما يناسب الطلاب أبد."],
                              "en": ["The library closes too early at the weekend.", "Opening hours do not suit students."]},
            "collections": {"msa": ["الكتب العربية الحديثة قليلة جدا.", "طلبت كتابا منذ شهر ولم يصل."],
                            "gulf": ["الكتب العربية الجديدة قليلة مره.", "طلبت كتاب من شهر وللحين ما وصل."],
                            "en": ["There are very few new Arabic books.", "I requested a book a month ago and it never arrived."]},
            "facilities": {"msa": ["التكييف في قاعة المطالعة معطل.", "شبكة الإنترنت في المكتبة ضعيفة."],
                           "gulf": ["المكيف في قاعة القراية خربان.", "النت في المكتبة ضعيف مره."],
                           "en": ["The air conditioning in the reading room is broken.", "The library's internet is very slow."]},
            "staff": {"msa": ["الموظف في مكتب الإعارة لم يتعاون معي.", "لم يجب أحد على استفساري في المكتب."],
                      "gulf": ["موظف الإعارة ما تعاون معي.", "محد رد على سؤالي بالمكتب."],
                      "en": ["The staff at the loans desk were unhelpful.", "Nobody at the desk answered my question."]},
            "events": {"msa": ["ألغيت ورشة الأطفال دون إشعار.", "التسجيل في الفعاليات يمتلئ بسرعة."],
                       "gulf": ["لغوا ورشة الأطفال وما علمونا.", "التسجيل بالفعاليات يخلص بسرعة."],
                       "en": ["The children's workshop was cancelled without notice.", "Event registration fills up too fast."]},
        },
        "brief": ("Nadwa's director wants the share of feedback about facilities in each branch, corrected for the "
                  "labelling model's errors, before deciding which two branches get the renovation budget."),
    },
    "raafid": {
        "org": ("Raafid Social Support Office", "مكتب رافد للدعم الاجتماعي"),
        "unit": "region",
        "places": ["north", "south", "east", "west", "central"],
        "categories": {
            "eligibility": {"msa": ["رفض طلبي رغم أنني أستوفي الشروط.", "لا أفهم سبب عدم أهليتي للدعم."],
                            "gulf": ["رفضوا طلبي وانا مستوفي الشروط.", "ما فهمت ليش ما طلعت مستحق."],
                            "en": ["My application was rejected although I meet the conditions.", "I do not understand why I am not eligible."]},
            "payments": {"msa": ["تأخر صرف الدعم لهذا الشهر.", "المبلغ المصروف أقل من المعتاد."],
                         "gulf": ["الدعم تأخر هالشهر.", "المبلغ نازل أقل من العادة."],
                         "en": ["This month's payment is late.", "The amount paid is lower than usual."]},
            "documents": {"msa": ["النظام لا يقبل رفع المستندات.", "طلبوا مني مستندا قدمته من قبل."],
                          "gulf": ["النظام ما يقبل ارفع الأوراق.", "طلبوا مني ورقة عطيتهم اياها قبل."],
                          "en": ["The system will not accept my documents.", "They asked for a document I already submitted."]},
            "appointments": {"msa": ["لا توجد مواعيد متاحة في الفرع.", "ألغي موعدي دون إشعار."],
                             "gulf": ["ما فيه مواعيد بالفرع.", "لغوا موعدي وما علموني."],
                             "en": ["There are no appointments available at the branch.", "My appointment was cancelled without notice."]},
            "staff": {"msa": ["الموظف رفض شرح القرار.", "لم يرد أحد على اتصالاتي."],
                      "gulf": ["الموظف ما رضى يشرح القرار.", "محد رد على اتصالاتي."],
                      "en": ["The employee refused to explain the decision.", "Nobody answered my calls."]},
        },
        "brief": ("Raafid's director wants the monthly share of enquiries about late payments in each region, with "
                  "intervals, to decide whether the payment-delay problem is national or regional."),
    },
}


def make_capstone(key: str):
    spec = CAPSTONE[key]
    cats = list(spec["categories"])
    r = rnd("capstone", key)
    rows = []
    for i in range(1, 2501):
        variety = choice_w(r, [("msa", 0.45), ("gulf", 0.35), ("en", 0.20)])
        category = choice_w(r, list(zip(cats, [0.18, 0.22, 0.25, 0.15, 0.20])))
        second = r.choice([c for c in cats if c != category]) if r.random() < 0.12 else ""
        bank = spec["categories"][category][variety]
        parts = [r.choice(OPENERS[variety]), r.choice(bank)]
        if second:
            parts.append(r.choice(spec["categories"][second][variety]))
        parts.append(r.choice(CLOSERS[variety]))
        text = " ".join(p for p in parts if p)
        if variety != "en":
            text = scriptify(r, text, r.choice(["web", "app", "email"]))
        pii = []
        if r.random() < 0.55:
            s, pii = pii_sentence(r, variety, "al_nuzha")
            s = s.replace("حي النزهة", "الحي").replace("resident of Al-Nuzha", "a member")
            text += " " + s
        rows.append({"id": f"{key[0].upper()}{i:05d}", "received": (date(2026, 1, 1) + timedelta(days=r.randrange(273))).isoformat(),
                     spec["unit"]: r.choice(spec["places"]), "text": text, "_variety": variety, "_category": category,
                     "_second": second, "_pii": pii})
    for k in r.sample(range(len(rows)), k=75):  # double submissions
        rows.append({**rows[k], "id": f"{key[0].upper()}{len(rows) + 1:05d}"})
    out = DATA / "capstone" / key
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "documents.csv", [{k: v for k, v in x.items() if not k.startswith("_")} for x in rows],
              ["id", "received", spec["unit"], "text"])
    gold_rows = rnd("cap-gold", key).sample(rows[:2500], k=200)
    gold, runs = [], []
    acc = {"P1": {"msa": 0.86, "gulf": 0.74, "en": 0.89}, "P2": {"msa": 0.86, "gulf": 0.77, "en": 0.90}}
    for x in gold_rows:
        rh = rnd("cap-coders", key, x["id"])
        gold.append({"id": x["id"], "text": redact_known(x["text"], x["_pii"]), "variety": x["_variety"],
                     "coder_a": human_label_c(rh, x, cats), "coder_b": human_label_c(rh, x, cats), "gold": x["_category"]})
        for p in ("P1", "P2"):
            for run in (1, 2, 3):
                runs.append({"id": x["id"], "prompt": p, "run": run, "label": run_label(x["id"], x, p, run, cats, acc)})
    write_csv(out / "gold.csv", gold, ["id", "text", "variety", "coder_a", "coder_b", "gold"])
    write_csv(out / "model_runs_gold.csv", runs, ["id", "prompt", "run", "label"])
    labels = [{"id": x["id"], "label": run_label(x["id"], x, "P1", 1, cats, acc)} for x in rows]
    write_csv(out / "model_labels_all.csv", labels, ["id", "label"])
    lines = [f"# Codebook: {spec['org'][0]} ({spec['org'][1]})", "",
             "Synthetic capstone corpus. Assign one category per document: the main subject of the request.", ""]
    lines += [f"- `{c}`" for c in cats]
    (out / "codebook.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    (out / "brief.md").write_text(f"# Brief: {spec['org'][0]}\n\n{spec['brief']}\n\nFiles: documents.csv (2,575 documents "
                                  f"as received, with personal data), gold.csv (200 redacted documents, two coders and the "
                                  f"adjudicated label), model_runs_gold.csv (two prompts, three runs; synthetic), "
                                  f"model_labels_all.csv (prompt 1, run 1, all documents; synthetic).\n",
                                  encoding="utf-8", newline="\n")
    return rows


def human_label_c(r, x, cats):
    if r.random() < (0.68 if x["_second"] else 0.95):
        return x["_category"]
    return x["_second"] or r.choice([c for c in cats if c != x["_category"]])


# ---------------------------------------------------------------- files

def write_csv(path: Path, rows: list[dict], fields: list[str], gz: bool = False) -> None:
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for row in rows:
        w.writerow({k: (v.isoformat() if isinstance(v, date) else v) for k, v in row.items() if k in fields})
    data = buf.getvalue().encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if gz:
        with open(path, "wb") as f:
            with gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as g:
                g.write(data)
    else:
        path.write_bytes(data)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8", newline="\n")


PROMPT_P1 = """You label citizen complaints for Sada Citizen Voice Centre.
Assign each complaint exactly one category: the main problem the citizen asks the centre to fix.
Categories:
- water_sewage: water supply, pressure, leaks, sewage overflow, manholes, flooding from sewage or pipes
- roads: potholes, pavements, excavations, speed bumps, bridges, road surfaces
- waste: rubbish collection, bins, dumping of waste
- lighting: street lights and poles
- noise: noise from workshops, construction, halls, generators
- permits: permit and licence applications, renewals, inspections for a licence
- parks: parks, gardens, play equipment, public toilets, walking tracks
- staff_service: how staff treated the citizen, unanswered calls, reports closed without action, waiting at a branch
Personal data has been replaced by tags such as [PHONE] and [NAME]; ignore the tags.
Reply with JSON only: {"labels": [{"id": "<id>", "label": "<category>"}, ...]} with one entry per complaint.
"""

PROMPT_P2 = """Sada Citizen Voice Centre receives complaints in Arabic (formal and Gulf dialect) and English.
Read each complaint and decide which department must act on it. Use one of these eight labels, exactly as written:
water_sewage (water and sewage networks, including streets flooded by sewage or a burst pipe), roads (road surfaces
and pavements), waste (cleanliness and rubbish), lighting (street lighting), noise, permits (permits and licences),
parks (parks and public facilities), staff_service (the behaviour of staff and the quality of the service itself).
When a complaint mentions two problems, choose the one the citizen asks to be fixed first.
Tags such as [PHONE] or [NAME] stand for removed personal data.
Return JSON only, in the form {"labels": [{"id": "...", "label": "..."}]}, one entry per complaint, in the given order.
"""

CODEBOOK = """# Sada complaint codebook (version 3)

Owner: Muhannad Al-Oqaili, head of complaint intake. Synthetic, for the DS-306 labs.

Assign **one** category to each complaint: the main problem the citizen asks the centre to fix. When a complaint
names two problems, the main one is the one described first and at more length. Do not code the tone.

| Code | Category | Includes | Does not include |
|---|---|---|---|
| `water_sewage` | Water and sewage (المياه والصرف الصحي) | Supply cuts, pressure, leaking pipes, sewage overflow, manholes, a street flooded by sewage or a burst pipe | Rain water on a damaged road with no pipe or sewage named (`roads`) |
| `roads` | Roads and pavements (الطرق والأرصفة) | Potholes, broken pavements, unfinished excavations, speed bumps, bridges | Road works that are noisy at night (`noise`) |
| `waste` | Waste and cleanliness (النظافة والنفايات) | Collection, bins, construction waste dumped | Dirty park toilets (`parks`) |
| `lighting` | Street lighting (إنارة الشوارع) | Lights off or on at the wrong time, leaning poles | Lighting inside a park (`parks`) |
| `noise` | Noise (الإزعاج والضوضاء) | Workshops, construction, halls, generators | |
| `permits` | Permits and licences (التصاريح والرخص) | Building permits, shop licences, licence inspections, rejections | Rude staff at a permits counter (`staff_service`) |
| `parks` | Parks and public facilities (الحدائق والمرافق العامة) | Play equipment, gardens, public toilets, walking tracks | |
| `staff_service` | Staff conduct and service (تعامل الموظفين وجودة الخدمة) | Rude staff, unanswered hotline, a report closed without action, waiting at a branch | A slow permit decision with no complaint about staff (`permits`) |

Coders work on redacted text. Personal data appears as `[PHONE]`, `[ID]`, `[EMAIL]` or `[NAME]`.
"""


def main() -> None:
    DATA.mkdir(exist_ok=True)
    rows = make_complaints()
    write_csv(DATA / "complaints.csv.gz", rows, ["id", "received", "channel", "form_lang", "district", "text"], gz=True)
    write_csv(DATA / "districts.csv",
              [{"district": k, "name_en": v[0], "name_ar": v[1], "population": v[2]} for k, v in DISTRICTS.items()],
              ["district", "name_en", "name_ar", "population"])
    write_csv(DATA / "dialect_map.csv", [{"variant": a, "canonical": b, "meaning": c} for a, b, c in DIALECT_MAP],
              ["variant", "canonical", "meaning"])
    (DATA / "codebook.md").write_text(CODEBOOK, encoding="utf-8", newline="\n")
    prompts = DATA / "prompts"
    prompts.mkdir(exist_ok=True)
    (prompts / "fahim_p1.md").write_text(PROMPT_P1, encoding="utf-8", newline="\n")
    (prompts / "fahim_p2.md").write_text(PROMPT_P2, encoding="utf-8", newline="\n")

    by_id = {x["id"]: x for x in rows}
    r = rnd("samples")
    audit = r.sample(rows, k=500)
    write_csv(DATA / "redaction_audit.csv",
              [{"id": x["id"], "text": x["text"], "pii": json.dumps(x["_pii"], ensure_ascii=False)} for x in audit],
              ["id", "text", "pii"])
    # the population for labelled samples: no copies (exact or resubmitted); campaign messages stay
    unique = [x for x in rows if x["_kind"] not in ("exact_copy", "resubmission")]
    picked = r.sample(unique, k=3340)
    gold_rows, pair_rows, pool_rows = picked[:300], picked[300:340], picked[340:]
    gold, runs = [], []
    for x in gold_rows:
        rh = rnd("coders", x["id"])
        gold.append({"id": x["id"], "district": x["district"], "variety": x["_variety"], "text": redact_known(x["text"], x["_pii"]),
                     "coder_a": human_label(rh, x), "coder_b": human_label(rh, x), "gold": x["_category"]})
        for p in ("P1", "P2"):
            batch_tokens = 650 if p == "P1" else 700
            for run in (1, 2, 3):
                runs.append({"id": x["id"], "prompt": p, "run": run, "label": run_label(x["id"], x, p, run),
                             "model": "google/gemma-4-31b-it:free", "temperature": 0.7, "batch_size": 10,
                             "prompt_tokens": round(batch_tokens / 10) + tokens(redact_known(x["text"], x["_pii"])),
                             "completion_tokens": 14, "recorded": "synthetic"})
    write_csv(DATA / "gold.csv", gold, ["id", "district", "variety", "text", "coder_a", "coder_b", "gold"])
    write_csv(DATA / "model_runs_gold.csv", runs, ["id", "prompt", "run", "label", "model", "temperature", "batch_size",
                                                    "prompt_tokens", "completion_tokens", "recorded"])
    pair = []
    for x in pair_rows:
        rh = rnd("pair", x["id"])
        pair.append({"id": x["id"], "text": redact_known(x["text"], x["_pii"]), "coder_1": human_label(rh, x),
                     "coder_2": human_label(rh, x)})
    write_csv(DATA / "pair40.csv", pair, ["id", "text", "coder_1", "coder_2"])
    pool = []
    for x in pool_rows:
        rp = rnd("routing", x["id"])
        label = x["_category"]
        if rp.random() < 0.12:
            label = CONFUSE[label] if rp.random() < 0.6 else rp.choice([c for c in CATEGORIES if c != label])
        pool.append({"id": x["id"], "text": redact_known(x["text"], x["_pii"]), "routing_label": label})
    write_csv(DATA / "pool.csv", pool, ["id", "text", "routing_label"])
    write_csv(DATA / "model_labels_all.csv.gz",
              [{"id": x["id"], "label": run_label(x["id"], x, "P1", 1), "prompt": "P1", "run": 1,
                "model": "google/gemma-4-31b-it:free", "recorded": "synthetic"} for x in rows],
              ["id", "label", "prompt", "run", "model", "recorded"], gz=True)

    reports, refs, ex_runs = make_inspections()
    write_jsonl(DATA / "inspections.jsonl", reports)
    write_jsonl(DATA / "inspections_reference.jsonl", refs)
    write_jsonl(DATA / "inspection_runs.jsonl", ex_runs)
    for key in CAPSTONE:
        make_capstone(key)

    # the trainer's key: the hidden truth, outside data/ so that a participant does not load it by accident
    truth = HERE / "solutions" / "truth"
    truth.mkdir(parents=True, exist_ok=True)
    write_csv(truth / "complaints_truth.csv.gz",
              [{"id": x["id"], "variety": x["_variety"], "category": x["_category"], "second": x["_second"],
                "kind": x["_kind"], "dup": x["_dup"], "n_pii": len(x["_pii"])} for x in rows],
              ["id", "variety", "category", "second", "kind", "dup", "n_pii"], gz=True)
    n_unique = len(unique)
    print(f"complaints {len(rows)} (unique {n_unique}), gold {len(gold)}, pool {len(pool)}, pair {len(pair)}, "
          f"inspections {len(reports)}")


if __name__ == "__main__":
    main()
