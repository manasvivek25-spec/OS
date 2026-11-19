import sys
sys.path.insert(0, '/mnt/c/Users/len/OS/src')
from lazy.policy.manifest import ManifestLoader
m = ManifestLoader(['/mnt/c/Users/len/OS/config/capabilities'])
print('Count:', len(m.list_capabilities()))
print('Caps:', m.list_capabilities())
