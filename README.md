# MIDI Note Tick Length Fixer
A simple utility to extend the length of notes in a MIDI file. This may be useful as some MIDI playback devices don't properly emulate notes of very short length (seemingly <4 ticks). This program extends these notes out to 4 ticks.

## Requirements
- Python >= 3.7
- [mido >= 1.2.10](https://github.com/mido/mido)

## TODO
- Attempt to fix MIDIs with malformed channels in which two of the same note overlap
