import sys
import re
import datetime
import math
from parse import parse
import bokeh
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.transform import cumsum

class Message:
    def __init__(self, time, sender, body):
        self.time = time
        self.sender = sender
        self.body = body

def parseMessages(data, date_format):
    date_formats = {
        "dd.mm.yy": ["\n(?=[0-9]{2}\.[0-9]{2}\.[0-9]{2}, [0-9]{2}:[0-9]{2} - .+: )", "{}.{}.{}, {}:{} - {}: {}"],
        "mm/dd/yy": ["\n(?=[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2}, [0-9]{2}:[0-9]{2} - .+: )", "{}/{}/{}, {}:{} - {}: {}"]
    }
    raw_messages = re.split(date_formats[date_format][0], data)
    
    messages = []
    for message in raw_messages:
        parsed = parse(date_formats[date_format][1], message)
        if parsed == None:
            continue
        if date_format == "dd.mm.yy":
            time = datetime.datetime(int("20" + parsed[2]), int(parsed[1]), int(parsed[0]), int(parsed[3]), int(parsed[4]))
        elif date_format == "mm/dd/yy":
            time = datetime.datetime(int("20" + parsed[2]), int(parsed[0]), int(parsed[1]), int(parsed[3]), int(parsed[4]))
        messages.append(Message(time, parsed[5], parsed[6]))

    return messages

def plot(messages):
    bokeh.io.curdoc().theme = "dark_minimal"

    p1 = figure(
        x_axis_label = "Time",
        y_axis_label = "Number of Messages",
        x_axis_type = "datetime",
        width = 1500, height = 750,
        title = "Messages by Time of Day"
    )
    data = {}
    for i in messages:
        k = datetime.datetime.combine(datetime.date.today(), datetime.time(i.time.hour, 0))
        if not k in data:
            data[k] = 0
        data[k] += 1
    source = {"x": sorted(data), "top": [data[i] for i in sorted(data)]}
    p1.vbar(source = source, width = datetime.time(0, 10))

    p2 = figure(
        x_axis_label = "Date",
        y_axis_label = "Number of Messages",
        x_axis_type = "datetime",
        width = 1500, height = 750,
        title = "Messages by Date"
    )
    data = {}
    for i in messages:
        k = datetime.datetime.combine(i.time.date(), datetime.time(0, 0))
        if not k in data:
            data[k] = 0
        data[k] += 1
    source = {"x": sorted(data), "top": [data[i] for i in sorted(data)]}
    p2.vbar(source = source)

    p3 = figure(
        width = 500, height = 500,
        x_range = (-0.5, 0.5),
        title = "Messages by Sender",
        toolbar_location = None,
        tools = "hover",
        tooltips = "@name: @value"
    )
    data = {}
    for i in messages:
        k = i.sender
        if not k in data:
            data[k] = 0
        data[k] += 1
    data = dict(sorted(data.items(), key = lambda x: 1 / x[1]))
    source = {
        "name": list(data.keys()),
        "value": list(data.values()),
        "start_angle": [sum(list(data.values())[0 : i]) / sum(data.values()) * 2 * math.pi for i in range(len(data.values()))],
        "end_angle": [sum(list(data.values())[0 : i + 1]) / sum(data.values()) * 2 * math.pi for i in range(len(data.values()))]
    }
    p3.wedge(x = 0, y = 1, radius = 0.4, source = source, line_color = "white")

    show(bokeh.layouts.column(p1, p2, p3))

def main(path = None):
    file_path = None
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
    if path != None:
        file_path = path
    
    if file_path == None:
        print("no file given")
        return
    chat_file = open(file_path, "r", encoding = "utf-8")

    date_formats = ["dd.mm.yy", "mm/dd/yy"]
    i = int(input("\n".join(["(" + str(i) + ") " + k for i, k in enumerate(date_formats)]) + "\ndate format: "))
    if not -1 < i < len(date_formats):
        print("invalid date format")
        return

    messages = parseMessages(chat_file.read(), date_formats[i])
    chat_file.close()

    plot(messages)

if __name__ == "__main__":
    main()
