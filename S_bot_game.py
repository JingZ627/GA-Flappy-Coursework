# This game is from the official documentation of freegames
# https://pypi.org/project/freegames/
                        
# pip install freegames

# Click on screen to control ball

# import modules
from random import *
from this import s
import turtle 
from freegames import vector

import copy
import random
from functools import partial
import operator
import numpy as np
from deap import algorithms, base, creator, tools, gp
import time

import threading

class game(object):
    
    # Set window title, color and icon
    def __init__(self, max_time):
        self.max_time = max_time
        self.routine = None
        self.t = turtle.Turtle()
        self.s = turtle.Screen()
        self.s.title("Flappy Ball")
        self.root = self.s._root
        self.root.iconbitmap("logo-ico.ico")
        self.s.bgcolor('#80ffd4')
        # self.root.attributes("-alpha", 0.5)
        self.s.setup(420, 420, 370, 0)
        
        
    def _reset(self):
        self.alive=True
        self.begin_time = time.time()
        self.bird = vector(0, 0)
        self.balls = []
        self.move_step=0
        self.speed=3
        self.velocity=0
        self.move_distance = 0
        self.time=0

        

        self.t.hideturtle()
        self.t.up()
        self.s.tracer(False)
        # t.onscreenclick(tap)
        self.move()
        # while
        # self.s.mainloop()\
        
        # th = threading.Thread(target=self.s.mainloop(), args=(self)) # 

        # th.start() # 開始
        
    # Move bird up in response to screen tap
    def tap(self):
        self.velocity-=0.3
        # up = vector(0, 30)
        # self.bird.move(up)
        self.move_step+=1
    
    def wait(self):
        self.move_step+=1
        self.move()

    def speed_up(self):
        self.speed+=0.1
        self.move_step+=1
    def speed_down(self):
        self.speed-=0.1
        self.move_step+=1

    # Return True if point on screen
    def inside(self,point):
        return -200 < point.x < 200 and -200 < point.y < 200

    # Draw screen objects
    def draw(self,alive):
        self.t.clear()
        self.t.goto(self.bird.x, self.bird.y)
        if alive:
            self.t.dot(13, 'green')
        else:
            self.t.dot(13, 'red')
        for ball in self.balls:
            self.t.goto(ball.x, ball.y)
            self.t.dot(20, '#862d2d')
        self.s.update()

    def move(self):
        self.move_distance+=1;
        # Update object positions
        self.velocity+=0.5
        self.bird.y -= self.velocity

        for ball in self.balls:
            # ball.x -= self.speed
            ball.x -= 5

        if randrange(10) == 0:
            y = randrange(-199, 199)
            ball = vector(199, y)
            self.balls.append(ball)

        while len(self.balls) > 0 and not self.inside(self.balls[0]):
            self.balls.pop(0)
        if not self.inside(self.bird):
            self.draw(False)
            # self.s.bye()
            self.alive=False
            
            # return

        for ball in self.balls:
            if abs(ball - self.bird) < 15:
                # print("-------dead")
                self.draw(False)
                # self.s.bye()
                self.alive=False
        #         return
        if not self.alive:
            return
        self.time+=1
        self.draw(True)
        self.s.ontimer(self.move, 50)

    def run(self,routine):
        self._reset()
        self.lastime = time.time()
        # print("____________here")
        
        while time.time() - self.begin_time < self.max_time and self.alive:
            
            self.s.update()
            if time.time() - self.lastime  > 0.1:
                self.lastime = time.time()
                routine()
                # print()
                
    def _conditional(self, condition, out1, out2):
        out1() if condition() else out2()

    def sense_target(self):
        for ball in self.balls:
            if  ball.x - self.bird.x <50 and self.bird.x + 10 < ball.y < self.bird.y - 10:
                return True 
            else: 
                continue
        return False
    def sense_up(self):
        if 0 < self.bird.y-50:
            return True 
        # else: 
        return False
    def sense_down(self):
        if  self.bird.y+50 < 400:
            return True 
        # else: 
        return False

    def if_target_ahead(self, out1, out2):
        return partial(self._conditional, self.sense_target, out1, out2)

    def if_border_up(self, out1, out2):
        return partial(self._conditional, self.sense_up, out1, out2)

    def if_border_down(self, out1, out2):
        return partial(self._conditional, self.sense_down, out1, out2)

class Prog(object):
    def _progn(self, *args):
        for arg in args:
            arg()

    def prog2(self, out1, out2): 
        return partial(self._progn, out1, out2)

    def prog3(self, out1, out2, out3):     
        return partial(self._progn, out1, out2, out3)

    # def prog10(self, out1):     
    #     return partial(self._progn, out1, out1, out1, out1, out1, out1, out1, out1, out1, out1, out1, out1, out1,)

def eval_func(individual):
    global robot, pset

    # Transform the tree expression to functionnal Python code
    routine = gp.compile(individual, pset)

    # Run the generated routine
    robot.run(routine)
    return robot.move_distance,

def create_toolbox():
    global robot, pset

    pset = gp.PrimitiveSet("MAIN", 0)
    pset.addPrimitive(robot.if_target_ahead, 2)
    pset.addPrimitive(robot.if_border_up, 2)
    pset.addPrimitive(robot.if_border_down, 2)
    pset.addPrimitive(Prog().prog2, 2)
    pset.addPrimitive(Prog().prog3, 3)
    # pset.addPrimitive(Prog().prog10, 1)
    pset.addTerminal(robot.tap)
    # pset.addTerminal(robot.speed_up)
    # pset.addTerminal(robot.speed_down)
    pset.addTerminal(robot.wait)

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    # Attribute generator
    toolbox.register("expr_init", gp.genFull, pset=pset, min_=1, max_=2)

    # Structure initializers
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr_init)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", eval_func)
    toolbox.register("select", tools.selTournament, tournsize=7)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=20))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=20))


    return toolbox
    

if __name__ == "__main__":
    global robot

    # Seed the random number generator
    random.seed(7)

    # Define the maximum number of moves
    max_time = 20

    # Create the robot object
    robot = game(max_time)

    # Create the toolbox
    toolbox = create_toolbox()
    
    
    # Define population and hall of fame variables
    population = toolbox.population(n=10)
    hall_of_fame = tools.HallOfFame(1)

    # Register the stats
    stats = tools.Statistics(lambda x: x.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    # Define parameters
    probab_crossover = 0.4
    probab_mutate = 0.4
    num_generations = 50
    
    # Run the algorithm to solve the problem
    algorithms.eaSimple(population, toolbox, probab_crossover, 
            probab_mutate, num_generations, stats, 
            halloffame=hall_of_fame)