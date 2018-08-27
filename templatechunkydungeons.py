import math
import random

ROOM_WIDTH, ROOM_HEIGHT = 14, 10
HORIZONTAL_ROOMS, VERTICAL_ROOMS = 6, 5
WIDTH, HEIGHT = ROOM_WIDTH*HORIZONTAL_ROOMS, ROOM_HEIGHT*VERTICAL_ROOMS

# Rooms have four sides, any of them can be open -> if we take an open side as a 1 and a closed side as a 0 each room type can be defined with 4 bits
# From most to least significant bit, they'll be assigned to the north, east, south, west walls
# E.g. 0b1010=10 would correspond to a room type with openings on the north and south

TYPE_MASK = 0x0F

def repeatStr(char, times):
    result = ''
    for i in range(times):
        result += char
    return result

def roomLineStr(type,lineNumber,stairs=False):
    result = ''
    if lineNumber==0 or lineNumber==ROOM_HEIGHT-1:
        result = repeatStr('# ', ROOM_WIDTH)
        if (lineNumber==0 and type[0]=='1') or (lineNumber==ROOM_HEIGHT-1 and type[2]=='1'):
            result = result[:math.ceil(ROOM_WIDTH/2)*2]+'· '+result[math.ceil(ROOM_WIDTH/2)*2+2:]
    else:
        result = '# '+repeatStr('· ',ROOM_WIDTH-2)+'# '
        if lineNumber==math.ceil(ROOM_HEIGHT/2):
            if type[3]=='1':
                result='· '+result[2:]
            if type[1]=='1':
                result=result[:-2]+'· '
            if stairs:
                result=result[:math.ceil(ROOM_WIDTH/2)*2]+'X '+result[math.ceil(ROOM_WIDTH/2)*2+2:]
    return result
        

def roomGridString(grid, start, end):
    lines = []
    result = ''
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            for k in range(ROOM_HEIGHT):
                if k+i*ROOM_HEIGHT>len(lines)-1:
                    lines.append(roomLineStr(grid[i][j], k, ([j,i]==start or [j,i]==end)))
                else:
                    lines[k+i*ROOM_HEIGHT]+=roomLineStr(grid[i][j], k, ([j,i]==start or [j,i]==end))
        for l in range(i*ROOM_HEIGHT,(i+1)*ROOM_HEIGHT):
            lines[l]+='\n'
            result+=lines[l]
    return result

def deepRandomWalk(previous, start, end, width, height):
    previous.append(start)
    goodPath = False
    if start[0]==end[0] and start[1]==end[1]:
        return previous, True
    else:
        possibleWalk = []
        if start[0]-1>=0 and [start[0]-1,start[1]] not in previous:
            possibleWalk.append([start[0]-1,start[1]])
        if start[0]+1<width and [start[0]+1, start[1]] not in previous:
            possibleWalk.append([start[0]+1, start[1]])
        if start[1]-1>=0 and [start[0],start[1]-1] not in previous:
            possibleWalk.append([start[0],start[1]-1])
        if start[1]+1<height and [start[0], start[1]+1] not in previous:
            possibleWalk.append([start[0], start[1]+1])
        random.shuffle(possibleWalk)
        for walkChoice in possibleWalk:
            newPath, goodPath = deepRandomWalk(previous, walkChoice, end, width, height)
            if goodPath:
                break
        if not goodPath:
            goodPath = False
            previous.pop()
        return previous, goodPath

def replaceChar(str, char, index):
    str = str[:index]+char+str[index+1:]
    return str

