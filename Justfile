lint:
    pylint .; flake8

test:
    pytest --hypothesis-show-statistics --tb=no -n=$(nproc)

isort:
    isort -e -m 4 -w 120 -y

pyanalyze:
    python -m pyanalyze --parallel -e condition_always_true -e method_first_arg -d incompatible_assignment -d unsupported_operation \
    -d possibly_undefined_name mw_flow_calculator

dockformat:
    docformatter -i -r --wrap-summaries 110 --wrap-descriptions 110 .

version v:
    poetry version {{v}} && dephell deps convert && git commit -am 'version++'
