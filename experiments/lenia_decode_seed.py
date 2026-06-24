"""
Decode official Lenia animal seeds from animals.json.
Uses the ch2val/rle2arr logic from the official LeniaND.py.
"""
import sys, json, numpy as np

# Constants matching official Lenia
DIM = 2
DIM_DELIM = {0: '', 1: '$', 2: '%', 3: '#', 4: '@A', 5: '@B', 6: '@C', 7: '@D', 8: '@E', 9: '@F'}

def ch2val(c):
    if c in '.b': return 0
    elif c == 'o': return 255
    elif len(c) == 1: return ord(c)-ord('A')+1
    else: return (ord(c[0])-ord('p')) * 24 + (ord(c[1])-ord('A')+25)

def val2ch(v):
    if v == 0: return ' .'
    elif v < 25: return ' ' + chr(ord('A')+v-1)
    else: return chr(ord('p') + (v-25)//24) + chr(ord('A') + (v-25)%24)

def _append_stack(list1, list2, count, is_repeat=False):
    list1.append(list2)
    if count != '':
        repeated = list2 if is_repeat else []
        list1.extend([repeated] * (int(count)-1))

def _recur_get_max_lens(dim, list1, max_lens):
    max_lens[dim] = max(max_lens[dim], len(list1))
    if dim < DIM-1:
        for list2 in list1:
            _recur_get_max_lens(dim+1, list2, max_lens)

def _recur_cubify(dim, list1, max_lens):
    more = max_lens[dim] - len(list1)
    if dim < DIM-1:
        list1.extend([[]] * more)
        for list2 in list1:
            _recur_cubify(dim+1, list2, max_lens)
    else:
        list1.extend([0] * more)

def rle2arr(st):
    stacks = [[] for _ in range(DIM)]
    last, count = '', ''
    delims = list(DIM_DELIM.values())
    st = st.rstrip('!') + DIM_DELIM[DIM-1]
    for ch in st:
        if ch.isdigit(): count += ch
        elif ch in 'pqrstuvwxy@': last = ch
        else:
            if last+ch not in delims:
                _append_stack(stacks[0], ch2val(last+ch)/255, count, is_repeat=True)
            else:
                dim = delims.index(last+ch)
                for d in range(dim):
                    _append_stack(stacks[d+1], stacks[d], count, is_repeat=False)
                    stacks[d] = []
            last, count = '', ''
    A = stacks[DIM-1]
    max_lens = [0 for _ in range(DIM)]
    _recur_get_max_lens(0, A, max_lens)
    _recur_cubify(0, A, max_lens)
    return np.asarray(A)

if __name__ == '__main__':
    # Load animals.json
    with open('exploring/Lenia/Python/animals.json', 'r', encoding='utf-8') as f:
        animals = json.load(f)
    
    # Find and decode all Orbium species
    def find_animals(data, species_list=None):
        if species_list is None:
            species_list = []
        for item in data:
            if 'params' in item and 'cells' in item:
                species_list.append(item)
            for key in item:
                if isinstance(item[key], list):
                    find_animals(item[key], species_list)
        return species_list
    
    species = find_animals(animals)
    print(f"Found {len(species)} species with seed patterns\n")
    
    # Decode first 5 Orbium species
    count = 0
    for sp in species:
        code = sp.get('code', '?')
        name = sp.get('name', '?')
        params = sp.get('params', {})
        cells_str = sp.get('cells', '')
        
        if code.startswith('O') or code.startswith('S'):
            cells = rle2arr(cells_str)
            print(f"[{code}] {name}")
            print(f"  Params: R={params.get('R')}, m={params.get('m')}, s={params.get('s')}, kn={params.get('kn')}, gn={params.get('gn')}, b={params.get('b')}")
            print(f"  Seed shape: {cells.shape}")
            print(f"  Seed range: [{cells.min():.4f}, {cells.max():.4f}]")
            print(f"  Seed mean: {cells.mean():.4f}")
            print(f"  Alive cells (>0.01): {(cells > 0.01).sum()} / {cells.size}")
            
            # Save the seed for use with JAX Lenia
            np.save(f'experiments/lenia_seed_{code}.npy', cells)
            print(f"  Saved: experiments/lenia_seed_{code}.npy")
            print()
            count += 1
            if count >= 10:
                break
