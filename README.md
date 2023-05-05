
# Flask Web Application for Evaluation System

`This is a Flask web application that provides an evaluation system for candidates. The system allows evaluators to log in, view candidate evaluations, and update evaluation scores.
`
## Dependencies

run the command 
`pip install -r requirements.txt`

## Configuration
`The application requires a MySQL database to store user and evaluation data. The database configuration is stored in the db.py file.`

## Usage
`To run the application, execute the app.py script. The application will be available at http://localhost:5000.`

## Routes
The application has the following routes:

`/` - the home page
`/register `- allows users to register for an account
`/login `- allows users to log in to the system
`/update `- allows evaluators to update candidate evaluation scores

## Functions
The application has the following functions:

1. get_json_data(e_id): This function retrieves candidate evaluation data from the database and returns it as a JSON object.
2. index(): This function renders the home page.
3. register(): This function handles user registration. It inserts a new user record into the database.
4. login(): This function handles user login. It retrieves the user's password from the database and checks it against the provided password. If the passwords match, the function retrieves the user's evaluation data and returns it as a JSON object.
5. update(): This function handles the updating of candidate evaluation scores. It calculates the total score and grade for the evaluation and updates the database accordingly.

## Essay Grading Algorithmi
`utils.py`
it is a grading algorithm for essays. The code includes functions for loading dependencies, grading essays, and mapping the final score to a grade. The grading algorithm includes components for evaluating grammar, content, format, and tone. The algorithm also calculates a final score and maps it to a grade using a pre-defined grade mapping.

The algorithm uses several natural language processing tools such as Spacy, NLTK, and SentenceTransformers to evaluate different aspects of the essays. It also includes a deep learning model for grammar correction and a punctuation model for punctuation correction. The algorithm penalizes for grammar and format issues and rewards for good content and tone.

The code is well-documented, and the variables and functions are named clearly. It follows the PEP 8 style guide for Python code. Overall, the code appears to be well-written and well-structured.

## Evaluation System Code 
`database.py`
It is the part of a larger system of an evaluation process. The code adds candidate details and responses to the database, retrieves questions, scores similarity logs, and stores the results.

There is a function add_candidate that inserts the candidate details into the candidate table. The add_to_response function inserts the candidate's response to each of the five questions into the responses table.

The get_question function retrieves all the questions from the questions table and returns a dictionary containing the question IDs, prompts, and answers. The score_similarity_logs function retrieves all the responses from the responses table and calculates various scores and logs for each response. It stores the logs in the logs table and the scores in the evaluations table.

The code uses the mysql-connector library to connect to a MySQL database and execute SQL queries. It also uses other libraries such as pandas and datetime for data processing and random for generating random numbers.






