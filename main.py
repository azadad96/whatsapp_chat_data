import sys
import re
import datetime
import math
from parse import parse
import matplotlib.pyplot as plt

class Message:
    def __init__(self, time, sender, body):
        self.time = time
        self.sender = sender
        self.body = body

def parseMessages(data):
    raw_messages = re.split("\n(?=[1-9]{1,2}\/[0-9]{1,2}\/[0-9]{2}, [0-9]{2}:[0-9]{2} - .+: )", data)
    
    messages = []
    for message in raw_messages:
        parsed = parse("{}/{}/{}, {}:{} - {}: {}", message)
        if parsed == None:
            continue
        time = datetime.datetime(int("20" + parsed[2]), int(parsed[0]), int(parsed[1]), int(parsed[3]), int(parsed[4]))
        messages.append(Message(time, parsed[5], parsed[6]))
    
    return messages

def plot(messages):
    people = {}
    for msg in messages:
        if not msg.sender in people:
            people[msg.sender] = 0
        people[msg.sender] = people[msg.sender] + 1
    data = {"others": 0}
    data.update(dict(sorted(people.items(), key = lambda item: item[1])))
    total = sum(data.values())
    for key in list(data.keys()):
        if data[key] < 0.03 * total and key != "others":
            data["others"] = data["others"] + data[key]
            del(data[key])
    if data["others"] == 0:
        del(data["others"])
    plt.subplot(121)
    plt.title("Messages by sender", color = "grey")
    patches, texts, autotexts = plt.pie(data.values(), labels = data.keys(), startangle = 90, autopct = "%1.1f%%", pctdistance = 0.875, colors = ["lightgrey" for i in data], explode = [0.01 for i in data])
    for i in texts:
        i.set_color("grey")
    for i in autotexts:
        i.set_color("grey")
    plt.gcf().gca().add_artist(plt.Circle((0, 0), 0.75, fc = "white"))
    
    counter = {}
    for msg in messages:
        time = msg.time.hour
        if not time in counter:
            counter[time] = 0
        counter[time] = counter[time] + 1
    data = {}
    data = dict(sorted(counter.items(), key = lambda item: item[1]))
    ax = plt.subplot(122)
    plt.title("Messages by time", color = "grey")
    plt.xlabel("hour of day")
    plt.ylabel("number of messages")
    plt.bar(data.keys(), data.values(), color = "lightgrey")
    plt.xticks(list(range(24)))
    ax.set_axisbelow(True)
    ax.yaxis.grid(True)
    ax.xaxis.label.set_color("grey")
    ax.yaxis.label.set_color("grey")
    ax.tick_params(colors = "grey")
    for i in ax.spines:
        ax.spines[i].set_color("grey")
    
    plt.subplots_adjust(wspace = 0.75)
    plt.show()

def main(path = None):
    file_path = None
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
    if path != None:
        file_path = path
    
    if file_path == None:
        return
    chat_file = open(file_path, "r")
    messages = parseMessages(chat_file.read())
    chat_file.close()

    plot(messages)

if __name__ == "__main__":
    main()
