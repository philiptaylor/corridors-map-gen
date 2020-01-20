import graphviz
import csv
import itertools
import os
import json
import svgwrite
import math
import urllib
import copy
import random

def canon_side(s):
    combs = (
        [s[i] for i in (0,1,2,3,4,5,6)],
        [s[i] for i in (1,4,0,3,6,2,5)],
        [s[i] for i in (4,6,1,3,5,0,2)],
        [s[i] for i in (6,5,4,3,2,1,0)],
        [s[i] for i in (5,2,6,3,0,4,1)],
        [s[i] for i in (2,0,5,3,1,6,4)],

        # Try mirroring too
        [s[i] for i in (1,0,4,3,2,6,5)],
        [s[i] for i in (4,1,6,3,0,5,2)],
        [s[i] for i in (6,4,5,3,1,2,0)],
        [s[i] for i in (5,6,2,3,4,0,1)],
        [s[i] for i in (2,5,0,3,6,1,4)],
        [s[i] for i in (0,2,1,3,5,4,6)],
    )
    return ''.join(sorted(combs)[0])

node_dupes = set()

url_blacklist = set()
with open('url-blacklist.txt') as file:
    for line in file:
        url_blacklist.add(line.strip())
        
nodes = []
def read_csv(fn):
    with open(fn, newline='') as csvfile:
        header = True
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            if header:
                header = False
                continue
            #print(row)
            url, center, sides_open, s1, s2, s3, s4, s5, s6, conf, trans_hash, count, rot = row
            if sides_open == '':
                sides_open = []
            else:
                sides_open = [int(s) for s in sides_open.split(',')]
                
            # XXX
            #sides_open = [i+1 for i in range(6) if i+1 not in sides_open]
            
            ok = True
            for s in [s1,s2,s3,s4,s5,s6]:
                if len(s) != 7:
                    print("Bad side '%s'" % s)
                    ok = False
            if ok:
                nodes.append( { 'url': url, 'center': center, 'open': sides_open, 'sides': [s1, s2, s3, s4, s5, s6], 'input': row, 'confidence': 1000 } )

def read_csv2(fn):
    with open(fn, newline='') as csvfile:
        header = True
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            if header:
                header = False
                continue
            #print(row)
            url, center, sides_open, s1, s2, s3, s4, s5, s6 = row[0:9]
            if center == "": continue
            if sides_open == "" or sides_open == "None":
                sides_open = []
            else:
                sides_open = [int(s)+1 for s in sides_open.split(',')]
            ok = True

            if any(s < 1 or s > 6 for s in sides_open):
                print("bad sides %s" % sides_open)
                ok = False

            for s in [s1,s2,s3,s4,s5,s6]:
                if len(s) != 7:
                    #print("Bad side '%s'" % s)
                    ok = False
            center = center[0].upper()
            if ok:
                nodes.append( { 'url': url, 'center': center, 'open': sides_open, 'sides': [s1, s2, s3, s4, s5, s6], 'input': row, 'confidence': 10 } )


def read_csv3(fn):
    with open(fn, newline='') as csvfile:
        header = True
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            if header:
                header = False
                continue
            #print(row)
            url, center, sides_open, s1, s2, s3, s4, s5, s6 = row[0:9]
            if center == "": continue
            sides_open = sides_open.replace(".", ",")
            if sides_open == "" or sides_open == "None":
                sides_open = []
            else:
                sides_open = [int(s) for s in sides_open.split(',')]
            ok = True

            if any(s < 1 or s > 6 for s in sides_open):
                print("bad sides %s" % sides_open)
                ok = False

            for s in [s1,s2,s3,s4,s5,s6]:
                if len(s) != 7:
                    #print("Bad side '%s'" % s)
                    ok = False
            center = center[0].upper()
            if ok:
                nodes.append( { 'url': url, 'center': center, 'open': sides_open, 'sides': [s1, s2, s3, s4, s5, s6], 'input': row, 'confidence': 0 } )

