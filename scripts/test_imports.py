import sys
sys.path.insert(0, '/mnt/c/Users/len/OS/src')
mods = [
    'lazy.audit.service',
    'lazy.brokers.comms_service',
    'lazy.brokers.fs_service',
    'lazy.brokers.hw_service',
    'lazy.brokers.sys_service',
    'lazy.brokers.web_service',
    'lazy.niche.fetch_service',
    'lazy.gateway.server',
    'lazy.llm.service',
    'lazy.outbox.service',
    'lazy.planner.service',
    'lazy.policy.service',
    'lazy.routines.service',
    'lazy.secrets.server',
    'lazy.tasks.service',
    'lazy.tuning.warmup'
]
for m in mods:
    try:
        __import__(m)
        print(f'[OK] {m}')
    except Exception as e:
        print(f'[FAIL] {m}: {e}')
