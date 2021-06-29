import argparse
import struct
import re
from io import BytesIO
import os

parser = argparse.ArgumentParser()
parser.add_argument("tool_mode", help="The mode for the tool. This can be extract or build.")
parser.add_argument("in_path", help="When extracting, this is the input BDT file. For building, this is the input folder (files inside this folder must be named with numerical values only, excluding the file extension)")
parser.add_argument("out_path", help="The output folder used for extracting or building an archive.")
parser.add_argument("out_name", nargs="?", default="output.bdt", help="The name of the output archive when building (optional, default is output.bdt).")
args = parser.parse_args()

tool_mode = args.tool_mode.lower()
in_path = args.in_path
out_folder = args.out_path
out_name = args.out_name

def read_u32(data, offset):
  data.seek(offset)
  return struct.unpack(">I", data.read(4))[0]

def write_u32(out_file, offset, new_value):
  new_value = struct.pack(">I", new_value)
  out_file.seek(offset)
  out_file.write(new_value)

def read_unknowns(data, offset):
  data.seek(offset)
  return data.read(28)

def write_unknowns(out_file, offset, new_value):
  out_file.seek(offset)
  out_file.write(new_value)

class MainHeader:
    def __init__(self):
       self.NumFiles = None
       self.Unknown = None

    def read(self):
        self.NumFiles = read_u32(BDTData, 0)
        self.Unknown = read_unknowns(BDTData, 4)

    def write(self, out_file):
        write_u32(out_file, 0, self.NumFiles)
        write_unknowns(out_file, 4, self.Unknown)

class FileHeader:
    def __init__(self, offset, fileindex):
        self.Offset = offset
        self.FileIndex = fileindex
        self.FileOffset = None
        self.FileLength = None

    def read(self):
        self.FileOffset = read_u32(BDTData, self.Offset)
        self.FileLength = read_u32(BDTData, self.Offset + 4)

    def write(self, out_file):
        write_u32(out_file, self.FileIndex * 8 + 0x20, self.FileOffset)
        write_u32(out_file, self.FileIndex * 8 + 4 + 0x20, self.FileLength)

class File(FileHeader):
    def __init__(self, FileHeader):
        self.Offset = FileHeader.Offset
        self.FileIndex = FileHeader.FileIndex
        self.FileOffset = FileHeader.FileOffset
        self.FileLength = FileHeader.FileLength
        self.data = None

    def read(self):
        BDTData.seek(self.FileOffset)
        self.data = BytesIO(BDTData.read(self.FileLength))

    def write(self, out_file):
        out_file.seek(self.FileOffset)
        out_file.write(self.data.read())

if tool_mode == "extract" or tool_mode == "e":
 if os.path.isfile(in_path) and in_path.endswith(".bdt"):

  if os.path.isdir(out_folder):
   bdt = open(in_path, "rb")
   BDTData = BytesIO(bdt.read())
 
   Main_Header = MainHeader()
   Main_Header.read()
   for header_index in range(Main_Header.NumFiles):
     header = FileHeader(header_index * 8 + 32, header_index)
     header.read()
     file = File(header)
     file.read()
     WriteFile = open(out_folder + str(file.FileIndex) + ".bms", "wb")
     WriteFile.write(file.data.read())
     WriteFile.close()

  else:
     print(out_folder + " is not a valid directory!")
 else:
    print(in_path + " is not a .bdt file!")

elif tool_mode == "build" or tool_mode == "b":
    if os.path.isdir(in_path) and len(os.listdir(in_path)) != 0:
        if os.path.isdir(out_folder):
            if not OutputFile.endswith(".bdt"):
                OutputFile = OutputFile + ".bdt"
            OutputFile = open(out_folder + "/" + out_name, "wb")

            Main_Header = MainHeader()
            Main_Header.NumFiles = len(os.listdir(in_path))
            Main_Header.Unknown = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            Main_Header.write(OutputFile)

            PreviousFileOffset = 8 * Main_Header.NumFiles + 0x20 #Set these to be correct for the first file to use, this allows us to simplify the loop
            PreviousFileLength = 0 #This will be set in the loop

            FilesToBuild = os.listdir(in_path)
            FilesToBuild.sort(key=lambda f: int(re.sub('\D', '', f))) #This sorts the files numerically. Assuming the files came from extractor above, this will put them back in the same order as before

            for index, file in enumerate(FilesToBuild):
                FileToCopy = open(in_path + "/" + file, "rb")
                DataToCopy = BytesIO(FileToCopy.read())

                File_Header = FileHeader(8 * index + 0x20, index)
                File_Header.FileOffset = PreviousFileOffset + PreviousFileLength
                File_Header.FileLength = DataToCopy.getbuffer().nbytes
                File_Header.write(OutputFile)

                PreviousFileOffset = File_Header.FileOffset
                PreviousFileLength = File_Header.FileLength
                
                ConstituentFile = File(File_Header)
                ConstituentFile.data = DataToCopy
                ConstituentFile.write(OutputFile)
        else:
            print(out_folder + " is not a valid directory!")
    elif len(os.listdir(in_path)) == 0:
        print(in_path + " is an empty directory!")
    else:
        print(in_path + " is not a valid directory!")
                