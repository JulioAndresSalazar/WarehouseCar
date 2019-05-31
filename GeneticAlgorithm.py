#Import required libraries
import csv, random

def randomDirection():
    #This function returns a random cardinal direction
    directions = 'NESW'
    direction_list = ''
    direction_list = direction_list + directions[random.randint(0,3)]
    return direction_list
    
def generateDirections():
    #This function returns a list of random cardinal directions 
    directions = 'NESW'
    direction_list = ''
    for i in range(direction_length):
        direction_list = direction_list + directions[random.randint(0,3)]
    return direction_list

def load_rooms(filename):
    #This function loads in room data for the warehouse
    rooms = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            rooms +=[row]
        #print(rooms) #optional 
        return rooms
        
def get_room(rooms, room_num):
    #This function returns the room data for a specific room number
    room = [] 
    for element in rooms:
        if str(room_num) == element[0]:
            room += (element)
        else:
            pass
    #print(room) #optional
    return room

def get_next_room_num(room, direction):
    #This function returns the next room number given a starting room and a direction
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
    #This function returns the type of room
    room_type = "Empty"
    room_type = room[5]
    return room_type

def generationZero():
    #This function creates an initial list of random directions
    generation = []
    for i in range(population_size):
        directions = generateDirections()
        generation.append(directions)
    return generation

def truncateDirections(start_room, directions): 
    #This function truncates the directions given to it at a solution point
    i = 0
    for i in range(len(directions)):
        type = get_room_type(get_room(rooms,start_room))
        if type == 'Product':
            return True
        next_room = get_next_room_num(get_room(rooms, start_room), directions[i])
        if next_room == '0':
            pass  
        else:
            start_room = next_room
            type = get_room_type(get_room(rooms,start_room))
            if type == 'Product':
                print('Product found!')
                return directions[0:i+1]
        i += 1
    print('no product')
    return directions[0:i+1] 

def sortGeneration(generation_0):
    #This function sorts the initial generation from shortest to longest
    new_generation = []
    j = 0
    for directions in generation_0:
        new_directions = truncateDirections(start_room, generation_0[j])
        if new_directions == True:
            return True
        else:
            new_generation.append(new_directions)
            j += 1
    new_generation.sort(key=len) 
    return new_generation
      
def cull(new_generation):
    #This function gets rid of the non-viable members of the generation
    next_gen = []
    i = 0
    while i < cull_number:  
        next_gen.append(new_generation[i])
        i += 1 
    return next_gen

def mutation(new_directions):
    #This function introduces random mutations into a set of directions
    random_direction = randomDirection()
    ls = list(new_directions)
    random_index = random.randint(0, len(new_directions)-1)
    ls[random_index] = random_direction
    new_directions = ''.join(ls)
    return new_directions

def randomlyCombine(next_gen):
    #This function randomly combines members of a generation
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
    #This is the main function loop
    generation_0 = generationZero()
    for i in range(generation_runs):
        sorted_generation = sortGeneration(generation_0) 
        if sorted_generation == True:
            result = 'Product already in room'
            return result
        else:
            culled_generation = cull(sorted_generation)
            new_generation = randomlyCombine(culled_generation)
            generation_0 = new_generation
    return culled_generation

def nextDoor():
    #This function returns the next door given a direction
    next_door = solution[0][0]
    if next_door == 'P':
        pass
    elif next_door != 'P':
        print('Next Door: ' + str(next_door) + '\n')
        
#Choose from four map sizes:
#'2x2' '4x4' '6x6' '9x9'
map_size = '2x2' 
rooms = load_rooms('/home/julio/Documents/ES2/Final Project/warehouse' + map_size + '.csv')

#Adjust these parameters as needed
direction_length = 10 #Determines how long the sets of directions are
population_size = 15 #Determines size of the generations
cull_number = 1 #A lower number is better
generation_runs = 8 #Determines how many times to run the script
prob_random = 0.4 #The probability of a mutation introduced into any given direction

#Change start_room as necessary
start_room = 11
solution = run()
print('Solution: ' + str(solution) + '\n')
