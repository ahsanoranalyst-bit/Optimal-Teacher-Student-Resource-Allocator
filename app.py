import tkinter as tk
import time

class SystemIntelligenceDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("System Intelligence - Core Logic Demo")
        self.root.geometry("800x600")
        self.root.configure(bg="#010101") # Pure Black Background

        # 1. Main Container Panel with Cyan Border simulation
        self.main_panel = tk.Frame(self.root, bg="#010c14", highlightbackground="#00FFFF", highlightthickness=2, bd=0)
        self.main_panel.place(relx=0.5, rely=0.5, anchor="center", width=700, height=500)

        # Subtle Gold background pattern simulation (using text)
        self.pattern_label = tk.Label(self.main_panel, text="[ SYSTEM_LOGIC // OP_RESEARCH ]", 
                                       fg="#222200", bg="#010c14", font=("Courier New", 10))
        self.pattern_label.place(x=10, y=10)

        # 2. The Title (Gold)
        self.title_label = tk.Label(self.main_panel, text="SYSTEM INTELLIGENCE", 
                                     fg="#ffd700", bg="#010c14", font=("Arial Black", 28, "bold"))
        self.title_label.pack(pady=(40, 20))

        # 3. The Text Container (Cyan)
        self.text_label = tk.Label(self.main_panel, text="", fg="#00ffff", bg="#010c14", 
                                    font=("Courier New", 14), justify="left", wraplength=600)
        self.text_label.pack(pady=20, padx=40)

        # The genuine English introduction text
        self.full_text = ("I am not just a program; I am the logic behind your success. "
                          "Built on advanced Operations Research, I analyze thousands "
                          "of possibilities in seconds to find the perfect solution for "
                          "your institution. Whether it's managing complex schedules "
                          "or predicting performance, I transform raw data into smart decisions. "
                          "Experience the power of automated intelligence.")
        
        self.char_index = 0
        
        # Start typing animation after a small delay
        self.root.after(1000, self.type_writer)

    def type_writer(self):
        """Logic for the typing animation effect."""
        if self.char_index < len(self.full_text):
            # Get current text and add the next character
            current_text = self.text_label.cget("text")
            next_char = self.full_text[self.char_index]
            
            # Update the label
            self.text_label.configure(text=current_text + next_char)
            
            self.char_index += 1
            
            # Call this function again after 50 milliseconds (adjust speed here)
            self.root.after(50, self.type_writer)
        else:
            # Animation complete - add a static flashing cursor simulation
            self.add_cursor()

    def add_cursor(self):
        """Simulate a blinking cursor at the end."""
        current_text = self.text_label.cget("text")
        if current_text.endswith("|"):
            self.text_label.configure(text=current_text[:-1])
        else:
            self.text_label.configure(text=current_text + "|")
        
        # Blink every 500ms
        self.root.after(500, self.add_cursor)

if __name__ == "__main__":
    # Initialize Tkinter
    root = tk.Tk()
    app = SystemIntelligenceDemo(root)
    # Start the application loop
    root.mainloop()
