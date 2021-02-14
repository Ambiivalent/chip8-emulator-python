from stack import Stack
import pygame
import numpy as np
import random

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

def CPUreset():
    """
    Resets CPU by initalizing all variables to default and loading file data and font data into memory
    Parameters:
        None
    """

    global memory, register, addI, PC, screen, st, FONT_add
    memory = np.zeros(0xFFF, dtype=np.uint8)                                                    # 0xFFF BYTES IN ARRAY
    register = np.zeros(16, dtype=np.uint8)                                                     # 16 REGISTERS IN CHIP 8
    addI = np.uint16(0)                                                                         # REGISTER I
    PC = np.uint16(0x200)                                                                       # STARTING POINT OF PROGRAM COUNTER
    screen = np.zeros((64,32) ,dtype=np.uint8)                                                  # 64x32 SCREEN
    st = Stack()                                                                                # 16 BYTE STACK THAT HOLDS NNN
                                                  

    # --------------- Begin File Loading ----------------------------------------------------------------------------------------------
    #file = np.fromfile("Chip-8 Games/Space Invaders [David Winter].ch8", dtype=np.uint8)
    #file = np.fromfile("Chip-8 Games/Pong (alt).ch8", dtype=np.uint8)
    #file = np.fromfile("Chip-8 Programs/chip8-test-rom.ch8", dtype=np.uint8)
    #file = np.fromfile("Chip-8 Programs/test_opcode.ch8", dtype=np.uint8)
    #file = np.fromfile("Chip-8 Programs/BC_test.ch8", dtype=np.uint8)
    for values in range(len(file)):
        memory[values + 0x200] = file[values]
    # --------------- Load Font -------------------------------------------------------------------------------------------------------
    counter = 0x50
    for letter in FONT:
        for codes in FONT[letter]:
            memory[counter] = codes
            counter += 1
        FONT_add[letter] = counter
# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------- ENCODE DECODE FUNCTION -----------------------------------------------------------------------------------------

def nextCode():
    """
    Calculates next instruction by combining two bytes of memory. Increments PC by two
    Parameters:
        None
    """
    global PC
    opCode = memory[PC]                                                                         # GRAB CURRENT INSTRUCTION
    opCode <<= 8                                                                                # SHIFT 8, PC IS 16 BIT WHILE CODE IS 8
    opCode |= memory[PC+1]                                                                      # GETTING NEXT BYTE
    PC += np.uint16(2)                                                                          # INCREMENT TWO INSTRUCTIONS
    return opCode                                                                               # RETURN OPCODE
def decode(opCode):
    """
    Takes current opcode and returns decoded value by checking MSB and LSB
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    NewOpCode = opCode & 0xF000
    if NewOpCode == 0x0000: NewOpCode = opCode & 0x00FF
    if NewOpCode == 0x8000: NewOpCode = opCode & 0xF00F
    if NewOpCode == 0xE000: NewOpCode = opCode & 0xF0FF
    if NewOpCode == 0xF000: NewOpCode = opCode & 0xF0FF
    return NewOpCode

# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------ OPCODE FUNCTION --------------------------------------------------------------------------------------------------

def returnNNN(opCode):
    """
    Returns from NNN and resets stack
    OPCODE: 00EE
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    PC = st.peek()                                                                              # RETURN FROM CALL
    st.pop()                                                                                    # REMOVE FROM STACK

# -------------------------------------------------------------------------------------------------------------------------------------

def displayClear(opCode):
    """
    Clears the current screen by resetting the array to 0
    OPCODE: 00E0
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global screen
    screen = np.zeros((64,32) ,dtype=np.uint8)                                                  # RESET SCREEN
    display.fill(BLACK)
# -------------------------------------------------------------------------------------------------------------------------------------

def jumpNNN(opCode):
    """
    Jumps to NNN of opCode
    OPCODE: 1NNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    PC = opCode & 0x0FFF                                                                        # JUMP TO NNN

# -------------------------------------------------------------------------------------------------------------------------------------

def callNNN(opCode):
    """
    Calls NNN of opCode and stores last instruction in stack
    OPCODE: 2NNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    st.push(PC)                                                                                 # ADD TO STACK
    PC = opCode & 0x0FFF                                                                        # CALL NNN

# -------------------------------------------------------------------------------------------------------------------------------------
def skipVxEqNN(opCode):
    """
    Skips the next instruction if VX equals NN.
    OPCODE: 3XNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    if register[(opCode & 0x0F00) >> 8] == (opCode & 0x00FF):
        PC += np.uint16(2)
