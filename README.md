# Clue-Less
Team Project for JHU Foundations of Software Engineering

# Team Candlestick Members
- Addison Hammer (ahammer6@jhu.edu)
- Alana Alfeche (aalfech1@jhu.edu)
- Graeme Knowles (gknowle4@jhu.edu)
- Shannon Schlademan (sschlad1@jhu.edu)

# Documents:
- [Project Folder](https://drive.google.com/drive/folders/1MPtxwYdEB16B4XT94usCdcyKpGkMTJ0X)
- [Team Charter](https://docs.google.com/document/d/1Jwko_LERLc9Ldu1NeS8Zrz19IWo6EHrIYxsK_FWFc9k)
- [Project Plan](https://drive.google.com/file/d/1AOW0EbOnT6eIRyOMgZe9MVxeiT19Eubq/view?usp=sharing)

# Build and Run Instructions:
1) Install Docker
2) Build and Run the docker compose script

(I'm using Windows and VSCode 2019)

    git clone https://github.com/addisonhammer/clue-less.git
    cd clue-less
    docker-compose build
    docker-compose up
3) This should start four containers:
   - clue-less_server  (localhost:5000)
   - clue-less_client  (localhost:5001)
   - clue-less_db      (not exposed)
   - clue-less_adminer (localhost:8080) (see #8)

4) If this is the first startup:
   Navigate to http://localhost:5000/api/db/create_database
   This will create the necessary database tables.

5) Navigate to http://localhost:5001/ to get the client form
   - Enter your name and click 'Submit' to generate, send, and display a random 'accusation'

6) The client will send the 'accusation' using a GET request via the docker network

7) The server will receive the 'accusation' and respond with a randomly generated "Valid/Invalid".

8) Naviate to http://localhost:8080/ to open the database admin website
   username and password can be found in the docker-compose script.
   Change System to PostgreSQL

Clue-Less is currently still in the early prototype phase, so functionality is extremely limited and only coarsely represents our desired architecture.