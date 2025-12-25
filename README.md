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
│  create-student-org.yml  →  setup-student-org.yml           │
│  sync-students.yml       →  update-semester.yml             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   GITHUB STRUCTURE                           │
├─────────────────────────────────────────────────────────────┤
│  ${MATERIALS_ORG}/           (materjalid)                   │
│  ${ORG_PREFIX}-{username}/   (õpilase org)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Variables (org-level)

Kõik dünaamiline - muuda variables, mitte koodi!

| Variable | Väärtus | Kirjeldus |
|----------|---------|-----------|
| `APP_ID` | `123456` | GitHub App ID |
| `MATERIALS_ORG` | `HKHK-Skills` | Materjalide org |
| `DEFAULT_BRANCH` | `main` | Default branch nimi |
| `STUDENT_ROLE` | `member` | Õpilase roll oma org'is |
| `TEACHER_ROLE` | `admin` | Õpetaja roll õpilase org'is |

---

## Secrets (org-level)

| Secret | Kirjeldus |
|--------|-----------|
| `APP_PRIVATE_KEY` | GitHub App private key |
| `STUDENTS_JSON` | Õpilaste andmed (JSON array) |
| `TEACHERS_JSON` | Õpetajate andmed (JSON array) |
| `GROUPS_JSON` | Gruppide andmed (JSON object) |

---

## JSON Struktuurid

### STUDENTS_JSON

```json
[
  {
    "github": "student-username",
    "group": "IT-25",
    "email": "student@school.edu.ee"
  },
  {
    "github": "another-student",
    "group": "IT-25",
    "email": "another@school.edu.ee"
  }
]
```

### TEACHERS_JSON

```json
[
  {
    "github": "teacher-owner",
    "subjects": ["NET"],
    "role": "owner"
  },
  {
    "github": "teacher-admin-1",
    "subjects": ["DOK", "DIG", "SKR", "PRO"],
    "role": "admin"
  },
  {
    "github": "teacher-admin-2",
    "subjects": ["SEC", "ITI", "LIN", "MIC"],
    "role": "admin"
  }
]
```

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
    "current_subjects": ["LIN", "WIN", "NET", "PRO"]
  },
  "ITS-25": {
    "name": "IT süsteemid 2025",
    "curriculum": "259013",
    "start_year": 2025,
    "end_year": 2029,
    "current_subjects": ["DOK", "LIN", "NET"]
  }
}
```

### config/subjects.json (PUBLIC)

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

---

## Organisatsioonid

| Muster | Näide | Tüüp | Visibility |
|--------|-------|------|------------|
| `${MATERIALS_ORG}` | `HKHK-Skills` | Materjalid | Public |
| `{eesnimi initial}{perenimi}` | `akreimann` | Õpilane | Private |
| `{grupp}-{projekt}` | `IT25-veebipood` | Projekt | Private |

---

## Teams (${MATERIALS_ORG} sees)

| Muster | Näide | Liikmed |
|--------|-------|---------|
| `teachers` | `teachers` | Kõik õpetajad |
| `teachers-{AINE}` | `teachers-DOK` | DOK aine õpetajad |
| `students-{GRUPP}` | `students-IT-25` | IT-25 õpilased |

Teams luuakse automaatselt TEACHERS_JSON ja GROUPS_JSON põhjal.

---

## Rollid ja Permissions

### ${MATERIALS_ORG} (materjalid)

| Roll | Kes | Permission | Allikas |
|------|-----|------------|---------|
| Owner | `role: owner` teachers | Admin | TEACHERS_JSON |
| Admin | `role: admin` teachers | Write | TEACHERS_JSON |
| Read | Õpilased | Read | STUDENTS_JSON → team |

### ${ORG_PREFIX}-{username} (õpilase org)

| Roll | Kes | Permission | Loogika |
|------|-----|------------|---------|
| Owner | `role: owner` teachers | Owner | TEACHERS_JSON |
| Admin | Õpetajad kelle ained ∩ grupi subjects | Admin | TEACHERS_JSON ∩ GROUPS_JSON |
| Member | Õpilane | Write | STUDENTS_JSON |

---

## Permission Matrix

### Org-level

| Permission | Owner | Admin | Member |
|------------|:-----:|:-----:|:------:|
| Org settings | ✅ | ❌ | ❌ |
| Manage members | ✅ | ✅ | ❌ |
| Manage teams | ✅ | ✅ | ❌ |
| Create repos | ✅ | ✅ | ⚙️ |
| Delete org | ✅ | ❌ | ❌ |

### Repo-level

| Permission | Admin | Write | Read |
|------------|:-----:|:-----:|:----:|
| Settings | ✅ | ❌ | ❌ |
| Push | ✅ | ✅ | ❌ |
| Pull request | ✅ | ✅ | ✅ |
| Clone | ✅ | ✅ | ✅ |

---

## Workflows

| Workflow | Trigger | Mida teeb |
|----------|---------|-----------|
| `create-student-org.yml` | Manual | Loob õpilase org'i |
| `setup-student-org.yml` | Called | Seadistab org'i (invites, repos) |
| `sync-students.yml` | Manual/Schedule | Sünkib teams ${MATERIALS_ORG} |
| `update-semester.yml` | Manual | Uuendab permissions |
| `transfer-ownership.yml` | Manual | Annab org'i õpilasele |

---

## Flow: Uus õpilane

```
1. Lisa STUDENTS_JSON:
   {"github": "uus-opilane", "group": "IT-25", "email": "..."}

