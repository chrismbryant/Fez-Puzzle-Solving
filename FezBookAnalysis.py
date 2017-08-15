import re
import numpy as np

tome_file = 'FezTomeRaw.txt'
order = [1, 5, 2, 6, 3, 7, 4, 8] # Found online. Originally discovered by others searching for appearances of "hexahedron."

class Tome():
    '''
    Class which allows you to create and manipulate a "Tome" object.
    '''
    
    def __init__(self, source=tome_file):
        '''
        Initialize tome object.
        '''
        self.source = source
        self.content = []
    
    def preprocess(self):
        '''
        Preprocess tome by converting txt to 3D array and reordering tome pages.
        '''
        def txt_to_array(self):
            '''
            Convert the txt file tome to a 3D array.
            '''
            with open(self.source, 'r') as f:
                text = f.read()
            pages = text.split('\n')
            chars = []
            for page in pages:
                lines = re.findall(r'([\w.][\w.]+)', page)
                splitlines = []
                for line in lines:
                    splitlines.append(np.array(list(line)))
                chars.append(np.array(splitlines))

            tome = np.array(chars)
            tome = np.rot90(chars, axes = (2,1))
            self.content = tome

        def reorder(self):
            '''
            Reorder the tome pages according to puzzle.
            '''
            ordered_tome = []
            for num in order:
                ordered_tome.append(self.content[num-1])
            self.content = np.array(ordered_tome)
            
        txt_to_array(self)
        reorder(self)
    
    def rot(self, ax1, ax2):
        '''
        Rotate 3D array along some axes-defined plane.
        '''
        self.content = np.rot90(self.content, axes = (ax1, ax2))
    
    def flip(self, ax):
        '''
        Flip 3D array across some axis.
        '''
        self.content = np.flip(self.content, axis = ax)
        
    def array_to_str(self):
        '''
        Convert 3D tome array into string.
        '''
        tomestr = ''
        shape = np.shape(self.content)
        for i in np.arange(shape[0]):
            for j in np.arange(shape[1]):
                for k in np.arange(shape[2]):
                    tomestr += self.content[i,j,k] + ' '
                tomestr += '\n'
            tomestr += '\n'
        self.content = tomestr
        print(self.content)
    
def main():

    mytome = Tome()
    mytome.preprocess()
    mytome.rot(0,2)
    mytome.array_to_str()

    with open('FezTomeDecoded.txt', 'w+') as f:
        text = f.write(mytome.content)

if __name__ == '__main__':
    main()