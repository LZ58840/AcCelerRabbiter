.PHONY: start setup stop restart clean reset

start:
	./start-prod.sh

setup: start
setup:
	./setup-sql.sh

stop:
	./stop-prod.sh

restart: stop
restart: start

clean: stop
clean:
	./clear-data.sh

reset: clean
reset: setup
