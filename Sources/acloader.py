
import sys

class ACFormatError(Exception): pass

class ACLoader:
  def __init__(self, name):
    self.materials = []
    self.objects = []
    self.file = file(name)

    if not self.file.next().strip() == "AC3Db":
      raise ACFormatError("File Header does not Match")

    for line in self.file:
      parts = line.strip().split()
      if parts[0] == 'MATERIAL':

        if not (parts[2] == 'rgb' and parts[6] == 'amb' and parts[10] == 'emis' and 
                parts[14] == 'spec' and parts[18] == 'shi' and parts[20] == 'trans'):
          raise ACFormatError("Material missing lighting components")

        self.materials.append({
          'name' : parts[1].strip('"'),
          'rgb'  : tuple([float(x) for x in parts[3:6]]),
          'amb'  : tuple([float(x) for x in parts[7:10]]),
          'emis' : tuple([float(x) for x in parts[11:14]]),
          'spec' : tuple([float(x) for x in parts[15:18]]),
          'shi'  : int(parts[19]),
          'trans': float(parts[21]),
        });

      elif type == 'OBJECT':
        obj = {
          'name':parts[1].stip(),
        }


if __name__ == "__main__":
  if (len(sys.argv) != 2):
    print "Usage: acloader.py <filename>"
    sys.exit(0)

  tmp = ACLoader(sys.argv[1])

  print tmp.materials
