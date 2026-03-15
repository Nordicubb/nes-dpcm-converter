import array as arr
import math
import wave as wav
import struct
import librosa
import soundfile as sf
import os
import pydub.utils
import sys

a = 0
b = 0
buffer = ""
current = 0
quality = 0
outsr = 44100
ntsc = True
cut = True
amp = False
keep = False
inname = ""
outname = "output.wav"

helptxt = "Nordicub's NES-Style DPCM Converter v1.3.0\nUSAGE:\ndpcmcomp -i <input file path> [options]\nOPTIONS:\n--help, -h, -? -- Show this help message.\n-i <filepath with extension> -- Specifies the input file. (required)\n-o <filepath> -- Specifies the output filename. (default = output.wav)\n-q <0-15> -- Set the internal sample rate using a sample rate table. (default = 15)\n-p -- Use the PAL sample rate table instead of NTSC.\n-sr <sample rate or \"off\"> -- Set the output file's sample rate. If the argument is \"off\" or 0, set to the internal sample rate. (default = 44100)\n-u -- Do not trim the output file.\n-a -- Double the output file's amplitude.\n-k -- If two consecutive input samples are equal, continue in the same direction instead of reversing."


def usage():
    print(helptxt)
    sys.exit()


if len(sys.argv) < 2:
    usage()

del sys.argv[0]

if sys.argv[0] == "-?" or sys.argv[0] == "-h" or sys.argv[0] == "--help":
    usage()

for i, v in enumerate(sys.argv):
    if v == "-i":
        inname = sys.argv[i + 1]
        break
if inname == "":
    usage()

ntsctab = [4182, 4710, 5264, 5593, 6258, 7046, 7919, 8363, 9420, 11186, 12604, 13983, 16885, 21307, 24858, 33144]
paltab = [4177, 4697, 5261, 5579, 6024, 7045, 7917, 8397, 9447, 11234, 12596, 14090, 16965, 21316, 25191, 33252]

try:
    for i, v in enumerate(sys.argv):
        if v == "-o":
            if sys.argv[i + 1].lower().endswith(".wav"):
                outname = sys.argv[i + 1]
            else:
                outname = sys.argv[i + 1] + ".wav"
            i += 2
        elif v == "-p":
            ntsc = False
            i += 1
        elif v == "-u":
            cut = False
            i += 1
        elif v == "-a":
            amp = True
            i += 1
        elif v == "-k":
            keep = True
            i += 1
        elif v == "-sr":
            if sys.argv[i + 1].lower() == "off":
                outsr = 0
            else:
                outsr = int(sys.argv[i + 1])
            i += 2
except Exception:
    usage()
try:
    for i, v in enumerate(sys.argv):
        if v == "-q":
            if ntsc:
                quality = ntsctab[int(sys.argv[i + 1])]
            else:
                quality = paltab[int(sys.argv[i + 1])]
            break
except Exception:
    usage()
if quality == 0:
    if ntsc:
        quality = ntsctab[15]
    else:
        quality = paltab[15]
if outsr == 0:
    outsr = quality

if os.path.isfile(outname):
    exists = input(f"File named {outname} already exists. Continue? (y/n) ")
    if exists.lower() != "y":
        sys.exit()

try:
    file = pydub.AudioSegment.from_file(inname)
    print("Converting to mono...")
    monofile = file.set_channels(1)
    monofile.export("tempwavdpcmcomp.wav", format="wav")
    print("Successfully converted to mono.")
    print(f"Resampling to {quality} Hz...")
    with wav.open("tempwavdpcmcomp.wav", "r") as wavf:
        file, sr = librosa.load("tempwavdpcmcomp.wav", sr=quality)
        sf.write("tempsrdpcmcomp.wav", file, sr)
    print(f"Successfully resampled to {quality} Hz.")
    print("Removing temp mono file...")
    os.remove("tempwavdpcmcomp.wav")
    print("Successfully removed temp mono file.")
except FileNotFoundError:
    print(f"ERROR: File {inname} not found.")
    sys.exit()
except PermissionError:
    print("ERROR: Insufficient permissions to create/remove files.")
    sys.exit()
except TypeError as e:
    usage()
except Exception:
    usage()

