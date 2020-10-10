# storemaven_spority_tracker
storemaven spotify tracker home assignment

# Set environment for running app
1. clone project to dir
2. in terminal: cd storemaven_spority_tracker/src
3. set mysql db -> in terminal: docker-compose up -d; (to track logs run> docker-compose logs -f)
4. create tables -> in terminal: python3 utils/db_utils.py (also can run from IDE this module)
5. start app -> in terminal: python3 spotify_tracker_app.py  (also can run from IDE this module)

# Run API requests from postman

>Create category entity:
POST 127.0.0.1:5000/entity/create

>Remove caregoty entity:
POST 127.0.0.1:5000/entity/remove

goot request:

{
	"categoryName": "Workout"
	
}

bad request:

{}
{"categoryName": "noam"} //not supported by spotify

>Trigger track all categories we've created:
POST 127.0.0.1:5000/track

valid requests:
{} -> no dry run
{"isDryRun" : 1} -> dry run: tracks will not be saved into db
