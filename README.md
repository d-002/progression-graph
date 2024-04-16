# progression-tree
Progression tree tool for games

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

## Save files format:
- `I name id`: loads an image from cached image *name* in `images/` into image object with ID *id*
- `P x y id`: creates a new point at coordinates (x, y) with ID *id*
- `L p1 p2 id`: creates a new link with strength *s* and ID *id*, attached to points of IDs *p1* and *p2*. These points should have been created before
- `AI p i`: attaches the image of ID *i* to point of ID *p*
- `AT p text`: attaches text to the point of ID *p*
- `# comment`: comment

## Main TODO
- Core mechanics described above
- IDs manager

## Optional TODO:
- Image file search box, use already existing image
- png transparent background option
