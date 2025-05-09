class TravelPackageDB:
    def __init__(self):
        self.packages = []

    def add_package(self, package):
        self.packages.append(package)

    def get_all_packages(self):
        return self.packages