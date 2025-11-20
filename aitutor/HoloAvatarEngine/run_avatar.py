#!/usr/bin/env python3
"""
Run HoloAvatar Engine

Usage:
    python -m aitutor.HoloAvatarEngine.run_avatar
"""
import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aitutor.HoloAvatarEngine.websocket_server import run_server


def main():
    print("=" * 50)
    print("  HoloAvatar Engine - Cutting Edge Open Source")
    print("=" * 50)
    print()
    print("Features:")
    print("  - XTTS-v2 voice synthesis (voice cloning)")
    print("  - LivePortrait real-time animation (12.8ms/frame)")
    print("  - Context-aware expressions")
    print("  - DASH adaptive learning integration")
    print()
    print("Starting server...")
    print()

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
