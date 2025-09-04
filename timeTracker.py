'''
Simple GUI tool based on tkinter for task tracking.
It allows you to start/stop a timer to estimate the time dedicated to a task and saves it to a JSON file for further processing (if desired).
The minimal design permits broad personalization.
'''

import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
import json

class TimeTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time Tracker")
        self.root.geometry("800x600")
        
        self.task = tk.StringVar()
        self.category = tk.StringVar()
        self.start_time = None
        self.is_running = False
        self.pause = ""
        #self.task_var = tk.StringVar()

        self.setup_ui()
        
    def setup_ui(self):
        # Insert Task
        self.task_label = tk.Label(
            self.root,
            text = 'Task to track',
            font=('Arial',10, 'bold')
        )
        self.task_label.pack(pady=10)
        
        self.task_entry = tk.Entry(
            self.root,
            textvariable = self.task,
            font=('Arial',10, 'bold')
        )
        self.task_entry.pack(pady=10)
        
        # Insert Category
        self.category_label = tk.Label(
            self.root,
            text = 'Category',
            font=('Arial',10, 'bold')
        )
        self.category_label.pack(pady=10)
        
        self.category_entry = tk.Entry(
            self.root,
            textvariable = self.category,
            font=('Arial',10, 'bold')
        )
        self.category_entry.pack(pady=10)
        
        
        # Start Button
        self.start_button = tk.Button(
            self.root,
            text="Start",
            command=self.start_tracking,
            width=10,
            height=2
        )
        self.start_button.pack(pady=20)
        
        # Stop button
        self.stop_button = tk.Button(
            self.root,
            text="Stop",
            command=self.stop_tracking,
            width=10,
            height=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(pady=10)
        
        # Time label
        self.time_label = tk.Label(
            self.root,
            text="00:00:00",
            font=("Arial", 24)
        )
        self.time_label.pack(pady=20)
        
        # Show deserved pause
        self.pause_label = tk.Label(
            self.root,
            text = "",
            font=('Arial',10, 'bold')
        )
        self.pause_label.pack(pady=10)
        # Update time display
        self.update_time()
        
    def start_tracking(self):
        self.start_time = datetime.now()
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_label.config(text="")
        
    def stop_tracking(self):
        if self.is_running:
            end_time = datetime.now()
            duration = int(((end_time - self.start_time).total_seconds())/60) #Setting duration in minutes  
            pause = int(duration*(15/60)) #hardcoding pause of 15 min every focus hour  
            # Save result
            self.save_result( 
                task=self.task.get(), 
                category=self.category.get(),
                start_time=self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
                duration=str(duration)
            )
            
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.time_label.config(text="00:00:00")
            self.pause_label.config(text=f"You focused for {duration} min.\nPlease, rest yourself for {pause} min.")


    def update_time(self):
        if self.is_running:
            elapsed = datetime.now() - self.start_time
            hours = elapsed.seconds // 3600
            minutes = (elapsed.seconds // 60) % 60
            seconds = elapsed.seconds % 60
            self.time_label.config(
                text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
        self.root.after(100, self.update_time)
        
    def save_result(self, task, category, start_time, end_time, duration):
        results_file = Path(f"{HOME}/time_tracking_results.json")
        
        # Load existing results or create new list
        if results_file.exists():
            with open(results_file, "r") as f:
                results = json.load(f)
        else:
            results = []
            
        # Add new result
        results.append({
            "task": task,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration
        })
        # Add category if not empty
        if category != "":
        	results[-1]["category"]=category
        
        # Save updated results
        with open(results_file, "w") as f:
            json.dump(results, f, indent=4)
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    #For the sake of simplicity, I've used a global constant for the HOME directory. Should be avoided in more complex implementation.
    global HOME
    HOME = os.getcwd()
    app = TimeTracker()
    app.run()
