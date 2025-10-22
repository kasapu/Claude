#!/usr/bin/env python3
"""
NLQ System Backend Server Runner

This script starts the FastAPI backend server with proper configuration.
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'anthropic',
        'psycopg2',
        'mysql',
        'snowflake',
        'databricks'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print(f"📦 Install with: pip install -r requirements.txt")
        return False

    return True


def check_env_file():
    """Check if .env file exists and has API key"""
    env_path = backend_dir.parent / '.env'

    if not env_path.exists():
        print("⚠️  .env file not found!")
        print(f"📝 Create one at: {env_path}")
        print("📋 Copy from .env.example and add your ANTHROPIC_API_KEY")
        return False

    # Check if API key is set
    with open(env_path) as f:
        content = f.read()
        if 'ANTHROPIC_API_KEY=sk-' not in content and 'ANTHROPIC_API_KEY=your_' in content:
            print("⚠️  ANTHROPIC_API_KEY not set in .env file!")
            print("🔑 Get your API key from: https://console.anthropic.com/")
            return False

    return True


def main():
    """Main entry point"""
    print("🚀 NLQ System Backend Server")
    print("━" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check environment
    if not check_env_file():
        sys.exit(1)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(backend_dir.parent / '.env')

    # Import and run server
    print("✅ All checks passed!")
    print("🔵 Starting server...")
    print()

    import uvicorn
    from api.main import app
    from config import settings

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
