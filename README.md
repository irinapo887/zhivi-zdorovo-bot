# Bot Biohacking Telegram 🌿

Bot automat care posteaza zilnic sfaturi de biohacking si naturopatie in rusa,
cu imagini de la Unsplash. Posteaza de 2 ori pe zi: 09:00 si 19:00.

---

## Pas 1 — Creeaza botul pe Telegram

1. Deschide Telegram si cauta @BotFather
2. Scrie `/newbot`
3. Alege un nume (ex: Biohacking Tips Bot)
4. Alege un username (ex: biohacking_tips_bot)
5. Copiaza TOKEN-ul primit (arata asa: 123456789:AAF...)

---

## Pas 2 — Adauga botul ca admin pe canalul tau

1. Mergi la canalul tau Telegram
2. Setari canal → Administratori → Adauga administrator
3. Cauta username-ul botului tau
4. Da-i permisiunea "Postare mesaje" si "Postare media"

---

## Pas 3 — Obtine cheia Unsplash (gratuit)

1. Mergi la https://unsplash.com/developers
2. Creeaza cont gratuit
3. Click "New Application"
4. Accepta termenii → copiaza "Access Key"

---

## Pas 4 — Obtine cheia Anthropic

1. Mergi la https://console.anthropic.com
2. API Keys → Create Key
3. Copiaza cheia (incepe cu sk-ant-...)

---

## Pas 5 — Deploy pe Railway (gratuit)

1. Mergi la https://railway.app si creeaza cont gratuit
2. "New Project" → "Deploy from GitHub repo"
3. Uploadeaza fisierele acestea pe GitHub (sau foloseste Railway CLI)
4. In Railway, mergi la "Variables" si adauga:

```
TELEGRAM_TOKEN = tokenul_de_la_botfather
TELEGRAM_CHANNEL = @username_canal_tau
ANTHROPIC_API_KEY = sk-ant-...
UNSPLASH_ACCESS_KEY = cheia_unsplash
TIMEZONE = Europe/Bucharest
```

5. Deploy! Botul porneste automat si face prima postare imediat.

---

## Ce face botul

- Posteaza automat la 09:00 si 19:00
- Rotatia prin 14 teme diferite de biohacking si naturopatie
- Fiecare postare: sfat practic scurt in rusa + imagine de la Unsplash
- Imagini relevante pentru fiecare tema
- Hashtag-uri in rusa incluse automat

## Teme acoperite

- NMN, NAD+, suplimente longevitate
- Post intermitent si autofagie
- Somn si recuperare
- Ritm circadian si vitamina D
- Minerale si micronutrienti
- Microbiom intestinal
- Crioterapie si hormezi
- Adaptogeni (ashwagandha, rhodiola)
- Exercitiu fizic
- Biomarkeri si analize
- Antioxidanti naturali
- Stres si recuperare
- Naturopatie si plante medicinale
- Cetoza si metabolism

---

## Cost lunar estimat

| Serviciu | Cost |
|---|---|
| Railway | Gratuit (500h/luna) |
| Unsplash | Gratuit (50 req/ora) |
| Anthropic API | ~3-8$ / luna (60 postari) |

Total: ~3-8$ pe luna doar pentru Anthropic API.
