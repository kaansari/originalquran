# filename: quick_setup.py
import subprocess
import time

def run_script(script_name):
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print('='*60)
    
    result = subprocess.run(['python3', script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    time.sleep(1)  # Small delay between scripts

# Run all scripts in order
scripts = [
    '01_reset_chroma.py',
    '02_create_collection.py', 
    '03_verify_collection.py',
    '04_test_queries.py'
]

for script in scripts:
    run_script(script)

print("\n" + "="*60)
print("SETUP COMPLETE!")
print("="*60)
print("\nYou can now run: python3 05_interactive_query.py")
print("for interactive searching.")