def read_csv4(fn):
    with open(fn, newline='') as csvfile:
        header = True
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            if header:
                header = False
                continue
            #print(row)
            url, _, _, bad_img, orientation, center, sides_open, s1, s2, s3, s4, s5, s6, _ = row
            if sides_open == '':
                sides_open = []
            else:
                sides_open = [int(s) for s in sides_open.split(',')]
            
            if bad_img == 'True': continue
            #if orientation: continue
            
            # XXX
            #sides_open = [i+1 for i in range(6) if i+1 not in sides_open]
            
            ok = True
            for s in [s1,s2,s3,s4,s5,s6]:
                if len(s) != 7:
                    #print("Bad side '%s'" % s)
                    ok = False
            if ok:
                nodes.append( { 'url': url, 'center': center, 'open': sides_open, 'sides': [s1, s2, s3, s4, s5, s6], 'input': row, 'confidence': -100 } )

def read_csv5(fn):
    with open(fn, newline='') as csvfile:
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            url, center, sides_open, s1, s2, s3, s4, s5, s6, _ = row
            sides_open = [int(s) for s in sides_open]
                
            ok = True
            for s in [s1,s2,s3,s4,s5,s6]:
                if len(s) != 7:
                    print("Bad side '%s'" % s)
                    ok = False
            if ok:
                nodes.append( { 'url': url, 'center': center, 'open': sides_open, 'sides': [s1, s2, s3, s4, s5, s6], 'input': row, 'confidence': 2000 } )

def read_csv6(fn):
    with open(fn, newline='') as csvfile:
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            src, _, url, center, sides_open, s1, s2, s3, s4, s5, s6, _, verified = row[0:13]
            if center == "": continue

            orig_sides_open = sides_open
            sides_open = sides_open.strip().replace(" and ", ",").replace("side ", "").replace("Side ", "").replace(".", ",").replace(" ", ",").replace(",,", ",")
            if sides_open in ("None", "N/A", ",", "Blank", "???", "4,6B", "5e", "Don't,Know", "_", "Side5"):
                continue
            else:
                try:
                    sides_open = [int(s) for s in sides_open.split(',') if s != '' and int(s) >= 1 and int(s) <= 6]
                    #if any(s < 1 or s > 6 for s in sides_open):\n",
                    #    print(repr(orig_sides_open))\n",
                except ValueError as e:
                    print(repr(orig_sides_open))
                    raise e
                
                #sides_open = sides_open.replace(".", ",")
            #if sides_open == "" or sides_open == "None":
            #    sides_open = []
            #else:
            #    sides_open = [int(s) for s in sides_open.split(',')]
            ok = True

            if any(s < 1 or s > 6 for s in sides_open):
                print("bad sides %s" % sides_open)
                ok = False

            for s in [s1,s2,s3,s4,s5,s6]:
                if len(s) != 7:
                    print("Bad side '%s'" % s)
                    ok = False
            center = center[0].upper()
            if ok:
                nodes.append( { 'url': url, 'center': center, 'open': sides_open, 'sides': [s1, s2, s3, s4, s5, s6], 'input': row,
                               #'confidence': (1000 if verified == 'VERIFIED' else 0)
                               'confidence': 0
                              } )

def read_csv7(fn):
    with open(fn, newline='') as csvfile:
        header = True
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            if header:
                header = False
                continue
            src, _, url, center, sides_open, s1, s2, s3, s4, s5, s6, _, verified, _ = row[0:14]
            if center == "": continue

            orig_sides_open = sides_open
            sides_open = sides_open.strip().replace(" and ", ",").replace("side ", "").replace("Side ", "").replace(".", ",").replace(" ", ",").replace(",,", ",")
            if sides_open in ("None", "N/A", ",", "Blank", "???", "4,6B", "5e", "Don't,Know", "_", "Side5"):
                continue
            else:
                try:
                    sides_open = [int(s) for s in sides_open.split(',') if s != '' and int(s) >= 1 and int(s) <= 6]
                    #if any(s < 1 or s > 6 for s in sides_open):\n",
                    #    print(repr(orig_sides_open))\n",
                except ValueError as e:
                    print(repr(orig_sides_open))
                    raise e
                
                #sides_open = sides_open.replace(".", ",")
            #if sides_open == "" or sides_open == "None":
            #    sides_open = []
            #else:
            #    sides_open = [int(s) for s in sides_open.split(',')]
            ok = True

            if any(s < 1 or s > 6 for s in sides_open):
                print("bad sides %s" % sides_open)
                ok = False

            for s in [s1,s2,s3,s4,s5,s6]:
                if len(s) != 7:
                    print("Bad side '%s'" % s)
                    ok = False
            center = center[0].upper()
            if ok:
                nodes.append( { 'url': url, 'center': center, 'open': sides_open, 'sides': [s1, s2, s3, s4, s5, s6], 'input': row, 'confidence': (1000 if verified == 'VERIFIED' else 0) } )


