import random
import copy

#---------------------- légendes ----------------------
print
symbols = ['B', 'W']

def opponent(color):		#inverse la couleur
	if color == 'W':
		return 'B'
	return 'W'

directions = {
	'NE': (-1,  0),
	'SW': ( 1,  0),
	'NW': (-1, -1),
	'SE': ( 1,  1),
	 'E': ( 0,  1),
	 'W': ( 0, -1)
}

opposite = {
	'NE': 'SW',
	'SW': 'NE',
	'NW': 'SE',
	'SE': 'NW',
	'E': 'W',
	'W': 'E'
}

posValues = [        #tableau de valorisation des postions sur le plateau
    [1.6, 1.6, 1.6, 1.6, 1.6, "X", "X", "X", "X"],
    [1.6, 2.5, 2.5, 2.5, 2.5, 1.6, "X", "X", "X"],
    [1.6, 2.5, 3.0, 3.0, 3.0, 2.5, 1.6, "X", "X"],
    [1.6, 2.5, 3.0, 3.35, 3.35, 3.0, 2.5, 1.6, "X"],
    [1.6, 2.5, 3.0, 3.35, 3.5, 3.35, 3.0, 2.5, 1.6],
    ["X", 1.6, 2.5, 3.0, 3.35, 3.35, 3.0, 2.5, 1.6],
    ["X", "X", 1.6, 2.5, 3.0, 3.0, 3.0, 2.5, 1.6],
    ["X", "X", "X", 1.6, 2.5, 2.5, 2.5, 2.5, 1.6],
    ["X", "X", "X", "X", 1.6, 1.6, 1.6, 1.6, 1.6]
]

#---------------------- fonctions basiques ----------------------

def count(state,letter):        #compte le nombre de fois qu'un symbole apparait sur le plateau
    board = state["board"]
    cnt = 0
    for line in board:
        for elem in line:
            if elem == letter:
                cnt += 1
    return cnt

def getStatus(state, pos):		#renvoie l'etat d'une case (W, B, E ou X)
	return state['board'][pos[0]][pos[1]]

def winner(state):      #donne le gagnant d'un etat du jeu (ou None si il n'y en a pas)
    black, white = count(state,"B"), count(state,"W")
    if black < 9:
        return 1
    if white < 9:
        return 0
    return None

def gameOver(state):    #renvoie si la partie est terminée pour cet état du jeu
    if winner(state) is not None:
        return True
    return False

def score(state, color):
    points = 0.0
    board = state["board"]
    for line in range(0,9):
        for column in range(0,9):
            if board[line][column] == color:
                points += posValues[line][column]
    return points


def utility(state):     #utilité d'un noeud final
    player = symbols[state["current"]]
    winner = winner(state)
    if player == winner:
        return 25
    if winner == None:
        return 0
    return -25

def heuristic(state):       #heuristique (écart de points avec l'adversaire en fonction des positions sur le plateau)
    player = state["current"]
    if gameOver(state):
        theWinner = winner(state)
        if theWinner == player:
            return 25
        return -25
    color = symbols[player]
    res = score(state,color) - score(state,opponent(color))
    return res


def positions(state, color):        #renvoie une liste des positions des pions d'une certaine couleur
    board = state["board"]
    pos = []
    for line in range(0,9):
        for column in range(0,9):
            if board[line][column] == color:
                pos.append([line, column])
    return pos

def newPos(pos, direction):		#calcule une position à partir d'une position de départ et d'une direction (équivalent à addDirection() dans le code du serveur)
	D = directions[direction]
	return [pos[0] + D[0], pos[1] + D[1]]

def sameLine(direction1, direction2):		#renvoie si deux directions sont les mêmes (peu importe le sens)
	if direction1 == direction2:
		return True
	if direction1 == opposite[direction2]:
		return True
	return False

def getDirectionName(directionTuple):	#transforme un tuple en direction
	for dirName in directions:
		if directionTuple == directions[dirName]:
			return dirName

def computeAlignement(marbles):		#renvoie la direction d'une ligne
	D = set()
	for i in range(len(marbles)-1):
		direction = (marbles[i+1][0]-marbles[i][0], marbles[i+1][1]-marbles[i][1])
		D.add(direction)
	return getDirectionName(D.pop())

def computeAlignementSort(marbles):		#renvoie la direction d'une ligne
	marbles = sorted(marbles, key=lambda L: L[0]*9+L[1])
	D = set()
	for i in range(len(marbles)-1):
		direction = (marbles[i+1][0]-marbles[i][0], marbles[i+1][1]-marbles[i][1])
		if direction not in directions.values():
			return None
		D.add(direction)
	return getDirectionName(D.pop()) if len(D) == 1 else None

