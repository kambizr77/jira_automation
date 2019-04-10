
REQUIRED = []
with open('./requirements.txt') as f:
    for line in f:
        REQUIRED.append(line.strip())



with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Box Jira Tools',
    version='0.0.1',
    description="Internal patching team tools",
    long_description=readme,
    author='Kambiz Rahmani',
    author_email='kambizrahmani@box.com',
    url='https://git.dev.box.net/kambizrahmani/patching_tools',
    license=license,
    install_requires=REQUIRED,
)
