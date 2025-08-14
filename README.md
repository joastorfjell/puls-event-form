# Puls Musikkverksted – Påmeldingsskjema

Enkel web‑app (Flask) for påmelding til ungdomsarrangement. Lagrer CSV og kan sende e‑post varsel.

## Kom i gang

1. Klargjør miljø
   - Installer Python 3.10+
   - Opprett og aktiver valgfritt virtualenv
   - `pip install -r requirements.txt`
   - Kopier `.env.example` til `.env` og juster verdier (e‑post valgfritt)

2. Kjør appen
   - `python app.py`
   - Åpne http://localhost:5000

## Konfigurasjon (.env)
- `FLASK_SECRET_KEY`: nøkkel for flash‑meldinger
- `PORT`: port (standard 5000)
- `SMTP_*` + `NOTIFY_EMAIL`: sett for å sende e‑post. Hvis tomt, hoppes sending over.

## Data og personvern
- Data lagres i `data/registrations.csv` i inntil 60 dager (manuelt slettbar).
- CSV felt: se første linje (header).

## Distribusjon
- Kan kjøres lokalt (Flask dev‑server) eller bak en omvendt proxy (nginx) med Gunicorn.
- Domeneidé: `paamelding.pulsmusikkverksted.no`.

### Vercel (serverless)
Appen er klar for Vercel:

- `vercel.json` ruter alle forespørsler til `api/index.py` (serverless inngang).
- `api/index.py` eksporterer en WSGI‑callable `app` fra `app.py` og bruker `ProxyFix`.
- CSV‑skriving deaktiveres automatisk på Vercel (via `VERCEL=1`), eller eksplisitt med `DISABLE_CSV=1`.

Steg:
1. Push koden til GitHub‑repo.
2. Opprett nytt Vercel‑prosjekt og koble til repoet.
3. Ingen build‑kommando trengs (Python runtime). Vercel vil lese `requirements.txt`.
4. Sett miljøvariabler i Vercel Project Settings (valgfritt for e‑post):
   - `FLASK_SECRET_KEY`
   - `NOTIFY_EMAIL`
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_TLS` (valgfritt)
   - `DISABLE_CSV=1` (valgfritt – settes implicit av Vercel)
5. Deploy. Åpne Vercel URLen.

Merk: På serverless skrives det ikke til `data/registrations.csv`. Bruk e‑post for å motta påmeldinger.

### GitHub
- Sørg for at `.gitignore` inkluderer `.env`, virtualenv og midlertidige filer (allerede satt opp).
- Git init og første commit:

```bash
git init
git add .
git commit -m "Init Puls påmelding"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

Valgfritt: Sett opp Vercel‑integrasjon mot repoet for auto‑deploy ved push.
