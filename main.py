import os.path
import sys

from mido import MidiFile
from mido import MidiTrack

if len(sys.argv) != 3:
    print("Missing input\nUsage: {} <input midi>".format(os.path.basename(sys.argv[0])))
    sys.exit(1)

mid = MidiFile(sys.argv[1], clip=True)
new_mid = MidiFile(ticks_per_beat=mid.ticks_per_beat)

total_fixed = 0                 # Total notes fixed
print("Searching file for short notes...")

for trackindex, track in enumerate(mid.tracks):
    notes_on = {}               # Temporarily store notes when they're triggered on
    new_messages = []           # Store all messages and their absolute times
    absolute_time = 0           # Keep track of message's absolute time to calculate its length

    # Search every message in the track
    for messageindex, message in enumerate(track):
        absolute_time += message.time

        if message.type == "note_on":
            # Trigger on/off notes
            if message.velocity > 0:
                # Message velocity > 0 means note on
                if message.note in notes_on:
                    # Note being triggered on is already in the dictionary (most likely the same note overlapping)
                    # TODO Automatically fix this
                    print(message)
                    print(notes_on)
                    print(messageindex)
                    print("The same note has already been triggered on. Are two of the same note overlapping?")
                    sys.exit(1)
                else:
                    # Add message index and absolute time when note was triggered on to the dictionary
                    notes_on[message.note] = {"message_index": messageindex,
                                              "absolute_time": absolute_time}
            else:
                # Message velocity == 0 means note off
                if message.note not in notes_on:
                    # Note being triggered off was never triggered on
                    print(message)
                    print(notes_on)
                    print(messageindex)
                    print("A note cannot be triggered off if it was not triggered on.")
                    sys.exit(1)
                else:
                    previous_note = notes_on[message.note]                          # Note on dictionary object
                    previous_absolute_time = previous_note["absolute_time"]         # Absolute time when note on
                    note_length = absolute_time - previous_absolute_time            # Note length in ticks

                    # Temporarily store the tick when the note is triggered on
                    new_note_absolute_time = absolute_time
                    if note_length <= 4:
                        new_note_absolute_time += 5-note_length
                        total_fixed += 1

                        #print("{} tick note detected starting at index {} and ending at {}.".format(note_length, previous_note["message_index"], messageindex))

                    # Add both the on and off trigger of the note along with their absolute time to the buffer
                    new_messages.append((previous_absolute_time, track[previous_note["message_index"]]))
                    new_messages.append((new_note_absolute_time, message))

                    # Remove note from the dictionary
                    notes_on.pop(message.note)

        else:
            # All other messages
            new_messages.append((absolute_time, message))

    # Sort new messages based on absolute time, then descending delta time
    new_messages.sort(key=lambda x: (x[0], -x[1].time))

    # Dictionary should be empty (all notes triggered on have also been triggered off)
    assert(len(notes_on) == 0)
    # Total messages should not have changed
    assert(len(track) == len(new_messages))

    for i, new_message in enumerate(new_messages):
        if i == 0:
            new_message[1].time = new_message[0]
        else:
            new_message[1].time = new_message[0] - new_messages[i-1][0]

    #if trackindex == 1:
    #    for t in new_messages:
    #        print(t)

    new_track = MidiTrack()
    new_mid.tracks.append(new_track)
    for new_message in new_messages:
        new_track.append(new_message[1])

print("Done!\n{} notes fixed".format(total_fixed))

new_mid.save(sys.argv[2])

