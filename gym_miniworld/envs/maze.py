import numpy as np
import math
from gym import spaces
from ..miniworld import MiniWorldEnv, Room
from ..entity import ImageFrame
from ..params import DEFAULT_PARAMS

'Importeirung der Objekte -> Ball, Box und Key'
from ..entity import Box, Ball, Key
'Importeirung von Ramdom -> Um Zufallszahlen zu generieren'
import random

class Maze(MiniWorldEnv):
    """
    Maze environment in which the agent has to reach a red box
    """

    'Allgemeiner Konstruktor der Oberklasse Maze'
    def __init__(
        self,
        num_rows=1,
        num_cols=15,
        room_size=1,
        max_episode_steps=None,
        **kwargs
    ):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.room_size = room_size
        self.gap_size = 0.25

        super().__init__(
            max_episode_steps = max_episode_steps or num_rows * num_cols * 24,
            **kwargs
        )

        # Allow only the movement actions
        self.action_space = spaces.Discrete(self.actions.move_forward+1)

    'Erstelle den Raum in Miniworld'
    def _gen_world(self, anzahl_obj = None):
        rows = []
        
        if anzahl_obj == None or anzahl_obj == 0:
            self.num_objs = random.randint(1,15)
        else:
            self.num_objs = anzahl_obj
            
        # For each row
        for j in range(self.num_rows):
            row = []

            # For each column
            for i in range(self.num_cols):

                min_x = i * (self.room_size + self.gap_size)
                max_x = min_x + self.room_size

                min_z = j * (self.room_size + self.gap_size)
                max_z = min_z + self.room_size

                room = self.add_rect_room(
                    min_x=min_x,
                    max_x=max_x,
                    min_z=min_z,
                    max_z=max_z,
                    wall_tex='brick_wall',
                    floor_tex='asphalt'
                )
                row.append(room)

            rows.append(row)

        visited = set()
        
        'Erstellung des Labyrinths und Plazierung der Objekte + Agent'
        def visit(i, j):
            """
            Recursive backtracking maze construction algorithm
            Quelle: https://stackoverflow.com/questions/38502
            """
            'Raumproportionen auslesen'
            room = rows[j][i]
            
            'Wenn Nachbar schon bekannt wird Raum hinzugefügt'
            visited.add(room)

            'Nachbar nach Zufallsprinzip festlegen'
            neighbors = self.rand.subset([(0,1), (0,-1), (-1,0), (1,0)], 4)

            'Für jeden möglichen Nachbarn ausführen'
            for dj, di in neighbors:
                ni = i + di
                nj = j + dj
                
                'Befindet sich der Nachbar im definierten Raum, soll Algorithmus fortgeführt werden'
                if nj < 0 or nj >= self.num_rows:
                    continue
                if ni < 0 or ni >= self.num_cols:
                    continue
                
                'Definition des Nachbarn an Zeite und Spalte orientieren'
                neighbor = rows[nj][ni]
                
                'Ist der Nachbar schon bekannt, Algo fortführen'
                if neighbor in visited:
                    continue
                
                'Alle Nachbarn gesichtet -> Nachbarn werden verbunden zu einem Labyrinth'
                if di == 0:
                    self.connect_rooms(room, neighbor, min_x=room.min_x, max_x=room.max_x)
                elif dj == 0:
                    self.connect_rooms(room, neighbor, min_z=room.min_z, max_z=room.max_z)
                
                'Rekursiever Aufruf der Funktion'
                visit(ni, nj)

        'Backtracking-Algo aufrühren -> Startpunkt oben Links'
        visit(0, 0)

        'Erstellen und plazieren der Objekte (Box)'
        'Boxen werden horizontal ausgerichtet'
        for obj in range(self.num_objs):
            self.box = self.place_entity(Box(color='red', size=0.9),dir=0)

        'Zähler auf 0 setzen'
        self.num_picked_up = 0
        
        'Plazieren des Agents'
        self.place_agent()

    def step(self, action):
        obs, reward, done, info = super().step(action)

        if self.agent.carrying:
            self.entities.remove(self.agent.carrying)
            self.agent.carrying = None
            self.num_picked_up += 1
            reward = 1

            if self.num_picked_up == self.num_objs:
                done = True
                
        return obs, reward, done, info

class MazeS2(Maze):
    def __init__(self):
        super().__init__(num_rows=2, num_cols=2)

class MazeS3(Maze):
    def __init__(self): # <-- Hier darf nur der eigene Konstruktor aufgerufen werden, ansonsten Crash !
        params = DEFAULT_PARAMS.no_random() # <-- Ab hier können nun die entsprechenden Parameter gesetzt werden
        params.set('forward_step', 0.9)
        params.set('turn_step', 90)
        super().__init__(num_rows=3, num_cols=3,room_size=5,params=params) # <-- Hier können nun die Parameter der Oberklasse übergeben werden
        
class MazeS3Fast(Maze):
    def __init__(self, forward_step=0.7, turn_step=45):

        # Parameters for larger movement steps, fast stepping
        params = DEFAULT_PARAMS.no_random()
        params.set('forward_step', forward_step)
        params.set('turn_step', turn_step)

        max_steps = 300

        super().__init__(
            num_rows=3,
            num_cols=3,
            params=params,
            max_episode_steps=max_steps,
            domain_rand=False
        )

'Eigenes Environment --HAWK--'        
class MazeHAWK(Maze):
    def __init__(self):
        super().__init__(num_rows=10, num_cols=10, room_size=5)

            