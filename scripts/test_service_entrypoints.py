import sys
sys.path.insert(0, '/mnt/c/Users/len/OS/src')
mods = [
    'lazy.audit.service',
    'lazy.policy.service',
    'lazy.planner.service',
    'lazy.tasks.service',
    'lazy.secrets.server',
    'lazy.brokers.fs_service',
    'lazy.brokers.web_service',
    'lazy.brokers.hw_service',
    'lazy.brokers.sys_service',
    'lazy.brokers.comms_service',
    'lazy.routines.service',
    'lazy.niche.fetch_service',
    'lazy.outbox.service',
    'lazy.llm.service',
    'lazy.gateway.server'
]

for m in mods:
    try:
        mod = __import__(m, fromlist=['main'])
        has_main = hasattr(mod, 'main')
        print(f'[OK] {m} (has_main={has_main})')
    except Exception as e:
        print(f'[FAIL] {m}: {e}')
