all: dtask.py
	source venv/bin/activate && \
	pyinstaller --onefile dtask.py

install: all
	cp dist/dtask /usr/local/bin/dtask
	cp dtask.1 /usr/local/man/man1/dtask.1

uninstall:
	rm /usr/local/bin/dtask
	rm /usr/local/man/man1/dtask.1

clean:
	rm -rf dist/ build/ dtask.spec
