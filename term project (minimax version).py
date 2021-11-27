#################################################
# term project.py: version of code that supports multiple boards
# Your name: Kavya Iyer
# Your andrew id: kavyai

import math, copy, random, sys
import cs112_f21_week10_linter
from cmu_112_graphics import *

def appStarted(app): #initialize variables
    app.size = 0
    app.rows, app.cols = 8, 8
    #store piece locations
    app.board = Board(app)
    app.margin = 60
    app.validSelectedPiece = True
    app.validMove = True
    app.miniMax = False
    app.bot = False
    app.inputNeeded = True

class Board(object):
    def __init__(self, app):
        self.moves = [0, 0]
        self.cellWidth = 80
        self.cellHeight = 80
        self.rows = app.rows
        self.cols = app.cols
        self.board = [[None] * self.cols for i in range (0, self.rows)] 
        self.legalMoves = []
       
        #place pieces on board
        
        #pawns
        for i in range(self.cols):
            self.board[1][i] = Pawn(app, (1, i), 'black')
            self.board[6][i] = Pawn(app, (6, i), 'white')

        #count of pawns on board
        self.nwPawn = 8
        self.nbPawn = 8

        #rooks
        self.board[0][0] = Rook(app, (0, 0), 'black')
        self.board[0][7] = Rook(app, (0, 7), 'black')
        self.board[7][0] = Rook(app, (7, 0), 'white')
        self.board[7][7] = Rook(app, (7, 7), 'white')

        #knights
        self.board[0][1] = Knight(app, (0,1), 'black')
        self.board[0][6] = Knight(app, (0,6), 'black')
        self.board[7][1] = Knight(app, (7,1), 'white')
        self.board[7][6] = Knight(app, (7,6), 'white')

        #bishops
        self.board[0][2] = Bishop(app, (0,2), 'black')
        self.board[0][5] = Bishop(app, (0,5), 'black')
        self.board[7][2] = Bishop(app, (7,2), 'white')
        self.board[7][5] = Bishop(app, (7,5), 'white')

        #queens
        self.board[0][3] = Queen(app, (0,3), 'black')
        self.board[7][3] = Queen(app, (7,3), 'white')

        #kings
        self.board[0][4] = King(app, (0, 4), 'black')
        self.board[7][4] = King(app, (7, 4), 'white')

        #tracking position of king
        self.bKingPos = (0, 4)
        self.wKingPos = (7, 4)

        #board states
        self.check = False
        self.checkmate = False
        self.gameOver = False

        #pieces conquered
        self.bConq = dict()
        self.wConq = dict()

        #player and piece
        self.selectedPiece = None
        self.currentPlayer = 'white'
        self.selectedPiecePosition = None

        #num of moves
        self.wMoves = 0
        self.bMoves = 0

    def draw(self, app, canvas): 
            #drawing board
            canvas.create_rectangle(app.margin, app.margin, 
            app.width-app.margin, app.height-app.margin)
            for row in range(self.rows):
                for col in range(self.cols):
                    self.drawCell(app, canvas, row, col)
                    #if there is a piece in that cell, ask piece to draw itself
                    if (self.board[row][col] != None):
                        self.board[row][col].draw(app, canvas)
            if app.board.selectedPiece!= None:
                app.board.selectedPiece.draw(app, canvas)

    def drawCell(self, app, canvas, row, col): #drawing one cell
        (startX, startY) = fromRowColToXY(row, col, app)
        if ((row + col)%2 == 0):
            fillColor = 'maroon'
        else:
            fillColor = 'tan'

        if self.selectedPiece != None:
            if ((row == self.selectedPiece.location[0]) and 
                (col == self.selectedPiece.location[1])):
                fillColor = 'gold'
            for move in self.selectedPiece.getLegalMoves(self):
                newPos = move[1]
                if ((row == newPos[0]) and (col == newPos[1])):
                    fillColor = 'light green'
                    break 
        canvas.create_rectangle(startX, startY, startX+self.cellWidth, 
            startY+self.cellHeight, fill = fillColor)

    #returns a list of legal moves for that color
    #list = list of values [old Pos, newPos]
    def getLegalMoves(self, color):
        legalMoves = []
        for row in self.board:
            for piece in row:
                if piece == None:
                    continue
                if piece.color != color:
                    continue
                moves = piece.getLegalMoves(self)
                if moves:
                    legalMoves.extend(moves)
        return legalMoves

