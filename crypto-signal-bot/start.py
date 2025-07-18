import os
import sys
import traceback
from dotenv import load_dotenv

print("✅ Bot is starting...")

try:
    load_dotenv()
    from runner import main as run_main
    run_main()
    print("✅ Bot run completed successfully.")
except Exception as e:
    print("❌ Bot failed to start or run.")
    print(traceback.format_exc())
    sys.exit(1)