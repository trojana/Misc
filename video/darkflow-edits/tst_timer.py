# !python

import os
import sys
import time

# time measurement
print('Stopclock running... (be patient)' )
stme = time.time()

time.sleep(1)

# time measurement
etme = time.time()
secs=etme-stme
print('Done. Elapsed time: ',  secs, 'secs (', stme, etme, ')')
    