########################
#HELPER FUNCTIONS
########################

def fromRowColToXY(row, col, app): #translate row/col to x/y pixel coords
    X = app.margin + (col*app.board.cellWidth)
    Y = app.margin + (row*app.board.cellWidth)
    return X, Y

def fromXYToRowCol(X, Y, app): #translate x/y pixel coords to row/col
    col = (X-app.margin)//app.board.cellWidth
    row = (Y-app.margin)//app.board.cellWidth
    return row, col

#is a path clear to traverse from start row (will be used by queen and bishop)
def isPathClearDiag(startRow, endRow, startCol, endCol, board):
    i, j = startRow, startCol
    if endCol < startCol:
        sign = -1
    else:
        sign = 1
    while i != endRow and j != endCol:
        if board.board[i][j] != None:
            return False
        else:
            i += 1
            j += (sign*1)
    return True

#is a path clear to traverse along a row (will be used by queen and rook)
def isPathClearRow(startPos, endPos, col, board):
    for tile in range (startPos, endPos):
        if board.board[tile][col] != None:
            return False
    return True

#is a path clear to traverse along a col (will be used by rook, pawn and queen)
def isPathClearCol(startPos, endPos, row, board):
    for tile in range (startPos, endPos):
        if board.board[row][tile] != None:
            return False
    return True

#helper for Rook
def isRookMoveValid(self, board, newPos):
    #can only move up/down same row or col
    if ((newPos[1] != self.location[1]) and (newPos[0] != self.location[0])):
        return False
    if (newPos[1] == self.location[1]): #moving along rows
        col = self.location[1]
        if (self.location[0] < newPos[0]):
            start = self.location[0] + 1
            end = newPos[0]
        else:
            start = newPos[0] + 1
            end = self.location[0]
        return isPathClearRow(start, end, col, board)
    else: #moving along cols
        row = self.location[0]
        if (self.location[1] < newPos[1]):
            start = self.location[1] + 1
            end = newPos[1]
        else:
            start = newPos[1] + 1
            end = self.location[1]
        return isPathClearCol(start, end, row, board)

#helper for Bishop
def isBishopMoveValid(self, board, newPos): #can only move diagonally
    if (abs(self.location[0]-newPos[0]) != abs(self.location[1]-newPos[1])):
        return False
    if (self.location[0] < newPos[0]):
        startRow = self.location[0]+1
        endRow = newPos[0]
        endCol = newPos[1]
        if (self.location[1] < newPos[1]):
            startCol = self.location[1]+1
        else:
            startCol = self.location[1]-1
    else:
        startRow = newPos[0] + 1
        endRow = self.location[0]
        endCol = self.location[1]
        if (self.location[1] > newPos[1]):
            startCol = newPos[1] + 1
        else:
            startCol = newPos[1] - 1
    return isPathClearDiag (startRow, endRow, startCol, endCol, board)

#return King position
def getKingPos(board, color):
    if (color == 'white'):
        return board.wKingPos
    else:
        return board.bKingPos

#finding check
def isCheck(self, board):
    #if next move of curr piece can take out King
    if (self.color == 'white'):
        oppColor = 'black'
    else:
        oppColor = 'white'
    kingPos = getKingPos(board, oppColor)
    return self.isMoveValid(board, kingPos)

