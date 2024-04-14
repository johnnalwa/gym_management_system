House Rent Prediction Web Application
This repository contains the code for a web application that predicts house rent prices.

Running the Application

Prerequisites:

Docker Desktop installed. Download it from the official Docker website: Docker Desktop: https://www.docker.com/products/docker-desktop.
Steps:

Clone the Repository:

git clone https://github.com/Anubhav-Goyal01/House-Rent-Prediction.git
Navigate to Project Directory:

cd House-Rent-Prediction
Build Docker Image:

docker build -t house-rent-prediction .
Run Docker Container:

docker run -p 5000:5000 house-rent-prediction
This command runs the application and maps the container port (5000) to your local machine port (5000).

Access the Application:

Open a web browser and navigate to http://localhost:5000 to use the House Rent Prediction web app.