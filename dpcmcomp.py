import array as arr
import math
import wave as wav
import struct
import librosa
import soundfile as sf
import os
from pydub import AudioSegment as Am
import sys

a = 0
b = 0
buffer = ""
current = 0
quality = 33144
outsr = 44100
ntsc = True
cut = True
amp = False
inname = ""
outname = "output.wav"

usage = "Nordicub's NES-Style DPCM Converter v1.1.1\nUSAGE:\ndpcmcomp -i <input file path> [options]\nOPTIONS:\n--help, -h, -? -- Show this help message.\n-i <filepath with extension> -- Specifies the input file. (required)\n-o <filepath> -- Specifies the output filename. (default = output.wav)\n-q <0-15> -- Set the internal sample rate using a sample rate table. (default = 15)\n-p -- Use the PAL sample rate table instead of NTSC.\n-sr <sample rate> -- Set the output file's sample rate. (default = 44100)\n-u -- Do not trim the output file.\n-a -- Double the output file's amplitude."

if len(sys.argv) < 2:
    print(usage)
    sys.exit()

del sys.argv[0]

if sys.argv[0] == "-?" or sys.argv[0] == "-h" or sys.argv[0] == "--help":
    print(usage)
    sys.exit()

for i, v in enumerate(sys.argv):
    if v == "-i":
        inname = sys.argv[i + 1]
        break
if inname == "":
    print(usage)
    sys.exit()

ntsctab = [4182, 4710, 5264, 5593, 6258, 7046, 7919, 8363, 9420, 11186, 12604, 13983, 16885, 21307, 24858, 33144]
paltab = [4177, 4697, 5261, 5579, 6024, 7045, 7917, 8397, 9447, 11234, 12596, 14090, 16965, 21316, 25191, 33252]

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
    elif v == "-sr":
        outsr = int(sys.argv[i + 1])
        i += 2

for i, v in enumerate(sys.argv):
    if v == "-q":
        if ntsc:
            quality = ntsctab[int(sys.argv[i + 1])]
        else:
            quality = paltab[int(sys.argv[i + 1])]
        break
if quality == 0:
    if ntsc:
        quality = ntsctab[15]
    else:
        quality = paltab[15]

if os.path.isfile(outname):
    exists = input(f"File named {outname} already exists. Continue? (y/n) ")
    if exists.lower() != "y":
        sys.exit()

try:
    file = Am.from_file(inname)
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
    print(usage)
    sys.exit()
except Exception:
    print(usage)
    sys.exit()

try:
    with wav.open("tempsrdpcmcomp.wav", "r") as wavff:
        for i, o in enumerate(arr.array("h", wavff.readframes(wavff.getnframes()))):
            print("Building output file... " + str(math.floor(len(buffer) / wavff.getnframes() * 100)) + "%", end="\r")
            if wavff.getsampwidth() == 1:
                v = math.floor((o / 2)/2)
            elif wavff.getsampwidth() == 2:
                v = math.floor((o / 2 ** 9 + 64)/2)
            elif wavff.getsampwidth() == 3:
                v = math.floor((o / 2 ** 17 + 64)/2)
            elif wavff.getsampwidth() == 4:
                v = math.floor((o / 2 ** 26 + 64)/2)
            if i == 0:
                a = v
                b = v
            else:
                a = b
                b = v
            if a < b:
                current = 1
            elif a == b:
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
    print(usage)
    sys.exit()
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
    print(usage)
    sys.exit()

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
    print(usage)
    sys.exit()
