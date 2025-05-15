git submodule init
git submodule update
cd AgentRun/agentrun-api
cp .env.example .env.dev
docker-compose up -d --build