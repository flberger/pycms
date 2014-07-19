help:
	@echo targets:
	@echo '    sdist'
	@echo '    exe'
	@echo '    user_install'
	@echo '    pypi'
	@echo '    doctest'
	@echo '    README.rst'
	@echo '    freecode'
	@echo '    sign'
	@echo '    clean'
	@echo '    commit.txt'
	@echo '    commit'
	@echo '    bitbucket'

ifdef PYTHON

sdist:
	rm -vf MANIFEST
	$(PYTHON) setup.py sdist --force-manifest --formats=zip

exe: sdist
	rm -rf build/exe.*
	$(PYTHON) setup.py build

user_install:
	$(PYTHON) setup.py install --user --record filelist.txt

pypi:
	$(PYTHON) setup.py register

doctest:
	$(PYTHON) -m doctest pycms-documentation.txt

else

sdist:
	@echo Please supply Python executable as PYTHON=executable.

exe:
	@echo Please supply Python executable as PYTHON=executable.

user_install:
	@echo Please supply Python executable as PYTHON=executable.

pypi:
	@echo Please supply Python executable as PYTHON=executable.

doctest:
	@echo Please supply Python executable as PYTHON=executable.

endif

README.rst: README
	pandoc --output README.rst README

freecode:
	@echo RETURN to submit to freecode.com using freecode-submit.txt, CTRL-C to cancel:
	@read DUMMY
	freecode-submit < freecode-submit.txt

sign:
	rm -vf dist/*.asc
	for i in dist/*.zip ; do gpg --sign --armor --detach $$i ; done
	gpg --verify --multifile dist/*.asc

clean:
	rm -vf `find . -iname '*.log'`
	rm -rvf `find . -type d -iname '__pycache__'`
	rm -vf `find . -iname '*.pyc'`

commit.txt:
	hg diff > commit.txt

commit: commit.txt
	@echo commit.txt:
	@echo ------------------------------------------------------
	@cat commit.txt
	@echo ------------------------------------------------------
	@echo RETURN to commit using commit.txt, CTRL-C to cancel:
	@read DUMMY
	hg commit --logfile commit.txt && rm -v commit.txt

bitbucket:
	hg push https://flberger@bitbucket.org/flberger/pycms
