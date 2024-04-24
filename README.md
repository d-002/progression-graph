# progression-graph
Progression graph tool for games

## Screenshots
*[upcoming]*

## Requirements
- python>=3.10
- pygame>=2.3.0

## Features
- Create points, add text and images to them, drag them around
- Link these points, lines can have different strength (size)
- Points can have different ranks, determining their size
- Save and open intuitively generated files
- Visualize the tree, export into png file

## Save files format
- `P x y r id`: creates a new point at coordinates (x, y), of rank r and with ID *id*
- `L p1 p2 id`: creates a new link with ID *id*, attached to points of IDs *p1* and *p2*. These points should have been created before. The link's width sepends on the maximum rank between *p1* and *p2*.
- `I name id`: loads an image from cached image *name* in `images/` into image object with ID *id*
- `Ai p i`: attaches the image of ID *i* to point of ID *p*
- `At p text`: attaches text to the point of ID *p*
- `# comment`: comment

## TODO
- Only save used images
- Trigger quit next frame when input returns None
- Save before quit?
- Message boxes, error when failed to load image
- Don't allow spaces in images: rename? replace?
- Cancel button in popups
- File selector for images?
- Save files, in zip?
- upload to png, transparent background option
- Change point and links ranks
- Hold shift to only edit X or Y coordinates?
- Scroll position and zoom in save file?
- Be more generous for displaying visible objects
- Change images and sizes on zoom
- Key to zoom back to original size
