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

## Controls
Click on an object to select it, hit Enter or Escape to unselect it. Escape can also be used to cancel creating a link.

Options will appear on top of the screen dependoing on the selection. Hit the corresponding keys to execute the different actions.

Zoom in and out with mouse scrolling, reset zoom with z.

Pressing Delete will detach the image from a point, or remove its text, or delete the point

## Save files format
- `P x y r id`: creates a new point at coordinates (x, y), of rank r and with ID *id*
- `L p1 p2 id`: creates a new link with ID *id*, attached to points of IDs *p1* and *p2*. These points should have been created before.
- `I name id`: loads an image from cached image *name* in `images/` into image object with ID *id*
- `Ai p i`: attaches the image of ID *i* to point of ID *p*
- `At p text`: attaches text to the point of ID *p*
- `# comment`: comment

## TODO
- Delete image, then text, then point
- Escape to exit popups
- points text
- Be more generous for displaying visible objects
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
- Change images and sizes on zoom
- Export to image with margin around elements, zoom 1
- Handle no duplicate links
