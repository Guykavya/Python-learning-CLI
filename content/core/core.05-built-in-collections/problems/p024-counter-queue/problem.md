# Queue at the counter

Simulate a queue at a ticket counter. Read commands, one per line, until `end`:

| Command | What to do |
|---|---|
| `join NAME` | add NAME to the back. If NAME is already in the queue, print `NAME is already in the queue` instead |
| `serve` | remove the person at the front and print `Serving NAME`, or print `Nobody to serve` if the queue is empty |
| `leave NAME` | remove NAME from wherever they are. If they are not in the queue, print `NAME is not in the queue` |
| `show` | print `Queue: ` followed by the names front to back, separated by spaces, or `Queue: (empty)` |

**Example**

Input:
```
join asha
join ravi
join asha
show
serve
leave meena
join meena
leave ravi
show
serve
serve
end
```
Output:
```
asha is already in the queue
Queue: asha ravi
Serving asha
meena is not in the queue
Queue: meena
Serving meena
Nobody to serve
```
