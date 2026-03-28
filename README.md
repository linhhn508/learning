Web reference: https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3#step-2-creating-a-base-application

Docker run: 

flask run -p 5000 -h 0.0.0.0

docker run -p 8000:5000 --name test_web_app --network=mynetwork web_app:latest
docker run -d --name test-mongo --network=mynetwork mongo:7.0.32-rc1