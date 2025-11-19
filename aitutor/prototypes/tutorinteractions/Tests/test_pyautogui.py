#!/usr/bin/env python3
"""
Test PyAutoGUI functionality
"""
import pyautogui
import time

def test_pyautogui():
    print("Testing PyAutoGUI...")
    
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    print(f"Screen size: {screen_width}x{screen_height}")
    
    # Get current mouse position
    current_x, current_y = pyautogui.position()
    print(f"Current mouse position: ({current_x}, {current_y})")
    
    # Test mouse movement (small movement to avoid disruption)
    print("\nMoving mouse slightly...")
    pyautogui.moveTo(current_x + 50, current_y + 50, duration=0.5)
    time.sleep(0.5)
    pyautogui.moveTo(current_x, current_y, duration=0.5)
    
    # Test fail-safe
    print(f"\nFail-safe is: {'ON' if pyautogui.FAILSAFE else 'OFF'}")
    
    print("\nPyAutoGUI is working correctly!")
    return True

if __name__ == "__main__":
    try:
        test_pyautogui()
    except Exception as e:
        print(f"Error: {e}")