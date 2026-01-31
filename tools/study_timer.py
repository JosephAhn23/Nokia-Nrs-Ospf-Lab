# -*- coding: utf-8 -*-
"""
Pomodoro Study Timer for NRS Certification
25-minute focused study sessions with breaks
"""
import time
import sys

def pomodoro_timer(minutes=25, break_minutes=5):
    """Run a Pomodoro study session"""
    print("=" * 60)
    print("NRS STUDY TIMER - Pomodoro Technique")
    print("=" * 60)
    print(f"\nStudy session: {minutes} minutes")
    print(f"Break: {break_minutes} minutes")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Study session
        print("🍅 STUDY SESSION STARTED")
        countdown(minutes, "Study")
        
        # Break
        print("\n☕ BREAK TIME")
        countdown(break_minutes, "Break")
        
        print("\n✅ Session complete!")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Timer stopped")

def countdown(minutes, label):
    """Countdown timer"""
    total_seconds = minutes * 60
    
    for remaining in range(total_seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        timer = f"{mins:02d}:{secs:02d}"
        print(f"\r{label}: {timer}", end='', flush=True)
        time.sleep(1)
    
    print(f"\r{label}: 00:00 - DONE!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        study_time = int(sys.argv[1])
    else:
        study_time = 25
    
    if len(sys.argv) > 2:
        break_time = int(sys.argv[2])
    else:
        break_time = 5
    
    pomodoro_timer(study_time, break_time)

