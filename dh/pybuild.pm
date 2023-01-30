# A debhelper build system class for building Python libraries
#
# Copyright: © 2012-2013 Piotr Ożarowski

# TODO:
# * support for dh --parallel

package Debian::Debhelper::Buildsystem::pybuild;

use strict;
use Dpkg::Control;
use Dpkg::Changelog::Debian;
use Debian::Debhelper::Dh_Lib qw(%dh error doit);
use base 'Debian::Debhelper::Buildsystem';

sub DESCRIPTION {
	"Python pybuild"
}

sub check_auto_buildable {
	my $this=shift;
	return doit('pybuild', '--detect', '--really-quiet', '--dir', $this->get_sourcedir());
}

sub new {
	my $class=shift;
	my $this=$class->SUPER::new(@_);
	$this->enforce_in_source_building();

	if (!$ENV{'PYBUILD_INTERPRETERS'}) {
		if ($ENV{'DEBPYTHON_DEFAULT'}) {
			$this->{pydef} = $ENV{'DEBPYTHON_DEFAULT'};}
		else {
			$this->{pydef} = `pyversions -vd 2>/dev/null`;}
		$this->{pydef} =~ s/\s+$//;
		if ($ENV{'DEBPYTHON_SUPPORTED'}) {
			$this->{pyvers} = $ENV{'DEBPYTHON_SUPPORTED'} =~ s/,/ /r;}
		else {
			$this->{pyvers} = `pyversions -vr 2>/dev/null`;}
		$this->{pyvers} =~ s/\s+$//;
		if ($ENV{'DEBPYTHON3_DEFAULT'}) {
			$this->{py3def} = $ENV{'DEBPYTHON3_DEFAULT'};}
		else {
			$this->{py3def} = `py3versions -vd 2>/dev/null`;}
		$this->{py3def} =~ s/\s+$//;
		if ($ENV{'DEBPYTHON3_SUPPORTED'}) {
			$this->{py3vers} = $ENV{'DEBPYTHON3_SUPPORTED'} =~ s/,/ /r;}
		else {
			$this->{py3vers} = `py3versions -vr 2>/dev/null`;
			if ($this->{py3vers} eq "") {
				# We swallowed stderr, above
				system("py3versions -vr");
				die('E: py3versions failed');
			}
		}
		$this->{py3vers} =~ s/\s+$//;
	}

	return $this;
}

sub configure {
	my $this=shift;
	foreach my $command ($this->pybuild_commands('configure', @_)) {
		doit(@$command);
	}
}

sub build {
	my $this=shift;
	foreach my $command ($this->pybuild_commands('build', @_)) {
		doit(@$command);
	}
}

sub install {
	my $this=shift;
	my $destdir=shift;
	foreach my $command ($this->pybuild_commands('install', @_)) {
		doit(@$command, '--dest-dir', $destdir);
	}
}

sub test {
	my $this=shift;
	foreach my $command ($this->pybuild_commands('test', @_)) {
		doit(@$command);
	}
}

sub clean {
	my $this=shift;
	foreach my $command ($this->pybuild_commands('clean', @_)) {
		doit(@$command);
	}
	doit('rm', '-rf', '.pybuild/');
	doit('find', '.', '-name', '*.pyc', '-exec', 'rm', '{}', ';');
}

