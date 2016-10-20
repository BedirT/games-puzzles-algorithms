# classic ttt: 3x3 board     RBH 2016
import numpy as np

class Cell: # each cell is one of these: empty, x, o
  n,e,x,o,chars = 9,0,1,2,'.xo' 

# each board position 0,1,2, so we can think of a board
#   position as a 9-digit number base 3
# so number of states is same as max 9-digit base_3 integer
ttt_states = 19683  # 3**Cell.n
powers_of_3 = np.array( # for converting position to base_3 int
  [1, 3, 9, 27, 81, 243, 729, 2187, 6561], dtype=np.int16)

def board_to_int(B):
  return sum(B*powers_of_3) # numpy multiplies vectors componentwise

# consider all possible symmetric positions, return min
def hash(L): # using numpy array indexing here
  return min([board_to_int( L[Syms[j]] ) for j in range(8)])

# convert from integer for board position
def base_3( y ): 
  assert(y <= ttt_states)
  L = [0]*Cell.n
  for j in range(9):
    y, L[j] = divmod(y,3)
    if y==0: break
  return np.array( L, dtype = np.int16)

# input-output ################################################
def char_to_cell(c): 
  return Cell.chars.index(c)

escape_ch   = '\033['
colorend    =  escape_ch + '0m'
textcolor   =  escape_ch + '0;37m'
stonecolors = (textcolor,\
               escape_ch + '0;35m',\
               escape_ch + '0;32m',\
               textcolor)

def genmoverequest(cmd):
  cmd = cmd.split()
  invalid = (False, None, '\n invalid genmove request\n')
  if len(cmd)==2:
    x = Cell.chars.find(cmd[1][0])
    if x == 1 or x == 2:
      return True, cmd[1][0], ''
  return invalid

def printmenu():
  print('  x b2         play X b 2')
  print('  o e3         play O e 3')
  print('  . a2         erase a 2')
  print('  g x/o           genmove')
  print('  [return]           quit')

def showboard(psn):
  def paint(s):  # s   a string
    if len(s)>1 and s[0]==' ': 
     return ' ' + paint(s[1:])
    x = Cell.chars.find(s[0])
    if x > 0:
      return stonecolors[x] + s + colorend
    elif s.isalnum():
      return textcolor + s + colorend
    return s

  pretty = '\n   ' 
  for c in range(3): # columns
    pretty += ' ' + paint(chr(ord('a')+c))
  pretty += '\n'
  for j in range(3): # rows
    pretty += ' ' + paint(str(1+j)) + ' '
    for k in range(3): # columns
      pretty += ' ' + paint(Cell.chars[psn.brd[rc_to_psn(j,k)]])
    pretty += '\n'
  print(pretty)
  print('hash ',hash(psn.brd),'  empty cells', psn.num_empty())

### position tuples of 8 symmetric ttt board permutations
Syms = np.array(( (0,1,2,3,4,5,6,7,8),
         (0,3,6,1,4,7,2,5,8),
         (2,1,0,5,4,3,8,7,6),
         (2,5,8,1,4,7,0,3,6),
         (8,7,6,5,4,3,2,1,0),
         (8,5,2,7,1,4,6,3,0),
         (6,7,8,3,4,5,0,1,2),
         (6,3,0,7,4,1,8,5,2)
         ), dtype = np.int8)

Win_lines = np.array(( # psn tuples of 8 winning lines
  (0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)
  ), dtype=np.int8)

# board positions
#   0 1 2
#   3 4 5
#   6 7 8
def rc_to_psn(r,c): return r*3 + c

class Position: # ttt board with x,o,e cells
  def solve(self):
    self.static_win = np.array( [0]*ttt_states, dtype = np.int8)
    tmp = self.brd
    for j in range(len(self.static_win)):
      self.brd = base_3(j)
      bitset = 0               
      if self.has_win(Cell.x): bitset += 2
      if self.has_win(Cell.o): bitset += 1
      self.static_win[j] = bitset
      # bitset 3: both    win
      # bitset 2: x only  win
      # bitset 1: o only  win
      # bitset 0: neither win
    self.brd = tmp
    
  def legal_moves(self):
    L = []
    for j in range(Cell.n):
      if self.brd[j]==Cell.e: 
        L.append(j)
    return L

  def asym_moves(self,cell):
    L = self.legal_moves()
    H, X = [], []
    for j in range(len(L)):
      p = L[j]
      #print('move to cell',p,end='')
      self.brd[p] = cell
      h = hash(self.brd)
      if h not in H:
        H.append(h)
        X.append(j)
      #print(h, H, X)
      self.brd[p] = Cell.e
    L = np.array(L)
    X = np.array(X)
    return L[X]

  def num_empty(self):
    return (self.brd == Cell.e).sum()
  
  def has_win(self, z):
    win_found = False
    for t in Win_lines:
      if (self.brd[t[0]] == z and
          self.brd[t[1]] == z and
          self.brd[t[2]] == z):
        return True
    return False

  def game_over(self):
    win_found = False
    for z in (Cell.x, Cell.o):
      if (self.has_win(z)):
        print('\n  game_over: ',Cell.chars[z],'wins\n')
        return True
    return False

  def putstone(self, row, col, color):
    self.brd[rc_to_psn(row,col)] = color

  def __init__(self, y):
    self.brd = base_3(y)
    self.static_win = None

  def genmove(self, request):
    if request[0]:
      print(' genmove coming soon')
    else:
      print(request[2])

  def makemove(self, cmd):
    parseok, cmd = False, cmd.split()
    if len(cmd)==2:
      ch = cmd[0][0]
      if ch in Cell.chars:
        q, n = cmd[1][0], cmd[1][1:]
        if q.isalpha() and n.isdigit():
          x, y = int(n) - 1, ord(q)-ord('a')
          if x>=0 and x < 3 and y>=0 and y < 3:
            self.putstone(x, y, char_to_cell(ch))
            return
          else: print('\n  coordinate off board')
    print('  ... ? ... sorry ...\n')

def playgame():
  p = Position(0)
#  p.solve()
  while True:
    showboard(p)
    print('legal moves', p.legal_moves(), p.asym_moves(Cell.x))
    if p.game_over():
      pass
    cmd = input(' ')
    if len(cmd)==0:
      print('\n ... adios :)\n')
      return
    if cmd[0][0]=='h':
      printmenu()
    elif cmd[0][0]=='g':
      p.genmove(genmoverequest(cmd))
    elif (cmd[0][0] in Cell.chars):
        p.makemove(cmd)
    else:
      print('\n try again \n')

playgame()
