from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.database import ExampleDatabase

default_profile = settings(
    max_examples=100,
    print_blob=True,
    deadline=1000,
    database=ExampleDatabase(settings.DATA_DIR / 'tmp/hypothesis'),
)

matrix_size_st = st.integers(min_value=0, max_value=15)
