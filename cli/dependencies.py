import pip


def install_compatible_omise():
    pip.main(["uninstall", "--yes", "omise"])
    pip.main(
        [
            "install",
            "git+https://github.com/omise/omise-python@bfcf283378a823139b9f19f10e84d42a98c5b1ac",
        ]
    )
