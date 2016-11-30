docker:
	@docker build -t mozilla/onyx . 

run:
	@docker run -d -p 5000:5000 --name onyx mozilla/onyx

start:
	@docker start onyx

stop:
	@docker stop onyx

log:
	@docker logs -f onyx

clean:
	@docker rm -f onyx

.PHONY: docker run start stop log clean
