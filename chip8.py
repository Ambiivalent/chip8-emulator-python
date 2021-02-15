from stack import Stack
import pygame, pygame.midi
import numpy as np
import random
# -------------------------------------------------------------------------------------------------------------------------------------
# THIS IS A CHIP-8 PYTHON EMULATOR THAT DEPENDS ON PYGAME AND NUMPY
# REFERENCES: 
# >>> https://en.wikipedia.org/wiki/CHIP-8
# >>> https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
# >>> https://www.reddit.com/r/EmuDev/
# CREATED BY KID FRIENDLY
# DISCORD: Kid Friendly#9195
# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

def CPUreset():
    """
    Resets CPU by initalizing all variables to default and loading file data and font data into memory
    Parameters:
        None
    """

    global memory, register, addI, PC, screen, st
    memory = np.zeros(0xFFF, dtype=np.uint8)                                                    # 0xFFF BYTES IN ARRAY
    register = np.zeros(16, dtype=np.uint8)                                                     # 16 REGISTERS IN CHIP 8
    addI = np.uint16(0)                                                                         # REGISTER I
    PC = np.uint16(0x200)                                                                       # STARTING POINT OF PROGRAM COUNTER
    screen = np.zeros((64,32) ,dtype=np.uint8)                                                  # 64x32 SCREEN
    st = Stack()                                                                                # 16 BYTE STACK THAT HOLDS NNN
                                                  

    # --------------- Begin File Loading ----------------------------------------------------------------------------------------------
    #file = np.fromfile("games/Space Invaders [David Winter] (alt).ch8", dtype=np.uint8)        # TEST GAME 1 ->> NOT PASSED   
    file = np.fromfile("games/Pong (alt).ch8", dtype=np.uint8)                                  # TEST GAME 2 ->> PASS
    #file = np.fromfile("programs/chip8-test-rom.ch8", dtype=np.uint8)                          # TEST ROM    ->> PASS
    #file = np.fromfile("programs/test_opcode.ch8", dtype=np.uint8)                             # TEST ROM    ->> PASS
    #file = np.fromfile("programs/BC_test.ch8", dtype=np.uint8)                                 # TEST ROM    ->> PASS

    for values in range(len(file)):
        memory[values + 0x200] = file[values]                                                   # LOAD FILE INTO MEMORY
    # --------------- Load Font -------------------------------------------------------------------------------------------------------
    counter = 0x0                                                                               # LOAD FONT INTO MEMORY 
    for letter in FONT:
        for codes in FONT[letter]:
            memory[counter] = codes
            counter += 1
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
    if NewOpCode == 0x0000: NewOpCode = opCode & 0x00FF                                         # CHECK 0x0 CODES
    if NewOpCode == 0x8000: NewOpCode = opCode & 0xF00F                                         # CHECK 0x8 CODES
    if NewOpCode == 0xE000: NewOpCode = opCode & 0xF0FF                                         # CHECK 0xE CODES
    if NewOpCode == 0xF000: NewOpCode = opCode & 0xF0FF                                         # CHECK 0xF CODES
    return NewOpCode

# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------ OPCODE FUNCTION --------------------------------------------------------------------------------------------------

def displayClear(opCode):
    """
    Clears the current screen by resetting the array to 0
    OPCODE: 00E0
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global screen
    screen = np.zeros((64,32) ,dtype=np.uint8)                                                 

# -------------------------------------------------------------------------------------------------------------------------------------

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

def jumpNNN(opCode):
    """
    Jumps to NNN of opCode
    OPCODE: 1NNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    PC = opCode & 0x0FFF                                                                         # JUMP TO NNN

# -------------------------------------------------------------------------------------------------------------------------------------

def callNNN(opCode):
    """
    Calls NNN of opCode and stores last instruction in stack
    OPCODE: 2NNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    st.push(PC)                                                                                  # ADD TO STACK
    PC = opCode & 0x0FFF                                                                         # CALL NNN

# -------------------------------------------------------------------------------------------------------------------------------------
def skipVxEqNN(opCode):
    """
    Skips the next instruction if VX equals NN.
    OPCODE: 3XNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global PC
    if register[(opCode & 0x0F00) >> 8] == (opCode & 0x00FF):                                    # CHECK EQUALITY WITH NN
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
    if register[(opCode & 0x0F00) >> 8] != (opCode & 0x00FF):                                    # CHECK INEQUALITY WITH NN
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
    if register[(opCode & 0x0F00) >> 8] == register[(opCode & 0x00F0) >> 4]:                      # CHECK EQUALITY WITH VY
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
    register[(opCode&0x0F00) >> 8] = (opCode & 0x00FF)                                            # SET VX IN REGISTER

