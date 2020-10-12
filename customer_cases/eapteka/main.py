import faulthandler
import logging

from customer_cases.eapteka import run

faulthandler.enable()
logging.basicConfig(format='%(message)s', level=logging.INFO)

TYPE = 'transport_simple_2'

run.run_pharmacy(type_m=TYPE,
                 time_pharmacy=1,
                 time_depot=1,
                 type_weight=15,
                 type_capacity=30,
                 driver_weight=200,
                 driver_capacity=400,
                 delay=1,
                 fg='25')
