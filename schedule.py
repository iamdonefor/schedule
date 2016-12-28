#!/usr/bin/env python
import argparse
from random import choice,shuffle
from copy import copy
from collections import defaultdict

DAY = 86400

class Track(object):
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

class Collection(object):
    pass_params = ["dt"]

    def __init__(self):
        self.count = 0
        self.tracks = []
        self.tracks_by_id = {}

    def add_track(self, name, duration, **kwargs):
        track = Track(name, duration)
        track.id = self.count
        self.tracks.append(track)
        self.tracks_by_id[self.count] = track

        for param in self.pass_params:
            setattr(track, param, kwargs.get(param, None))
        
        self.count += 1

class Generator(object):
    def __init__(self, collection):
        self.c = collection
        self.tracks = copy(collection.tracks)
        self.idx = 0

    def next(self):
        if self.idx == self.c.count:
            raise StopIteration
        track = self.tracks[self.idx]
        self.idx += 1
        return (track, int(round(track.duration)))

    def shuffle(self):
        shuffle(self.tracks)
        self.idx = 0

    def __iter__(self):
        return self
        
def load_from_file(filename):
    c = Collection()

    with open(filename) as infile:
        while True:
            s = infile.readline()
            if not s: break
            try:
                (name, duration, dt,) = s.split()
                duration = float(duration)
            except ValueError:
    #            print s.rstrip()
                continue
            c.add_track(name, duration, dt=dt)

    return c

# next item returns anything as first arg and int as second
def pack(target, generator, precision=5):
    times = [None] * int(round(target))
    tlen = len(times)
    items = {}
    path = []
    points = [0] 

    for (i,v) in generator:
        items[i] = v
        newpoints = []

        for p in points:
            if p + v >= tlen:  
                continue
            if times[p+v] is None:
                times[p+v] = i
                newpoints.append(p+v)
        points += newpoints

        # check early exit
        for t in range(tlen-1, tlen-precision, -1):
            if times[t] is not None:
                break

    # find best
    for t in range(tlen-1, 0, -1):
        if times[t] is not None:
            break

    # reconstruct
    while True:
        i = times[t]
        v = items[i]
        path.append(i)
        t -= v
        if t == 0:
            break

    return path

def score(pl):
    penalty = 0.0
    ttime = 0.0
    dtimes = defaultdict(float)
    dtinst = defaultdict(int)

    for track in pl:
        ttime += track.duration
        dtimes[track.dt] += track.duration
        dtinst[track.dt] += 1

    for dt in ['mrn', 'day', 'eve', 'ngt']:
        penalty += abs(dtimes[dt] - DAY/4)*0.1

    penalty += abs(DAY - ttime) * 10

    return penalty

def print_playlist(pl):
    ttime = 0.0
    dtimes = defaultdict(float)
    for track in pl:
        ttime += track.duration
        dtimes[track.dt] += track.duration

    print ttime, "-".join(str(t.id) for t in pl)
    print ",".join("%s:%s" % (i,v) for (i,v) in dtimes.items())
    

def main(args):
    tracks = load_from_file(args.tracks)
    jingles = load_from_file(args.jingles)
    gen = Generator(tracks)
    pls = []

    jingles_to_play = [choice(jingles.tracks) for i in range(5)]
    jingles_duration = sum(jingle.duration for jingle in jingles_to_play)
    jingles_duration = 0
#    print "-".join(str(x.id)+x.dt for x in jingles_to_play), jingles_duration

    for i in range(30):
        path = pack(DAY-jingles_duration, gen)
        pls.append((score(path), path))
        gen.shuffle()

    pls.sort()
    print_playlist(pls[0][1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tracks", dest="tracks", default="tracks", help="tracks file")
    parser.add_argument("-j", "--jingles", dest="jingles", default="jingles", help="jingles file")
    parser.add_argument("-d", "--duration", dest="duration", default="86400.0", help="duration")
    args = parser.parse_args()

    main(args)
