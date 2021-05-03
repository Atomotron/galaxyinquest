# Galaxy Inquest

Our game for LD 46

Ludumdare page (with release info): https://ldjam.com/events/ludum-dare/46/galaxy-inquest

## Requirements

To run it you need:
- Python
- pygame (`pip install pygame`)
- numpy (`pip install numpy`)

## Credits

- Art, UI mockups, design iteration - Ellen KG
- Sound Design - Zhohan
- Music - Trey
- UI and growth model stuff - Carl
- Physics and some coding - Cocohop
- Coding and some physics - Skully
- Writing the credits - (see commit history)

## Bugs fixed after release
- Wildfires and blizzards now heat and cool the planet, instead of cooling and heating it. (We got this backwards)
- Enlightenment sound plays even when the game ends on the same frame.
- Event frequency no longer varies with framerate.
- Enlightenment may no longer progress when population is falling.
