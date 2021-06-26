import gc
import h5py

def close_all_h5():
    '''
    Closes all h5 objects in workspace. Not tested thoroughly.
    from here: https://stackoverflow.com/questions/29863342/close-an-open-h5py-data-file
    also see: pytables is able to do this with a simple function
        ```
        import tables
        tables.file._open_files.close_all()
        ```
    '''
    for obj in gc.get_objects():   # Browse through ALL objects
        if isinstance(obj, h5py.File):   # Just HDF5 files
            try:
                obj.close()
            except:
                pass # Was already closed
    gc.collect()



def show_group_items(hObj):
    '''
    simple function that displays all the items and groups in the
     highest hierarchical level of an h5 object or python dict.
    See 'show_item_tree' to view the whole tree
    RH 2021

    args:
        hObj: 'hierarchical Object' hdf5 object or subgroup object OR python dictionary
    returns: NONE

    ##############

    example usage:
        with h5py.File(path , 'r') as f:
            h5_handling.show_group_items(f)
    '''
    for ii,val in enumerate(list(iter(hObj))):
        if isinstance(hObj[val] , h5py.Group):
            print(f'{ii+1}. {val}:----------------')
        if isinstance(hObj[val] , dict):
            print(f'{ii+1}. {val}:----------------')
        else:
            if hasattr(hObj[val] , 'shape') and hasattr(hObj[val] , 'dtype'):
                print(f'{ii+1}. {val}:   shape={hObj[val].shape} , dtype={hObj[val].dtype}')
            else:
                print(f'{ii+1}. {val}:   type={type(hObj[val])}')



def show_item_tree(hObj=None , path=None, show_metadata=True , print_metadata=False, indent_level=0):
    '''
    recursive function that displays all the items and groups in an h5 object or python dict
    RH 2021

    args:
        hObj:
            'hierarchical Object'. hdf5 object OR python dictionary
        path (Path or string):
            If not None, then path to h5 object is used instead of hObj
        show_metadata (bool): 
            whether or not to list metadata with items
        print_metadata (bool): 
            whether or not to show values of metadata items
        indent_level: 
            used internally to function. User should leave blank
    returns: NONE

    ##############
    
    example usage:
        with h5py.File(path , 'r') as f:
            h5_handling.show_item_tree(f)
    '''

    if path is not None:
        with h5py.File(path , 'r') as f:
            show_item_tree(hObj=f, path=None, show_metadata=show_metadata, print_metadata=print_metadata, indent_level=indent_level)
    else:
        indent = f'  '*indent_level
        if hasattr(hObj, 'attrs') and show_metadata:
            for ii,val in enumerate(list(hObj.attrs.keys()) ):
                if print_metadata:
                    print(f'{indent}METADATA: {val}: {hObj.attrs[val]}')
                else:
                    print(f'{indent}METADATA: {val}: shape={hObj.attrs[val].shape} , dtype={hObj.attrs[val].dtype}')
        
        for ii,val in enumerate(list(iter(hObj))):
            if isinstance(hObj[val] , h5py.Group):
                print(f'{indent}{ii+1}. {val}:----------------')
                show_item_tree(hObj[val], show_metadata=show_metadata, print_metadata=print_metadata , indent_level=indent_level+1)
            elif isinstance(hObj[val] , dict):
                print(f'{indent}{ii+1}. {val}:----------------')
                show_item_tree(hObj[val], show_metadata=show_metadata, print_metadata=print_metadata , indent_level=indent_level+1)
            else:
                if hasattr(hObj[val] , 'shape') and hasattr(hObj[val] , 'dtype'):
                    print(f'{indent}{ii+1}. {val}:   shape={hObj[val].shape} , dtype={hObj[val].dtype}')
                else:
                    print(f'{indent}{ii+1}. {val}:   type={type(hObj[val])}')


def make_h5_tree(dict_obj , h5_obj , group_string=''):
    '''
    This function is meant to be called by write_dict_to_h5. It probably shouldn't be called alone.
    This function creates an h5 group and dataset tree structure based on the hierarchy and values within a python dict.
    There is a recursion in this function.

    RH 2021
    '''
    for ii,(key,val) in enumerate(dict_obj.items()):
        if group_string=='':
            group_string='/'
        if isinstance(val , dict):
            # print(f'making group:  {key}')
            h5_obj[group_string].create_group(key)
            make_h5_tree(val , h5_obj[group_string] , f'{group_string}/{key}')
        else:
            # print(f'saving:  {group_string}: {key}')
            h5_obj[group_string].create_dataset(key , data=val)
def write_dict_to_h5(path_save , input_dict , write_mode='w-', show_item_tree_pref=True):
    '''
    Writes an h5 file that matches the hierarchy and data within a pythin dict.
    This function calls the function 'make_h5_tree'

    RH 2021
   
    args:
        path_save (string or Path): full path name of file to write
        input_dict (dict): dict containing only variables that can be written as a 'dataset' in an h5 file (generally np.ndarrays and strings)
        write_mode ('w' or 'w-'): the priveleges of the h5 file object. 'w' will overwrite. 'w-' will not overwrite
        show_item_tree_pref (bool): whether you'd like to print the item tree or not
    '''
    with h5py.File(path_save , write_mode) as hf:
        make_h5_tree(input_dict , hf , '')
        if show_item_tree_pref:
            print(f'==== Successfully wrote h5 ile. Displaying h5 hierarchy ====')
            show_item_tree(hf)




def h5py_dataset_iterator(g, prefix=''):
    '''
    Made by Akshay. More general version of above. Could be useful.
    '''
    for key in g.keys():
        item = g[key]
        path = '{}/{}'.format(prefix, key)
        if isinstance(item, h5py.Dataset): # test for dataset
            yield (path, item)
        elif isinstance(item, h5py.Group): # test for group (go down)
            yield from h5py_dataset_iterator(item, path)