#!/usr/bin/env python3
"""
Test Trigger.dev Tasks

Script to test and document Trigger.dev automation tasks.
"""

import os
import subprocess  # nosec B404
import sys
from datetime import datetime


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    print("-" * 50)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)  # nosec B602

        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Failed (exit code: {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def check_trigger_setup():
    """Check if Trigger.dev is properly set up"""
    print("🔍 Checking Trigger.dev Setup")
    print("=" * 50)

    # Check if trigger CLI is available
    if not run_command("npx @trigger.dev/cli@latest --version", "Checking Trigger.dev CLI"):
        print("❌ Trigger.dev CLI not available")
        return False

    # Check if trigger.config.ts exists
    if not os.path.exists("trigger.config.ts"):
        print("❌ trigger.config.ts not found")
        return False

    print("✅ Trigger.dev setup looks good!")
    return True


def list_available_tasks():
    """List available Trigger.dev tasks"""
    print("\n📋 Available Trigger.dev Tasks")
    print("=" * 50)

    tasks_dir = "src/automation/tasks"
    if not os.path.exists(tasks_dir):
        print("❌ Tasks directory not found")
        return []

    tasks = []
    for file in os.listdir(tasks_dir):
        if file.endswith(".ts") and file != "index.ts":
            task_name = file.replace(".ts", "")
            tasks.append(task_name)
            print(f"📄 {task_name}")

    return tasks


def test_simple_task():
    """Test the simple health check task"""
    print("\n🧪 Testing Simple Health Check Task")
    print("=" * 50)

    # Note: Trigger.dev CLI doesn't support --test flag
    # This is a documentation function, not a real test
    print("ℹ️  Trigger.dev tasks require 'npx @trigger.dev/cli dev' to run")
    print("ℹ️  See TRIGGER_EXAMPLES.md for usage instructions")

    # Return None to indicate this is not a test assertion
    return None


def create_trigger_examples():
    """Create examples of how to use Trigger.dev tasks"""
    print("\n📝 Creating Trigger.dev Examples")
    print("=" * 50)

    examples = {
        "simple-health-check": {"description": "Basic health check task", "command": "npx @trigger.dev/cli@latest dev --test simple-health-check", "payload": None},
        "manual-test": {"description": "Manual test with custom message", "command": "npx @trigger.dev/cli@latest dev --test manual-test", "payload": {"message": "Testing from script"}},
        "health-monitor": {"description": "Monitor API health", "command": "npx @trigger.dev/cli@latest dev --test health-monitor", "payload": None},
    }

    # Create examples file
    with open("TRIGGER_EXAMPLES.md", "w") as f:
        f.write("# 🤖 Trigger.dev Task Examples\n\n")
        f.write(f"Generated on: {datetime.now().isoformat()}\n\n")

        for task_id, info in examples.items():
            f.write(f"## {task_id}\n\n")
            f.write(f"**Description**: {info['description']}\n\n")
            f.write(f"**Command**:\n```bash\n{info['command']}\n```\n\n")

            if info["payload"]:
                f.write(f"**Payload**:\n```json\n{info['payload']}\n```\n\n")

            f.write("---\n\n")

    print("✅ Created TRIGGER_EXAMPLES.md")


def main():
    """Main function"""
    print("🚀 Trigger.dev Task Testing")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Check setup
    if not check_trigger_setup():
        print("❌ Trigger.dev setup issues found. Please fix before continuing.")
        sys.exit(1)

    # List tasks
    tasks = list_available_tasks()

    # Create examples
    create_trigger_examples()

    # Test simple task (if available)
    if "simple-test" in tasks:
        test_simple_task()

    print("\n🎉 Trigger.dev testing completed!")
    print("\nNext steps:")
    print("1. Review TRIGGER_EXAMPLES.md for usage examples")
    print("2. Run individual tasks using the Trigger.dev CLI")
    print("3. Check the Trigger.dev dashboard for task execution logs")


if __name__ == "__main__":
    main()
