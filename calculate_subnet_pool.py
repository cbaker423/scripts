
UPPERBOUND = 256
start = "172.0.0.1"
end = "172.0.0.254"

start = [int(x) for x in start.split(".")]
end = [int(x) for x in end.split(".")]

diff= [(y - x) for x, y in zip(start, end)]
diff.pop(diff.__len__() - 1)
diff = [d+1 for d in diff if d != 0]
import pdb; pdb.set_trace()
maximum = reduce(lambda x, y: x*y, diff) * UPPERBOUND
missing = start[3] + UPPERBOUND - (end[3] + 1)
total = maximum - missing
print total

