# HKHK-Skills Admin

## Seadistamine

### 1. Secret: STUDENTS_JSON

**Settings → Secrets → Actions → New secret**

Name: `STUDENTS_JSON`

Value (kopeeri ja muuda):
```json
{
  "students": [
    {"email": "opilane1@hkhk.edu.ee", "group": "IT-25"},
    {"email": "opilane2@hkhk.edu.ee", "group": "IT-25"}
  ],
  "teachers": [
    {"email": "opetaja1@hkhk.edu.ee"},
    {"email": "opetaja2@hkhk.edu.ee"}
  ]
}
```

### 2. GitHub App

1. https://github.com/settings/apps/new
2. Permissions: **Organization → Members** (Read & Write)
3. Install to **HKHK-Skills**
4. Secret: `APP_PRIVATE_KEY` → .pem sisu
5. Variable: `APP_ID` → App ID

## Kasutamine

**Actions → Sync Students → Run workflow**

- `dry_run: true` → näitab mida teeks
- `dry_run: false` → saadab kutsed