# -------------------------------------------------------------------------------------------------------------------------------------

def addVX(opCode):
    """
    Adds NN to Register VX
    OPCODE: 7XNN
    Parameters:
        opCode: (16 bit hexadecimal number)
    """
    global register
    register[(opCode&0x0F00) >> 8] += (opCode & 0x00FF)                                           # ADD VX IN REGISTER

# -------------------------------------------------------------------------------------------------------------------------------------
def setVxToVy(opCode):
    """
    Sets VX to the value of VY.
    OPCODE: 8XY0
    Parameters:
        opCode: (16 bit hexadecimal number)
    """ 
    global register
    register[(opCode&0x0F00) >> 8] = register[(opCode&0x00F0) >> 4]                                # SET VX TO VY
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
    register[(opCode&0x0F00) >> 8] |= register[(opCode&0x00F0) >> 4]                                # VX = VX OR VY 
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
    register[(opCode&0x0F00) >> 8] &= register[(opCode&0x00F0) >> 4]                                # VX = VX AND VY
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
    register[(opCode&0x0F00) >> 8] ^= register[(opCode&0x00F0) >> 4]                                 # VX = VX XOR VY
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
    if register[(opCode&0x0F00) >> 8] >= 0xFF: register[0xF] = 1                                     # CHECK FOR CARRY
    else: register[0xF] = 0
    register[(opCode&0x0F00) >> 8] += register[(opCode&0x00F0) >> 4]                                 # ADD VX VY 

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
    if  register[(opCode&0x0F00) >> 8] < register[(opCode&0x00F0) >> 4]: register[0xF] = 0            # CHECK FOR BORROW
    try: register[(opCode&0x0F00) >> 8] -= register[(opCode&0x00F0) >> 4]                             # IGNORE UNDERFLOW
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
    register[0xF] = register[(opCode & 0x0F00) >> 8] & 0x1                                             # VF = LSB
    register[(opCode & 0x0F00) >> 8] >>= 1                                                             # SHIFT VX RIGHT
    register[(opCode & 0x0F00) >> 8] &= 1                                                              # FIX SIGNED SHIFT


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
    if  register[(opCode&0x0F00) >> 8] > register[(opCode&0x00F0) >> 4]: register[0xF] = 0             # CHECK FOR BORROW
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
    register[0xF] = register[(opCode & 0x0F00) >> 8] >> 7                                             # VF = MSB
    register[(opCode & 0x0F00) >> 8] <<= 1                                                            # SHIFT LEFT 1
    register[(opCode & 0x0F00) >> 8] &= 1                                                             # FIX SIGNED SHIFT

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
    if register[(opCode & 0x0F00) >> 8] != register[(opCode & 0x00F0) >> 4]:                          # CHECK INEQUALITY VX VY
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
    addI = opCode & 0x0FFF                                                                            # SET REGISTER I

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
    PC = (opCode & 0x0FFF) + register[0]                                                              # JUMP NNN + V0

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
    register[(opCode & 0x0F00) >> 8] = random.randint(0,255) & (opCode & 0x00FF)                      # RANDOM NUM & NN 

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
    x = (opCode & 0x0F00) >> 8                                                                        # GET X FROM DXYN
    y = (opCode & 0x00F0) >> 4                                                                        # GET Y FROM DXYN
    OriginalX,OriginalY = register[x], register[y]                                                    # GET X,Y FROM REGISTER
    register[0xF] = 0                                                                                 # SET VF TO 0

    for height in range(opCode & 0x000F):                                                             # LOOP 0 -> N
        spriteData = memory[addI + height]                                                            # GET SPRITE FROM MEMORY[ADDRESS I + OFFSET]
        y = (OriginalY + height) % 32                                                                 # INCREMENT Y
        for spriteBit in range(8):                                                                    # LOOP EACH BIT IN BYTE
            if spriteData & (0x80 >> spriteBit):                                                      # GRAB MSB
                x = (OriginalX + spriteBit) % 64                                                      # INCREMENT X
                if screen[x][y]: register[0xF] |= 1                                                   # CHECK IF SPRITE COLLIDE
                screen[x][y] ^= 1                                                                     # FLIP SPRITE

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
    x = (opCode & 0x0F00) >> 8                                                                        # GET X
    for keys in KEYBOARD:                                                                          
        if keys == register[x]:                                                                       # IF MATCHING KEY
            if current_key[KEYBOARD[keys]]: 
                PC += np.uint16(2)                                                                    # SKIP
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
    x = (opCode & 0x0F00) >> 8                                                                        # GET X
    for keys in KEYBOARD:
        if keys == register[x]:                                                                       # IF MATCHING KEY
            if current_key[KEYBOARD[keys]] == 0:                                                      # CHECK NOT PRESSED
                PC += np.uint16(2)                                                                    # SKIP
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
    register[(opCode & 0x0F00) >> 8] = delay_timer                                                    # VX TO DELAY TIMER

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
    press = False                                                                                     # STATE OF KEYSTROKE
    for keys in KEYBOARD:
        if current_key[KEYBOARD[keys]]:                                                               # CHECK IF ON
            press = True
            register[(opCode & 0x0F00) >> 8] = keys                                                   # VX TO KEYSTROKE
    if not press: PC -= 4                                                                             # ELSE SKIP

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
    delay_timer = register[(opCode & 0x0F00) >> 8]                                                    # DELAY TIMER TO VX

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
    sound_timer = register[(opCode & 0x0F00) >> 8]                                                    # SOUND TIMER TO VX

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
    addI = addI + register[(opCode & 0x0F00) >> 8]                                                    # ADD I + VX
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
    addI = register[(opCode & 0x0F00) >> 8] * 5                                                       # ADD I TO VX * 5 (5 DATA IN FONT)
    
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
    x = register[(opCode & 0x0F00) >> 8]                                                              # GET X
    memory[addI] =(x%1000) /100                                                                       # GET 100s PLACE VALUE
    memory[addI+1] = (x%100) / 10                                                                     # GET 10s PLACE VALUE
    memory[addI+2] = x % 10                                                                           # GET 1s PLACE VALUE

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
        memory[addI + values] = register[values]                                                      # SET MEMORY AT I TO V0-VX

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
        register[values] = memory[addI + values]                                                     # SET V0-VX TO MEMORY AT I

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------DEBUG FUNCTIONS---------------------------------------------------------------------------------------------------------

