def pytest_addoption(parser):
    parser.addoption("--t", action="store", default="butter_fingers_perturbation")


def pytest_generate_tests(metafunc):
    option_value = metafunc.config.option.t
    if "perturbation_type" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("perturbation_type", [option_value])