2. Käivita: create-student-org.yml
   Input: student_github = "student-username"
   
3. Workflow loeb:
   - STUDENTS_JSON → leiab grupi (IT-25)
   - GROUPS_JSON → leiab current_subjects
   - TEACHERS_JSON → leiab õpetajad nende ainete jaoks
   - config/subjects.json → leiab repo nimed

4. Workflow loob:
   - Org: ${ORG_PREFIX}-uus-opilane
   - Invites: owner + admins + student
   - Repos: {subject.material_repo}-labs + portfolio

5. Käivita: sync-students.yml
   - Lisab õpilase ${MATERIALS_ORG}/teams/students-IT-25
```

---

## Flow: Uus semester

```
1. Uuenda GROUPS_JSON:
   "IT-25": { "current_subjects": ["uued", "ained"] }

2. Käivita: update-semester.yml

3. Workflow:
   - Loeb GROUPS_JSON
   - Uuendab permissions kõigis ${ORG_PREFIX}-* org'ides
   - Lisab/eemaldab õpetajaid vastavalt uutele ainetele
```

---

## Flow: Lõpetamine

```
1. Käivita: transfer-ownership.yml
   Input: student_github = "student-username"

2. Workflow:
   - Eemaldab kõik õpetajad org'ist
   - Teeb õpilase Owner'iks
   - Õpilane saab portfoolio!
```

---

## Failide struktuur

```
admin/
├── config/
│   └── subjects.json            # Ainete definitsioonid (public)
│
├── scripts/
│   └── create_student_org.sh    # Backup skript
│
├── .github/
│   └── workflows/
│       ├── create-student-org.yml
│       ├── setup-student-org.yml
│       ├── sync-students.yml
│       ├── update-semester.yml
│       └── transfer-ownership.yml
│
└── README.md
```

---

## Lisa uus aine

1. Lisa `config/subjects.json`:
```json
{
  "UUS": {
    "code": "UUS",
    "name": "Uus aine",
    "name_en": "New Subject",
    "module": "Mingi moodul",
    "material_repo": "uus-aine"
  }
}
```

2. Lisa õpetaja `TEACHERS_JSON`:
```json
{"github": "opetaja", "subjects": ["UUS"], "role": "admin"}
```

3. Lisa grupile `GROUPS_JSON`:
```json
"IT-25": { "current_subjects": [..., "UUS"] }
```

---

## Lisa uus grupp

1. Lisa `GROUPS_JSON`:
```json
{
  "IT-26": {
    "name": "Info- ja kommunikatsioonitehnoloogia 2026",
    "curriculum": "259012",
    "start_year": 2026,
    "end_year": 2030,
    "current_subjects": ["DOK", "DIG", "NET"]
  }
}
```

2. Lisa õpilased `STUDENTS_JSON`:
```json
{"github": "uus-opilane", "group": "IT-26", "email": "..."}
```

---

## Lisa uus õpetaja

1. Lisa `TEACHERS_JSON`:
```json
{
  "github": "uus-opetaja",
  "subjects": ["DOK", "LIN"],
  "role": "admin"
}
```

2. Käivita `sync-students.yml` - lisab õpetaja team'idesse

---

## Tulevikus: Keycloak

```
TAHVEL → KEYCLOAK → GITHUB

Keycloak asendab JSON secrets:
- STUDENTS_JSON → Keycloak Users (group: students/*)
- TEACHERS_JSON → Keycloak Users (group: teachers/*)
- GROUPS_JSON → Keycloak Groups (students/*)

Workflow muutub:
  secrets.STUDENTS_JSON → keycloak.api.get_users()
```

---

## Links

| Ressurss | URL |
|----------|-----|
| HKHK-Skills | https://github.com/HKHK-Skills |
| GitHub Education | https://education.github.com |
| GitHub Classroom | https://classroom.github.com |
| Keycloak | https://www.keycloak.org |
