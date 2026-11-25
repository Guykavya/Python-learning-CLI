# Why a funnel can mislead

Chapters 3.4 and 3.7. A shop's overall **checkout rate** (share of carts that start checkout) fell from 62% in March to 58% in April. The product team wants to redesign the checkout. Then an analyst splits
the same two months by device:

| | March carts | March rate | April carts | April rate |
|---|---|---|---|---|
| desktop | 6,000 | 70% | 3,000 | 72% |
| mobile | 4,000 | 50% | 7,000 | 52% |
| **all** | 10,000 | **62%** | 10,000 | **58.0%** |

Both devices **improved**, but the total fell.

In `answer.md`, in about 200 to 300 words, explain:

1. why this happens (name the effect, and say which number changed besides the two rates);
2. what you would tell the product team about the redesign;
3. what you should always do before comparing a funnel between two periods;
4. two other ways in which a funnel can mislead (think of how steps and sessions are defined).

## Example

A start: "The overall rate is an average of the two device rates, weighted by how many carts each device has. In April the weights changed: mobile, the weaker device, went from 40% of the carts to 70%..."