def isOnBoard(pos):		#renvoie si les coordonnees sont sur le plateau
	l, c = pos
	if min(pos) < 0:
		return False
	if max(pos) > 8:
		return False
	if abs(c-l) >= 5:
		return False
	return True

def Out(position, posOut):      #dit si une position est en dehors du plateau
    if position in posOut:
        return True
    if max(position) > 8 or min(position) < 0:
        return True
    return False

def isEmpty(state, pos):		#renvoie si une case est vide
	return getStatus(state, pos) == 'E'

def isFree(state, pos):		#renvoie si une case est libre (inclut le dehors du plateau)
	if isOnBoard(pos):
		return isEmpty(state, pos)
	else:
		return True

#---------------------- Détermination des coups possibles ----------------------

def TwoAlign(positions):        #renvoie les paires de pions qui sont alignés
    lines = []
    dir = {'NE': (-1, 0),'E': (0, 1),'NW': (-1, -1)}
    for direction in dir:
        for position1 in positions:
            for position2 in positions:
                if newPos(position1, direction) == position2:
                    lines.append([position1,position2])
    return lines

def ThreeAlign(positions):          #renvoie les triplets de pions qui sont alignés
    lines = []
    dir = {'NE': (-1, 0),'E': (0, 1),'NW': (-1, -1)}
    for direction in dir:
        for position1 in positions:
            for position2 in positions:
                for position3 in positions:
                    if newPos(position1, direction) == position2 and newPos(position2, direction) == position3:
                        lines.append([position1,position2,position3])
    return lines

def MoveOne(positions, freePos):     #renvoie les déplacements possibles avec un seul pion (dans des cases vides)
    moves = []
    for position in positions:
        for direction in directions:
            if newPos(position, direction) in freePos:
                moves.append([[position],direction])
    return moves

def MoveTwo(positions, freePos):       #renvoie les déplacements possibles avec deux pions (dans une case vide)
    moves = []
    for position in positions:
        for direction in directions:
            if newPos(position[0], direction) in freePos or newPos(position[0], direction) in position:
                if newPos(position[1], direction) in freePos or newPos(position[1], direction) in position:
                    moves.append([position,direction])
    return moves

def MoveThree(positions, freePos):          #renvoie les déplacements possibles avec deux pions (dans des cases vides)
    moves = []
    for position in positions:
        for direction in directions:
            if newPos(position[0], direction) in freePos or newPos(position[0], direction) in position:
                if newPos(position[1], direction) in freePos or newPos(position[1], direction) in position:
                    if newPos(position[2], direction) in freePos or newPos(position[2], direction) in position:
                        moves.append([position,direction])
    return moves

def TwoPushOne(pos, posAdv, freePos, posOut):           #renvoie les coups possibles ou 2 pions en poussent 1
    moves = []
    for position in pos:
        dir = computeAlignement(position)
        if newPos(position[1], dir) in posAdv:
            if newPos(newPos(position[1], dir), dir) in freePos or Out(newPos(newPos(position[1], dir), dir), posOut) == True:
                moves.append([position,dir])
        dirOpp = opposite[dir]
        if newPos(position[0], dirOpp) in posAdv:
            if newPos(newPos(position[0], dirOpp), dirOpp) in freePos or Out(newPos(newPos(position[0], dirOpp), dirOpp), posOut) == True:
                moves.append([position,dirOpp])
    return moves

def ThreePushOne(pos, posAdv, freePos, posOut):      #renvoie les coups possibles ou 3 pions en poussent 1
    moves = []
    for position in pos:
        dir = computeAlignement(position)
        if newPos(position[2], dir) in posAdv:
            if newPos(newPos(position[2], dir), dir) in freePos or Out(newPos(newPos(position[2], dir), dir), posOut) == True:
                moves.append([position,dir])
        dirOpp = opposite[dir]
        if newPos(position[0], dirOpp) in posAdv:
            if newPos(newPos(position[0], dirOpp), dirOpp) in freePos or Out(newPos(newPos(position[0], dirOpp), dirOpp), posOut) == True:
                moves.append([position,dirOpp])
    return moves

