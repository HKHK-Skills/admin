#!/usr/bin/env python3
"""
HKHK Student Organization Creator

Loob õpilase organisatsiooni GitHubis Playwright abil.
Pärast loomist käivita setup-student-org.yml workflow.

Kasutamine:
    python create_student_org.py --student jaan-tamm
    python create_student_org.py --student jaan-tamm --dry-run
    python create_student_org.py --bulk students.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright pole installitud!")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)


ORG_PREFIX = os.getenv("ORG_PREFIX", "HKHK")
GITHUB_URL = "https://github.com"


def create_org(page, org_name: str, dry_run: bool = False) -> bool:
    """Loob ühe organisatsiooni."""
    
    print(f"\n{'🔍 DRY RUN: ' if dry_run else '🚀 '}Creating org: {org_name}")
    
    if dry_run:
        print(f"   Would create: {GITHUB_URL}/organizations/new")
        print(f"   Org name: {org_name}")
        return True
    
    # Mine org loomise lehele
    page.goto(f"{GITHUB_URL}/organizations/new")
    
    # Oota kuni leht laeb
    page.wait_for_load_state("networkidle")
    
    # Vali Free plan
    free_button = page.locator("text=Create a free organization")
    if free_button.is_visible():
        free_button.click()
        page.wait_for_load_state("networkidle")
    
    # Sisesta org nimi
    name_input = page.locator("input[name='organization[login]']")
    name_input.fill(org_name)
    
    # Sisesta email (kasutab sama mis kontol)
    email_input = page.locator("input[name='organization[billing_email]']")
    if email_input.is_visible() and email_input.input_value() == "":
        # Jäta tühjaks või kasuta default
        pass
    
    # Vali "My personal account"
    personal_radio = page.locator("input[value='personal']")
    if personal_radio.is_visible():
        personal_radio.check()
    
    # Accept terms
    terms_checkbox = page.locator("input[name='terms_of_service']")
    if terms_checkbox.is_visible():
        terms_checkbox.check()
    
    # Submit
    submit_button = page.locator("button[type='submit']:has-text('Next')")
    if not submit_button.is_visible():
        submit_button = page.locator("button[type='submit']")
    
    submit_button.click()
    
    # Oota tulemust
    page.wait_for_load_state("networkidle")
    
    # Kontrolli kas õnnestus
    if org_name.lower() in page.url.lower():
        print(f"   ✅ Created: {GITHUB_URL}/{org_name}")
        return True
    else:
        print(f"   ❌ Failed to create {org_name}")
        print(f"   Current URL: {page.url}")
        return False


def login_github(page) -> bool:
    """Kontrollib kas oled sisse logitud, kui ei siis ootab."""
    
    page.goto(f"{GITHUB_URL}/organizations/new")
    page.wait_for_load_state("networkidle")
    
    # Kui oled login lehel
    if "login" in page.url:
        print("\n⚠️  Palun logi GitHubi sisse brauseris...")
        print("   Skript jätkab automaatselt pärast login'i.")
        
        # Oota kuni kasutaja logib sisse (max 5 min)
        page.wait_for_url(f"{GITHUB_URL}/**", timeout=300000)
        
        # Mine uuesti org loomise lehele
        page.goto(f"{GITHUB_URL}/organizations/new")
        page.wait_for_load_state("networkidle")
    
    return "login" not in page.url


def main():
    parser = argparse.ArgumentParser(description="Create HKHK student organizations")
    parser.add_argument("--student", type=str, help="Student GitHub username")
    parser.add_argument("--bulk", type=str, help="JSON file with students")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually create")
    parser.add_argument("--headless", action="store_true", help="Run without browser window")
    
    args = parser.parse_args()
    
    if not args.student and not args.bulk:
        parser.print_help()
        sys.exit(1)
    
    # Kogu õpilased
    students = []
    
    if args.student:
        students.append(args.student)
    
    if args.bulk:
        with open(args.bulk) as f:
            data = json.load(f)
            if isinstance(data, list):
                students.extend([s.get("github", s) if isinstance(s, dict) else s for s in data])
            else:
                students.extend([s.get("github", s) if isinstance(s, dict) else s for s in data.get("students", [])])
    
    print(f"📋 Students to process: {len(students)}")
    for s in students:
        print(f"   - {ORG_PREFIX}-{s}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - no changes will be made")
        return
    
    # Käivita Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        
        # Kasuta olemasolevat profiili (säilitab login'i)
        context = browser.new_context(
            storage_state=Path.home() / ".hkhk-github-state.json"
            if (Path.home() / ".hkhk-github-state.json").exists()
            else None
        )
        
        page = context.new_page()
        
        # Login check
        if not login_github(page):
            print("❌ Ei saanud GitHubi sisse logida")
            browser.close()
            sys.exit(1)
        
        # Salvesta login state
        context.storage_state(path=Path.home() / ".hkhk-github-state.json")
        
        # Loo org'id
        created = 0
        failed = 0
        
        for student in students:
            org_name = f"{ORG_PREFIX}-{student}"
            
            if create_org(page, org_name, dry_run=args.dry_run):
                created += 1
                
                # Salvesta state pärast igat edu
                context.storage_state(path=Path.home() / ".hkhk-github-state.json")
            else:
                failed += 1
        
        browser.close()
    
    print(f"\n📊 Results: {created} created, {failed} failed")
    
    if created > 0:
        print(f"\n👉 Next steps:")
        print(f"   1. Go to GitHub Actions")
        print(f"   2. Run 'Setup Student Organization' workflow")
        print(f"   3. Enter student username and org name")


if __name__ == "__main__":
    main()
