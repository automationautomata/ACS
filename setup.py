import os

from setuptools import setup

package_name = 'pyvistaqt'
req = '''certifi==2024.7.4
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
docutils==0.21.2
idna==3.8
Kivy==2.3.0
kivy-deps.angle==0.4.0
kivy-deps.glew==0.3.1
kivy-deps.sdl2==0.7.0
Kivy-Garden==0.1.5
Pygments==2.18.0
pypiwin32==223
pyserial==3.5
pywin32==306
requests==2.32.3
schedule==1.2.2
tornado==6.4.1
urllib3==2.2.2'''.split('\n')
print(req)
setup(
    name=package_name,
    packages=[package_name, package_name],
    description='SKUD',
    license='MIT',
    python_requires='>=3.7',
    setup_requires=["setuptools>=45", "setuptools_scm>=6.2"],
    install_requires=req
)