read_csv('d:/games/destiny2/crunch8.csv')
read_csv2('Copy of Explorers Vault Master List - Primary.csv')
read_csv3('master.csv')
read_csv4('crunchall5.csv')
read_csv5('d:/games/destiny2/self-confirmed.csv')
#read_csv6('combined_out.csv')
#read_csv6('20-01-19_1400pt_combined_out.csv')
read_csv7('combined_out_20200119_185845.csv')

#print(nodes)

print('Total nodes with dupes: %d' % len(nodes))

# Dupe removal:

# Remove URL dupes if very confident
nodes_url = {}
for node in nodes:
    key = node['url']
    nodes_url.setdefault(key, []).append(node)
nodes = []
for ns in nodes_url.values():
    ns = sorted(ns, key = lambda n: -n['confidence'])
    if ns[0]['confidence'] >= 2000:
        nodes.append(ns[0])
    else:
        nodes += ns

# Remove exact dupes
nodes_unique = {}
for node in nodes:
    key = (node['center'], tuple(node['open']), tuple(node['sides']))
    nodes_unique.setdefault(key, []).append(node)
nodes = [ sorted(ns, key = lambda n: -n['confidence'])[0] for ns in nodes_unique.values() ]

print('Total nodes minus exact dupes: %d' % len(nodes))

if 1:
    # Find 'similar' nodes (3+ sides identical)
    # Sort by likeliness (e.g. number of nodes sharing that side)
    side_freq = {}
    partial_sides_to_dupe_group = {}
    dupe_groups = []
    for node in nodes:
        for i in range(6):
            side = node['sides'][i]
            side_freq[(side, i)] = side_freq.get((side, i), 0) + 1

        #if len([s for s in node['sides'] if s == 'BBBBBBB']) == 0:
        #    continue

        group_id = None
        for side_ids in itertools.combinations(range(6), 3):
            bad_sides = False
            partial_sides = ''
            for i in side_ids:
                # Don't match duplicates based on blank sides
                if node['sides'][i] == 'BBBBBBB':
                    bad_sides = True
                partial_sides += node['sides'][i]

            # If we match another node, put this node in that one's dupe group
            # If there are no matches, put this in a new dupe group
            if not bad_sides and partial_sides in partial_sides_to_dupe_group:
                group_id = partial_sides_to_dupe_group[partial_sides]
                break

        if group_id is None:
            group_id = len(dupe_groups)
            dupe_groups.append([])
            partial_sides_to_dupe_group[partial_sides] = group_id
        dupe_groups[group_id].append(node)
        node['dupe_group'] = group_id

    nodes = []
    for group_nodes in dupe_groups:
        if len(group_nodes) > 1:
            #print(group_nodes)
            group_nodes = sorted(group_nodes,
                                 key = lambda n:
                                     (-n['confidence']/1000,
                                      -sum(side_freq.get((n['sides'][i], (i+3)%6), 0) for i in range(6))
                                     )
                                )
        nodes.append(group_nodes[0])
        #nodes += group_nodes

