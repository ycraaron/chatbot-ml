import numpy as np


def test_dynamic_pooling():
    """
    tensorflow while_loop:
        might not be able to loop through tensorflow object
    
    numpy:
        => use numpy for similar matrix then dynamic pooling ??
        http://cs231n.github.io/python-numpy-tutorial/
        https://github.com/kuleshov/cs228-material/blob/master/tutorials/python/cs228-python-tutorial.ipynb
        https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.nditer.html
    
    zero word vector + if euclidean distance
        if we use zero word vector, then we have to get rid of zero before min-pooling
        or we could try max pooling or get rid of zero first before min-pool
        or we could use cosine distance + max pooling
        zero vector in cosine similarity return 0
        
    DYNAMIC POOLING LAYER
        GIVEN MATRIX SIZE, RETURN FIXED SIZE OF GRID OF INDEXES

    """
    ROW_SIZE = 5
    COL_SIZE = 5
    # when last loop
    # index_matrix
    a = np.arange(209).reshape(11, 19)

    value_matrix = np.random.random(209).reshape(11, 19)

    # print('original matrix:', a)

    ## horizontal loop
    # for x in np.nditer(a, flags=['external_loop']):
    #     print(x)
    # ## vertical loop
    # for x in np.nditer(a, flags=['external_loop'], order='F'):
    #     print(x)

    mat_row, mat_col = a.shape # 7, 11
    row_quotient, row_remainder = divmod(mat_row, ROW_SIZE)
    # print(row_quotient, row_remainder) # 2, 1
    col_quotient, col_remainder = divmod(mat_col, COL_SIZE)
    # print(col_quotient, col_remainder) # 3, 2

    # for row in mat_row:
    #     for col in mat_col:            
    #         curr = matrix[row * mat_col + col]

    #######################################################    
    arr = []    
    col_leader_arr = []
    row_leader_arr = []
    ## get only 1st element from entire matrix
    for row in range(0, (mat_row-row_remainder), row_quotient):           
        for col in range(0, (mat_col-col_remainder), col_quotient):
            num = row * mat_col + col
            ## when loop to 2nd to last 
            if(col == (col_quotient*(COL_SIZE-1))):
                col_leader_arr.append(num)

            if(row == (row_quotient*(ROW_SIZE-1))):
                row_leader_arr.append(num)

            arr.append(num)   
    # print(arr)
    # print(col_leader_arr)
    # print(row_leader_arr)
    
    ## gather elements of edge cases
    global_arr = []
    mini_arr = []
    col_toadd_arr =[]
    row_toadd_arr =[]
    last_lonely_arr =[]
    last_element = mat_col*(row_quotient*(ROW_SIZE-1)) + (COL_SIZE-1)*col_quotient
    # last_element = list(set(col_leader_arr).intersection(row_leader_arr))    
    # print("last eleemnt", last_element)

    ## create all nums based on 1st element
    for element in arr:        
        ## expand grid numbers
        for i in range(0,row_quotient):            
            for j in range(0,col_quotient):                                                
                curr = (i * mat_col) + ( element + j)
                mini_arr.append(curr)
                
                ## orphan element that needs to be added
                if(curr in col_leader_arr):
                    ## calculate orphan elements to add to leader
                    next_curr = (i * mat_col) + ( element + j + col_quotient)
                    # print("next_curr", next_curr)
                    for ii in range(0,row_quotient):
                        for iii in range(0, col_remainder):
                            col_toadd_arr.append(next_curr + (mat_col*ii) +iii)
                
                # print(col_toadd_arr)
                mini_arr = mini_arr + col_toadd_arr
                col_toadd_arr = []

                ## orphan element that needs to be added
                if (curr in row_leader_arr):
                    next_row_curr = curr + (row_quotient*mat_col)
                    for jj in range(0, row_remainder):
                        for jjj in range(0, col_quotient):
                            row_toadd_arr.append(next_row_curr + (jj*mat_col) + jjj)
                
                # print("row_toadd_arr: ", row_toadd_arr)                
                mini_arr = mini_arr + row_toadd_arr
                row_toadd_arr = []

                if(curr == last_element):
                    next_last_element = last_element + (row_quotient*mat_col) + col_quotient
                    # print("next_last_element", next_last_element)
                    for z in range(0, row_remainder):
                        for zz in range(0, col_remainder):
                            last_lonely_arr.append(next_last_element + (z*mat_col) + zz )
                # print("last_lonely_arr", last_lonely_arr)
                mini_arr = mini_arr + last_lonely_arr
                last_lonely_arr = []

        global_arr.append(mini_arr)
        mini_arr = []
    
    print('global arr', global_arr)
    result = find_max_with_index_matrix(row_size=ROW_SIZE, column_size=COL_SIZE, matrix_grid_value=a, matrix_grid_index=global_arr, with_index=False)
    print('result', result)
    return result


# multiple max value
#
def find_max_with_index_matrix(row_size, column_size, matrix_grid_value, matrix_grid_index, with_index=False):
    """
    given an array, loop through its grid, return biggest number within its grid
    :param row_size: the horizontal size of the return matrix
    :param column_size: the vertical size of the return matrix
    :param matrix_grid_value: matrix stores the values in each grid
    :param matrix_grid_index: matrix stores the indices in each grid
    :param with_index: set it True to get index matrix
    :return: grid max value matrix, and its index matrix

    arr_value_result: stores each grid's max value
    arr_index_result: stores index of each grid's max value
    """
    number = len(matrix_grid_value) * len(matrix_grid_value[0])

    # transform the value matrix into a list
    ls_matrix_value = matrix_grid_value.reshape(1, number)[0]
    print('matrix value', matrix_grid_value)
    print('matrix index', matrix_grid_index)

    arr_value_result = np.zeros(row_size*column_size)
    arr_index_result = np.zeros(row_size*column_size)

    i = 0
    ls_dic_grid = []
    # loop through all grids
    for ls_grid_index in matrix_grid_index:
        # use set to eliminate duplicate values
        set_value = set()
        dic_index_value = {}
        # loop through each grid to find max value
        for index in ls_grid_index:
            cell_value = ls_matrix_value[index]
            dic_index_value[index] = cell_value
            set_value.add(cell_value)
        max_value = max(set_value)
        arr_value_result[i] = max_value
        i += 1
        ls_dic_grid.append(dic_index_value)

    if with_index:
        arr_index_result = find_max_index(arr_value_result, ls_dic_grid, arr_index_result)
        ls_result = [arr_index_result.reshape(row_size, column_size), arr_value_result.reshape(row_size, column_size)]
        return ls_result
    else:
        return arr_value_result.reshape(row_size, column_size)


def find_max_index(arr_value_result, ls_dic_grid, arr_index_result):
    """
    :param arr_result: the grid max value matrix
    :param dic_index_value: list of index-value dictionary
    :param arr_index: the initial max value index matrix
    :return: array's grid max value index matrix

    value: max value of a grid
    dic_grid: the grid which the value is from
    """
    i = 0
    # for each max value, find its index
    for value in arr_value_result:
        dic_grid = ls_dic_grid[i]
        for key in dic_grid:
            if dic_grid[key] == value:
                # print(key, value)
                arr_index_result[i] = key
        i += 1
    return arr_index_result

test_dynamic_pooling()