# -------------------------------------------------------------------------------------------------------------------------------------
def skipVxNotNN(opCode):
    """
    Skips the next instruction if VX doesn't equal NN.
    OPCODE: 4XNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    if register[(opCode & 0x0F00) >> 8] != (opCode & 0x00FF):
        PC += np.uint16(2)
# -------------------------------------------------------------------------------------------------------------------------------------
def VxEqVy(opCode):
    """
    Skips the next instruction if VX equals VY.
    OPCODE: 5XY0
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    if register[(opCode & 0x0F00) >> 8] == register[(opCode & 0x00F0) >> 4]:
        PC += np.uint16(2)
# -------------------------------------------------------------------------------------------------------------------------------------

def setVX(opCode):
    """
    Sets Register VX to NN 
    OPCODE: 6XNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global register
    register[(opCode&0x0F00) >> 8] = (opCode & 0x00FF)                                          # SET VX IN REGISTER

# -------------------------------------------------------------------------------------------------------------------------------------

def addVX(opCode):
    """
    Adds NN to Register VX
    OPCODE: 7XNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global register
    register[(opCode&0x0F00) >> 8] += (opCode & 0x00FF)                                         # ADD VX IN REGISTER

# -------------------------------------------------------------------------------------------------------------------------------------
def setVxToVy(opCode):
    """
    Sets VX to the value of VY.
    OPCODE: 8XY0
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode&0x0F00) >> 8] = register[(opCode&0x00F0) >> 4]
# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def setVxOrVy(opCode):
    """
    Sets VX to VX or VY
    OPCODE: 8XY1
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode&0x0F00) >> 8] |= register[(opCode&0x00F0) >> 4]
# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def setVxAndVy(opCode):
    """
    Sets VX to VX and VY. 
    OPCODE: 8XY2
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode&0x0F00) >> 8] &= register[(opCode&0x00F0) >> 4]
# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def setVxXORVy(opCode):
    """
    Sets VX to VX xor VY. 
    OPCODE: 8XY3
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode&0x0F00) >> 8] ^= register[(opCode&0x00F0) >> 4]
# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VxPlusVy(opCode):
    """
    Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't.
    OPCODE: 8XY4
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    if register[(opCode&0x0F00) >> 8] >= 0xFF: register[0xF] = 1
    else: register[0xF] = 0
    register[(opCode&0x0F00) >> 8] += register[(opCode&0x00F0) >> 4]


# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VxSubVy(opCode):
    """
    VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
    OPCODE: 8XY5
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[0xF] = 1
    if  register[(opCode&0x0F00) >> 8] < register[(opCode&0x00F0) >> 4]: register[0xF] = 0
    try: register[(opCode&0x0F00) >> 8] -= register[(opCode&0x00F0) >> 4]
    except RuntimeWarning: pass

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VxShift1R(opCode):
    """
    Stores the least significant bit of VX in VF and then shifts VX to the right by 1
    OPCODE: 8XY6
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode & 0x0F00) >> 8] = register[(opCode & 0x00F0) >> 4]
    if register[(opCode & 0x0F00) >> 8] & 0x0F:
        register[0xF] = 1
    else: register[0xF] = 0
    register[(opCode & 0x0F00) >> 8] >>= 1

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VySubVx(opCode):
    """
    Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
    OPCODE: 8XY7
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[0xF] = 1
    if  register[(opCode&0x0F00) >> 8] > register[(opCode&0x00F0) >> 4]: register[0xF] = 0
    try: register[(opCode&0x0F00) >> 8] = register[(opCode&0x00F0) >> 4] - register[(opCode&0x0F00) >> 8]
    except RuntimeWarning: pass

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VxShift1L(opCode):
    """
    Stores the most significant bit of VX in VF and then shifts VX to the left by 1.
    OPCODE: 8XYE
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode & 0x0F00) >> 8] = register[(opCode & 0x00F0) >> 4]
    if register[(opCode & 0x0F00) >> 8] & 0xF0:
        register[0xF] = 1
    else: register[0xF] = 0
    register[(opCode & 0x0F00) >> 8] <<= 1

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def skipVxEqVy(opCode):
    """
    Skips the next instruction if VX doesn't equal VY. (Usually the next instruction is a jump to skip a code block)
    OPCODE: 9XY0
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global PC
    if register[(opCode & 0x0F00) >> 8] != register[(opCode & 0x00F0) >> 4]:
        PC += np.uint16(2)

# -------------------------------------------------------------------------------------------------------------------------------------

