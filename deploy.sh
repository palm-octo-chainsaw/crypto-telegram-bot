docker rm -f crypto-bot || true
docker rmi -f telegram-bot || true
docker build -t telegram-bot .
docker run --name crypto-bot -d telegram-bot