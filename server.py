import asyncio
import websockets
import json

class Character:
    def __init__(self, name, position, player_id):
        self.name = name
        self.position = position
        self.player_id = player_id

    def move(self, new_position):
        self.position = new_position

class Pawn(Character):
    def valid_moves(self, board):
        x, y = self.position
        potential_moves = []

        if y > 0 and (board[x][y - 1] == '' or board[x][y - 1].player_id != self.player_id):
            potential_moves.append((x, y - 1))
        if y < 4 and (board[x][y + 1] == '' or board[x][y + 1].player_id != self.player_id):
            potential_moves.append((x, y + 1))
        if self.player_id == 'A' and x < 4 and (board[x + 1][y] == '' or board[x + 1][y].player_id != self.player_id):
            potential_moves.append((x + 1, y))
        if self.player_id == 'B' and x > 0 and (board[x - 1][y] == '' or board[x - 1][y].player_id != self.player_id):
            potential_moves.append((x - 1, y))
        if x > 0 and (board[x - 1][y] == '' or board[x - 1][y].player_id != self.player_id):
            potential_moves.append((x - 1, y))
        if x < 4 and (board[x + 1][y] == '' or board[x + 1][y].player_id != self.player_id):
            potential_moves.append((x + 1, y))

        return potential_moves

class Hero1(Character):
    def valid_moves(self, board):
        x, y = self.position
        potential_moves = []

        if y > 1 and (board[x][y - 2] == '' or board[x][y - 2].player_id != self.player_id):
            potential_moves.append((x, y - 2))
        if y < 3 and (board[x][y + 2] == '' or board[x][y + 2].player_id != self.player_id):
            potential_moves.append((x, y + 2))
        if self.player_id == 'A' and x < 3 and (board[x + 2][y] == '' or board[x + 2][y].player_id != self.player_id):
            potential_moves.append((x + 2, y))
        if self.player_id == 'B' and x > 1 and (board[x - 2][y] == '' or board[x - 2][y].player_id != self.player_id):
            potential_moves.append((x - 2, y))
        if x > 1 and (board[x - 2][y] == '' or board[x - 2][y].player_id != self.player_id):
            potential_moves.append((x - 2, y))
        if x < 3 and (board[x + 2][y] == '' or board[x + 2][y].player_id != self.player_id):
            potential_moves.append((x + 2, y))

        return potential_moves

class Hero2(Character):
    def valid_moves(self, board):
        x, y = self.position
        potential_moves = []

        if x > 1 and y > 1 and (board[x - 2][y - 2] == '' or board[x - 2][y - 2].player_id != self.player_id):
            potential_moves.append((x - 2, y - 2))
        if x > 1 and y < 3 and (board[x - 2][y + 2] == '' or board[x - 2][y + 2].player_id != self.player_id):
            potential_moves.append((x - 2, y + 2))
        if x < 3 and y > 1 and (board[x + 2][y - 2] == '' or board[x + 2][y - 2].player_id != self.player_id):
            potential_moves.append((x + 2, y - 2))
        if x < 3 and y < 3 and (board[x + 2][y + 2] == '' or board[x + 2][y + 2].player_id != self.player_id):
            potential_moves.append((x + 2, y + 2))

        return potential_moves

class Game:
    def __init__(self):
        self.board = [[None for _ in range(5)] for _ in range(5)]
        self.players = {'A': [], 'B': []}
        self.current_turn = 'A'
        self.initialize_characters()

    def initialize_characters(self):
        self.players['A'] = [
            Pawn('A-P1', (0, 0), 'A'),
            Pawn('A-P2', (0, 1), 'A'),
            Pawn('A-P3', (0, 2), 'A'),
            Hero1('A-H1', (0, 3), 'A'),
            Hero2('A-H2', (0, 4), 'A'),
        ]
        self.players['B'] = [
            Pawn('B-P1', (4, 0), 'B'),
            Pawn('B-P2', (4, 1), 'B'),
            Pawn('B-P3', (4, 2), 'B'),
            Hero1('B-H1', (4, 3), 'B'),
            Hero2('B-H2', (4, 4), 'B'),
        ]

        for player_id, characters in self.players.items():
            for character in characters:
                x, y = character.position
                self.board[x][y] = character

    def add_player(self, player_id, characters):
        self.players[player_id] = characters
        for character in characters:
            x, y = character.position
            self.board[x][y] = character

    def move_character(self, player_id, character_name, new_position):
        for character in self.players[player_id]:
            if character.name == character_name:
                if new_position in character.valid_moves(self.board):
                    old_x, old_y = character.position
                    opponent_char = self.board[new_position[0]][new_position[1]]
                    if opponent_char and opponent_char.player_id != player_id:
                        self.players[opponent_char.player_id].remove(opponent_char)
                    self.board[old_x][old_y] = None
                    character.move(new_position)
                    new_x, new_y = new_position
                    self.board[new_x][new_y] = character
                    self.switch_turn()
                    return True
        return False

    def get_game_state(self):
        game_state = [[None for _ in range(5)] for _ in range(5)]
        for x in range(5):
            for y in range(5):
                char = self.board[x][y]
                if char:
                    game_state[x][y] = {'name': char.name, 'player': char.player_id}
        return {
            'game_state': game_state,
            'current_turn': self.current_turn,
        }

    def switch_turn(self):
        self.current_turn = 'B' if self.current_turn == 'A' else 'A'

game = Game()

async def handle_connection(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        action = data['action']

        if action == 'join':
            player_id = data['player_id']
            characters_info = data['characters']
            characters = []

            for char_info in characters_info:
                name, pos = char_info['name'], tuple(char_info['position'])
                if 'P' in name:
                    characters.append(Pawn(name, pos, player_id))
                elif 'H1' in name:
                    characters.append(Hero1(name, pos, player_id))
                elif 'H2' in name:
                    characters.append(Hero2(name, pos, player_id))

            game.add_player(player_id, characters)
            await websocket.send(json.dumps({'status': 'player_added', 'game_state': game.get_game_state()}))

        elif action == 'move':
            player_id = data['player_id']
            character_name = data['character_name']
            new_position = tuple(data['new_position'])

            if game.move_character(player_id, character_name, new_position):
                await websocket.send(json.dumps({'status': 'move_successful', 'game_state': game.get_game_state()}))
            else:
                await websocket.send(json.dumps({'status': 'move_failed'}))

        elif action == 'state':
            await websocket.send(json.dumps(game.get_game_state()))

start_server = websockets.serve(handle_connection, 'localhost', 1245)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
