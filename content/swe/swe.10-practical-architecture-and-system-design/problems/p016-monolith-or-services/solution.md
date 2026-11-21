## Approach

The model answer is in `answer.md`. The method is the same in every case: **list the real reasons to split (people and load), price the network (availability tax, operations), then choose the smallest shape that fixes the real pain**. A modular monolith with the right seams keeps the options open: a split later is a cut along a line that already exists.

## Cost

Nothing to build. The expensive mistake is the reverse of over-engineering: a split chosen for fashion, which cannot be undone cheaply.

## Another way

Write an ADR for your own project (chapter 18): "stay a modular monolith; revisit when notification sending needs a different scaling profile or a second team owns it". A decision with a **Revisit when** line is easy to reverse in the right moment.
