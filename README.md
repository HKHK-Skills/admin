# HKHK-Skills Admin

Õpilaste ja õpetajate automaatne kutsumine GitHub organisatsiooni.

## Seadistamine

### 1. GitHub App loomine

1. Mine: https://github.com/settings/apps/new
2. Täida:
   - **Name:** `HKHK-Skills-Sync`
   - **Homepage URL:** `https://github.com/HKHK-Skills`
   - **Webhook:** ❌ Active OFF
3. **Organization permissions:**
   - Members → Read and write
   - Projects → Read and write
   - Webhooks → Read and write
4. **Where can this be installed:** Only on this account
5. Klikka **Create GitHub App**

### 2. App seadistamine

1. **Generate private key** → .pem fail laetakse alla
2. Mine **Advanced** → **Make public**
3. Mine **Install App** → vali **HKHK-Skills** org

### 3. Secrets (HKHK-Skills org tasemel)

**HKHK-Skills → Settings → Secrets and variables → Actions → New organization secret**

| Secret | Väärtus | Repository access |
|--------|---------|-------------------|
| `STUDENTS_JSON` | Õpilaste JSON (vaata allpool) | Selected → admin |
| `APP_PRIVATE_KEY` | .pem faili sisu* | Selected → admin |

*Kopeeri .pem: `cat ~/Downloads/*.pem | pbcopy`

### 4. Variables (HKHK-Skills org tasemel)

**HKHK-Skills → Settings → Secrets and variables → Actions → Variables → New organization variable**

| Variable | Väärtus |
|----------|---------|
| `APP_ID` | App ID numbrist (nt `2533231`) |

### 5. STUDENTS_JSON formaat

```json
{
  "students": [
    {"name": "Eesnimi Perenimi", "email": "email@hkhk.edu.ee", "group": "IT-25"}
  ],
  "teachers": [
    {"name": "Eesnimi Perenimi", "email": "email@hkhk.edu.ee"}
  ]
}
```

## Kasutamine

**HKHK-Skills/admin → Actions → Sync Students → Run workflow**

| Valik | Tulemus |
|-------|---------|
| `dry_run: true` | Näitab mida teeks (ohutu test) |
| `dry_run: false` | Saadab päriselt kutsed |

## Mida workflow teeb

1. Loeb `STUDENTS_JSON` secret'ist andmed
2. Loob teamid: `students-it-25`, `teachers`
3. Saadab org kutsed emailide järgi
4. Lisab liikmed õigetesse teamidesse