def ThreePushTwo(pos, posAdv, freePos, posOut):         #renvoie les coups possibles ou 3 pions en poussent 2
    moves = []
    for position in pos:
        dir = computeAlignement(position)
        if newPos(position[2], dir) in posAdv and newPos(newPos(position[2], dir), dir) in posAdv:
            if newPos(newPos(newPos(position[2], dir), dir), dir) in freePos or Out(newPos(newPos(newPos(position[2], dir), dir), dir), posOut) == True:
                moves.append([position,dir])
        dirOpp = opposite[dir]
        if newPos(position[0], dirOpp) in posAdv and newPos(newPos(position[0], dirOpp), dirOpp) in posAdv:
            if newPos(newPos(newPos(position[0], dirOpp), dirOpp), dirOpp) in freePos or Out(newPos(newPos(newPos(position[0], dirOpp), dirOpp), dirOpp), posOut) == True:
                moves.append([position,dirOpp])
    return moves

def moves(state):       #renvoie les coups possibles
    color = symbols[state["current"]]
    pos = positions(state,color)
    posAdv = positions(state,opponent(color))
    freePos = positions(state,"E")
    posOut = positions(state,"X")
    res = []
    one = MoveOne(pos, freePos)
    random.shuffle(one)
    res.extend(one)
    two = MoveTwo(TwoAlign(pos), freePos)
    random.shuffle(two)
    res.extend(two)
    three = MoveThree(ThreeAlign(pos), freePos)
    random.shuffle(three)
    res.extend(three)
    twoone = TwoPushOne(TwoAlign(pos), posAdv, freePos, posOut)
    random.shuffle(twoone)
    res.extend(twoone)
    threeone = ThreePushOne(ThreeAlign(pos), posAdv, freePos, posOut)
    random.shuffle(threeone)
    res.extend(threeone)
    threetwo = ThreePushTwo(ThreeAlign(pos), posAdv, freePos, posOut)
    random.shuffle(threetwo)
    res.extend(threetwo)
    return res

#---------------------- Applique un coup au plateau de jeu ----------------------

def moveOneMarble(state, pos, direction):		#met à jour l'état après le déplacement d'un pion dans une case vide
	li, ci = pos			#"ligne initiale" et "colonne initiale"
	ld, cd = newPos(pos, direction)
	color = getStatus(state, pos)
	try:
		destStatus = getStatus(state, (ld, cd))
	except:
		destStatus = 'X'
	
	res = copy.copy(state)		#vide la case initiale
	res['board'] = copy.copy(res['board'])
	res['board'][li] = copy.copy(res['board'][li])
	res['board'][li][ci] = 'E'

	if destStatus == 'E':		#remplit la case ou l'on se deplace
		res['board'][ld] = copy.copy(res['board'][ld])
		res['board'][ld][cd] = color

	return res

def moveMarbles(state, marbles, direction):		#met à jour l'état après le déplacement de plusieurs pions dans une case vide
	for pos in marbles:
		state = moveOneMarble(state, pos, direction)
	return state

def moveMarblesTrain(state, marbles, direction):		#met à jour l'état après avoir poussé des pions adverses
	if direction in ['E', 'SE', 'SW']:
		marbles = sorted(marbles, key=lambda L: -(L[0]*9+L[1]))
	else:
		marbles = sorted(marbles, key=lambda L: L[0]*9+L[1])

	color = getStatus(state, marbles[0])

	pos = newPos(marbles[0], direction)
	toPush = []
	while not isFree(state, pos):
		toPush.append(pos)
		pos = newPos(pos, direction)

	state = moveMarbles(state, list(reversed(toPush)) + marbles, direction)

	return state

def apply(state, move):      #met à jour l'etat du jeu (plateau de jeu, tour...)

		marbles = move['marbles']

		if len(marbles) != 0:
			marblesDir = computeAlignementSort(marbles)

			if len(marbles) == 1:
				state = moveOneMarble(state, marbles[0], move['direction'])
			elif sameLine(move['direction'], marblesDir):
				state = moveMarblesTrain(state, marbles, move['direction'])
			else:
				state = moveMarbles(state, marbles, move['direction'])
		
		state['current'] = (state['current'] + 1) % 2
		return state

#---------------------- Détermine le meilleur coup ----------------------

def NegamaxWithPruningLimitedDepth(state, depth=2, alpha=float('-inf'), beta=float('+inf')):
    if gameOver(state) or depth==0:
        return -heuristic(state), None
    theValue, theMove = float('-inf'), None
    for move in reversed(moves(state)):
        mov = {"marbles":move[0],"direction":move[1]}
        newState = apply(state, mov)
        value, _ = NegamaxWithPruningLimitedDepth(newState, depth-1, -beta, -alpha)
        if value > theValue:
            theValue, theMove = value, mov
        alpha = max(alpha, theValue)
        if alpha >= beta:
            break
    return -theValue, theMove


#---------------------- Renvoie le coup ----------------------

def next(state):        #renvoie le coup à jouer
    _, move = NegamaxWithPruningLimitedDepth(state)
    return move