import argparse

if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('inputFile')
    argParser.add_argument('-export', dest='exportPath')
    args = argParser.parse_args()
    
    fout = open(args.exportPath, 'wb')
    fout.write(b'blah')
    fout.close()