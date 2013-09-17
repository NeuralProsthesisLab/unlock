import numpy as np
import scipy.io as sio

def fileParser(file_name,mat_export='off'):
    """Assumes text file input has: 1) \n after each row and 2) numpy data with [] arrays.
       See http://www.ibm.com/developerworks/opensource/library/os-python8/ for I/O reference.
    """

    # open the file
    myfile = open(file_name,"r")

    # count the number of lines
    n_lines = 0
    for line in myfile.readlines(): n_lines+=1
    n_cols =  len(line.split())
    myfile.seek(0)
    data = np.zeros((n_lines,n_cols))

    # write it to a data variable
    idx_row=-1
    for line in myfile.readlines():
        temp_line = line
        idx_row+=1; idx_col=0
        for item in temp_line.split():
            if item[0] == '[':
                item = item.strip('[')  # remove left bracket
            elif item[-1] == ']':
                item = item.strip(']')  # remove right bracket
            item = item.strip(',')      # remove comma
            data[idx_row,idx_col] = np.float(item)
            idx_col+=1
    myfile.close()

    # Export option for MATLAB users
    if mat_export == 'on':
        sio.savemat(file_name[:-4]+'.mat',{'data':data})

    return data