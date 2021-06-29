# TWWHD-BDT-Tool
A tool that allows you to extract files from the .bdt file found in JAudioRes/Seqs and rebuild them back into the archive

In `content\Cafe\<game region>\AudioRes\JAudioRes\Seqs` there is a unique .bdt archive that seems to only be used in TWWHD (it's different from the similarly named archive in Dark Souls) that stores the sequenced music tracks for the game. The sequences inside the archive are all stored as .bms files, the same format used on the GameCube. Most tracks are identical with a couple exceptions.

The extractor places the files in a folder and names each one based on their "index" in the archive. The building process sorts them by this index so that they are in the same order as the original file (a non-numerical name, excluding the file extension, will cause it to fail). This also means that renaming files to each other will switch their positions in the file and switch the tracks in the game. This does work, but has issues with loaded/unloaded banks the same way the music randomizer for the original WW does.

# Usage
To run the program as a python script, navigate to the folder containing the .py file and run `TWWHD_BDT_Extractor.py <mode> <in_path> <out_path> <out_name [optional]>`

Mode can be either `extract` or `build`
When extracting `in_path` is the path to the .bdt archive you want to extract. When building, this is the directory containing the files that you want put inside the archive.

When extracting `out_path` is the path to the folder you want to extract to. When building, this is the directory where you want the archive to be placed.

When building, `out_name` is the name of the archive to be created. If not given, it defaults to output.bdt. It is also ignored when extracting.

# BDT File Format
The .bdt file begins with a 0x20 byte main header, and is followed by smaller headers for each of the files inside the archive

This archive contains .bms files, the same format used for sequenced audio in the original TWW

As far as I have found, this type of archive is only used in TWWHD

MAIN HEADER:

`Offset    Size    Type      Desc

0x00      4       uint32    Number of files in the archive

0x04      ?       ???       Unknown. Always 0x00000000...

0x08      ?       ???       Unknown. Always 0x00000000...

0x0C      ?       ???       Unknown. Always 0x00000000...

0x10      ?       ???       Unknown. Always 0x00000000...

0x14      ?       ???       Unknown. Always 0x00000000...

0x18      ?       ???       Unknown. Always 0x00000000...

0x1C      ?       ???       Unknown. Always 0x00000000...

0x20    START OF CONSTITUENT FILE HEADERS/END OF MAIN HEADER`

Following the main header, there is a 0x8 byte header for each of the constituent files (as listed in the main header)

`Offset    Size    Type    Desc

0x00    4    uint32    Offset to beginning of constituent file (relative to the start of the archive)

0x04    4    uint32    Length of the constituent file`

These smaller headers are placed continuously in a row following the main header. For example:

A .bdt with 3 files would have a main header like this (in hex):

`00 00 00 03 00 00 00 00 00 00 00 00 00 00 00 00

00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`

If each file was 0x34 bytes long, the collection of individual file headers would look like this:

`00 00 00 38 00 00 00 34 00 00 00 6C 00 00 00 34

00 00 00 A0 00 00 00 34 <file data here>`

Together, the file would look like:

`00 00 00 03 00 00 00 00 00 00 00 00 00 00 00 00

00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

00 00 00 38 00 00 00 34 00 00 00 6C 00 00 00 34

00 00 00 A0 00 00 00 34 <file data here>`
