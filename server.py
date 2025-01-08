import socket
import threading
import json
from Jeu_du_Yathzee.game import YahtzeeGame

class YahtzeeServer:
    def __init__(self, host='localhost', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = []
        self.pseudos = []
        self.games = {}
        
    def broadcast(self, message, game_id):
        encoded_message = json.dumps(message).encode('utf-8')
        for client in self.games[game_id]['clients']:
            try:
                client.send(encoded_message)
            except:
                continue
            
    def handle_client(self, client, pseudo, game_id):
        game = self.games[game_id]['game']
        player_id = game.add_player()
        
        client.send(json.dumps({
            'type': 'player_id',
            'id': player_id,
            'current_player': game.current_player
        }).encode('utf-8'))
        
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    continue
                    
                data = json.loads(message)
                
                if data['type'] == 'chat':
                    self.broadcast({
                        'type': 'chat',
                        'message': data['message'],
                        'sender': data['sender']
                    }, game_id)
                
                elif data['type'] == 'roll':
                    if game.current_player != player_id:
                        continue
                        
                    dice = game.roll_dice(data['keep_positions'])
                    response = {
                        'type': 'roll_result',
                        'dice': dice,
                        'rolls_left': game.rolls_left
                    }
                    self.broadcast(response, game_id)
                
                elif data['type'] == 'score':
                    if game.current_player != player_id:
                        continue
                        
                    score = game.score_move(data['category'])
                    next_player = game.current_player
                    response = {
                        'type': 'score_update',
                        'scoring_player': player_id,
                        'next_player': next_player,
                        'category': data['category'],
                        'score': score,
                        'total_score': game.scores[player_id]
                    }
                    self.broadcast(response, game_id)
                    
                    if game.is_game_over():
                        winner = game.get_winner()
                        end_response = {
                            'type': 'game_over',
                            'winner': self.pseudos[winner],
                            'final_scores': {self.pseudos[p]: s for p, s in game.scores.items()}
                        }
                        self.broadcast(end_response, game_id)
                
            except Exception as e:
                print(f"Erreur: {e}")
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                pseudo = self.pseudos[index]
                self.pseudos.remove(pseudo)
                break
                
    def start(self):
        while True:
            client, address = self.server.accept()
            print(f"Nouvelle connexion de {address}")
            
            client.send('NICK'.encode('utf-8'))
            pseudo = client.recv(1024).decode('utf-8')
            self.pseudos.append(pseudo)
            self.clients.append(client)
            
            # Créer ou rejoindre une partie
            game_id = len(self.games)
            if len(self.games) == 0 or len(self.games[game_id-1]['clients']) >= 4:
                self.games[game_id] = {
                    'clients': [client],
                    'game': YahtzeeGame()
                }
            else:
                game_id -= 1
                self.games[game_id]['clients'].append(client)
            
            print(f"Le pseudo du client est {pseudo}")
            
            thread = threading.Thread(target=self.handle_client, args=(client, pseudo, game_id))
            thread.start()

if __name__ == "__main__":
    server = YahtzeeServer()
    server.start()