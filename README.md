# Automazione Scheda - THE GARRET

Questo workflow automatizza l'aggiunta degli utenti con abbonamento "Scheda" alla lista Brevo.

## Struttura Repository

```
.
├── .github/
│   └── workflows/
│       └── sync_scheda.yml      # Workflow GitHub Actions
├── scripts/
│   ├── scarica_abbonamenti.py   # Il tuo script esistente
│   ├── scarica_brevo.py         # Il tuo script esistente
│   └── aggiungi_a_lista_brevo.py # Script per aggiungere alla lista
└── README.md
```

## Setup

### 1. Crea il repository GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TUO_USERNAME/garret-automation.git
git push -u origin main
```

### 2. Aggiungi i Secrets

Vai su **GitHub → Repository → Settings → Secrets and variables → Actions → New repository secret**

Aggiungi:

| Nome | Valore |
|------|--------|
| `BREVO_API_KEY` | `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` |

Aggiungi anche eventuali altri secrets necessari per scaricare i CSV (es. credenziali Wellness in Cloud).

### 3. Abilita GitHub Actions

- Vai su **Actions** nel repository
- Clicca **"I understand my workflows, go ahead and enable them"**

### 4. Test manuale

- Vai su **Actions → Sync Abbonamenti Scheda → Run workflow**
- Clicca **Run workflow**

## Come funziona

1. ⏰ Ogni 10 minuti GitHub Actions esegue il workflow
2. 📥 Scarica i CSV aggiornati (abbonamenti + Brevo)
3. 🔍 Trova utenti con abbonamento "Scheda"
4. ✅ Li aggiunge alla lista "Scheda" su Brevo (se non già presenti)
5. 📧 Da Brevo parte il flow automatico con l'email

## Note

- GitHub Actions ha un limite di 2000 minuti/mese per repo privati (gratis per repo pubblici)
- Ogni 10 minuti = ~4320 esecuzioni/mese = ok se ogni run è veloce (~1 min)
- Se vuoi ridurre le esecuzioni, modifica il cron in `sync_scheda.yml`

## Modifica frequenza

Nel file `.github/workflows/sync_scheda.yml`, modifica la riga cron:

```yaml
# Ogni 10 minuti
- cron: '*/10 * * * *'

# Ogni 30 minuti
- cron: '*/30 * * * *'

# Ogni ora
- cron: '0 * * * *'

# Ogni 6 ore
- cron: '0 */6 * * *'
```