def generatePath(grid, start, end):
    print("generatePath from {0} to {1}".format(start,end))
    path, goodPath = deepRandomWalk([], start, end, len(grid[0]), len(grid))

    for i in range(len(path)-1): #FIX
        print(grid)
        if path[i+1][0]==path[i][0]+1: # going east
            grid[path[i][1]][path[i][0]]=replaceChar(grid[path[i][1]][path[i][0]], '1', 1)
            grid[path[i+1][1]][path[i+1][0]]=replaceChar(grid[path[i+1][1]][path[i+1][0]], '1', 3)
        elif path[i+1][0]==path[i][0]-1: # going west
            grid[path[i][1]][path[i][0]]=replaceChar(grid[path[i][1]][path[i][0]], '1', 3)
            grid[path[i+1][1]][path[i+1][0]]=replaceChar(grid[path[i+1][1]][path[i+1][0]], '1', 1)
        elif path[i+1][1]==path[i][1]+1: # going south
            grid[path[i][1]][path[i][0]]=replaceChar(grid[path[i][1]][path[i][0]], '1', 2)
            grid[path[i+1][1]][path[i+1][0]]=replaceChar(grid[path[i+1][1]][path[i+1][0]], '1', 0)
        elif path[i+1][1]==path[i][1]-1: # going north
            grid[path[i][1]][path[i][0]]=replaceChar(grid[path[i][1]][path[i][0]], '1', 0)
            grid[path[i+1][1]][path[i+1][0]]=replaceChar(grid[path[i+1][1]][path[i+1][0]], '1', 2)

    return grid, path


def randomOpenRoom(grid):
    reachable = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] != '0000':
                reachable.append([j,i])
    random.shuffle(reachable)
    return reachable[0]


def randomUnreachableRoom(grid):
    unreachable = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '0000':
                unreachable.append([j,i])
    random.shuffle(unreachable)
    return unreachable[0]


def hasUnreachableRooms(grid):
    unreachable = False
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '0000':
                unreachable = True
                break
    return unreachable


def countUnreachableRooms(grid):
    count = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '0000':
                count += 1
    return count


def fullyConnectRooms(roomGrid):
    while hasUnreachableRooms(roomGrid):
        unreachableRoom = randomUnreachableRoom(roomGrid)
        openRoom = randomOpenRoom(roomGrid)
        generatePath(roomGrid, unreachableRoom, openRoom)
    return roomGrid


def percentageUnreachable(grid):
    count = countUnreachableRooms(grid)
    return (count/(len(grid)*len(grid[0])))*100


def connectRoomsEnsuringMinimum(grid, percentage):
    while (100 - percentageUnreachable(grid)) < percentage:
        unreachableRoom = randomUnreachableRoom(grid)
        openRoom = randomOpenRoom(grid)
        generatePath(grid, unreachableRoom, openRoom)
    return grid
            

def main():
    print("\nWorld size: {0}x{1}".format(WIDTH,HEIGHT))
    print("Room size: {0}x{1}".format(ROOM_WIDTH,ROOM_HEIGHT))
    roomGrid = [['0000' for x in range(HORIZONTAL_ROOMS)] for y in range(VERTICAL_ROOMS)]
    print("Grid size: {0}x{1}\n".format(len(roomGrid[0]),len(roomGrid)))

    start= [random.randint(0,len(roomGrid)-1), random.randint(0,len(roomGrid[0])-1)]
    end = [random.randint(0,len(roomGrid)-1), random.randint(0,len(roomGrid[0])-1)]
    print("{0} to {1}".format(start, end))
    while start==end:
        end = [random.randint(0,len(roomGrid)-1), random.randint(0,len(roomGrid[0])-1)]
    
    roomGrid, mainPath = generatePath(roomGrid, start, end)
    print(roomGridString(roomGrid, start, end))

    hasUnreachable = hasUnreachableRooms(roomGrid)
    print("Has unreachable rooms?: {0}".format(hasUnreachable))
    if hasUnreachable:
        unreachableCount = countUnreachableRooms(roomGrid)
        percentage = percentageUnreachable(roomGrid)
        print("Has {0} unreachable rooms accounting for {1}%".format(unreachableCount, percentage))
        print("{0}% of the map is visitable".format(100-percentage))
        roomGrid = connectRoomsEnsuringMinimum(roomGrid, 70)
        print("\nEnsuring 70% of grid connected:")
        print(roomGridString(roomGrid, start, end))
        unreachableCount = countUnreachableRooms(roomGrid)
        percentage = percentageUnreachable(roomGrid)
        print("Has {0} unreachable rooms accounting for {1}%".format(unreachableCount, percentage))
        print("{0}% of the map is visitable".format(100-percentage))
    # too many openings in rooms -> either go from a random unreachable room to the CLOSEST open room, or don't connect everything and just settle for a minimum percentage
    
    


if __name__ == "__main__":
    main()

