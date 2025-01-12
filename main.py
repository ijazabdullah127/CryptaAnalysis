import threading
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk,ImageDraw
from matplotlib.figure import Figure
from tkinter import simpledialog

from CasearCipher.CaesarCipher import score_text, caesar_decrypt
from MonoAlphabeticCipher.MonoAlpha import calculate_frequencies,suggest_mappings,apply_mappings_to_ciphertext,english_freq
from MonoAlphabeticCipher.HillClimbing.CryptanalysisMonoAlpha import HillClimbing
from VigenereCipher.KasiskiMethod import analyze
from ColumnarTranspositionCipher.CTCipher import  indexcoincidence,breakcolumnarcipher
from AffineCipher.AffineCipher import breakaffine
from PlayFairCipher.PlayFairCipher import playfair
from SubstitutionCipher.SubCipher import breaksubstitutioncipher
from VigenereCipher.HitAndTry import decrypt_text,auto_decrypt_text
from PolyBiusSquareCipher.PolyBiusSquareCipher import breakpolybiussquare
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class PremiumButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=40, color="#0ea5e9", hover_color="#0284c7"):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.color = color
        self.hover_color = hover_color
        
        self.rect = self.create_rounded_rect(5, 5, width-5, height-5, 12, fill=color)
        self.text_id = self.create_text(width/2, height/2, text=text, fill="white", 
                                      font=('Inter', 12, 'bold'))
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        
    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.color)
        
    def on_click(self, event):
        self.itemconfig(self.rect, fill=self.color)
        
    def on_release(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.command()
class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, colors, fonts):
        super().__init__(parent)
        self.title("Analysis Results")
        self.colors = colors
        self.fonts = fonts
        
        # Set window size and position
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.configure(bg=self.colors['bg'])
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg=self.colors['secondary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="ANALYSIS RESULTS", 
                font=self.fonts['subtitle'], bg=self.colors['secondary'], 
                fg=self.colors['primary']).pack(pady=15)
        
        # Results content
        content = tk.Frame(self, bg=self.colors['bg'], padx=30, pady=20)
        content.pack(fill='both', expand=True)
        
        # Results text area
        self.results_text = tk.Text(content, wrap='word', 
                                  font=('Consolas', 12),
                                  bg=self.colors['secondary'],
                                  fg=self.colors['text'],
                                  padx=15, pady=15)
        self.results_text.pack(fill='both', expand=True)
        
        # Make text read-only
        self.results_text.config(state='disabled')
    def clear_screen(self):
        self.results_text.delete(1.0, tk.END)
    def update_results(self, text):
        self.results_text.config(state='normal')
       
        self.results_text.insert(tk.END, text)
        self.results_text.config(state='disabled')
class CircularLoader(tk.Canvas):
    def __init__(self, parent, size=100, color='#0ea5e9', bg='#0f172a', width=4):
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0)
        self.size = size
        self.color = color
        self.width = width
        self.angle = 0
        self.arc_length = 270  # Length of the arc in degrees
        self.animation_speed = 20  # Degrees to rotate per frame
        self.is_running = False
        
    def start(self):
        self.is_running = True
        self.animate()
        
    def stop(self):
        self.is_running = False
        
    def animate(self):
        if not self.is_running:
            return
            
        # Clear previous arc
        self.delete('all')
        
        # Calculate arc coordinates
        pad = self.width + 2
        x1 = pad
        y1 = pad
        x2 = self.size - pad
        y2 = self.size - pad
        
        start = self.angle
        extent = self.arc_length
        
        # Draw arc
        self.create_arc(x1, y1, x2, y2, 
                       start=start, 
                       extent=extent,
                       width=self.width,
                       style='arc',
                       outline=self.color)
        
        # Update angle for next frame
        self.angle = (self.angle + self.animation_speed) % 360
        
        # Schedule next frame
        self.after(16, self.animate)  # ~60 FPS
