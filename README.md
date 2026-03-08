# Nordicub's NES-Style DPCM Converter
A command-line program meant to turn audio files into 1-bit delta-modulated 7-bit PCM in the style of the NES.

You need to install [FFmpeg](https://www.ffmpeg.org/download.html) for this program to work.

Nordicub's NES-Style DPCM Converter v1.1.0 <br>
USAGE: <br>
dpcmcomp -i <input file path> \[options] <br>
OPTIONS: <br>
--help, -h, -? -- Show this help message. <br>
-i \<filepath with extension> -- Specifies the input file. (required) <br>
-o \<filepath> -- Specifies the output filename. (default = output.wav) <br>
-q \<0-15> -- Set the internal sample rate using a sample rate table. (default = 15) <br>
-p -- Use the PAL sample rate table instead of NTSC. <br>
-sr \<sample rate> -- Set the output file's sample rate. (default = 44100) <br>
-u -- Do not trim the output file. <br>
-a -- Double the output file's amplitude. <br>
-k -- If two consecutive input samples are equal, continue in the same direction instead of reversing.
