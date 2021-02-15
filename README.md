# chip8 emulator python
 A WIP chip-8 emulator for python using numpy and pygame

To use, install numpy and pygame

```
pip install numpy
pip install pygame
```

Change line 33 in chip.py to a ROM directory 
```python
file = np.fromfile("{YOUR GAME NAME HERE}.ch8", dtype=np.uint8)
```