#looking for checkmate
def isCheckMate(self, board):
    if (self.color == 'white'):
        oppColor = 'black'
    else:
        oppColor = 'white'
    kingPos = getKingPos(board, oppColor)
    kingPiece = board.board[kingPos[0]][kingPos[1]]

    #check potential moves of king and see if each move can be conquered
    possibleKingMoves = kingPiece.getLegalMoves(board)
    posKingConq = [0]*len(possibleKingMoves)

    for row in board.board:
        for piece in row:
            if (piece == None):
                continue
            if (piece.color != self.color):
                continue
            for i in range(len(possibleKingMoves)):
                if (piece.isMoveValid(board, possibleKingMoves[i][1]) == True):
                    posKingConq[i] = 1
                #if we have 1's across board, done
                if (posKingConq.count(1) == len(posKingConq)):
                    self.gameOver = True
                    return True
    return False

def getLegalMovesBishop(self, board):
    legalMoves = []
    currPos = self.location
    newPos = list(currPos)

    #rook can only move along rows and cols
    for row in range(board.rows):
        if (row == currPos[0]):
            continue
        newPos[0] = row
        newPos[1] = currPos[1]
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])
    
    #bishop moves diagonally

    #move top left
    newPos[0] = currPos[0]
    newPos[1] = currPos[1]
    while(1):
        newPos[0] -= 1
        newPos[1] -= 1
        if (newPos[0] < 0 or newPos[1] < 0):
            break
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])

    #move top right
    newPos[0] = currPos[0]
    newPos[1] = currPos[1]
    while(1):
        newPos[0] -= 1
        newPos[1] += 1
        if (newPos[0] < 0 or newPos[1] < 0):
            break
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])
    
    #move bottom left
    newPos[0] = currPos[0]
    newPos[1] = currPos[1]
    while(1):
        newPos[0] += 1
        newPos[1] -= 1
        if (newPos[0] >= board.rows or newPos[1] < 0):
            break
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])
    
    #move bottom right
    newPos[0] = currPos[0]
    newPos[1] = currPos[1]
    while(1):
        newPos[0] += 1
        newPos[1] += 1
        if (newPos[0] >= board.rows or newPos[1] >= board.cols):
            break
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])

    return legalMoves

def getLegalMovesRook(self, board):
    legalMoves = []
    currPos = self.location
    newPos = list(currPos)

    #rook can only move along rows and cols
    for row in range(board.rows):
        if (row == currPos[0]):
            continue
        newPos[0] = row
        newPos[1] = currPos[1]
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])
    
    for col in range(board.cols):
        if (col == currPos[1]):
            continue
        newPos[0] = currPos[0]
        newPos[1] = col
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])
    
    return legalMoves

def getPieceValues(piece, color):
    #chess piece values from chessprogramming.org
    pawnValue = 10
    knightValue = 35
    bishopValue = 35
    rookValue = 50
    queenValue = 100
    kingValue = 900

    sign = 1
    if color == 'white':
        sign = -1
    
    if piece == 'Pawn':
        return (sign*pawnValue)
    elif piece == 'Knight':
        return (sign*knightValue)
    elif piece == 'Bishop':
        return (sign*bishopValue)
    elif piece == 'Rook':
        return (sign*rookValue)
    elif piece == 'Queen':
        return (sign*queenValue)
    else:
        return (sign*kingValue)

