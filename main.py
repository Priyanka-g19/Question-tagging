import openai,os,json
from flask import Flask,request,jsonify,render_template
from ratelimit import limits,sleep_and_retry
from dotenv import load_dotenv



#from logger import logging
#from exception import customException


app=Flask(__name__)
#global config
#with open("config.yaml","r") as f:
#    config= yaml.full_load(f)



def configure():
    load_dotenv()


@app.route("/")
def index():
    return render_template('index.html')

# Define rate limiting parameters
#RATE_LIMIT = config["RATE_LIMIT"]  # maximum number of requests per minute
#RATE_PERIOD = config["RATE_PERIOD"]  # time period in seconds for rate limit

RATE_LIMIT =50
RATE_PERIOD =60

# Define rate limiter decorator
@sleep_and_retry
@limits(calls=RATE_LIMIT, period=RATE_PERIOD)
@app.route("/chatgpt",methods=["GET","POST"])
def chat_gpt():
    #logging.info("Entered the chatgpt function")
    if request.method == "GET" or request.method == "POST":
        try:
            prompt='Identify the subject, topic,subtopic,  difficulty level from [Easy, Medium, Hard],blooms taxonomy level for the question only. Q. '
            #logging.info("Taking the prompt as Question from the user")
            prompt += request.args.get("prompt")
            print(prompt)
            api_key = os.getenv('API_KEY')

            openai.api_key=api_key
            #logging.info("Running the chatgpt api")

            response= openai.ChatCompletion.create(
                 model="gpt-3.5-turbo",
                 messages=[{"role": "user", "content": prompt}],
                 n=1,
                 stop=None,
                 temperature = 0.7,
                 presence_penalty=0
            )
            #logging.info("storing the output from chat gpt")
            text = response['choices'][0]['message']['content'].strip()

            # return jsonify(
            #     OUTPUT = prepare_json(text)
            # )
            #
            #logging.info("Returning the output from chatpt api as json in html")
            return render_template("index.html",output=prepare_json(text))
        except Exception as e:
            return jsonify(
                ERROR = f"{e}"
            )


def  prepare_json(output):
    #logging.info("Entered the method to convert chatgpt text response to json response")
    #logging.info("Converting chatgpt response to list")
    lst=output.split('\n')
    #logging.info("Creating lists within the list to separate group subject,topic,subtopic,blooms taxonomy anf difficulty level separately")
    new_lst=[lst[i].split(':') for i in range(0,len(lst))]
    out = {}
    #logging.info("Converting nested list into dictionary")
    for val in new_lst:
        if len(val) > 0:
            out[val[0]] = val[1].split(",")
    #logging.info("Converting dictionary to json")
    return json.dumps(out)



if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)
