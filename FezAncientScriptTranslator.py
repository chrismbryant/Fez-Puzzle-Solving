import re
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from shutil import copyfile

# When analyzing the text:
my_file = 'Fez Transcription.txt'
file_unique = 'Fez Transcription (without duplicates).txt'
English_order = ['E', 'T', 'A','O', 'I', 'N', 'S', 'H', 'R', 'D', 'L', 'C', 'U', 'M', 'W', 'F', 'G', 'Y', 'P', 'B', 'V', 'K', 'J', 'X', 'Q', 'Z']

# When copying images:
source_path = 'Examples/Original/'             # Where to copy from
dest_path = 'Examples/Translated/'             # Where to copy to
ref_doc = 'Fez Transcription_TRANSLATION.txt'  # Reference document from which to obtain the new file names

# Through trial and error, let's fill in blanks until we have a correct dictionary of character translations.
# UPDATE: I have decoded the characters. The list below is complete and correct. 
NA = '?'
correct_dict = {
    1: 'I',
    2: 'O',
    3: 'U', # U=V
    4: 'C',
    5: 'A',
    6: 'S',
    7: 'M',
    8: 'G',
    9: 'T',
    10: 'B', # Recently added
    11: 'H',
    12: 'N',
    13: 'Y',
    14: 'F',
    15: 'L',
    16: 'R',
    17: 'P',
    18: 'W',
    19: 'D',
    20: 'E',
    21: 'Q', # Q=K
    22: 'Z',
    23: 'X', # Recently added
    24: 'J', # Recently added  
}

##### --------------------------- REMOVE DUPLICATES FUNCTION --------------------------- #####

def rmdup(redundant_file=my_file):
    '''
    Remove duplicates to from file and output new file of unique text.
    '''
    with open(redundant_file, 'r') as r:
        text = r.read()
    text = text.split('START')[-1] 
    text = 'START\n' + text
    text = re.sub(r'(\_\d+\_[\w/]+.*\n)', r'', text)
    with open(file_unique, 'w+') as f:
        f.write(text)

##### ---------------------------FREQUENCY ANALYSIS FUNCTIONS--------------------------- #####

# In this section, we try to decode the language through a basic comparison of letter
# frequency to the letter frequency of English. Warning: this tactic is not particularly
# successful. 

def preprocess(training_file):
    '''
    The preprocess() function preprocesses the file by converting it into a 1D array 
    of all the numbers (characters to be translated) that appear in the document.
    '''
    
    # Open the text file, dump the text into a string variable "text", and close the file.
    with open(my_file, 'r') as f:
        text = f.read()

    # Here we process the data for letter frequency analysis.
    text = text.split('START')[-1]            # remove everything before the start tag
    text = re.sub(r'_\d+_.\t', r'', text)     # remove the image identification
    text = re.sub(r'[\t\n\r ]+', r'', text)   # remove unnecessary tabs, new lines, returns, and spaces
    text = re.sub(r'[\.-]',r' ',text)         # replace all "." and "-" with " ". 
    
    # Convert the data in "text" into an array of numbers.
    numlist = []
    numbers = re.findall(r'(\d+) ', text)
    for number in numbers:
        numlist.append(int(number))
    numarray = np.array(numlist)
    return numarray

def num_count(numarray):
    '''
    The num_count(numarray) function counts up the number of times each character ever 
    appears, and returns sorted array of the labels and the number of times each appears. 
    '''
    
    # Count up the times each number appears in the array.
    x = np.arange(1, np.amax(numarray) + 1)
    y = [np.count_nonzero(numarray == k) for k in x]

    # Sort the results 
    y_sorted = sorted(y, reverse = True) # sorted number of character counts
    labels_sorted = [i[0] + 1 for i in sorted(enumerate(y), key = lambda p: p[1], reverse = True)]
    return labels_sorted, y_sorted

def make_freq_dict(labels_sorted, freq_order):
    '''
    Makes a dictionary according to the frequency analysis.
        {label : 'letter'}
    '''
    
    freq_dict = {}
    for idx, label in enumerate(labels_sorted):
        freq_dict[label] = freq_order[idx]
    return freq_dict