# Delete bogus entrances/exit
def is_bad_entrance(node):
    is_entrance = False
    for i in range(6):
        if i+1 in node['open'] and node['sides'][i] == 'BBBBBBB':
            is_entrance = True
    if not is_entrance:
        return False
    if is_entrance and node['sides'][2] == 'CHBDBCD':
        return False
    if is_entrance and node['sides'][0] == 'DTSTDDP':
        return False
    return True

# Delete impossible cases
def is_bad_walls(node):
    if len(node['open']) >= 6:
        return True
    if len(node['open']) <= 0:
        return True
    return False

nodes = [ n for n in nodes if not is_bad_entrance(n) and not is_bad_walls(n) and n['url'] not in url_blacklist ]
        
for i in range(len(nodes)):
    nodes[i]['id'] = i
        
print('Total nodes: %d' % len(nodes))
print('Edge nodes: %d' % len(list(n for n in nodes if any(s for s in n['sides'] if s == 'BBBBBBB'))))
for i in range(7):
    print('%d blank: %d' % (i, len(list(n for n in nodes if i == len(list(s for s in n['sides'] if s == 'BBBBBBB'))))))


blacklist = set([ ])

# side_to_node = { ('ABCD etc', 1): [ node id, ... ] }
side_to_node = {}
for node in nodes:
    if node['id'] in blacklist: continue
    for i in range(6):
        side = node['sides'][i]
        side_to_node.setdefault((side, i), []).append(node['id'])

canon_side_to_node = {}
for node in nodes:
    if node['id'] in blacklist: continue
    for i in range(6):
        side = node['sides'][i]
        canon_side_to_node.setdefault(canon_side(side), []).append(node['id'])


hex_r = 16
hex_sep = 32

def dir_to_offset(dir):
    return ( (0, -2), (1, -1), (1, 1), (0, 2), (-1, 1), (-1, -1) )[dir]

def add_hexagon(dr, x, y, center, walls, sides, node):
    if len(node['url']):
        url = 'view.html?' + ','.join([
            node['url'],
            node['center'],
            ''.join([str(i) for i in node['open']]),
            *node['sides']
        ])
        link = dr.add(dr.a(url))
    else:
        link = dr
    g = link.add(dr.g())

    bg_color = '#ffffff'
    if node['confidence'] >= 2000:
        bg_color = '#ffff00'
    elif node['confidence'] >= 1000:
        bg_color = '#ffffe0'
    bg_hex = g.add(dr.polyline(fill=bg_color))
    
    g.translate(x * hex_sep*math.cos(math.pi/6), y * hex_sep/2)
    for i in range(6):
        a0 = 2*math.pi*(i-0.5)/6
        a1 = 2*math.pi*(i+0.5)/6
        if sides and sides[i] == 'BBBBBBB' and not walls[i]:
            g.add(dr.line(start=(hex_r*math.sin(a0), -hex_r*math.cos(a0)), end=(hex_r*math.sin(a1), -hex_r*math.cos(a1)),
                     stroke='green', stroke_width=4))
        elif sides and sides[i] == 'BBBBBBB':
            g.add(dr.line(start=(hex_r*math.sin(a0), -hex_r*math.cos(a0)), end=(hex_r*math.sin(a1), -hex_r*math.cos(a1)),
                     stroke='red', stroke_width=4))
        elif walls[i]:
            g.add(dr.line(start=(hex_r*math.sin(a0), -hex_r*math.cos(a0)), end=(hex_r*math.sin(a1), -hex_r*math.cos(a1)),
                     stroke='blue', stroke_width=2))
        else:
            g.add(dr.line(start=(hex_r*math.sin(a0), -hex_r*math.cos(a0)), end=(hex_r*math.sin(a1), -hex_r*math.cos(a1)),
                     stroke='gray', stroke_width=1))
        if center != 'B':
            g.add(dr.text(center))
            
        bg_hex.points.append( (hex_r*math.sin(a0), -hex_r*math.cos(a0)) )

