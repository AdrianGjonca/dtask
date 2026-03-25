all: dtask.py
	source venv/bin/activate && \
	pyinstaller --onefile dtask.py

install: all
	cp dist/dtask /usr/local/bin/dtask

uninstall:
	rm /usr/local/bin/dtask

clean:
	rm -rf dist/ build/ dtask.spec
