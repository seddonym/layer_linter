from failurepackage.one import alpha

def foo():
    from failurepackage.three.gamma import BAZ
    return alpha.BAR + BAZ