def print_debug():
    """
    Debug function that prints all important information for the emulation. Function will only run if debug = True.
    Uncomment certain values as needed.
    Parameters:
        None
    """
    if currentCode != 0: print("C------>" + hex(currentCode))
    if decoded != 0: print("D------>" + hex(decoded))
    print(f"PC: {PC}")
    #if decoded not in OPCODES: raise SystemExit
    #print(f"REGISTER: {register}")
    #print(f"DELAY TIMER: {delay_timer}")

# -------------DRAW FUNCTIONS----------------------------------------------------------------------------------------------------------

def render():
    """
    Renders all values of screen to display. 
    Parameters:
        None
    """
    colour = BLACK
    for x in range(len(screen)):
        for y in range(len(screen[0])):
            if screen[x][y]: colour = WHITE
            else: colour = BLACK
            pygame.draw.rect(display, colour,pygame.Rect((x*10, y*10), (10,10)))

# -------------VARIABLE DECLARATION----------------------------------------------------------------------------------------------------

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
                     0xB000: jumpNNNV0,    0xC000: randNumVx,  0xD000: drawScreen, 0xE09E: VXpressed,
                     0xE0A1: VXnotPressed, 0xF007: VxtoTimer,  0xF00A: getKeyWait, 0xF015: timerToVx,
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
# -------------------------------------------------------------------------------------------------------------------------------------
# -----------------MAIN LOOP-----------------------------------------------------------------------------------------------------------

CPUreset()                                                                                       # INITIALIZE CPU
pygame.init()                                                                                    # INITALIZE PYGAME
pygame.midi.init()                                                                               # INITALIZE SOUNDS

playing = True
debug = False

display = pygame.display.set_mode((640,320))                                                     # 640x320 DISPLAY
clock = pygame.time.Clock()                                                                      # PYGAME CLOCK
fx = pygame.midi.Output(0)
fx.set_instrument(113)

pygame.display.set_caption("CHIP-8 EMULATOR")

while (playing):
    current_key = pygame.key.get_pressed()                                                       # GRAB CURRENT KEYSTROKE
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False                                            # CHECK FOR QUITTING

    currentCode = nextCode()                                                                     # GRAB NEXT INSTRUCTION
    decoded = decode(currentCode)                                                                # DECODE NEXT INSTRUCTION

    if debug: print_debug()

    OPCODES.get(decoded, lambda x: None )(currentCode)                                           # LINK INSTRUCTION TO FUNCTION
    render()                                                                                     # RENDER SCREEN

    if delay_timer > 0: delay_timer -= 1                                                         # DECREMENT DELAY TIMER
    if sound_timer > 0:                                                                          # DECREMENT SOUND TIMER
        sound_timer -= 1
        fx.note_on(64,127)                                                                       # PLAY SOUND FX

    pygame.display.flip()                                                                        # UPDATE DISPLAY
    clock.tick(1000)                                                                             # TICK GAME CLOCK
# -------------------------------------------------------------------------------------------------------------------------------------