def add_dummy_hexagon(dr, x, y, off_x, off_y, dense_map):
    #g = dr.add(dr.g())
    #link = dr.add(dr.a("data:text/plain,%s" % title))
    
    # Check neighbours
    # For each side facing us, find all nodes with that side (or any rotation)
    # List them all

    candidates = set()
    canon_sides = set()
    for d in range(6):
        off = dir_to_offset(d)
        neighbour = dense_map.get( (x + off[0], y + off[1]), None)
        if neighbour and 'dummy' not in neighbour: #and neighbour['confidence'] < 2000:
            s = neighbour['sides'][(d+3)%6]
            if s != 'BBBBBBB':
                cs = canon_side(s)
                candidates |= set(canon_side_to_node.get(cs, []))
                canon_sides.add(cs)

    if len(candidates) == 0:
        return
                
    cand_links = []
    best_cand = 0
    for node_id in candidates:
        node = nodes[node_id]
        best_cand = max(best_cand, len([ 1 for s in node['sides'] if canon_side(s) in canon_sides ]))
        cand_links.append('%s%s <a href="view.html?%s">%s</a>' % (
            ('(confirmed?) ' if node['confidence'] >= 2000 else ''),
            ' '.join([
                node['center'],
                ''.join([str(i) for i in node['open']]),
                *[ ('<b>%s</b>' % s if canon_side(s) in canon_sides else s) for s in node['sides'] ]
            ]),
            ','.join([
                node['url'],
                node['center'],
                ''.join([str(i) for i in node['open']]),
                *node['sides']
            ]),
            node['url']
        ))
        
    if best_cand < 2:
        return
                          
    url = 'multi.html?' + urllib.parse.quote('<br>'.join(cand_links))
    link = dr.add(dr.a(url))
    g = link.add(dr.g())

    bg_color = '#e0e0e0'
    bg_hex = g.add(dr.polyline(fill=bg_color))
    
    g.translate((x + off_x) * hex_sep*math.cos(math.pi/6), (y + off_y) * hex_sep/2)
    for i in range(6):
        a0 = 2*math.pi*(i-0.5)/6
        a1 = 2*math.pi*(i+0.5)/6
        bg_hex.points.append( (hex_r*math.sin(a0), -hex_r*math.cos(a0)) )

def add_edge(dr, x, y, dir):

    r = hex_r*math.cos(math.pi/6)
    offset = dir_to_offset(dir)
    x0 = x*hex_sep*math.cos(math.pi/6) + r*math.sin(math.pi*dir/3)
    y0 = y*hex_sep/2 + r*-math.cos(math.pi*dir/3)
    x1 = (x+offset[0])*hex_sep*math.cos(math.pi/6) - r*math.sin(math.pi*dir/3)
    y1 = (y+offset[1])*hex_sep/2 - r*-math.cos(math.pi*dir/3)
    
    dr.add(dr.line(start=(x0, y0), end=(x1, y1),
                     stroke='black', stroke_width=2))

def add_edge2(dr, x0, y0, x1, y1):

    x0 = x0*hex_sep*math.cos(math.pi/6)
    y0 = y0*hex_sep/2
    x1 = x1*hex_sep*math.cos(math.pi/6)
    y1 = y1*hex_sep/2
    
    dr.add(dr.line(start=(x0, y0), end=(x1, y1),
                     stroke='#ff0000', stroke_width=2))

    
dr = svgwrite.Drawing("test.svg", (2000, 4000))

# Smaller number == preferred
def node_score(n):
    node = nodes[n]
    is_emblem_entrance = False
    is_big_entrance = False
    is_entrance = False
    for i in range(6):
        if i+1 in node['open'] and node['sides'][i] == 'BBBBBBB':
            is_entrance = True
    if is_entrance and node['sides'][1] == 'DHDSPTT':
        is_emblem_entrance = True
    if is_entrance and node['sides'][2] == 'CHBDBCD':
        is_big_entrance = True
    
    return ((0 if is_emblem_entrance else 1), (0 if is_big_entrance else 1), (0 if is_entrance else 1))

cluster_x = 1
cluster_y = 1
cluster_ynext = 1

#print(side_to_node)

