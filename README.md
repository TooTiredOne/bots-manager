# bots-manager

A simple service for adding/removing/listing bots with basic auth

Deployed version is available here: https://another-bots-manager.herokuapp.com <br>
API Swagger documentation is available here: https://another-bots-manager.herokuapp.com/docs

## Heroku Deployment

1. create new app on heroku website with name `<app-name>`
2. clone this repo and cd into it
3. `$ heroku login`
4. `$ heroku git:remote -a <app-name>`
5. in `app/routing/bots.py`, change `HOSTNAME` to  `<app-name>` with no slashes
6. `$ git add .` 
7. `$ git commit -m "changed hostname"`

- If you want to deploy using docker, run `$ heroku stack:set container`

8. `$ git push heroku master`


## Useful commands

### Creating virtual environment
```
make venv
```

### Run formatters
```
make format
```

### Run linters
```
make lint
```

### Run local session
```
make up
```
(you won't be able to add bots though)