loader=0
class StyledProgressWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.window_ready = threading.Event()
        # Configure fonts
        self.fonts = {
            'title': tkfont.Font(family="Inter", size=64, weight="bold"),
            'subtitle': tkfont.Font(family="Inter", size=24),
            'text': tkfont.Font(family="Inter", size=16)
        }
        
        # Configure colors
        self.colors = {
            'bg': '#0f172a',
            'primary': '#0ea5e9',
            'secondary': '#1e293b',
            'accent': '#7dd3fc',
            'text': '#f1f5f9'
        }
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        self.title("Cryptanalysis Progress")
        window_width = 300
        window_height = 500
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        position_top = int(screen_height / 2 - window_height / 2)
        position_left = int(screen_width / 2 - window_width / 2)
        
        self.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
        self.configure(bg=self.colors['bg'])
        
    def create_widgets(self):
        # Create main frame
        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text="Analysis in Progress",
            font=self.fonts['subtitle'],
            fg=self.colors['text'],
            bg=self.colors['bg']
        )
        title_label.pack(pady=(0, 30))
        
        # Create loading status label
        self.status_label = tk.Label(
            main_frame,
            text="Analyzing patterns...",
            font=self.fonts['text'],
            fg=self.colors['accent'],
            bg=self.colors['bg']
        )
        self.status_label.pack(pady=(0, 20))
        
        # Create and pack the circular loader
        self.loader = CircularLoader(
            main_frame,
            size=120,
            color=self.colors['primary'],
            bg=self.colors['bg'],
            width=6
        )
        self.loader.pack(pady=(0, 30))
        
        # Stop button
        self.stop_button = tk.Button(
            main_frame,
            text="Stop Analysis",
            font=self.fonts['text'],
            bg=self.colors['primary'],
            fg=self.colors['text'],
            activebackground=self.colors['accent'],
            activeforeground=self.colors['bg'],
            relief='flat',
            padx=20,
            pady=10,
            command=self.stop_clicked
        )
        self.stop_button.pack()
        
        # Start the loader animation
        self.loader.start()
        
        # Start status message updates
        self.update_status()

    def stop_clicked(self):
        if hasattr(self, 'on_stop'):
            self.on_stop()
        self.loader.stop()
        self.destroy()  
        global loader
        loader=1

    def update_status(self):
        """Rotate through different status messages"""
        messages = [
            "Analyzing patterns...",
            "Processing data...",
            "Evaluating solutions...",
            "Optimizing results..."
        ]
        current = getattr(self, '_message_index', 0)
        self.status_label.config(text=messages[current])
        self._message_index = (current + 1) % len(messages)
        
        if hasattr(self, 'loader') and self.loader.is_running:
            self.after(2000, self.update_status)
        
    def stop_clicked(self):
        if hasattr(self, 'on_stop'):
            self.on_stop()
        self.loader.stop()
        self.destroy()
class GraphWindow(tk.Toplevel):
    def __init__(self, parent, colors, fonts):
        super().__init__(parent)
        self.title("Analysis Graphs")
        self.colors = colors
        self.fonts = fonts
        
        # Set window size and position
        window_width = 1200
        window_height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.configure(bg=self.colors['bg'])
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg=self.colors['secondary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="ANALYSIS GRAPHS", 
                font=self.fonts['subtitle'], bg=self.colors['secondary'], 
                fg=self.colors['primary']).pack(pady=15)
        
        # Graph container
        self.graph_frame = tk.Frame(self, bg=self.colors['bg'], padx=20, pady=20)
        self.graph_frame.pack(fill='both', expand=True)
    
    
    def plot_frequency_analysis(self, cipher_freqs):
        # Clear previous plot
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        
        # Sort frequencies for better visualization
        eng_items = sorted(english_freq.items())
        eng_letters, eng_freqs = zip(*eng_items)
        
        # Create sorted cipher frequencies matching English alphabet
        cipher_freqs_sorted = []
        for letter in eng_letters:
            cipher_freqs_sorted.append(cipher_freqs.get(letter, 0))
        
        # Plot English frequencies
        ax1.bar(eng_letters, eng_freqs, color='blue', alpha=0.5, label='English')
        ax1.set_title('Standard English Letter Frequencies')
        ax1.set_ylabel('Frequency (%)')
        
        # Plot cipher frequencies
        ax2.bar(eng_letters, cipher_freqs_sorted, color='red', alpha=0.5, label='Ciphertext')
        ax2.set_title('Ciphertext Letter Frequencies')
        ax2.set_ylabel('Frequency (%)')
        
        for ax in (ax1, ax2):
            ax.set_xlabel('Letters')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        
        # Embed plot in tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


        