#given piece name, return table
def returnPieceEvaluationTable(piece, color):
    #using evaluation tables from chessprogramming.org
    #white (black = reverse of white)
    pwTable = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    pbTable = [elem for elem in pwTable][::-1]

    nwTable = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50],

    ]

    nbTable = [elem for elem in nwTable][::-1]

    bwTable = [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0 , 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20],
    ]

    bbTable = [elem for elem in bwTable][::-1]

    rwTable = [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20],
    ]

    rbTable = [elem for elem in rwTable][::-1]

    qwTable = [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-5, 0, 5, 5, 5, 5, 5, 0, -10],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ]

    qbTable = [elem for elem in qwTable][::-1]

    kwTable = [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20]
    ]

    kbTable = [elem for elem in kwTable][::-1]

    if (piece == 'Pawn'):
        if color == 'black':
            selectedTable = pbTable
        else:
            selectedTable = pwTable
    elif (piece == 'Rook'):
        if color == 'black':
            selectedTable = rbTable
        else:
            selectedTable = rwTable
    elif (piece == 'Knight'):
        if color == 'black':
            selectedTable = nbTable
        else:
            selectedTable = nwTable
    elif (piece == 'Bishop'):
        if color == 'black':
            selectedTable = bbTable
        else:
            selectedTable = bwTable
    elif (piece == 'Queen'):
        if color == 'black':
            selectedTable = qbTable
        else:
            selectedTable = qwTable
    else:
        if color == 'black':
            selectedTable = kbTable
        else:
            selectedTable = kwTable
    return selectedTable

#computer movements
def getPieceToMove(board, color):
    pieceList = ['Pawn', 'Knight', 'Bishop', 'Rook', 'Queen', 'King']

    while (1):

        randomPiece = random.choice(pieceList)
        selectedTable = returnPieceEvaluationTable(randomPiece, 'black')

        #find piece on board to move
        for row in board.board:
            for piece in row:
                if (piece == None):
                    continue
                if (piece.name == randomPiece) and (piece.color == color):
                    #find a position and try to move
                    for i in range (board.rows):
                        for j in range(board.cols):
                            if selectedTable[i][j] < 0:
                                continue
                            else:
                                newPos = (i, j)
                                if (piece.isMoveValid(board, newPos) == True):
                                    return (piece.location, newPos)
    print("couldn't move :( ")

def evaluatePosition(board):
    score = 0

    for i in range(board.rows):
        for j in range (board.cols):
            piece = board.board[i][j]
            if (piece != None):
                selectedTable = \
                returnPieceEvaluationTable(piece.name, piece.color)
                score += (getPieceValues(piece, piece.color) \
                            + selectedTable[i][j])
    return score

#########################
#MINIMAX
#########################
def minimax(board, depth, maxi, alpha, beta):
    if (depth == 0 or board.gameOver == True):
        return [evaluatePosition(board), None]
    if (maxi == True): #maximizer
        bestScore = -9999
        bestMove = []
        for move in board.getLegalMoves('black'):
            #make a deep copy of board
            newBoard = copy.deepcopy(board)
            oldPos = move[0]
            newPos = move[1]
            piece = newBoard.board[oldPos[0]][oldPos[1]]
            piece.moveTo(newBoard, newPos)

            scoreAndMoveList = minimax(newBoard, depth-1, False, alpha, beta)
            score = scoreAndMoveList[0]
            if (score > bestScore):
                bestScore = score
                bestMove = [oldPos, newPos]
            
            alpha = max(alpha, bestScore)
            if beta <= alpha:
                break

    else: #minimizer
        bestScore = 9999
        bestMove = []

        for move in board.getLegalMoves('white'):
            #make a deep copy of board
            newBoard = copy.deepcopy(board)
            oldPos = move[0]
            newPos = move[1]
            piece = newBoard.board[oldPos[0]][oldPos[1]]
            piece.moveTo(newBoard, newPos)

            scoreAndMoveList = minimax(newBoard, depth-1, True, alpha, beta)
            score = scoreAndMoveList[0]
            if (score < bestScore):
                bestScore = score
                bestMove = [oldPos, newPos]

            beta = min(beta, bestScore)
            
            if beta <= alpha:
                break

    return [bestScore, bestMove]


#computer move (no minimax)
def makeBotMove(board):
    location, newPos = getPieceToMove(board, 'black')
    piece = board.board[location[0]][location[1]]
    piece.moveTo(board, newPos)