def make_letter_hist(labels, counts, save=False, letter_freq_desc=English_order, correct_order=False): 
    '''
    The make_letter_hist(labels, counts) function generates a histogram with each 
    character count and a best guess at the corresponding English character based on 
    the frequency of character appearances in the whole English language.
    '''
    
    fig, ax = plt.subplots()
    #fig, ax = plt.subplots(figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')

    bar_labels = tuple(str(label) for label in labels)
    bar_pos = np.arange(len(labels))
        
    plt.bar(bar_pos, counts, align='center', alpha=0.7)
    plt.xticks(bar_pos, bar_labels)
    plt.xlabel('Original Character Label')
    plt.ylabel('# of counts')
    plt.title('Frequency Distribution of Characters in Fez Ancient Script,\n & Corresponding Best English Guess')

    for i, v in enumerate(counts):
        ax.text(i-0.25, v+0.5, letter_freq_desc[i])
    
    if correct_order:
        c = 0
        for i in labels:
            ax.text(c-0.25, 0.3*counts[c], correct_dict[i])
            c += 1
        
    if save:
        plt.savefig('hist.png')
    
    plt.show()

    
##### -------------------------TRANSLATOR FILE OUTPUT FUNCTION------------------------- #####


def translate(infile, decoder=correct_dict, freq=False, HTML=False):
    '''The translate(infile) function "translates" the Fez script into English according
    to a decoder dictionary. By default, the decoder is set to the correct dictionary.
    If freq=True, the translator will use the dictionary "freq_dict" guessed by
    frequency analysis (which is based on the assumption that the frequency of character
    appearances in the example text match the average frequency of character appearances
    in the English language).
    
    I implemented an optional HTML setting for no particular reason (originally, it was
    to generate colored according to the uncertainty of the character translation, but 
    the code ended up being relatively easy to crack, so I never finished the color
    functionality).'''
    
    def transl_process(decoder, original):
        '''This is where the actual number-to-letter translation and output-string-creation 
        occurs. Here, we replace each number with the corresponding letter of the alphabet 
        as indicated by the decoder dictionary, and return the translated string.'''
    
        def my_replace(match):
            number = match.group(1)
            punct = match.group(2)
            return decoder[int(number)] + punct
        
        transl = re.sub(r'(\d+)([.-])', my_replace, original) # Number --> letter
        transl = re.sub(r'(\d+_)[.+\t+]', r'\1    ', transl)  # Cleanup
        transl = re.sub(r'-', r'', transl)                    # Cleanup
        transl = re.sub(r'\.\t+', r' ', transl)               # Cleanup
        transl = transl.split('START')[-1]                    # Cleanup
        
        return transl
    
    file_in = open(infile, 'r')
    original = file_in.read() 
    file_in.close()
    
    if freq:
        suffix = '_FREQUENCY TRANSLATION'
        decoder = freq_dict
    else:
        suffix = '_TRANSLATION' # default
        
    if HTML:
        ext = '.html'
    else:
        ext = '.txt' # default
        
    transl = transl_process(decoder, original)
    
    filename = infile.split('.')[0]
    extension = suffix + ext
    
    file_out = open(filename + extension, 'w+')
    
    if HTML:
        transl = re.sub(r'(_\d+_)', r'<br>\1&nbsp&nbsp&nbsp&nbsp', transl)
        file_out.write('<font face="Open Sans" color="black">')
        file_out.write(transl)
        file_out.write('</font>')
    else:
        file_out.write(transl) # Write the translation to the output file
    
    file_out.close()
    
    print('Translation successfully written to \"%s%s"' % (filename, extension))


##### ---------------------------IMAGE COPY/RENAME FUNCTIONS--------------------------- #####


def overwrite_safety(dest, input_capability=False):
    '''The function overwrite_safety(dest) acts as a failsafe for each copy instance, 
    preventing unwanted overwriting. It also allows for input() if running on 
    a frontend that can take input.'''
    
    if input_capability == False:
        overwrite = 'n'
        skip_or_cancel = 's'
        if os.path.isfile(dest):
            print('Warning! File name \"%s\" already taken. Skipping.' % dest.split('/')[-1])
            skip = True
            return skip
    
    elif input_capability == True:
        
        if os.path.isfile(dest):
            overwrite = input('Warning! File name \"%s\" already taken. Overwrite? (Y/N)' % dest.split('/')[-1])
            if overwrite.lower() == 'y':
                return # exits the failsafe 'overwrite_status' function
            else:
                skip_or_cancel = input('Got it, don\'t overwrite. Skip (S) this one, or cancel (C) everything?')
                skip_or_cancel = 's'
                if ans.lower() == 's':
                    skip = True
                    return skip # continues to next iteration
                else:
                    print('Cancel. Okay, see ya!')
                    sys.exit()                 
                        
