import datetime, _datetime
if 1:
    import cPickle as pickle
else:
    import pickle

cases = (datetime, "Python"), (_datetime, "C")

def pickleit(thing):
    s = pickle.dumps(thing, 1)
    return len(s)

typenames = "date", "datetime", "timedelta"

for typename in typenames:
    for mod, way in cases:
        obj = getattr(mod, typename)(2000, 12, 13)
        print "pickling", obj, "via", way, "-- pickle length", pickleit(obj)

for typename in typenames:
    for i in range(1, 11):
        for mod, way in cases:
            ctor = getattr(mod, typename)
            objs = [ctor(j+1, 3, 4) for j in range(i**2)]
            plen = pickleit(objs)
            print "list of %3d %ss via %6s -- %4d bytes, %5.2f bytes/obj" % (
                  len(objs), typename, way, plen, float(plen)/len(objs))