#computer move with minimax
def makeBotMoveMiniMax(board):
    scoreAndMove = minimax(board, 3, True, -10000, 10000)
    score = scoreAndMove[0]
    move = scoreAndMove[1]
    piece = None

    if (move!= None):
        oldPos = move[0]
        newPos = move[1]
        piece = board.board[oldPos[0]][oldPos[1]]
    if (piece != None):
        piece.moveTo(board, newPos)

#########################
#CLASSES
#########################

#parent class + child class for each piece type
class Piece(object):
    def __init__(self, app, pos, color):
       #tuple to store row, col of current piece
       self.location = pos
       #piece color
       self.color = color
       #offset of 40 pixels for images
       self.offset = 40
    
    def moveTo(self, board, newPos):
        if self.isMoveValid(board, newPos) == False:
            return False
        #make the move
        board.board[self.location[0]][self.location[1]] = None
        position = list(self.location)
        position[0] = newPos[0]
        position[1] = newPos[1]
        self.location = tuple(position)
        
        #figure out conquered piece
        conqPiece = board.board[newPos[0]][newPos[1]]
        if (conqPiece != None):
            #update counts for each piece type
            if (conqPiece.color == 'white'):
                if conqPiece.name not in board.bConq:
                    board.bConq[conqPiece.name] = 1
                else:
                    board.bConq[conqPiece.name] += 1
            else:
                if conqPiece.name not in board.wConq:
                    board.wConq[conqPiece.name] = 1
                else:
                    board.wConq[conqPiece.name] += 1
            #if it's a king, game over
            if (isinstance(conqPiece, King) == True):
                board.gameOver = True
            #if it's a pawn, game over if all pawns are dead
            if (isinstance(conqPiece, Pawn) == True):
                if (conqPiece.color == 'white'):
                    board.nwPawn -= 1
                    if (board.nwPawn == 0):
                        board.gameOver = True
                else:
                    board.nbPawn -= 1
                    if (board.nbPawn == 0):
                        board.gameOver = True

        #update board
        board.board[newPos[0]][newPos[1]] = self

        #keep track of king's position
        if(isinstance(self, King) == True):
            if (self.color == 'white'):
                board.wKingPos = newPos
            else:
                board.bKingPos = newPos
        
        #check?
        board.check = isCheck(self, board)
        if (board.check == True):
            board.checkmate = isCheckMate(self, board)
            if (board.checkmate == True):
                board.gameOver = True
        return True
    
    def __isMoveValid__(self, board, newPos):
        if not newPos: 
            return False
        newRow = newPos[0]
        newCol = newPos[1]
        if ((newRow<0) or (newRow > board.rows-1) or (newCol < 0) 
            or (newCol > board.cols-1)):
            return False
        
        #can move only if empty/capturing opponent
        if board.board[newRow][newCol] == None:
            return True
        else:
            piece = board.board[newRow][newCol]
            if piece.color == self.color: 
                return False
        return True

    def __draw__(self, app, canvas):
        (startX, startY) = fromRowColToXY(self.location[0], self.location[1], 
                                            app)
        #add offset so piece is displayed properly
        startX += self.offset
        startY += self.offset
        if app.board.selectedPiece == self:
            if app.board.selectedPiecePosition != None:
                startX = app.board.selectedPiecePosition[0]
                startY = app.board.selectedPiecePosition[1]
        imgAnchor = CENTER
        canvas.create_image(startX, startY, 
                image = ImageTk.PhotoImage(self.image), anchor = imgAnchor)

