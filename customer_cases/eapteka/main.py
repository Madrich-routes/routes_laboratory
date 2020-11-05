import faulthandler
import logging

from customer_cases.eapteka import run

faulthandler.enable()
logging.basicConfig(format='%(message)s', level=logging.INFO)

# TYPE = 'pedestrian'
# TYPE = 'bicycle'
TYPE = 'transport_simple'
# TYPE = 'transport_complex'

run.run_pharmacy(
    type_m=TYPE,
    time_pharmacy=5,
    time_depot=10,
    type_weight=15,
    type_capacity=40,
    driver_weight=200,
    driver_capacity=400,
    delay=5,
    fg=TYPE + "_1_bet",  # номер результата
)

def main():
    ...

if __name__ == "__main__":
    main()
