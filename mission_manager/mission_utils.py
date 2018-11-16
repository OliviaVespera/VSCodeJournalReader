from datetime import datetime
from time import mktime, strptime

def create_steps(descs, conditions, edges):
    m_steps = []
    for index in range(len(descs)):
        m_steps.append({"desc":descs[index],
        "conditions":conditions[index]})

    for i in range(len(edges)):
        m_steps[i]["edge"] = edges[i]
    print("steplist created!")
    return m_steps


def convert_time_stamp(timestamp_string):
    # return parser(timestamp_string)
    return datetime.fromtimestamp(
        mktime(strptime(timestamp_string,"%Y-%m-%dT%H:%M:%SZ"))
    )