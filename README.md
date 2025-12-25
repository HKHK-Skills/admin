# HKHK GitHub Education System

Automaatne süsteem õpilaste GitHub organisatsioonide haldamiseks.

## Arhitektuur

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCE                              │
│         (praegu JSON secrets, hiljem Keycloak)              │
├─────────────────────────────────────────────────────────────┤
│  STUDENTS_JSON  │  TEACHERS_JSON  │  GROUPS_JSON            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   GITHUB ACTIONS                             │
├─────────────────────────────────────────────────────────────┤
│  setup-student-org.yml   →  Seadistab õpilase org'i        │
│  sync-students.yml       →  Sünkib teams HKHK-Skills        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   GITHUB STRUCTURE                           │
├─────────────────────────────────────────────────────────────┤
│  HKHK-Skills/            (materjalid, PUBLIC)               │
│  {initial}{perenimi}/    (õpilase org, nt akreimann)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Org Nime Genereerimine

Õpilase org nimi genereeritakse **emailist** automaatselt:

| Email | Org nimi |
|-------|----------|
| `eesnimi.perenimi@hkhk.edu.ee` | `eperenimi` |
| `jaan.tamm@hkhk.edu.ee` | `jtamm` |
| `märt.põõsas@hkhk.edu.ee` | `mpoosas` |

**Loogika:**
1. Võta email prefix: `alex.kreimann`
2. Eralda eesnimi + perenimi: `alex`, `kreimann`
3. Võta eesnime initsiaal: `a`
4. Ühenda: `a` + `kreimann` = `akreimann`
5. Normaliseeri (täpitähed, lowercase): `ä→a`, `ö→o`, `ü→u`, `õ→o`

**GitHub org nime reeglid:**
- Tähed (a-z), numbrid (0-9), sidekriips (-)
- Ei tohi: tühikud, punktid, alakriipsud, täpitähed
- Max 39 tähemärki

---

## Secrets (org-level)

| Secret | Kirjeldus | Kus kasutada |
|--------|-----------|---------------|
| `GH_PAT` | Personal Access Token (classic) | Kõik workflow'd |
| `STUDENTS_JSON` | Õpilaste andmed (JSON array) | setup/sync |
| `TEACHERS_JSON` | Õpetajate andmed (JSON array) | setup/sync |
| `GROUPS_JSON` | Gruppide andmed (JSON object) | setup/sync |

### GH_PAT - Personal Access Token

**Miks PAT, mitte GitHub App?**
- GitHub App tuleb installida IGASSE org'i eraldi
- PAT töötab kõigis org'ides kus sina oled owner
- Automaatne App installimine vajab Enterprise plaani

**Loomine:** https://github.com/settings/tokens → **Classic token** (mitte fine-grained!)

**Vajalikud scope'id:**

| Scope | Miks vajalik |
|-------|---------------|
| `repo` | Repode loomine, kirjutamine õpilaste org'ides |
| `admin:org` | Org'ide haldus, kutsete saatmine, teams |
| `read:user` | Kasutajate ID pärimine kutsete jaoks |
| `project` | Valikuline - Projects haldamine |
| `write:discussion` | Valikuline - Discussions haldamine |

**Expiration:** 90+ päeva (või "No expiration")

**Repository access:** Selected repositories → `admin`

**TÄHTIS:** 
- Token on seotud SINU kontoga
- Kui sina lahkud: loo uus token teise owner'i kontolt
- Uuenda `GH_PAT` secret

### Vana: APP_PRIVATE_KEY (deprecated)

GitHub App enam ei kasutata, sest:
- App tuleb installida igasse org'i eraldi
- Automaatne installimine vajab Enterprise plaani
- PAT on lihtsam ja töötab kohe

---

## JSON Struktuurid (Secrets)

### STUDENTS_JSON

```json
[
  {
    "name": "Eesnimi Perenimi",
    "email": "eesnimi.perenimi@hkhk.edu.ee",
    "group": "IT-25"
  }
]
```

**NB!** `github` username pole vajalik - kutse läheb emailile ja õpilane loob/seob oma konto.

### TEACHERS_JSON

```json
[
  {
    "github": "teacher-github-username",
    "subjects": ["DOK", "LIN"],
    "role": "owner"
  },
  {
    "github": "another-teacher",
    "subjects": ["NET", "PRO"],
    "role": "admin"
  }
]
```

**Rollid:**
- `owner` - Kõik õigused, saab org'i kustutada, ownership transfer
- `admin` - Kutsed, repod, teams, aga ei saa org'i kustutada

### GROUPS_JSON

