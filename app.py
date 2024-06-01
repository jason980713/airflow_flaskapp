from datetime import date, datetime, timedelta
import time
from numpy import random
import pandas as pd
from faker import Faker
from flask import Flask, jsonify, request


def _generate_events(end_date):
    events = pd.concat(
        [
            _generate_events_for_day(date=end_date - timedelta(days=(30 - i)))
            for i in range(30)
        ],
        axis=0,
    )
    print("a")
    return events


def _generate_events_for_day(date):
    seed = int(time.mktime(date.timetuple()))
    Faker.seed(seed)
    random_state = random.RandomState(seed)
    n_users = random_state.randint(low=50, high=100)
    n_events = random_state.randint(low=200, high=2000)
    fake = Faker()
    users = [fake.ipv4() for _ in range(n_users)]
    return pd.DataFrame(
        {
            "user": random_state.choice(users, size=n_events, replace=True),
            "date": pd.to_datetime(date),
        }
    )


def _str_to_datetime(value):
    if value is None:
        return None
    return datetime.strptime(value, "%Y-%m-%d")


app = Flask(__name__)
# 2019년 1월 5일까지 30개의 간격으로 날짜 쪼개기.
app.config["events"] = _generate_events(end_date=date(year=2019, month=1, day=5))


# 요청이 오면.
@app.route("/events")
def events():
    start_date = _str_to_datetime(request.args.get("start_date", None))
    end_date = _str_to_datetime(request.args.get("end_date", None))
    events = app.config.get("events")
    if start_date is not None:
        events = events.loc[events["date"] >= start_date]
    if end_date is not None:
        events = events.loc[events["date"] < end_date]
    # 이벤트를 dict 로 변형해서 json 으로 생성해서 리턴.
    return jsonify(events.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
