## Approach

Build the tree with a queue on paper, one node at a time, then walk it in the order of the printing function.

## Expected output

```text
1: left=2 right=3
2: left=None right=4
4: left=None right=None
3: left=5 right=None
5: left=6 right=None
6: left=None right=None
size 6
height 4
leaves 2
leaf values [4, 6]
```

## Why

| queue (front first) | entries used | what happens |
|---|---|---|
| `1` | `1` | the root |
| `1` | `2, 3` | `1` gets left `2`, right `3` |
| `2, 3` | `None, 4` | `2` gets no left child and right `4` |
| `3, 4` | `5, None` | `3` gets left `5`, no right child |
| `4, 5` | `None, None` | `4` is a leaf |
| `5` | `6` | `5` gets left `6`; the list ends |

The tree is (each child is written next to the word `left` or `right`):

```text
1
|-- left  2
|     |-- right 4
|-- right 3
      |-- left  5
            |-- left 6
```

`describe` is a preorder walk: `1`, then the left subtree (`2`, `4`), then the right subtree (`3`, `5`, `6`). The longest path is `1 - 3 - 5 - 6`: 4 nodes, so the height is 4. The leaves are `4` and `6`. Ten list entries make six nodes: four of the entries are `None` (three gaps that fill a missing child, plus the entry after `6` that the list does not contain).