try:
    with wav.open("tempsrdpcmcomp.wav", "r") as wavff:
        info = pydub.utils.mediainfo_json("tempsrdpcmcomp.wav")
        audio_streams = [x for x in info["streams"] if x["codec_type"] == "audio"]
        isfloat = audio_streams[0].get("sample_fmt")
        step = 1
        if wavff.getsampwidth() == 1:
            typecode = "B"
        elif wavff.getsampwidth() == 2:
            typecode = "h"
        elif wavff.getsampwidth() == 3:
            typecode = "B"
            step = 3
        elif wavff.getsampwidth() == 4:
            if isfloat == "flt":
                typecode = "f"
            else:
                typecode = "l"
        elif wavff.getsampwidth() == 8:
            typecode = "d"
        frames = arr.array(typecode, wavff.readframes(wavff.getnframes()))
        for i in range(0, len(frames), step):
            print("Building output file... " + str(math.floor(len(buffer) / wavff.getnframes() * 100)) + "%", end="\r")
            o = frames[i]
            if wavff.getsampwidth() == 1:
                v = math.floor(o / 2)
            elif wavff.getsampwidth() == 2:
                v = math.floor((o / 2 ** 9 + 64))
            elif wavff.getsampwidth() == 3:
                o = (o << 8 | frames[i + 1]) << 8 | frames[i + 2]
                v = math.floor((o / 2 ** 17 + 64))
            elif wavff.getsampwidth() == 4:
                if isfloat != "flt":
                    v = math.floor((o / 2 ** 26 + 64))
                else:
                    v = math.floor(o / ((max(frames) - min(frames)) / 127))
            elif wavff.getsampwidth() == 8:
                v = math.floor(o / ((max(frames) - min(frames)) / 127))
            if i == 0:
                a = v
                b = v
            else:
                a = b
                b = v
            if a < b:
                current = 1
            elif a == b:
                if not keep:
                    current = int(not current)
            else:
                current = 0
            if buffer == "":
                buffer = str(current)
            else:
                buffer = buffer + str(current)
except FileNotFoundError:
    print(f"ERROR: File tempsrdpcmcomp.wav not found.")
    sys.exit()
except PermissionError:
    print("ERROR: Unable to read file.")
    sys.exit()
except Exception:
    usage()
try:
    print("Output file built successfully.")
    print("Removing temp resampled file...")
    os.remove("tempsrdpcmcomp.wav")
    print("Successfully removed temp resampled file.")
except FileNotFoundError:
    print(f"ERROR: File tempsrdpcmcomp.wav not found.")
    sys.exit()
except PermissionError:
    print("ERROR: Insufficient permissions to delete files.")
    sys.exit()
except Exception:
    usage()

if cut:
    print("Cutting builded file...")
    cutlen = math.floor(((len(buffer)/8)-1)/16)
    if cutlen > 255:
        cutlen = 255
    buffer = buffer[:cutlen*8*16+8]
    print("Successfully cut builded file.")

try:
    with wav.open("tempencodedpcmcomp.wav", "w") as f:
        f.setnchannels(1)
        f.setsampwidth(1)
        f.setframerate(quality)
        h = 128
        counter = 0
        for i, s in enumerate(buffer):
            print("Encoding output file... " + str(math.floor(counter / len(buffer) * 100)) + "%", end="\r")
            if amp and i == 0:
                h -= 64
            if not amp:
                h -= 64
            if amp and i > 0:
                h = math.floor(h / 2)
            if int(s) == 0:
                if h >= 2:
                    h -= 2
                else:
                    h += 2
            else:
                if h <= 125:
                    h += 2
                else:
                    h -= 2
            if amp:
                h *= 2
            if not amp:
                h += 64
            for j in range(0, 1):
                f.writeframes(struct.pack("<B", h))
            counter += 1
    print("Output file encoded successfully.")
    print(f"Resampling to {outsr} Hz...")
    file, sr = librosa.load("tempencodedpcmcomp.wav", sr=outsr)
    sf.write(outname, file, sr)
    print(f"Succesfully resampled to {outsr} Hz.")
    print("Removing temp encoded file...")
    os.remove("tempencodedpcmcomp.wav")
    print("Successfully removed temp encoded file.")
    print("Finished!")
except PermissionError:
    print(f"ERROR: Insufficient permissions to create files.")
    sys.exit()
except Exception:
    usage()