def setI(opCode):
    """
    Set Register I to NNN
    OPCODE: ANNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global addI
    addI = opCode & 0x0FFF                                                                      # SET REGISTER I

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def jumpNNNV0(opCode):
    """
    Jumps to the address NNN plus V0.
    OPCODE: BNNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global PC
    PC = (opCode & 0x0FFF) + register[0]

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def randNumVx(opCode):
    """
    Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.
    OPCODE: CXNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode & 0x0F00) >> 8] = random.randint(0,255) & (opCode & 0x00FF)

# -------------------------------------------------------------------------------------------------------------------------------------

def drawScreen(opCode):
    """
    Draws sprite data from register I using coordinates from Register VX and Register VY
    with sprite height of N.
    OPCODE: DXYN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global register, screen
    x = (opCode & 0x0F00) >> 8                                                                  # GET X FROM DXYN
    y = (opCode & 0x00F0) >> 4                                                                  # GET Y FROM DXYN
    OriginalX,OriginalY = register[x], register[y]                                              # GET X,Y FROM REGISTER
    register[0xF] = 0                                                                           # SET VF TO 0

    for height in range(opCode & 0x000F):                                                       # LOOP 0 -> N
        spriteData = memory[addI + height]                                                      # GET SPRITE FROM MEMORY[ADDRESS I + OFFSET]
        y = (OriginalY + height) % 32                                                           # INCREMENT Y
        for spriteBit in range(8):                                                              # LOOP EACH BIT IN BYTE
            if spriteData & (0x80 >> spriteBit):                                                # GRAB MSB
                x = (OriginalX + spriteBit) % 64                                                # INCREMENT X
                if screen[x][y]: register[0xF] |= 1                                             # CHECK IF SPRITE COLLIDE
                screen[x][y] ^= 1                                                               # FLIP SPRITE
                if screen[x][y]:                                                                # CHECK IF SPRITE IS ON
                    pygame.draw.rect(display, WHITE, pygame.Rect((x*10,y*10), (10,10)))         # DRAW PIXEL

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VXpressed(opCode):
    """
    Skips the next instruction if the key stored in VX is pressed. (Usually the next instruction is a jump to skip a code block)
    OPCODE: EX9E
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global PC
    x = (opCode & 0x0F00) >> 8
    for keys in KEYBOARD:
        print(register[x])
        raise SystemExit
        if keys == register[x]:
            if current_key[KEYBOARD[keys]]: 
                PC += np.uint16(2)
                break

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VXnotPressed(opCode):
    """
    Skips the next instruction if the key stored in VX isn't pressed. (Usually the next instruction is a jump to skip a code block)
    OPCODE: EXA1
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global PC
    x = (opCode & 0x0F00) >> 8
    for keys in KEYBOARD:
        if keys == register[x]:
            if current_key[KEYBOARD[keys]] == 0: 
                PC += np.uint16(2)
                break

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VxtoTimer(opCode):
    """
    Sets VX to the value of the delay timer.
    OPCODE: FX07
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode & 0x0F00) >> 8] = delay_timer

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def getKeyWait(opCode):
    """
    A key press is awaited, and then stored in VX. (Blocking Operation. All instruction halted until next key event)
    OPCODE: FX0A
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global PC, register
    press = False
    for keys in KEYBOARD:
        if current_key[KEYBOARD[keys]]:
            press = True
            register[(opCode & 0x0F00) >> 8] = keys
    if not press: PC -= 2

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def timerToVx(opCode):
    """
    Sets the delay timer to VX.
    OPCODE: FX15
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global delay_timer
    delay_timer = register[(opCode & 0x0F00) >> 8]

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def soundToVx(opCode):
    """
    Sets the sound timer to VX.
    OPCODE: FX18
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global sound_timer
    sound_timer = register[(opCode & 0x0F00) >> 8]

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def VxPlusI(opCode):
    """
    Adds VX to I. VF is not affected.[c]
    OPCODE: FX1E
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global addI
    addI = addI + register[(opCode & 0x0F00) >> 8]
    addI = np.uint16(addI)

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def ItoFont(opCode):
    """
    Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
    OPCODE: FX29
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global addI
    addI = FONT_add[(opCode & 0x0F00) >> 8]
    
# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def setBCD(opCode):
    """
    Stores the binary-coded decimal representation of VX, with the most significant of three digits at the address in I, the middle digit 
    at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of VX, place the hundreds 
    digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.)
    OPCODE: FX33
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global memory
    x = register[(opCode & 0x0F00) >> 8]
    memory[addI] = (x//100)
    memory[addI+1] = (x%100) // 10
    memory[addI+2] = x % 10

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def regDump(opCode):
    """
    Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, 
    but I itself is left unmodified    
    OPCODE: FX55
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global memory
    for values in range(((opCode & 0x0F00) >> 8) + 1):
        memory[addI + values] = register[values]