#piece images from 
#https://commons.wikimedia.org/wiki/Category:PNG_chess_pieces/
class Pawn(Piece):
    def __init__(self, app, pos, color):
        super().__init__(app, pos, color)
        self.name = 'Pawn'
        if (self.color == 'white'):
            self.image = app.loadImage('wPawn.png')
        else:
            self.image = app.loadImage('bPawn.png')

    def draw(self, app, canvas):
        super().__draw__(app, canvas)

    def isMoveValid(self, board, newPos):
        if (super().__isMoveValid__(board, newPos) == False):
            return False
        #pawn can't capture directly in same column
        if (newPos[1] == self.location[1]):
            if (board.board[newPos[0]][newPos[1]] != None):
                return False
        if self.color == 'black':
            start = self.location[0]
            end = newPos[0]
        else:
            start = newPos[0]
            end = self.location[0]
        #pawn can't move sideways
        if (newPos[0] == self.location[0] and newPos[1] != self.location[1]):
            return False
        #can't move backwards
        if (start > end):
            return False
        #can't move more than 2 spaces
        elif (end-start > 2):
            return False
        elif (end-start == 2):
            if (self.color == 'white' and self.location[0] != 6):
                return False
            elif (self.color == 'black' and self.location[0] != 1):
                return False
        #check for pawn capture case where it moves diagonally
        if (end-start == 1) and (abs(newPos[1]-self.location[1]) == 1):
            piece = board.board[newPos[0]][newPos[1]]
            if (piece == None):
                return False
        return True
    
    def getLegalMoves(self, board):
        legalMoves = []
        currPos = self.location
        newPos = list(currPos)

        if (self.color == 'black'):
            #move down
            newPos[0] = currPos[0] + 1
            newPos[1] = currPos[1]
            if (self.isMoveValid(board, newPos) == True):
                legalMoves.append([currPos, tuple(newPos)])
            newPos[0] += 1
            if (self.isMoveValid(board, newPos) == True):
                legalMoves.append([currPos, tuple(newPos)])
        else: #moves up
            newPos[0] = currPos[0] - 1
            newPos[1] = currPos[1]
            if (self.isMoveValid(board, newPos) == True):
                legalMoves.append([currPos, tuple(newPos)])
            newPos[0] -= 1
            if (self.isMoveValid(board, newPos) == True):
                legalMoves.append([currPos, tuple(newPos)])
        #check for conquests
        if (self.color == 'black'):
            newPos[0] = currPos[0] + 1
        else:
            newPos[0] = currPos[0] - 1
        newPos[1] = currPos[1]+1
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])
        newPos[1] = currPos[1] - 1
        if (self.isMoveValid(board, newPos) == True):
            legalMoves.append([currPos, tuple(newPos)])
        return legalMoves
        
class Bishop(Piece): 
    def __init__(self, app, pos, color):
        super().__init__(app, pos, color)
        self.name = 'Bishop'
        if (self.color == 'white'):
            self.image = app.loadImage('wBishop.png')
        else:
            self.image = app.loadImage('bBishop.png')
    
    def isMoveValid(self, board, newPos):
        if (super().__isMoveValid__(board, newPos) == False):
            return False
        return isBishopMoveValid(self, board, newPos)
    
    def getLegalMoves(self, board):
        return getLegalMovesBishop(self, board)

    def draw(self, app, canvas):
        super().__draw__(app, canvas)

class Knight(Piece):
    def __init__(self, app, pos, color):
        super().__init__(app, pos, color)
        self.name = 'Knight'
        if (self.color == 'white'):
            self.image = app.loadImage('wKnight.png')
        else:
            self.image = app.loadImage('bKnight.png')

    def isMoveValid(self, board, newPos):
        if (super().__isMoveValid__(board, newPos) == False):
            return False
        validDirs = [(2,1), (1,2), (-2,1), (1, -2), (2, -1), (-1, 2), (-1, -2),\
            (-2,-1)]
        currRow = self.location[0]
        currCol = self.location[1]
        for x in validDirs:
            if ((currRow + x[0] == newPos[0]) and 
                (currCol + x[1] == newPos[1])):
                return True
        return False

    def getLegalMoves(self, board):
        legalMoves = []
        currPos = self.location
        newPos = list(currPos)

        #knight only has 8 possible moves
        validDirs = [(2,1), (1,2), (-2,1), (1, -2), (2, -1), (-1, 2), (-1, -2),\
            (-2,-1)]
        
        for move in validDirs:
            newPos[0] = currPos[0] + move[0]
            newPos[1] = currPos[1] + move[1]
            if (self.isMoveValid(board, newPos) == True):
                legalMoves.append([currPos, tuple(newPos)])
        
        return legalMoves


    def draw(self, app, canvas):
        super().__draw__(app, canvas)

