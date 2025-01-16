from typing import cast
from click import group, option, argument, pass_context, Context
import pendulum as p
from pendulum import Time, timezone
from parsedatetime import Calendar

from jean_loup.pisugar import PiSugar


def parse_time(time_text: str) -> Time:
    cal = Calendar()
    time, _ = cal.parse(time_text)
    time = Time(hour=time.tm_hour, minute=time.tm_min)
    return time


@group()
@option("--fake", is_flag=True, required=False)
@pass_context
def app(context: Context, fake: bool):
    pi_sugar = PiSugar.fake() if fake else PiSugar.genuine()
    context.obj = context.with_resource(pi_sugar)


@app.command()
@pass_context
def get_battery_level(context: Context):
    pi_sugar = cast(PiSugar, context.obj)
    battery_level = pi_sugar.battery_level
    print(battery_level)


@app.command()
@argument("time_text", type=str, required=True)
@pass_context
def set_wakeup_time(context: Context, time_text: str):
    pi_sugar = cast(PiSugar, context.obj)
    time = parse_time(time_text)
    print(time)
    pi_sugar.wakeup_time = time


@app.command()
@pass_context
def get_wakeup_time(context: Context):
    pi_sugar = cast(PiSugar, context.obj)
    wakeup_time = pi_sugar.wakeup_time
    print(wakeup_time)


@app.command()
@pass_context
def unset_wakeup_time(context: Context):
    pi_sugar = cast(PiSugar, context.obj)
    pi_sugar.wakeup_time = None


@app.command()
@pass_context
def now(context: Context):
    pi_sugar = cast(PiSugar, context.obj)
    now_date_time = pi_sugar.now()
    print(now_date_time)


@app.command()
@option("--delay", type=int, required=False)
@pass_context
def power_off(context: Context, delay: int | None = None):
    pi_sugar = cast(PiSugar, context.obj)
    pi_sugar.power_off(delay)
