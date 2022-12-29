# Copyright © 2012-2020 Piotr Ożarowski <piotr@debian.org>
#           © 2020 Scott Kitterman <scott@kitterman.com>
#           © 2021 Stuart Prescott <stuart@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pathlib import Path
import logging
import os.path as osp
import shutil
import sysconfig
try:
    import tomli
except ModuleNotFoundError:
    # Plugin still works, only needed for autodetection
    pass
try:
    from installer import install
    from installer.destinations import SchemeDictionaryDestination
    from installer.sources import WheelFile
except ModuleNotFoundError:
    SchemeDictionaryDestination = WheelFile = install = None

from dhpython.build.base import Base, shell_command

log = logging.getLogger('dhpython')


class BuildSystem(Base):
    DESCRIPTION = 'Generic PEP517 build system'
    SUPPORTED_INTERPRETERS = {'python3', 'python{version}'}
    REQUIRED_FILES = ['pyproject.toml']
    OPTIONAL_FILES = {}
    CLEAN_FILES = Base.CLEAN_FILES | {'build'}

    def detect(self, context):
        """Return certainty level that this plugin describes the right build
        system

        This method uses cls.{REQUIRED}_FILES (pyroject.toml) only; any
        other PEP517 compliant builder (such as the flit) builder should
        indicate higher specificity than this plugin.

        :return: 0 <= certainty <= 100
        :rtype: int
        """
        result = super().detect(context)
        # Temporarily reduce the threshold while we're in beta
        result -= 20

        try:
            with open('pyproject.toml', 'rb') as f:
                pyproject = tomli.load(f)
            if pyproject.get('build-system', {}).get('build-backend'):
                result += 10
            else:
                # Not a PEP517 built package
                result = 0
        except NameError:
            # No toml, no autdetection
            result = 0
        except FileNotFoundError:
            # Not a PEP517 package
            result = 0
        if result > 100:
            return 100
        return result

    def clean(self, context, args):
        super().clean(context, args)
        if osp.exists(args['interpreter'].binary()):
            log.debug("removing '%s' (and everything under it)",
                      args['build_dir'])
            osp.isdir(args['build_dir']) and shutil.rmtree(args['build_dir'])
        return 0  # no need to invoke anything

    def configure(self, context, args):
        if install is None:
            raise Exception("PEP517 plugin dependencies are not available. "
                            "Please Build-Depend on pybuild-plugin-pyproject.")
        # No separate configure step
        return 0

    def build(self, context, args):
        self.build_step1(context, args)
        self.build_step2(context, args)

    @shell_command
    def build_step1(self, context, args):
        """ build a wheel using the PEP517 builder defined by upstream """
        log.info('Building wheel for %s with "build" module',
                 args['interpreter'])
        context['ENV']['FLIT_NO_NETWORK'] = '1'
        context['ENV']['HOME'] = args['home_dir']
        return ('{interpreter} -m build '
                '--skip-dependency-check --no-isolation --wheel '
                '--outdir ' + args['home_dir'] +
                ' {args}'
               )

    def build_step2(self, context, args):
        """ unpack the wheel into pybuild's normal  """
        log.info('Unpacking wheel built for %s with "installer" module',
                 args['interpreter'])
        extras = {}
        for extra in ('scripts', 'data'):
            path = Path(args["home_dir"]) / extra
            if osp.exists(path):
                log.warning(f'{extra.title()} directory already exists, '
                            'skipping unpack. '
                            'Is the Python package being built twice?')
                return
            extras[extra] = path
        destination = SchemeDictionaryDestination(
            {
                'platlib': args['build_dir'],
                'purelib': args['build_dir'],
                'scripts': extras['scripts'],
                'data': extras['data'],
            },
            interpreter=args['interpreter'].binary_dv,
            script_kind='posix',
        )

        # FIXME this next step will unpack every single wheel file it finds
        # which is probably ok since each wheel is built in a separate
        # directory; but perhaps it should only accept the correctly named
        # wheels that match the current interpreter?
        # python-packaging has relevant utilities in
        #   - packaging/utils.py::parse_wheel_filename
        #   - packaging/tags.py (although it is current-interpreter-centric)
        wheels = Path(args['home_dir']).glob('*.whl')
        for wheel in wheels:
            if wheel.name.startswith('UNKNOWN'):
                raise Exception(f'UNKNOWN wheel found: {wheel.name}. Does '
                                'pyproject.toml specify a build-backend?')
            with WheelFile.open(wheel) as source:
                install(
                    source=source,
                    destination=destination,
                    additional_metadata={},
                )

    def install(self, context, args):
        log.info('Copying package built for %s to destdir',
                 args['interpreter'])
        try:
            paths = sysconfig.get_paths(scheme='deb_system')
        except KeyError:
            # Debian hasn't patched sysconfig schemes until 3.10
            # TODO: Introduce a version check once sysconfig is patched.
            paths = sysconfig.get_paths(scheme='posix_prefix')

        # start by copying the data and scripts
        for extra in ('data', 'scripts'):
            src_dir = Path(args['home_dir']) / extra
            if not src_dir.exists():
                continue
            target_dir = args['destdir'] + paths[extra]
            log.debug('Copying %s directory contents from %s -> %s',
                      extra, src_dir, target_dir)
            shutil.copytree(
                src_dir,
                target_dir,
                dirs_exist_ok=True,
            )

        # then copy the modules
        module_dir = args['build_dir']
        target_dir = args['destdir'] + args['install_dir']
        log.debug('Copying module contents from %s -> %s',
                  module_dir, target_dir)
        shutil.copytree(
            module_dir,
            target_dir,
            dirs_exist_ok=True,
        )

    @shell_command
    def test(self, context, args):
        scripts = Path(args["home_dir"]) / 'scripts'
        if scripts.exists():
            context['ENV']['PATH'] = f"{scripts}:{context['ENV']['PATH']}"
        context['ENV']['HOME'] = args['home_dir']
        return super().test(context, args)
