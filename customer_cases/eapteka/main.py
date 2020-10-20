import faulthandler
import logging

from customer_cases.eapteka import run

faulthandler.enable()
logging.basicConfig(format='%(message)s', level=logging.INFO)

TYPE = 'bicycle'

run.run_pharmacy(
    type_m=TYPE,
    time_pharmacy=5,
    time_depot=10,
    type_weight=15,
    type_capacity=30,
    driver_weight=200,
    driver_capacity=400,
    delay=5,
    fg='26',  # номер результата
)
