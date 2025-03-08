# docker run -d -p 8000:8000 --env-file .env.prod --name dokoola-backend dokoola-backend

env_file=.env.prod
image=dokoola-backend

docker run -d \
    -p 8000:8000 \
    --name dokoola-backend \
    $image