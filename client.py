import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter.font import Font

class YahtzeeClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pseudo = input("Choisissez votre pseudo: ")
        self.player_id = None
        self.used_categories = set()  # Pour suivre les catégories utilisées
        
        # Configuration interface graphique
        self.window = tk.Tk()
        self.window.title(f"Yahtzee - {self.pseudo}")
        self.window.configure(bg='#2C3E50')
        self.window.geometry("800x1200")
        
        # Création d'un canvas
        self.canvas = tk.Canvas(self.window, bg='#2C3E50', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2C3E50')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=780)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=10)
        self.scrollbar.pack(side="right", fill="y")
        
        # Styles
        self.title_font = Font(family="Helvetica", size=24, weight="bold")
        self.dice_font = Font(family="Helvetica", size=18, weight="bold")
        self.button_font = Font(family="Helvetica", size=12)
        self.text_font = Font(family="Helvetica", size=10)
        
        # Rubrique "Règles du jeu"
        self.rules_button = tk.Button(self.scrollable_frame, text="Règles du jeu",
                                    command=self.show_rules,
                                    font=self.button_font,
                                    bg='#E67E22', fg='white')
        self.rules_button.pack(pady=5)
        
        # Zone de chat
        self.chat_frame = tk.Frame(self.scrollable_frame, bg='#2C3E50')
        self.chat_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.chat_label = tk.Label(self.chat_frame, text="Chat", 
                                 font=self.button_font, bg='#2C3E50', fg='white')
        self.chat_label.pack(pady=(0, 5))
        
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, height=5, width=50)
        self.chat_display.pack(pady=5)
        
        self.chat_input_frame = tk.Frame(self.chat_frame, bg='#2C3E50')
        self.chat_input_frame.pack(fill=tk.X)
        
        self.chat_entry = tk.Entry(self.chat_input_frame)
        self.chat_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.send_button = tk.Button(self.chat_input_frame, text="Envoyer",
                                   command=self.send_message,
                                   bg='#3498DB', fg='white')
        self.send_button.pack(side=tk.RIGHT)
        
        self.chat_entry.bind('<Return>', lambda e: self.send_message())
        
        # Statut du joueur
        self.status_label = tk.Label(self.scrollable_frame, text="En attente...", 
                                   font=self.button_font, bg='#2C3E50', fg='white')
        self.status_label.pack(pady=10)
        
        # Affichage des dés
        self.dice_frame = tk.Frame(self.scrollable_frame, bg='#2C3E50')
        self.dice_frame.pack(pady=20)
        self.dice_buttons = []
        self.dice_states = [False] * 5
        
        for i in range(5):
            btn = tk.Button(self.dice_frame, text="?", width=3, height=1,
                          font=self.dice_font, bg='white',
                          command=lambda x=i: self.toggle_die(x))
            btn.pack(side=tk.LEFT, padx=10)
            self.dice_buttons.append(btn)
        
        # Bouton pour lancer les dés
        self.roll_button = tk.Button(self.scrollable_frame, text="Lancer les dés",
                                   font=self.button_font, bg='#3498DB', fg='white',
                                   command=self.roll_dice)
        self.roll_button.pack(pady=20)
        
        # Catégories de score (en grille 4x4)
        self.categories_frame = tk.Frame(self.scrollable_frame, bg='#2C3E50')
        self.categories_frame.pack(pady=20)
        self.category_buttons = {}
        
        categories = [
            "As", "Deux", "Trois", "Quatre", "Cinq", "Six",
            "Brelan", "Carré", "Full", "Petite Suite",
            "Grande Suite", "Yahtzee", "Chance"
        ]
        
        # Création de la grille de catégories
        for i, cat in enumerate(categories):
            row = i // 4  
            col = i % 4   
            
            btn = tk.Button(self.categories_frame, 
                          text=f"{cat}: ?",
                          font=self.button_font,
                          bg='#34495E', fg='white',
                          width=15,
                          command=lambda x=cat: self.score_category(x))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.category_buttons[cat] = btn
            
        # Onglets développeurs
        credits_text = "Développé par:\nBéranger\nGaillor\nNarindrasoa"
        self.credits_label = tk.Label(self.scrollable_frame, text=credits_text,
                                    font=self.text_font, bg='#2C3E50', fg='#95A5A6')
        self.credits_label.pack(pady=20)

    def show_rules(self):
        rules = """Règles du Yahtzee:

1. Le jeu se joue avec 5 dés
2. À votre tour, vous avez droit à 3 lancers
3. Après chaque lancer, vous pouvez conserver certains dés
4. Vous devez remplir une case de score à la fin de votre tour

Combinaisons:
- As à Six: Somme des dés correspondants
- Brelan: 3 dés identiques (somme de tous les dés)
- Carré: 4 dés identiques (somme de tous les dés)
- Full: 3 dés identiques + 2 dés identiques (25 points)
- Petite Suite: 4 dés qui se suivent (30 points)
- Grande Suite: 5 dés qui se suivent (40 points)
- Yahtzee: 5 dés identiques (50 points)
- Chance: Somme de tous les dés"""
        
        messagebox.showinfo("Règles du Yahtzee", rules)

    def send_message(self):
        message = self.chat_entry.get().strip()
        if message:
            data = {
                'type': 'chat',
                'message': message,
                'sender': self.pseudo
            }
            self.client.send(json.dumps(data).encode('utf-8'))
            self.chat_entry.delete(0, tk.END)

    def toggle_die(self, index):
        self.dice_states[index] = not self.dice_states[index]
        if self.dice_states[index]:
            self.dice_buttons[index].config(bg='#E74C3C')
        else:
            self.dice_buttons[index].config(bg='white')

    def roll_dice(self):
        keep_positions = [i for i, kept in enumerate(self.dice_states) if kept]
        message = {
            'type': 'roll',
            'keep_positions': keep_positions
        }
        self.client.send(json.dumps(message).encode('utf-8'))

    def score_category(self, category):
        if category not in self.used_categories:  # Vérifier si la catégorie n'a pas déjà été utilisée
            message = {
                'type': 'score',
                'category': category
            }
            self.client.send(json.dumps(message).encode('utf-8'))

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                
                if message == 'NICK':
                    self.client.send(self.pseudo.encode('utf-8'))
                else:
                    try:
                        data = json.loads(message)
                        
                        if data['type'] == 'player_id':
                            self.player_id = data['id']
                            if data['current_player'] == self.player_id:
                                self.status_label.config(text="C'est votre tour!", fg='#2ECC71')
                            else:
                                self.status_label.config(text="En attente de votre tour...", fg='white')
                        
                        elif data['type'] == 'chat':
                            self.chat_display.insert(tk.END, f"{data['sender']}: {data['message']}\n")
                            self.chat_display.see(tk.END)
                        
                        elif data['type'] == 'roll_result':
                            for i, value in enumerate(data['dice']):
                                self.dice_buttons[i].config(text=str(value))
                                
                        elif data['type'] == 'score_update':
                            # Ne mettre à jour que si c'est le score du joueur actif
                            if data['scoring_player'] == self.player_id:
                                category = data['category']
                                self.used_categories.add(category)  # Marquer la catégorie comme utilisée
                                self.window.after(0, lambda cat=category, score=data['score']: (
                                    self.category_buttons[cat].config(
                                        text=f"{cat}: {score}",
                                        state='disabled',  # Désactiver le bouton
                                        bg='#7F8C8D'  # Changer la couleur pour montrer qu'il est utilisé
                                    )
                                ))
                            
                            if data['next_player'] == self.player_id:
                                self.status_label.config(text="C'est votre tour!", fg='#2ECC71')
                            else:
                                self.status_label.config(text="En attente de votre tour...", fg='white')
                            
                        elif data['type'] == 'game_over':
                            messagebox.showinfo("Partie terminée", 
                                f"Gagnant: {data['winner']}\nScores finaux: {data['final_scores']}")
                                
                    except json.JSONDecodeError as e:
                        print(f"Erreur de décodage JSON: {e}")
                        
            except Exception as e:
                print(f"Erreur de connexion: {e}")
                self.client.close()
                break

    def start(self):
        try:
            self.client.connect(('localhost', 5000))
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()
            self.window.mainloop()
        except Exception as e:
            print(f"Impossible de se connecter au serveur: {e}")

if __name__ == "__main__":
    client = YahtzeeClient()
    client.start()