class Rook(Piece): 
    def __init__(self, app, pos, color):
        super().__init__(app, pos, color)
        self.name = 'Rook'
        if (self.color == 'white'):
            self.image = app.loadImage('wRook.png')
        else:
            self.image = app.loadImage('bRook.png')

    def isMoveValid(self, board, newPos):
        if (super().__isMoveValid__(board, newPos) == False):
            return False
        return isRookMoveValid(self, board, newPos)

    def getLegalMoves(self, board):
        return getLegalMovesRook(self, board)
       
    def draw(self, app, canvas):
        super().__draw__(app, canvas)

class Queen(Piece): 
    def __init__(self, app, pos, color):
        super().__init__(app, pos, color)
        self.name = 'Queen'
        if (self.color == 'white'):
            self.image = app.loadImage('wQueen.png')
        else:
            self.image = app.loadImage('bQueen.png')
    
    def isMoveValid(self, board, newPos):
        if (super().__isMoveValid__(board, newPos) == False):
            return False
        if ((isBishopMoveValid(self, board, newPos) == False) and 
        (isRookMoveValid(self, board, newPos) == False)):
            return False
        return True

    def getLegalMoves(self, board): #moves like rook/bishop, has same legal move
        legalMoves = getLegalMovesBishop(self, board)
        legalMoves.extend(getLegalMovesRook(self, board))
        return legalMoves        
    
    def draw(self, app, canvas):
        super().__draw__(app, canvas)

class King(Piece):
    def __init__(self, app, pos, color):
        super().__init__(app, pos, color)
        self.name = 'King'
        if (self.color == 'white'):
            self.image = app.loadImage('wKing.png')
        else:
            self.image = app.loadImage('bKing.png')
    
    def isMoveValid(self, board, newPos):
        if (super().__isMoveValid__(board, newPos) == False):
            return False
        validDirs = [ (-1, -1), (-1, 0), (-1, +1),
                    ( 0, -1),          ( 0, +1),
                     (+1, -1), (+1, 0), (+1, +1) ]
        currRow = self.location[0]
        currCol = self.location[1]
        for x in validDirs:
            if ((currRow + x[0] == newPos[0]) and 
                (currCol + x[1] == newPos[1])):
                return True
        return False

    def getLegalMoves(self, board):
        legalMoves = []
        currPos = self.location
        newPos = list(currPos)

        #king only has 8 valid moves
        validDirs = [ (-1, -1), (-1, 0), (-1, +1),
                    ( 0, -1),          ( 0, +1),
                     (+1, -1), (+1, 0), (+1, +1) ]
        
        for move in validDirs:
            newPos[0] = currPos[0] + move[0]
            newPos[1] = currPos[1] + move[1]
            if (self.isMoveValid(board,newPos) == True):
                legalMoves.append([currPos, tuple(newPos)])

        return legalMoves

    def draw(self, app, canvas):
        super().__draw__(app, canvas)

def mouseMoved(app, event):
    if app.board.selectedPiece == None:
        app.board.selectedPiecePosition = None
    else:
        app.board.selectedPiecePosition = (event.x, event.y)

def mouseDragged(app, event):
    if app.board.selectedPiece == None:
        app.board.selectedPiecePosition = None
    else:
        app.board.selectedPiecePosition = (event.x, event.y)

