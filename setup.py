from setuptools import setup, find_packages

install_requires = [
      'pefile',
      'click'
]

test_requires = [
      'pytest'
]

setup(name='dfrus64',
      version='0.0.1',
      # description='',
      url='https://github.org/dfint/dfrus64',
      author='insolor',
      author_email='insolor@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=install_requires,
      test_requires=test_requires,
      zip_safe=False)