def get_new_filename(image, ref_doc):
    '''For an image file (e.g. "IMG_9500.jpg"), find the text translation in "ref_doc" 
    and return it appended to the image number string'''
    
    img_num = image.split('.')[0]  # chop off the extension
    img_num = img_num.split('_')[-1] # chop off the prefix and underscore, leaving just the number
   
    with open(ref_doc, 'r') as f:
        text = f.read()
    
    match = re.search(r'%s_.+[\t\r](\w.*)\.' % img_num, text) ### Why doesn't this work?
        
    if not match:
        print('Oops. Looks like \"%s\" doesn\'t have a translation yet. That\'s okay. I\'ll skip it.\n' % image)
        return
    else:
        translation = match.group(1)
        return img_num + '_' + translation   
                        
def copy_translate_rename(src, dest):
    '''The function copy_translate_rename(dest) copies all the images in the 'src' 
    directory to the 'dest' directory, renaming them with the translation string
    associated with each image.'''
    
    old_images = os.listdir(source_path)
    counter = 0
    
    for img in old_images:
        
        skip = False
        img_extn = ('.') + img.split('.')[-1] # gets the image extension (e.g. jpg or png)
        old_path = source_path + img
        translation = get_new_filename(img, ref_doc) # for a given 'IMG_####.ext', find the new translated file name
        
        if translation is None:
            continue
        else:
            new_path = dest_path + translation + img_extn # output file path with translation as file name
              
        new_name = new_path.split('/')[-1]
        
        skip = overwrite_safety(new_path) # prevents unwanted overwriting
        if skip:
            continue
        
        try:
            copyfile(old_path, new_path) # copies file to new location with new name
        except:
            print('Oops. I couldn\'t copy this for some reason:\nSkipping \"%s\" --> \"%s\"\n' % (img, new_name))
            continue
               
        print('Copied/Renamed: %s --> %s\n' % (img, new_name))
        counter += 1
        
    print('--------------------------------------------\n')   
    print('All done! Successfully copied %d of %d files.\n' % (counter, len(old_images)))


##### --------------------------SIMPLE COMMAND LINE INTERFACE-------------------------- #####


def quickinterface():
    '''
    An incomplete command line user interface to quickly run the most useful parts
    of the module. 
    '''
    def intro():
        print('\nWelcome to the Fez translator.\n')
        print('I will operate on the following source documents:')
        print('   - \"%s\"' % my_file)
        print('   - \"%s\"' % file_unique)
        print('\nWhen I copy/rename image files, they will be...')
        print('   - Copied from \"%s\" to \"%s\"' % (source_path, dest_path))
        print('   - Renamed using the reference document \"%s\"' % ref_doc)
    
    def body():
        print('\n--------------------------------------------\n')   
        ans = input('Frequency Analysis (a) or File Translation (t)?')

        if ans.lower() == 'a':
            print('\nFrequency Analysis:')
            numarray = preprocess(my_file)
            labels, y_sorted = num_count(numarray)
            freq_dict = make_freq_dict(labels, English_order)
            make_letter_hist(labels, y_sorted, correct_order=True)

        else:
            ans = input('Translate files and copy images? (y/n): ')
            if ans.lower() == 'y' or ans.lower() == 'yes':
                translate(my_file)
                translate(file_unique)
                copy_translate_rename(source_path, dest_path)
            else:
                print()
    
        ans = input('Again? (q = quit):')
        if ans.lower() == 'q':
            print('Now exiting.')
            quit()
        else:
            body()
    
    intro()
    body()

    
##### ------------------------------------ MAIN ---------------------------------------- #####


def main():

    rmdup()
    quickinterface()

if __name__ == '__main__':
    main()