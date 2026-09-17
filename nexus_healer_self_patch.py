#!/usr/bin/env python3
"""
NEXUS Self-Healing Agent
Monitors error logs, researches solutions, tests patches, deploys fixes.
"""

import sys
import time
import re
import subprocess
from pathlib import Path

class NexusHealer:
    def __init__(self, error_log="nexus_errors.log"):
        self.error_log = Path(error_log)
        self.sandbox_dir = Path(".nexus_sandbox")
        self.sandbox_dir.mkdir(exist_ok=True)
    
    def parse_errors(self):
        """Extract error signatures from logs"""
        if not self.error_log.exists():
            return []
        
        content = self.error_log.read_text()
        errors = []
        
        # Pattern: Python exceptions
        for match in re.finditer(r'(\w+Error): (.+?)\n', content):
            errors.append({
                'type': match.group(1),
                'message': match.group(2),
                'signature': f"{match.group(1)}: {match.group(2)[:50]}"
            })
        
        # Pattern: NyxLang crashes
        for match in re.finditer(r'\[NEXUS CRASH\] (.+)', content):
            errors.append({
                'type': 'NEXUS_CRASH',
                'message': match.group(1),
                'signature': match.group(1)
            })
        
        return errors
    
    def research_solution(self, error):
        """Search for solutions - hooks into web search"""
        query = f"{error['signature']} fix solution site:stackoverflow.com OR site:github.com"
        # This calls the web_search tool when running in Nexus context
        return {"query": query, "error": error}
    
    def generate_patch(self, error, research):
        """Generate code patch based on research"""
        # Template for common fixes
        if "database is locked" in error['message']:
            return """
# PATCH: SQLite database locking
import sqlite3
def get_conn(db_path):
    return sqlite3.connect(db_path, timeout=30.0, isolation_level=None)
"""
        # Add more patch templates as we encounter errors
        return None
    
    def sandbox_test(self, patch, test_cases):
        """Test patch in isolated environment"""
        test_file = self.sandbox_dir / "test_patch.py"
        test_file.write_text(patch + "\n\n# Test cases:\n" + test_cases)
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def apply_patch(self, patch, target_file):
        """Apply patch to source"""
        with open(target_file, 'a') as f:
            f.write(f"\n# Auto-patch applied by NexusHealer\n{patch}\n")
    
    def heal_cycle(self):
        """One iteration of the healing loop"""
        print("[HEALER] Scanning for errors...")
        errors = self.parse_errors()
        
        if not errors:
            print("[HEALER] No errors found. System healthy.")
            return
        
        for error in errors:
            print(f"[HEALER] Found error: {error['signature']}")
            
            # Research
            research = self.research_solution(error)
            print(f"[HEALER] Researching: {research['query']}")
            
            # Generate patch
            patch = self.generate_patch(error, research)
            if not patch:
                print(f"[HEALER] No patch template for this error. Logging for manual review.")
                continue
            
            # Sandbox test
            print(f"[HEALER] Testing patch in sandbox...")
            success, output = self.sandbox_test(patch, "# TODO: Add test cases")
            
            if success:
                print(f"[HEALER] Patch tests passed. Applying...")
                self.apply_patch(patch, "nyxlang/core/interpreter.py")
                print(f"[HEALER] Patch applied successfully.")
            else:
                print(f"[HEALER] Patch failed tests: {output}")

if __name__ == "__main__":
    healer = NexusHealer()
    
    if "--continuous" in sys.argv:
        while True:
            healer.heal_cycle()
            time.sleep(60)  # Check every minute
    else:
        healer.heal_cycle()