sub pybuild_commands {
	my $this=shift;
	my $step=shift;
	my @options = @_;
	my @result;

	my $dir = $this->get_sourcedir();
	if (not grep {$_ eq '--dir'} @options and $dir ne '.') {
		# if --dir is not passed, PYBUILD_DIR can be used
		push @options, '--dir', $dir;
	}

	if (not grep {$_ eq '--verbose'} @options and $dh{QUIET}) {
		push @options, '--quiet';
	}

	my @deps;
	if ($ENV{'PYBUILD_INTERPRETERS'}) {
		push @result, ['pybuild', "--$step", @options];
	}
	else {
		# get interpreter packages from Build-Depends{,-Indep}:
		# NOTE: possible problems with alternative/versioned dependencies
		@deps = $this->python_build_dependencies();

		# When depends on python{3,}-setuptools-scm, set
		# SETUPTOOLS_SCM_PRETEND_VERSION to upstream version
		# Without this, setuptools-scm tries to detect current
		# version from git tag, which fails for debian tags
		# (debian/<version>) sometimes.
		if ((grep /python3-(setuptools-scm|hatch-vcs)/, @deps) && !$ENV{'SETUPTOOLS_SCM_PRETEND_VERSION'}) {
			my $changelog = Dpkg::Changelog::Debian->new(range => {"count" => 1});
			$changelog->load("debian/changelog");
			my $version = @{$changelog}[0]->get_version();
			$version =~ s/-[^-]+$//;  # revision
			$version =~ s/^\d+://;    # epoch
			$version =~ s/~/-/;       # ignore tilde versions
			$ENV{'SETUPTOOLS_SCM_PRETEND_VERSION'} = $version;
		}

		# When depends on python{3,}-pbr, set PBR_VERSION to upstream version
		# Without this, python-pbr tries to detect current
		# version from pkg metadata or git tag, which fails for debian tags
		# (debian/<version>) sometimes.
		if ((grep /python3-pbr/, @deps) && !$ENV{'PBR_VERSION'}) {
			my $changelog = Dpkg::Changelog::Debian->new(range => {"count" => 1});
			$changelog->load("debian/changelog");
			my $version = @{$changelog}[0]->get_version();
			$version =~ s/-[^-]+$//;  # revision
			$version =~ s/^\d+://;    # epoch
			$ENV{'PBR_VERSION'} = $version;
		}

		my @py3opts = ('pybuild', "--$step");

		if (($step eq 'test' or $step eq 'autopkgtest') and
				$ENV{'PYBUILD_TEST_PYTEST'} ne '1' and
				$ENV{'PYBUILD_TEST_NOSE2'} ne '1' and
				$ENV{'PYBUILD_TEST_NOSE'} ne '1' and
				$ENV{'PYBUILD_TEST_CUSTOM'} ne '1' and
				$ENV{'PYBUILD_TEST_TOX'} ne '1') {
			if (grep {$_ eq 'tox'} @deps and $ENV{'PYBUILD_TEST_TOX'} ne '0') {
				push @py3opts, '--test-tox'}
			elsif (grep {$_ eq 'python3-pytest'} @deps and $ENV{'PYBUILD_TEST_PYTEST'} ne '0') {
				push @py3opts, '--test-pytest'}
			elsif (grep {$_ eq 'python3-nose2'} @deps and $ENV{'PYBUILD_TEST_NOSE2'} ne '0') {
				push @py3opts, '--test-nose2'}
			elsif (grep {$_ eq 'python3-nose'} @deps and $ENV{'PYBUILD_TEST_NOSE'} ne '0') {
				push @py3opts, '--test-nose'}
		}

		my $py3all = 0;
		my $py3alldbg = 0;

		my $i = 'python{version}';

		# Python 3
		if ($this->{py3vers}) {
			if (grep {$_ eq 'python3-all' or $_ eq 'python3-all-dev'} @deps) {
				$py3all = 1;
				push @result, [@py3opts, '-i', $i, '-p', $this->{py3vers}, @options];
			}
			if (grep {$_ eq 'python3-all-dbg'} @deps) {
				$py3alldbg = 1;
				push @result, [@py3opts, '-i', "$i-dbg", '-p', $this->{py3vers}, @options];
			}
		}
		if ($this->{py3def}) {
			if (not $py3all and grep {$_ eq 'python3' or $_ eq 'python3-dev'} @deps) {
				push @result, [@py3opts, '-i', $i, '-p', $this->{py3def}, @options];
			}
			if (not $py3alldbg and grep {$_ eq 'python3-dbg'} @deps) {
				push @result, [@py3opts, '-i', "$i-dbg", '-p', $this->{py3def}, @options];
			}
		}
		# TODO: pythonX.Y → `pybuild -i python{version} -p X.Y`

	}
	if (!@result) {
		use Data::Dumper;
		die('E: Please add appropriate interpreter package to Build-Depends, see pybuild(1) for details.' .
		    'this: ' . Dumper($this) .
		    'deps: ' . Dumper(\@deps));
	}
	return @result;
}

sub python_build_dependencies {
	my $this=shift;

	my @result;
	my $c = Dpkg::Control->new(type => CTRL_INFO_SRC);
	if ($c->load('debian/control')) {
		for my $field (grep /^Build-Depends/, keys %{$c}) {
			my $builddeps = $c->{$field};
			while ($builddeps =~ /(?:^|[\s,])((pypy|python|tox)[0-9\.]*(-[^\s,\(]+)?)(?:[\s,\(]|$)/g) {
				my $dep = $1;
				$dep =~ s/:(any|native)$//;
				if ($dep) {push @result, $dep};
			}
		}
	}

	return @result;
}

1
