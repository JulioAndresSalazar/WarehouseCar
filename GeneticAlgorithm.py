#Genetic algorithm for path planning
import csv
import random

def randomDirection():
    directions = 'NESW'
    direction_list = ''
    direction_list = direction_list + directions[random.randint(0,3)]
    return direction_list
    
def generateDirections():
    directions = 'NESW'
    direction_list = ''
    for i in range(direction_length):
        direction_list = direction_list + directions[random.randint(0,3)]
    return direction_list

def load_rooms(filename):
    rooms = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            rooms +=[row]
        #print(rooms)
        return rooms
        
def get_room(rooms, room_num):
    room = [] 
    for element in rooms:
        if str(room_num) == element[0]:
            room += (element)
        else:
            pass
    #print(room)
    return room

def get_next_room_num(room, direction):
    next_room_num = 0
    if direction == 'N':
        next_room_num = room[1]
    elif direction == 'E': 
        next_room_num = room[2]
    elif direction == 'S': 
        next_room_num = room[3]
    elif direction == 'W': 
        next_room_num = room[4]
    return next_room_num

def get_room_type(room):
    room_type = "Empty"
    room_type = room[5]
    #if map_size == '2x2':
    #    room_type = room[5]
    #elif map_size == '4x4':
    #elif map_size == '6x6':
    #elif map_size == '9x9'
    #print(room_type)
    return room_type
        
#def normalizeLength(string1, string2):
#    string1 = string1 + string2[len(string1):] # add onto pop1 any extra characters from pop2
#    string2 = string2 + string1[len(string2):] # add onto pop2 any extra characters from pop1
#    return string1, string2

def generationZero():
    generation = []
    for i in range(population_size):
        directions = generateDirections()
        #print(directions)
        generation.append(directions)
    #print('Generation 0: ' + str(generation) + '\n')
    return generation

def truncateDirections(start_room, directions): 
    i = 0
    for i in range(len(directions)):
        type = get_room_type(get_room(rooms,start_room))
        if type == 'Product':
            return True
        next_room = get_next_room_num(get_room(rooms, start_room), directions[i])
        if next_room == '0':
            #print('dead end, staying in room: ' + str(start_room))
            pass  
        else:
            start_room = next_room
            #print('now in room: ' + str(start_room))
            type = get_room_type(get_room(rooms,start_room))
            #print(type)
            if type == 'Product':
                #print('Product found!')
                #print(start_room)
                #print('i: ' + str(i))
                return directions[0:i+1]
        i += 1
    #print('no product')
    #print('i: ' + str(i))
    return directions[0:i+1] 

def sortGeneration(generation_0):
    new_generation = []
    j = 0
    for directions in generation_0:
        new_directions = truncateDirections(start_room, generation_0[j]) #actual truncate/check if solution
        if new_directions == True:
            return True
        else:
            #print(new_directions)
            new_generation.append(new_directions)
            j += 1
    new_generation.sort(key=len) 
    return new_generation
      
def cull(new_generation):
    next_gen = []
    i = 0
    while i < cull_number:  
        next_gen.append(new_generation[i])
        i += 1 
    return next_gen

def mutation(new_directions):
    random_direction = randomDirection()
    ls = list(new_directions)
    random_index = random.randint(0, len(new_directions)-1)
    ls[random_index] = random_direction
    new_directions = ''.join(ls)
    return new_directions

def randomlyCombine(next_gen):
    next_gen_0 = []
    for i in range(population_size):
        index1 = random.randint(0, len(next_gen) - 1)
        index2 = random.randint(0, len(next_gen) - 1)
        chance = random.uniform(0,1)
        #print(chance)
        new_directions = next_gen[index1] + next_gen[index2]
        #print(new_directions)
        if chance < prob_random:
            new_directions = mutation(new_directions)
            #print(new_directions)
        next_gen_0.append(new_directions)
    return next_gen_0

def run():
    generation_0 = generationZero()
    for i in range(generation_runs):
        sorted_generation = sortGeneration(generation_0) #we truncate here at the solution point
        #print('Sorted/Truncated Generation: ' + str(sorted_generation) + '\n')
        if sorted_generation == True:
            result = 'Product already in room'
            return result
        else:
            culled_generation = cull(sorted_generation)
            #print('Culled Generation: ' + str(culled_generation) + '\n')
            new_generation = randomlyCombine(culled_generation)
            #print('New Generation: ' + str(new_generation) + '\n')
            generation_0 = new_generation
    return culled_generation

def nextDoor():
    next_door = solution[0][0]
    if next_door == 'P':
        pass
    elif next_door != 'P':
        print('Next Door: ' + str(next_door) + '\n')
        
#Choose from four map sizes:
#'2x2' '4x4' '6x6' '9x9'
#2 moves 
#6 moves
#10 moves
#16 moves
map_size = '2x2' 
rooms = load_rooms('/home/julio/Documents/ES2/Final Project/warehouse' + map_size + '.csv')

#Manipulate genetic algorithm parameters
direction_length = 10 #20 good
population_size = 15 #20 good size
cull_number = 1 #lower = better
generation_runs = 8 #from 5 to 10
prob_random = 0.4 

#Change start_room as necessary
start_room = 11
solution = run()
print('Solution: ' + str(solution) + '\n')