```json
{
  "IT-25": {
    "name": "Info- ja kommunikatsioonitehnoloogia 2025",
    "curriculum": "259012",
    "start_year": 2025,
    "end_year": 2029,
    "current_subjects": ["DOK", "DIG", "SEC", "OPS", "ITI", "NET", "WIN", "LIN", "SKR", "MIC", "PRO"]
  },
  "IT-24": {
    "name": "Info- ja kommunikatsioonitehnoloogia 2024",
    "curriculum": "259012",
    "start_year": 2024,
    "end_year": 2028,
    "current_subjects": ["DOK", "LIN", "NET", "PRO"]
  }
}
```

---

## config/subjects.json (PUBLIC)

See fail on PUBLIC - ei sisalda isikuandmeid, ainult ainete info.

```json
{
  "DOK": {
    "code": "DOK",
    "name": "Dokumentatsiooni loomine",
    "name_en": "Documentation",
    "module": "Oskused eluks ja tööks",
    "material_repo": "dokumentatsioon"
  }
}
```

**Täielik ainete nimekiri:**

| Kood | Aine | Moodul |
|------|------|--------|
| DOK | Dokumentatsiooni loomine | Oskused eluks ja tööks |
| DIG | Digisisu loomine | Digioskuste arendamine |
| SEC | Digiturvalisus ja probleemilahendus | Digioskuste arendamine |
| OPS | Op.süsteemide ja küberturbe alused | IT valdkonna alusteadmised |
| ITI | Sissejuhatus IT valdkonda ja IT töökoht | IT valdkonna alusteadmised |
| NET | Arvutivõrkude alused | IT valdkonna alusteadmised |
| WIN | Windows operatsioonisüsteemid | Põhiõpingud |
| LIN | Linux operatsioonisüsteemide haldus | Põhiõpingud |
| SKR | Skriptimisvahendid | Valiõpingud |
| MIC | Mikrokontrollerid ja robootika | Valiõpingud |
| PRO | Programmeerimise alused | Põhiõpingud |

---

## GDPR / Privaatsus

| Andmed | Asukoht | Nähtavus |
|--------|---------|----------|
| Õpilaste nimed, emailid | `STUDENTS_JSON` secret | Peidetud |
| Õpetajate GitHub usernames | `TEACHERS_JSON` secret | Peidetud |
| Gruppide info | `GROUPS_JSON` secret | Peidetud |
| Ainete koodid, nimed | `config/subjects.json` | Public |

**Miks secrets?**
- Repo on public (et teised koolid saaksid kasutada)
- Isikuandmed peavad olema peidetud (GDPR)
- Secrets on encrypted ja nähtavad ainult workflow'dele

---

## Rollid ja Permissions

### Õpilase org'is (nt `akreimann`)

| Roll | Kes | Kuidas määratakse |
|------|-----|-------------------|
| **Owner** | `role: owner` õpetajad | TEACHERS_JSON |
| **Admin** | Õpetajad kelle ained kattuvad grupi ainetega | TEACHERS_JSON + GROUPS_JSON |
| **Member** | Õpilane ise | Email kutse |

**Näide:**
- Õpilane grupis IT-24
- IT-24 current_subjects: `["DOK", "LIN", "NET", "PRO"]`
- Õpetaja X õpetab: `["DOK", "DIG", "SKR", "PRO"]`
- Ühisosa: `["DOK", "PRO"]` → Õpetaja X saab admin õigused

### HKHK-Skills org'is (materjalid)

| Roll | Kes |
|------|-----|
| **Owner** | Peamine admin |
| **Admin** | Teised õpetajad |
| **Read** | Õpilased (teams kaudu) |

---

## Workflows

| Workflow | Eesmärk | Staatus |
|----------|---------|--------|
| `setup-student-org.yml` | Seadistab õpilase org'i (kutsed, repod) | ✅ Töötab |
| `create-student-org.yml` | Üritab org'i API kaudu luua, kutsub setup | ⚠️ Vajab uuendust (kasutab App, mitte PAT) |
| `setup-roles.yml` | Loob custom repository roles | ⚠️ Vajab Team/Enterprise plaani |
| `sync-students.yml` | Sünkib teams HKHK-Skills'is | ✅ Töötab |

---

### setup-student-org.yml

**Trigger:** Manual (workflow_dispatch)

**Input:** `student_email` (nt `eesnimi.perenimi@hkhk.edu.ee`)

**Mida teeb:**
1. Leiab õpilase STUDENTS_JSON'ist emaili järgi
2. Genereerib org nime: `eesnimi.perenimi` → `eperenimi`
3. Kontrollib kas org eksisteerib (kui ei → juhised käsitsi loomiseks)
4. Kutsub owner õpetajad (TEACHERS_JSON `role: owner`)
5. Kutsub admin õpetajad (kelle ained kattuvad grupi ainetega)
6. Kutsub õpilase (emailile)
7. Loob repod: `{material_repo}` + `portfolio`

---

### create-student-org.yml

