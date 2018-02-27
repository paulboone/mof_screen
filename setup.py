from setuptools import setup, find_packages
import versioneer

setup(
    name="mof_screen",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        'lammps_interface',
    ],
    include_package_data=True,
    packages=find_packages(),
    entry_points={
          'console_scripts': [
              'gen_mof_flex_ff_rigid_molecule_lammps_config = mof_screen.gen_mof_flex_ff_rigid_molecule_lammps_config:cmdline'
          ]
      },
)
