from pkg_resources import load_entry_point
import pysrt
import re
import os
import json
from dotenv import load_dotenv

load_dotenv('../.env')

# regex to find speakers, e. g. (John:), or JOHN:
BOUNDARY_REGEX_STR = "^\(.*?:\)|^(- )??(Mc)??[A-Z &-'\.]+?:|(^(Pl)|(MRS. McHUGH)|(Narrator)|(Barney)|(Ted)|(Lily)|(Ferguson)|(Artur)|(Marshall)|(Woman)|(Man)|(Manos)|(All)|(Jeff)|(Robin)|(Bob)|(Rich)|(Radio announcer)|(Grandma lois)|(Boys)|(Both)|(MEADOw)|(Waiter)|(Mrs. Mosby)|(Mr. Mosby)|(Waitress)|(Robotic voice)|(Janice)|(Boy)|(Recording)|(Arthur)|(911 OPERATOR):)"
# steps between logging progress
LOG_FREQ = 1000
# get time in milliseconds from a SubRipTime object
def timestamp_to_ms(ts: pysrt.SubRipTime):
    return ((ts.hours * 60 + ts.minutes) * 60 + ts.seconds) * 1000 + ts.milliseconds

def main():
    bound_regex = re.compile(BOUNDARY_REGEX_STR)
    sp_turns = {}
    step = 0
    for filename in os.listdir(os.environ['SUBTITLES_PATH']):
        # json key corresponding to the scene
        clip_name = filename[:-4] if filename[-4:] == ".srt" else filename
        # read file
        subs = pysrt.open(os.path.join(os.environ['SUBTITLES_PATH'], filename))
        # use the regex to find transitions between speakers
        bounds_ind = []
        cur_speaker = ""
        for (i, sub) in enumerate(subs):
            speaker = bound_regex.match(sub.text)
            if not speaker:
                continue
            speaker = speaker.group(0)
            if speaker != cur_speaker:
                    bounds_ind.append(i)
                    cur_speaker = speaker
        timestamps = [{"start": timestamp_to_ms(subs[bounds_ind[i]].start),
                       "end": timestamp_to_ms(subs[bounds_ind[i + 1] - 1].end)}
                      for i in range(len(bounds_ind) - 1)]
        # edge cases
        if len(bounds_ind) > 0:
            timestamps.append({"start": timestamp_to_ms(subs[bounds_ind[-1]].start),
                               "end": timestamp_to_ms(subs[-1].end)})
        else:
            timestamps.append({"start": timestamp_to_ms(subs[0].start),
                               "end": timestamp_to_ms(subs[-1].end)})
        sp_turns[clip_name] = timestamps
        # logging
        step += 1
        if step % LOG_FREQ == 0:
            print(f'{step}/{len(os.listdir(os.environ["SUBTITLES_PATH"]))} files processed')

    # save file
    with open(os.environ['ST_PATH'], 'w') as f:
        json.dump(sp_turns, f)


if __name__ == "__main__":
    main()