class VeilBreakerElite:
    def __init__(self, root):
        self.root = root
        self.root.title("Veil Breaker Elite")
        
        # Set fixed window size (adjust as needed for your screen)
        window_width = 1400
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate x and y coordinates for the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 4
        
        # Set the geometry of the window
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        
        # Custom fonts
        self.title_font = tkfont.Font(family="Inter", size=64, weight="bold")
        self.subtitle_font = tkfont.Font(family="Inter", size=24)
        self.text_font = tkfont.Font(family="Inter", size=16)
        
        self.fonts = {
            'title': tkfont.Font(family="Inter", size=64, weight="bold"),
            'subtitle': tkfont.Font(family="Inter", size=24),
            'text': tkfont.Font(family="Inter", size=16)
        }
        # Colors
        self.colors = {
            'bg': '#0f172a',
            'primary': '#0ea5e9',
            'secondary': '#1e293b',
            'accent': '#7dd3fc',
            'text': '#f1f5f9'
        }
        self.image_references = [] 
        self.results_window = None
        self.graph_window = None
        self.text=None
        self.results=None
        self.population_size=None
        self.max_iterations=None
        # Store the current text input widget
        self.current_text_input = None
        self.root.configure(bg=self.colors['bg'])
        self.create_main_frame()

    def get_values(self):
        # Ask user for population size and max iterations
        population_size = simpledialog.askinteger("Input", "Enter Population Size:",
                                                  parent=self.root, minvalue=1, maxvalue=10000)
        max_iterations = simpledialog.askinteger("Input", "Enter Max Iterations:",
                                                  parent=self.root, minvalue=1, maxvalue=10000)
        return  population_size , max_iterations   
    def get_key(self):
        # Ask user for key size 
        key_size = simpledialog.askinteger("Input", "Enter Guessed Key Length:",
                                                  parent=self.root, minvalue=1, maxvalue=10000)
        
        return  key_size  
    def get_temperature(self):
        # Ask user for temperature 
        message="\n*NOTE: The starting temperature can have a major impact on the success of a Simulated Annealing Algorithm.\nFor Example:\n\t0 - 500 characters : Temperature = 10\n\t500 - 1000 characters : Temperature = 20"
        temperature = simpledialog.askinteger("Input", f"Enter Temperature:",
                                                  parent=self.root, minvalue=10, maxvalue=20)
        
        return  temperature 
        
    def get_HitandTryvalues(self):
    
     decryption_type = None
     while decryption_type not in ['auto', 'manual']:
        decryption_type = simpledialog.askstring("Input", "Do you want automatic decryption or manual? (Enter 'auto' or 'manual')",
                                                 parent=self.root).lower()
        if decryption_type not in ['auto', 'manual']:
            simpledialog.messagebox.showerror("Invalid Input", "Please enter 'auto' for automatic or 'manual' for manual.")

     if decryption_type == 'manual':
        # If manual, ask for ngram value and key length
        ngram_value = simpledialog.askinteger("Input", "Enter Ngram Value:",
                                              parent=self.root, minvalue=1, maxvalue=4)
        key_length = simpledialog.askinteger("Input", "Enter Key Length:",
                                             parent=self.root, minvalue=1, maxvalue=20)
        return decryption_type, ngram_value, key_length
     else:
        # If automatic decryption
        return decryption_type, None, None
    def getChunkSize(self):
        chunk_size = simpledialog.askinteger("Input", "Enter Chunk Size(n):",
                                                  parent=self.root, minvalue=1, maxvalue=10000)
        return chunk_size
    def create_main_frame(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True)
        
        # Center title frame
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(fill='x', pady=(50, 30))
        
        # Project title (centered)
        title_container = tk.Frame(title_frame, bg=self.colors['bg'])
        title_container.pack(expand=True)
        
        tk.Label(title_container, text="VEIL", 
                font=self.title_font, bg=self.colors['bg'], 
                fg=self.colors['primary']).pack(side='left')
        tk.Label(title_container, text="BREAKER", 
                font=self.title_font, bg=self.colors['bg'], 
                fg=self.colors['accent']).pack(side='left', padx=(10, 0))
        
        # Content frame with image and info
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill='both', expand=True, padx=50)
        
        # Left frame for team info
        left_frame = tk.Frame(content_frame, bg=self.colors['bg'], width=800)
        left_frame.pack(side='left', fill='y', padx=(0, 20))
        left_frame.pack_propagate(False)
        
        # Team section
        team_frame = tk.Frame(left_frame, bg=self.colors['secondary'], padx=40, pady=30)
        team_frame.pack(fill='x', pady=20)
        
        tk.Label(team_frame, text="Team Members", 
                font=self.subtitle_font, bg=self.colors['secondary'], 
                fg=self.colors['primary']).pack(pady=(0, 20))
        
        members = [
            {"name": "Syed Muhammad Anas Nauman"},
            {"name": "Hamza Arfan"},
            {"name": "Abdullah"}
        ]
        
        for member in members:
            member_frame = tk.Frame(team_frame, bg=self.colors['secondary'])
            member_frame.pack(pady=10)
            
            tk.Label(member_frame, text=member["name"], 
                    font=self.text_font, bg=self.colors['secondary'], 
                    fg=self.colors['accent']).pack()
           
        
        # Launch button
        PremiumButton(left_frame, "Launch Analysis Suite", 
                     self.show_analysis_page,
                     width=300, height=60).pack(pady=30)
        
        # Right frame for character image
        right_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Load and display character image
        # Replace 'path_to_your_image.png' with your actual image path
        try:
            image = Image.open('images/character2.png')
            # Calculate appropriate size while maintaining aspect ratio
            image_width = 1500 # Adjust as needed
            aspect_ratio = image.height / image.width
            image_height = int(image_width * aspect_ratio)
            image = image.resize((image_width, image_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            image_label = tk.Label(right_frame, image=photo, bg=self.colors['bg'])
            image_label.image = photo  # Keep a reference
            image_label.pack(expand=True)
        except:
            # Fallback if image loading fails
            placeholder = tk.Label(right_frame, 
                                 text="Character Image\nPlaceholder", 
                                 font=self.text_font,
                                 bg=self.colors['secondary'],
                                 fg=self.colors['text'],
                                 width=40, height=20)
            placeholder.pack(expand=True)
    def create_image(self, path, size=(350, 160)):
        try:
            # Load and resize the image
            original = Image.open("images/"+path)
            resized = original.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(resized)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            # Create a placeholder if image loading fails
            return self.create_placeholder_image(size)
    
    def create_placeholder_image(self, size):
        # Create a placeholder image with a lock icon or similar
        img = Image.new('RGB', size, self.colors['secondary'])
        draw = ImageDraw.Draw(img)
        # Draw a simple icon (e.g., a rectangle)
        draw.rectangle([size[0]//2, size[1]//2, 3*size[0]//2, 3*size[1]//2], 
                      outline=self.colors['text'])
        return ImageTk.PhotoImage(img)
    def show_analysis_page(self):
        # Clear main window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create analysis page
        analysis_frame = tk.Frame(self.root, bg=self.colors['bg'])
        analysis_frame.pack(fill='both', expand=True)
        
        # Header with back button
        header = tk.Frame(analysis_frame, bg=self.colors['secondary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        back_btn = PremiumButton(header, "← Back", self.show_main_page,
                               width=100, height=40)
        back_btn.pack(side='left', padx=20, pady=20)
        
        tk.Label(header, text="ANALYSIS SUITE", 
                font=self.subtitle_font, bg=self.colors['secondary'], 
                fg=self.colors['primary']).pack(padx=10,pady=15)
        
        # Algorithm grid
        content = tk.Frame(analysis_frame, bg=self.colors['bg'], padx=50, pady=30)
        content.pack(fill='both', expand=True)
        
        algorithms = [
    ("Caesar cipher", "C-cipher", "caesar.jpg"),
    ("MonoAlphabetic Cipher", "MonoAlphabetic", "mono.jpg"),
    ("Vigenere Cipher", "vigenere-cipher", "vigenere.jpg"),
     ("Affine Cipher", "affine-cipher", "affine.jpg"),
     ("Polybius Square Cipher", "Polybius Square-cipher", "poly.jpg"),
     ("Columnar Transposition Cipher", "CT-cipher", "col.jpg"),
    #("Substitution Cipher", "Substitution-cipher", "sub.jpg"),
     ("Play Fair Cipher", "PlayFair-cipher", "pf.jpg")
   
   
]
        
        
    
    
        row = 0
        col = 0
        
        for algo_name, algo_id, img_path in algorithms:
            # Create frame for each algorithm
            algo_frame = tk.Frame(content, bg=self.colors['secondary'],
                                padx=5, pady=0)
            algo_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Load and display image
            img = self.create_image(img_path)
            self.image_references.append(img)  # Keep reference
            
            image_label = tk.Label(algo_frame, image=img, 
                                 bg=self.colors['secondary'])
            image_label.pack(pady=(0, 0))
            
            # Algorithm name
            name_label = tk.Label(algo_frame, text=algo_name,
                                font=self.text_font,
                                bg=self.colors['secondary'],
                                fg=self.colors['text'])
            name_label.pack(pady=(0, 15))
            
            # Select button
            PremiumButton(algo_frame, "Select",
                         lambda a=algo_id: self.show_tool_page(a),
                         width=150, height=40).pack()
            
            # Grid layout management
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Configure grid columns to be equally weighted
        for i in range(3):
            content.grid_columnconfigure(i, weight=1)
    
    def show_main_page(self):
        # Clear window and recreate main page
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_main_frame()
    
    def show_tool_page(self, algorithm):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create tool page
        tool_frame = tk.Frame(self.root, bg=self.colors['bg'])
        tool_frame.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(tool_frame, bg=self.colors['secondary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        back_btn = PremiumButton(header, "← Back", self.show_analysis_page,
                               width=100, height=40)
        back_btn.pack(side='left', padx=20, pady=20)
        
        tk.Label(header, text=f"{algorithm.upper()} ANALYSIS", 
                font=self.fonts['subtitle'], bg=self.colors['secondary'], 
                fg=self.colors['primary']).pack(pady=20)
        
        # Content
        content = tk.Frame(tool_frame, bg=self.colors['bg'], padx=50, pady=30)
        content.pack(fill='both', expand=True)
        
        # Input section
        input_frame = tk.Frame(content, bg=self.colors['secondary'], padx=30, pady=30)
        input_frame.pack(fill='x', pady=20)
        
        tk.Label(input_frame, text="Enter Ciphertext", 
                font=self.fonts['text'], bg=self.colors['secondary'], 
                fg=self.colors['text']).pack(pady=(0, 10))
        
        self.current_text_input = tk.Text(input_frame, height=10, 
                                        font=('Consolas', 14), bg=self.colors['bg'], 
                                        fg=self.colors['text'],
                                        insertbackground=self.colors['text'])
        self.current_text_input.pack(fill='x')
        
        # Analysis tools
        tools_frame = tk.Frame(content, bg=self.colors['secondary'], padx=30, pady=30)
        tools_frame.pack(fill='x', pady=20)
        
        tk.Label(tools_frame, text="Analysis Tools", 
                font=self.fonts['text'], bg=self.colors['secondary'], 
                fg=self.colors['text']).pack(pady=(0, 20))
        
        tools = []
        if(algorithm=='C-cipher'):
            tools=["Brute Force Attack"]
        elif(algorithm=='MonoAlphabetic'):
            tools=["Frequency Analysis",
                   "Display Frequency Graphs", "Hilling Climbing(NLP)"]
        elif(algorithm=='vigenere-cipher'):
            tools=["Kasiski Method",
                   "Hit and Try"]
        elif(algorithm=='affine-cipher'):
            tools=["Brute Force"]
        elif(algorithm=='Polybius Square-cipher'):
             tools = [
            "Fitness Algorithm"
            
        ]
        elif(algorithm=='CT-cipher'):
             tools = [
            "Index Coincidence" ,
            "Hill Climbing Algorithm"
        ]
       #elif (algorithm=='Substitution-cipher'):
         #  tools=["Hill Climbing & Trigram's"]
        elif(algorithm=='PlayFair-cipher'):
            tools = [
            "SimulatedAnnealing"
           
        ]





        tools_grid = tk.Frame(tools_frame, bg=self.colors['secondary'])
        tools_grid.pack()
        
        for i, tool in enumerate(tools):
            PremiumButton(tools_grid, tool, 
                         lambda t=tool: self.run_analysis(t, algorithm),
                         width=250, height=50).grid(row=i//2, column=i%2, 
                                                  padx=10, pady=10)
        
    def run_hill_climbing(self):
     
      self.results = HillClimbing(self.text, self.max_iterations, self.population_size)
    def create_progress_window(self):
           progressWindow = StyledProgressWindow()
           progressWindow.window_ready.set()
           progressWindow.mainloop()
           

    def run_analysis(self, tool, algorithm):
        print(tool,algorithm)
        # Get input text
        if self.current_text_input:
            text = self.current_text_input.get("1.0", tk.END).strip()
        else:
            text = ""
        
        if not text:
            messagebox.showwarning("Input Required", "Please enter some text to analyze.")
            return
        
      
        if tool == "Brute Force Attack" and  algorithm=="C-cipher":
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            results = []
            
            for shift in range(26):
              decrypted = caesar_decrypt(text, shift)
              score = score_text(decrypted)
              results.append((score, shift, decrypted))
            
            # Sort results by score (highest first)
            results.sort(reverse=True)
            self.results_window.clear_screen()
            # Display top 5 results
            self.results_window.update_results("Top 5 most likely solutions:\n\n")
            for score, shift, text in results[:5]:
                self.results_window.update_results(f"Shift: {shift}\n")
                self.results_window.update_results(f"Text: {text}\n")
                self.results_window.update_results(f"Confidence Score: {score:.2%}\n")
                self.results_window.update_results( "-" * 50 + "\n\n")

        elif tool == "Frequency Analysis" and  algorithm=="MonoAlphabetic":
              if not self.results_window or not self.results_window.winfo_exists():
                self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
              else:
                self.results_window.destroy()
                self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
              self.results_window.update_results("Letter Frequencies in Ciphertext:\n\n")
              frequencies = calculate_frequencies(text)
              for letter, freq in sorted(frequencies.items()):
                    self.results_window.update_results(f"{letter}: {freq:.2f}%\n")
              self.results_window.update_results("\nSuggested Letter Mappings (based on frequency analysis):\n\n")
              mappings = suggest_mappings(frequencies)
              for cipher_letter, eng_letter in mappings.items():
                   self.results_window.update_results(f"{cipher_letter} → {eng_letter}\n")
              self.results_window.update_results("\n\nDecrypted Text After Frequency Analysis:\n")
              self.results_window.update_results(apply_mappings_to_ciphertext(text,mappings)+"\n")
              
        elif tool == "Display Frequency Graphs" and  algorithm=="MonoAlphabetic": 
            if not self.graph_window or not self.graph_window.winfo_exists():
             self.graph_window = GraphWindow(self.root, self.colors, self.fonts)
            else:
             self.graph_window.destroy()
             self.graph_window = GraphWindow(self.root, self.colors, self.fonts) 
            frequencies = calculate_frequencies(text)
            self.graph_window.plot_frequency_analysis(frequencies)

        elif tool == "Hilling Climbing(NLP)" and  algorithm=="MonoAlphabetic":
              
              population_size , max_iterations =  self.get_values()
              
              loader_thread = threading.Thread(target=self.create_progress_window)
              loader_thread.start()
              
              
              
              
              self.text=text
              self.population_size=population_size
              self.max_iterations=max_iterations
             
              hill_climbing_thread = threading.Thread(target=self.run_hill_climbing)
              
            
              hill_climbing_thread.start()
              
              hill_climbing_thread.join()
               
              if not self.results_window or not self.results_window.winfo_exists():
                self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
              else:
                self.results_window.destroy()
                self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
              self.results_window.update_results("Results After Hill Climbing:\n\n")
              
              for result in self.results:
                    self.results_window.update_results(str(result) + "\n" + "-"*40 + "\n")
              
        elif algorithm == "vigenere-cipher" and  tool=="Kasiski Method":        
            chunk_size=self.getChunkSize()
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            self.results_window.update_results("\nKasiski Analysis Results:\n\n")
            result=analyze(text,chunk_size)
            if not result:  # This checks for empty lists or similar empty structures
              self.results_window.update_results("\n\nNo Repeated Chunk Found!\n")
            else:
              self.results_window.update_results(f"\n\n{result}\n")
        elif algorithm == "vigenere-cipher" and  tool=="Hit and Try":        
            decryption_type, ngram_value, key_length=self.get_HitandTryvalues()
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            self.results_window.update_results("\nHit and Try Results:\n\n")
            
            results=None
            loader_thread = threading.Thread(target=self.create_progress_window)
            
            if(decryption_type=='manual'):
              results=decrypt_text(text,key_length,ngram_value)
            elif(decryption_type=='auto'):
              loader_thread.start()
              results=auto_decrypt_text(text)
            print(results)
            for result in  results:
                self.results_window.update_results(f"\nKey Length: {result['key_length']}\n")
                self.results_window.update_results(f"Key: {result['Key']}\n")
                self.results_window.update_results(f"Ngram: {result['ngram']}\n")
                self.results_window.update_results(f"Decrypted Text: {result['decrypted_text']}\n")
                
                self.results_window.update_results(f"English Percentage: {result['english_percentage']}\n")
                self.results_window.update_results("-" * 40)  # Separator for readability
            
           
        
        elif tool == "Brute Force" and  algorithm=="affine-cipher":
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            result=breakaffine(text)
            self.results_window.update_results(f"Brute Force Attack Results:\n\n {result}\n")

        elif tool == "Fitness Algorithm" and  algorithm=='Polybius Square-cipher':
            loader_thread = threading.Thread(target=self.create_progress_window)
            loader_thread.start()
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            result=breakpolybiussquare(text)
            self.results_window.update_results(f"Best Result Through Fitness Algorithm :\n\n {result}\n")

        elif tool == "Index Coincidence" and  algorithm=='CT-cipher':
            
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            result=indexcoincidence(text)
            self.results_window.update_results(f"Index Coincidence Results :\n\n {result}\n")

        elif algorithm=='Substitution-cipher' and tool=="Hill Climbing & Trigram's":
            
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            result=breaksubstitutioncipher(text)
            self.results_window.update_results(f"Hill Climbing & Trigram's Results :\n\n {result}\n")

        elif tool == "Hill Climbing Algorithm" and  algorithm=='CT-cipher':
            loader_thread = threading.Thread(target=self.create_progress_window)
            
            keysize=self.get_key()
            loader_thread.start()
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            result=breakcolumnarcipher(text, keysize)

            self.results_window.update_results(f"Best Result Through Hill Climbing Algorithm :\n\n {result}\n")
        elif tool == "Hill Climbing Algorithm & Trigram's statistic" and  algorithm=='Substitution-cipher':
            loader_thread = threading.Thread(target=self.create_progress_window)
            loader_thread.start()
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            result=breaksubstitutioncipher(text)
            self.results_window.update_results(f"Best Result Through Hill Climbing Algorithm & Trigram's statistic :\n\n {result}\n") 
        elif algorithm =='PlayFair-cipher'and tool == "SimulatedAnnealing":
            
            loader_thread = threading.Thread(target=self.create_progress_window)
            temperature=self.get_temperature()
            loader_thread.start()
            if not self.results_window or not self.results_window.winfo_exists():
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            else:
             self.results_window.destroy()
             self.results_window = ResultsWindow(self.root, self.colors, self.fonts)
            
            results=playfair(text,temperature)
            self.results_window.update_results(f"Results Through Simulated Annealing Algorithm :\n\n") 
            for result in results:
             
             self.results_window.update_results(f"\nKey: {result['key']}\n")
             self.results_window.update_results(f"Score: {result['score']}\n")
             self.results_window.update_results(f"Text: {result['text']}\n")
                
         
             self.results_window.update_results("-" * 40)  
        
       
    
def main():
    root = tk.Tk()
    app = VeilBreakerElite(root)
    root.mainloop()

if __name__ == "__main__":
    main()