def try_fill_gap(gap, min_matches, min_conf, flip_walls=False):
    # Find candidates that match >= 1 neighbouring edge
    candidates = set()
    for d in range(6):
        off = dir_to_offset(d)
        neighbour = cluster_map.get( (gap[0] + off[0], gap[1] + off[1]), None)
        if neighbour:
            #if neighbour['confidence'] < min_conf:
            #    continue
            s = neighbour['sides'][(d+3)%6]
            if s != 'BBBBBBB':
                candidates |= set(side_to_node.get( (s, d), [] ))

    for cand in candidates:
        if cand not in free_nodes:
            continue

        cand = nodes[cand]
        
        if cand['confidence'] < min_conf:
            continue

        # XXX: if min_matches = 1, reject ambiguous sides

        matches = 0
        mismatches = 0
        for d in range(6):
            off = dir_to_offset(d)
            neighbour = cluster_map.get( (gap[0] + off[0], gap[1] + off[1]), None)
            if neighbour:
                is_open = d+1 in cand['open']
                if flip_walls:
                    is_open = not is_open
                if cand['sides'][d] == neighbour['sides'][(d+3)%6] and \
                    is_open == (((d+3)%6)+1 in neighbour['open']):
                    if cand['sides'][d] != 'BBBBBBB':
                        matches += 1
                else:
                    mismatches += 1

        if matches >= min_matches and mismatches == 0:
            if flip_walls:
                cand['open'] = [ i for i in range(1, 7) if i not in cand['open'] ]
            cluster.append(cand['id'])
            cluster_map[gap] = cand
            free_nodes.remove(cand['id'])
            gaps.remove(gap)
            for d in range(6):
                off = dir_to_offset(d)
                new_gap = (gap[0] + off[0], gap[1] + off[1])
                if new_gap not in cluster_map and cand['sides'][d] != 'BBBBBBB':
                    gaps.add(new_gap)

            return True
    
    return False

def create_dense_map(sparse_map, min_x, min_y, max_x, max_y):
    cluster_map = dict(sparse_map)
    for y in range(min_y, max_y+1):
        for x in range(min_x, max_x+1):
            if (x + y) % 2 == 0:
                if (x, y) not in sparse_map:
                    walls = set()
                    
                    if x == min_x:
                        walls.add(4)
                        walls.add(5)
                        walls.add(6)
                    elif x == min_x+1:
                        walls.add(5)
                    if x == max_x:
                        walls.add(1)
                        walls.add(2)
                        walls.add(3)
                    elif x == max_x-1:
                        walls.add(2)
                    if y == min_y:
                        walls.add(1)
                        walls.add(2)
                        walls.add(6)
                    elif y == min_y+1:
                        walls.add(2)
                    if y == max_y:
                        walls.add(3)
                        walls.add(4)
                        walls.add(5)
                    elif y == max_y-1:
                        walls.add(4)
                        
                    for d in range(6):
                        off = dir_to_offset(d)
                        neighbour = (x + off[0], y + off[1])
                        if neighbour in sparse_map:
                            if (d+3)%6+1 not in sparse_map[neighbour]['open']:
                                walls.add(d+1)
                        
                    cluster_map[(x, y)] = {
                        'dummy': True,
                        'open': [i for i in range(1,7) if i not in walls]
                    }
    return cluster_map
    

def find_path(rng, cluster_map, start, goal):
    found = False
    path = []
    explored = set()
    open_nodes = [start]
    preds = { start: None }
    
    while len(open_nodes):
        curr = open_nodes.pop()
        curr_node = cluster_map[curr]
        new_open = []
        for d in range(6):
            if d+1 in curr_node['open']:
                off = dir_to_offset(d)
                neighbour = (curr[0] + off[0], curr[1] + off[1])
                if neighbour in cluster_map:
                    if neighbour in open_nodes:
                        pass
                    elif neighbour in preds:
                        pass
                    else:
                        preds[neighbour] = curr
                        new_open.append(neighbour)
                        
                        explored.add((curr, neighbour))
                        
                        if neighbour == goal:
                            found = True
                            break
    
        rng.shuffle(new_open)
        open_nodes += new_open
    
        if found:
            break
    
    if found:
        curr = goal
        while curr:
            pred = preds[curr]
            if pred:
                path.append( (pred, curr) )
            curr = pred
    
    return path
    #return explored

