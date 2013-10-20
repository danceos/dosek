def abstract():
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')


variable_counter = 0
def new_variable_name():
    global variable_counter
    retval = "var_" + str(variable_counter)
    variable_counter += 1
    return retval
