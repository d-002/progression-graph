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
- Save and open intuitively generated files
- Visualize the tree, export into png file

## Save files format
- `P x y id`: creates a new point at coordinates (x, y) with ID *id*
- `L p1 p2 id`: creates a new link with strength *s* and ID *id*, attached to points of IDs *p1* and *p2*. These points should have been created before
- `I name id`: loads an image from cached image *name* in `images/` into image object with ID *id*
- `Ai p i`: attaches the image of ID *i* to point of ID *p*
- `At p text`: attaches text to the point of ID *p*
- `# comment`: comment

## Main TODO
- Core mechanics described above
- Handle objects deletion and IDs
- Handle deletion of old objects in open_file

### Optional TODO
- Save files, in zip?
- Image file search box, use already existing image
- png transparent background option
- point as block, specify size with rank system?
- hold shift to only edit X or Y coordinate
- Scroll position and zoom in save file?
- Be more generous for displaying visible objects
- Cursor system for inputbox?