**Trigger:** Manual (workflow_dispatch)

**Input:** `student_github` (GitHub username)

**Mida teeb:**
1. Üritab org'i luua API kaudu (vajab Enterprise/Campus)
2. Kui õnnestub → kutsub `setup-student-org.yml`
3. Kui ei õnnestu → annab juhised käsitsi loomiseks

**NB:** Praegu kasutab GitHub App tokenit. Vajab uuendust PAT kasutamiseks.

---

### setup-roles.yml

**Trigger:** Manual (workflow_dispatch)

**Input:** `org_name`

**Mida teeb:**
- Loob custom repository roles `config/roles.json` põhjal

**NB:** Custom roles vajab GitHub Team või Enterprise plaani. Free plaanil ei tööta.

---

### sync-students.yml

**Trigger:** Manual või Schedule

**Mida teeb:**
- Sünkroniseerib teams HKHK-Skills org'is
- Loob `students-{grupp}` teams
- Lisab õpilased õigetesse team'idesse

---

## Flow: Uue õpilase lisamine

```
1. Lisa STUDENTS_JSON:
   {"name": "Uus Õpilane", "email": "uus.opilane@hkhk.edu.ee", "group": "IT-25"}

2. Loo org KÄSITSI: github.com/organizations/new
   - Nimi: uopilane (genereeritud emailist)
   - Plan: Free

3. Käivita workflow: setup-student-org.yml
   - Input: uus.opilane@hkhk.edu.ee

4. Workflow:
   - Kutsub õpetajad org'i
   - Kutsub õpilase (email)
   - Loob repod
```

**Miks org käsitsi?**
- GitHub API ei luba org'e luua Free plaanil
- Campus Program võib seda muuta
- Kuni selle ajani: 30 sek käsitsi tööd per õpilane

---

## Flow: Lõpetamine (Ownership Transfer)

```
1. Käivita: transfer-ownership.yml (TODO)
   Input: student_email

2. Workflow:
   - Eemaldab kõik õpetajad org'ist
   - Teeb õpilase Owner'iks
   - Õpilane saab oma portfoolio!
```

---

## Flow: Uus semester

```
1. Uuenda GROUPS_JSON:
   "IT-25": { "current_subjects": ["uued", "ained"] }

2. Käivita: update-semester.yml (TODO)

3. Workflow:
   - Uuendab permissions kõigis õpilaste org'ides
   - Lisab/eemaldab õpetajaid vastavalt uutele ainetele
```

---

## Failide struktuur

```
admin/
├── config/
│   └── subjects.json              # Ainete definitsioonid (PUBLIC)
│
├── .github/
│   └── workflows/
│       ├── setup-student-org.yml    # ✅ Seadistab õpilase org'i
│       ├── create-student-org.yml   # ⚠️ Loob org'i (vajab uuendust)
│       ├── setup-roles.yml          # ⚠️ Custom roles (vajab Team/Enterprise)
│       ├── sync-students.yml        # ✅ Sünkib teams
│       ├── update-semester.yml      # TODO
│       └── transfer-ownership.yml   # TODO
│
└── README.md
```

---

## Troubleshooting

### "Resource not accessible by integration" (403)

**Põhjus:** Token/App ei saa ligi org'ile

**Lahendus PAT puhul:**
1. Kontrolli et PAT scope'id on õiged (repo, admin:org, read:user)
2. Kontrolli et sina oled org'i owner
3. Kontrolli et PAT pole aegunud

### Org ei eksisteeri

**Põhjus:** Org tuleb luua käsitsi enne workflow käivitamist

**Lahendus:**
1. Mine: https://github.com/organizations/new
2. Nimi: (workflow ütleb mis nimi)
3. Plan: Free
4. Käivita workflow uuesti

### Kutse ei lähe

**Põhjus:** Vale email või kasutaja juba org'is

**Lahendus:**
1. Kontrolli emaili STUDENTS_JSON'is
2. Kontrolli kas kasutaja pole juba org'is

---

## Tulevikus

### Campus Program

Kui Campus Program kinnitatakse:
- Võib-olla saab org'e API kaudu luua
- Rohkem Actions minuteid
- Codespaces tunnid

### Keycloak integratsioon

```
TAHVEL → KEYCLOAK → GITHUB

Keycloak asendab JSON secrets:
- STUDENTS_JSON → Keycloak Users
- TEACHERS_JSON → Keycloak Users  
- GROUPS_JSON → Keycloak Groups
```

---

## Links

| Ressurss | URL |
|----------|-----|
| HKHK-Skills | https://github.com/HKHK-Skills |
| admin repo | https://github.com/HKHK-Skills/admin |
| GitHub Education | https://education.github.com |
| Campus Program | https://education.github.com/schools |

---

*Viimati uuendatud: Detsember 2025*