def mousePressed(app, event):
    position = fromXYToRowCol(event.x, event.y, app)
    if not position:
        return None

    if app.board.gameOver == True:
        return None

    if (app.board.selectedPiece == None):
        selectedPiece = app.board.board[position[0]][position[1]]
        if (selectedPiece != None and selectedPiece.color == 
                                    app.board.currentPlayer):
            app.board.selectedPiece = selectedPiece
            app.board.legalMoves = selectedPiece.getLegalMoves(app.board)
    elif (app.board.selectedPiece.location == position): #unselect a piece
        app.board.selectedPiece = None
    else:
        if (app.board.selectedPiece.moveTo(app.board, position) == True):
            app.board.selectedPiece = None
            app.board.legalMoves = []
            if app.board.currentPlayer == 'white':
                app.board.wMoves += 1
                if (app.bot):
                    #simple AI move
                    makeBotMove(app.board)
                    app.board.bMoves += 1
                elif (app.miniMax): #miniMax move
                    makeBotMoveMiniMax(app.board)
                    app.board.bMoves += 1
                else:
                    #manual move
                    app.board.currentPlayer = 'black'
            else: #only if black is not a bot
                if (app.bot == False and app.miniMax == False):
                    app.board.bMoves += 1
                    app.board.currentPlayer = 'white'

def redrawAll(app, canvas): #visuals
    #user input
    if (app.inputNeeded == True):
        startScreen_redrawAll(app, canvas)
    else:
        app.board.draw(app, canvas)
        bString = "Black: " + "Moves = "+ str(app.board.bMoves) + ' Conq = ' + \
                    str(app.board.bConq)
        wString = "White: " + "Moves = "+ str(app.board.wMoves) + ' Conq = ' + \
                    str(app.board.wConq)
        canvas.create_text(app.margin, app.height/76 + 20, text = bString, 
                            anchor = W, font = ('Pursia', 12, 
                        'bold italic'), fill = 'black') 
        canvas.create_text(app.margin, app.height/76 + 40, 
            text = wString, anchor = W, font = ('Pursia', 12, 
                        'bold italic'), fill = 'black')
        canvas.create_text(app.width//2, app.height - app.margin + 30, 
        text = 'Press space bar to exit.', 
                font = ('Pursia', 12, 'bold italic'), fill = 'black')    
        if app.board.checkmate == True:
            canvas.create_text(app.width//2, app.height/76, 
            text = 'Checkmate: Game Over!', font = ('Pursia', 12, 
                        'bold italic'), 
            fill = 'black')
        elif app.board.check == True and app.board.gameOver == False:
            canvas.create_text(app.width//2, app.height/76, 
            text = 'Check!', font = ('Pursia', 12, 
                        'bold italic'), 
            fill = 'black')
        elif app.board.gameOver == True:
            canvas.create_text(app.width//2, app.height/76, 
            text = 'Game Over!', font = ('Pursia', 12, 
                        'bold italic'), 
            fill = 'black')

def startScreen_redrawAll(app, canvas):
    canvas.create_text(app.width//2, app.height//2, 
            text = 'WELCOME TO CHECKMATE! \n Press 1 to play against simple'
             + ' AI, \n press 2 to play 2 player mode, \npress 3 to play'
             + ' against the Minimax computer',
            font = ('Pursia', 30, 'bold italic'), fill = 'black')

def keyPressed(app, event):
    if (app.inputNeeded == True):
        if (event.key == '1'):
            app.bot = True
            app.inputNeeded = False
        elif (event.key == '3'):
            app.miniMax = True
            app.inputNeeded = False
        elif (event.key == '2'):
            app.inputNeeded = False
    else:
        if (event.key == 'Space'):
            app.inputNeeded = True
            appStarted(app)

def playChess(): #start game
    runApp(width = 760, height = 760)

def main():
    cs112_f21_week10_linter.lint()
    playChess()

if (__name__ == '__main__'):
    main()

