import json
import random
import time
import requests
from itertools import count

from flask import Flask, Response, render_template, stream_with_context

application = Flask(__name__)
random.seed()  # Initialize the random number generator


@application.route('/')
def index():
    return render_template('index.html')


index = count()
data_y_vals =[]
numerator = []
denominator = []
theta_hat = []
forecast_y_vals = []
forecast_error = []


@application.route('/chart-data')
def chart_data():
    def generate_random_data():
        while True:
            i = next(index)
            r = requests.get("https://random-data-api.com/api/number/random_number")
            num = r.json()['number']
            data_y_vals.append(num)
            # forecast = 5000000000

            if i >= 1:
                numerator.append(num * data_y_vals[i - 1])
                denominator.append(num * num)
                theta_hat.append(sum(numerator) / sum(denominator))

            if i >= 2:  # when there's a
                forecast = data_y_vals[i - 1] * theta_hat[i - 2]
                forecast_y_vals.append(forecast)
                forecast_error.append(num - forecast)
            else:  # if there's not enough data to generate a forecast, use midpoint
                forecast = 5000000000

            if i < 1:
                json_data = json.dumps(
                    {'index': i, 'number': num, 'forecast': forecast})
                yield f"data:{json_data}\n\n"
            elif i < 2:
                json_data = json.dumps(
                    {'index': i,
                     'number': num,
                     'forecast': forecast,
                     'index2': i-1,
                     'theta': theta_hat[i-1]
                     })
                yield f"data:{json_data}\n\n"
            else:
                json_data = json.dumps(
                    {'index': i,
                     'number': num,
                     'forecast': forecast,
                     'index2': i - 1,
                     'theta': theta_hat[i - 1],
                     'index3': i-2,
                     'forecast_error': forecast_error[i-2]
                     })
                yield f"data:{json_data}\n\n"
            time.sleep(1)

    response = Response(stream_with_context(generate_random_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == '__main__':
    application.run(debug=True, threaded=True)
