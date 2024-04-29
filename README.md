# progression-graph
Progression graph tool for games

## Screenshots
*[upcoming]*

## Requirements
- python>=3.10
- pygame>=2.3.0

## Features
- Create points, add text and images to them, drag them around. The text is displayed on hover for lower ranked (sized) points, and always for higher ranks.
- Link these points, links have different sizes depending on the max rank of the connected points
- Points can have different ranks, determining their size
- Save and open intuitively formatted files
- Visualize the tree, export into png file
- Points have a state: to do, doing, completed, with different colors. You can cycle them with c while selected, and their state updates the connected links. This allows to keep track of the project's state easily.

## Controls
Click on an object to select it, hit Enter or Escape to unselect it. Escape can also be used to cancel creating a link.

Options will appear on top of the screen dependoing on the selection. Hit the corresponding keys to execute the different actions.

Zoom in and out with mouse scrolling, reset zoom with z.

Pressing Delete will detach the image from a point, or remove its text, or delete the point

## Save files format
- `P x y r s id`: creates a new point at coordinates (x, y), of rank r, states and with ID *id*
- `L p1 p2 id`: creates a new link with ID *id*, attached to points of IDs *p1* and *p2*. These points should have been created before.
- `I name id`: loads an image from the images in the zip file into image object with ID *id*
- `Ai p i`: attaches the image of ID *i* to point of ID *p*
- `At p text`: attaches text to the point of ID *p*
- `# comment`: comment
- `_S x y`: puts the camera at position (x, y) in the unit coordinate system
- `_Z z`: sets the zoom to z, values less than 0.01 are set back to 0.01

## TODO
- Zip file faster load/save: use diff
- Change images and sizes on zoom
- Unselect when exporting
