# Game-of-life-on-GPU
pytorch implementation of the game of life imagined by John Horton Conway (1937–2020) using a convolution kernel.

It occured to me that a simple kernel would easily allow to compute the game of life using a GPU so here it is.

Control:

- 0-8 aplhanum: Cell count needed to light one up (default 3).
- 0-8 Numpad: Cell count which will no die on next turn (default 2)
- F: Added an extra feat of a maximum life duration for each cell. Natural selection will show up.
- Z: Adds a chance of resurrection.
- E: Empty board
- R: Random board
- A: auto-restart if no cell remains. Like if you want to let the game run with the max life duration and expect some pattern to emerge.
- H: hide/show commands
- Space: pause / unpause

You can edit the screen resolution within the file, respectively x and y.

Left mouse click can turn on or off cells.

![image](https://github.com/user-attachments/assets/bfd8b2d8-9ffc-4b6e-aa1d-f8bd559c2a63)

Wonderful isn't it!