def path_to_str(cluster_map, edges):
    out = []
    for p0,p1 in edges:
        if p1 in cluster_map:
            c = cluster_map[p1]['center']
            if c != 'B':
                out.append(c)
        else:
            pass
            #if len(out) and out[-1] != '?':
            #    out.append('?')
    return ''.join(out)
    
free_nodes = set(range(len(nodes)))
clusters = []
while len(free_nodes):
    n = sorted(free_nodes, key=node_score)[0]
    free_nodes.remove(n)
    
    # List of node IDs in this cluster
    cluster = [n]
    # Map from coordinates to nodes
    cluster_map = { (0, 0): nodes[n] }
    # List of adjacent gap coordinates, i.e. currently empty and waiting to be filled in
    gaps = set([ (0, -2), (1, -1), (1, 1), (0, 2), (-1, 1), (-1, -1) ])
    
    i = 0
    while 1:
        i += 1
        if i % 100 == 0:
            print("%d..." % i)
        found = False
        
        attempts = (
            # neighbours reqd; min conf; wall flip
            (2, 2000, False),
            (1, 2000, False),
            (3, 1000, False),
            (2, 1000, False),
            (3, 0, False),
            (2, 0, False),
            (1, 0, False),
            #(3, -100, False),
            #(2, -100, False),
            #(1, -100, False),
            (3, 1000, True),
            (3, 0, True),
            (4, -100, False),
            (3, -100, False),
            (2, -100, False),
        )

        for (reqd, min_conf, flip_walls) in attempts:
            if not found:
                for gap in gaps:
                    if try_fill_gap(gap, reqd, min_conf=min_conf, flip_walls=flip_walls):
                        found = True
                        break
                        
        if not found: break
    
    min_x = min(x for x,y in cluster_map.keys())
    max_x = max(x for x,y in cluster_map.keys())
    min_y = min(y for x,y in cluster_map.keys())
    max_y = max(y for x,y in cluster_map.keys())
    
    #print(max_x - min_x, max_y - min_y)
    
    entrances = []

    #print("Create dense")
    
    dense_map = create_dense_map(cluster_map, min_x, min_y, max_x, max_y)
    
    #print("SVG hex")
    
    for pos,node in dense_map.items():
        if 'dummy' in node:
            add_dummy_hexagon(dr,
                        pos[0], pos[1],
                        -min_x + cluster_x, -min_y + cluster_y,
                        dense_map)
        else:
            walls = [1,1,1,1,1,1]
            for w in node['open']:
                walls[w-1] = 0
            add_hexagon(dr,
                        pos[0] - min_x + cluster_x, pos[1] - min_y + cluster_y,
                        node['center'], walls, node['sides'], node)

            for i in range(6):
                if node['sides'][i] == 'BBBBBBB' and i+1 in node['open']:
                    entrances.append(pos)
    
    #print("Finding paths")
    
    if len(entrances) >= 2:
        rng = random.Random(0)
        # Find a randomised path between entrances
        all_edges = set()
        for i in range(100):
            path_edges = find_path(rng, dense_map, entrances[0], entrances[1])
            all_edges |= set(path_edges)
            print("Path %d %s" % (len(path_edges), path_to_str(cluster_map, path_edges)))
        for edge in all_edges:
            add_edge2(dr,
                      edge[0][0] - min_x + cluster_x,
                      edge[0][1] - min_y + cluster_y,
                      edge[1][0] - min_x + cluster_x,
                      edge[1][1] - min_y + cluster_y,
                     )
    
    cluster_ynext = max(cluster_ynext, cluster_y + max_y - min_y + 2 + 1)
    if cluster_x < 30:
        cluster_x += max_x - min_x + 2
    else:
        cluster_x = 1
        cluster_y = cluster_ynext

    clusters.append(cluster)
    
    if len(cluster) > 100:
        print("Cluster size %d" % len(cluster))

dr.save()