# -------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------------------
def regLoad(opCode):
    """
    Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 
    for each value written, but I itself is left unmodified    
    OPCODE: FX65
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    for values in range(((opCode & 0x0F00) >> 8) + 1):
        register[values] = memory[addI + values]

# -------------------------------------------------------------------------------------------------------------------------------------
# ---------------VARIABLE DECLARATION--------------------------------------------------------------------------------------------------

memory, register, addI, PC, screen = (0,0,0,0,0)
st = Stack()
delay_timer = 0
sound_timer = 0

WHITE, BLACK = (250,250,250),(0,0,0)

OPCODES =           {0x00E0: displayClear, 0x00EE: returnNNN,  0x1000: jumpNNN,    0x2000: callNNN,
                     0x3000: skipVxEqNN,   0x4000: skipVxNotNN,0x5000: VxEqVy,     0x6000: setVX,     
                     0x7000: addVX,        0x8000: setVxToVy  ,0x8001: setVxOrVy,  0x8002: setVxAndVy,
                     0x8003: setVxXORVy,   0x8004: VxPlusVy,   0x8005: VxSubVy,    0x8006: VxShift1R,
                     0x8007: VySubVx,      0x800E: VxShift1L,  0x9000: skipVxEqVy, 0xA000: setI,    
                     0xB000: jumpNNNV0,    0xC000: randNumVx,  0xD000: drawScreen, 0xE00E: VXpressed,
                     0xE001: VXnotPressed, 0xF007: VxtoTimer,  0xF00A: getKeyWait, 0xF015: timerToVx,
                     0xF018: soundToVx,    0xF01E: VxPlusI,    0xF029: ItoFont,    0xF033: setBCD,   
                     0xF055: regDump,      0xF065: regLoad                                            }

FONT = {
                     0x0: (0xF0, 0x90, 0x90, 0x90, 0xF0),
                     0x1: (0x20, 0x60, 0x20, 0x20, 0x70),
                     0x2: (0xF0, 0x10, 0xF0, 0x80, 0xF0),
                     0x3: (0xF0, 0x10, 0xF0, 0x10, 0xF0),
                     0x4: (0x90, 0x90, 0xF0, 0x10, 0x10),
                     0x5: (0xF0, 0x80, 0xF0, 0x10, 0xF0),
                     0x6: (0xF0, 0x80, 0xF0, 0x90, 0xF0),
                     0x7: (0xF0, 0x10, 0x20, 0x40, 0x40),
                     0x8: (0xF0, 0x90, 0xF0, 0x90, 0xF0),
                     0x9: (0xF0, 0x90, 0xF0, 0x10, 0xF0),
                     0xA: (0xF0, 0x90, 0xF0, 0x90, 0x90),
                     0xB: (0xE0, 0x90, 0xE0, 0x90, 0xE0),
                     0xC: (0xF0, 0x80, 0x80, 0x80, 0xF0),
                     0xD: (0xE0, 0x90, 0x90, 0x90, 0xE0),
                     0xE: (0xF0, 0x80, 0xF0, 0x80, 0xF0),
                     0xF: (0xF0, 0x80, 0xF0, 0x80, 0x80)
}
KEYBOARD = {
                     0x1: pygame.K_1, 0x2: pygame.K_2, 0x3: pygame.K_3, 0xC: pygame.K_4,
                     0x4: pygame.K_q, 0x5: pygame.K_w, 0x6: pygame.K_e, 0xD: pygame.K_r,
                     0x7: pygame.K_a, 0x8: pygame.K_s, 0x9: pygame.K_d, 0xE: pygame.K_f,
                     0xA: pygame.K_z, 0x0: pygame.K_x, 0xB: pygame.K_c, 0xF: pygame.K_v,
}
FONT_add = {}
# -------------------------------------------------------------------------------------------------------------------------------------
# -----------------MAIN LOOP-----------------------------------------------------------------------------------------------------------

CPUreset()
playing = True
pygame.init()
display = pygame.display.set_mode((640,320))
clock = pygame.time.Clock()

while (playing):
    current_key = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    currentCode = nextCode()
    decoded = decode(currentCode)
    if currentCode != 0: print("C------>" + hex(currentCode))
    if decoded != 0: print("D------>" + hex(decoded))
    print(f"PC: {PC}")
   # if decoded not in OPCODES: raise SystemExit
    OPCODES.get(decoded, lambda x: None )(currentCode)
    if not (pygame.time.get_ticks() % 1000):
        if delay_timer > 0: delay_timer -= 60
        if sound_timer > 0: sound_timer -= 60
    #print(f"REGISTER: {register}")
    pygame.display.flip()
    clock.tick(40)

# -------------------------------------------------------------------------------------------------------------------------------------