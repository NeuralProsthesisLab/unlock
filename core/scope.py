
PROTOTYPE = "scope.PROTOTYPE"
SINGLETON = "scope.SINGLETON"

def convert(scope_str):
    "This function converts the string-version of scope into the internal, enumerated version."
    if scope_str == "prototype":
        return PROTOTYPE
    elif scope_str == "singleton":
        return SINGLETON
    else:
        raise Exception("Can not handle scope %s" % s)
        
    