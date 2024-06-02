# progression-graph
Progression graph tool for games

## Screenshots
![](https://github.com/d-002/progression-graph/assets/69427207/ba704b64-ad56-4a3e-90d5-f2dc26d2c171)
![](https://github.com/d-002/progression-graph/assets/69427207/2c4a48c5-ea13-4f6f-9a83-974eb9726fbf)
![](https://github.com/d-002/progression-graph/assets/69427207/19dc0699-c994-44f0-90d1-7bf9309813e6)

## Requirements
- python>=3.10
- pygame>=2.3.0

## Features
- Create nodes, add text and images to them, drag them around. The text is displayed on hover for lower ranked (sized) nodes, and always for higher ranks.
- Link these nodes, links have different sizes depending on the max rank of the connected nodes
- Nodes can have different ranks, determining their size
- Save and open intuitively formatted files (zip-like format)
- Visualize the tree, export into png file
- Nodes have a state: to do, doing, completed, with different colors. You can cycle them while selected, and their state updates the connected links.

## Controls
Click on an object to select it, hit Escape to unselect it. Escape can also be used to cancel creating a link.

Click and hold right click to select multiple nodes

When a node is selected, press S to cycle its state, R to cycle its rank, or create a link with L and click another node to connect them.

Options will appear on top of the screen dependoing on the selection. Hit the corresponding keys to execute the different actions.

When no object is selected, you can zoom in and out with the mouse wheel, and reset the zoom with Z.  
S saves the current file, W saves to a new file, N opens a new file, O opens a file.

Pressing Delete will detach the image from a point, or remove its text, or delete the point if there is nothing in it.  
You can also remove the text or the image from a point by adding an empty text or hitting Cancel in the input popup.

You can export the graphs you created with E (export without background) and F (filled background), and quit with Q or the regular window means.

## Save files format
- `P x y r s id`: creates a new point at coordinates (x, y), of rank r, states and with ID *id*
- `L n1 n2 id`: creates a new link with ID *id*, attached to nodes of IDs *n1* and *n2*. These nodes should have been created before.
- `I name id`: loads an image from the images in the zip file into image object with ID *id*
- `Ai n i`: attaches the image of ID *i* to node of ID *n*
- `At n text`: attaches text to the node of ID *n*
- `# comment`: comment
- `_S x y`: puts the camera at position (x, y) in the unit coordinate system
- `_Z z`: sets the zoom to z, values less than 0.01 are set back to 0.01

## TODO
- Allow empty text
- Change images and sizes on zoom, not text?
