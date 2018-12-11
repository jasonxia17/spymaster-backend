# spymaster-backend

This repository contains the backend code for the SpyMaster app. The backend consists of an API that can handle two different tasks. The first task is to convert an image of the game board to a list of words on the game board. The second task is to generate a clue based on the words on the game board.

## Setup
We used [Tesseract](https://en.wikipedia.org/wiki/Tesseract_(software)) for text detection. You must have this installed in order the run the code. Also, we used a word vector model for clue generation (specifically, the model trained on Google News). You must download [this file](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/) and include it in the project directory. Finally, you should run this command to install all required packages:

```
pip3 install -r requirements.txt
```

## Frontend App
The repository for the mobile app can be found here:

https://github.com/Nicholas2750/spymaster-mobile-app
