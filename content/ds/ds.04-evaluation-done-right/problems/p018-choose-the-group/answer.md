## Model answer

1. **Group by `patient_id`.** New patients are what the model will meet; a patient's visits share stable traits and personal risk, so if the same patient is on both sides the model recognises them and the score is too optimistic. Not `hospital_id`: the model will run at the same hospitals, so seeing them in training is realistic.
2. **Split by time, and keep `receipt_id` together.** Deployment means **future** receipts from known customers, so train on earlier dates and test on later ones. Lines of one receipt must stay on the same side (they share a basket and a moment). Grouping by `customer_id` is not needed, because known customers are exactly the deployment situation.
3. **Group by `machine_id` (and respect time inside each machine).** New machines are the deployment case, and readings one minute apart on the same machine are nearly copies; a row split would let the model memorise each machine. Within the training machines, features must use only past readings.

**Checklist: your answer should mention**
- [ ] the group is the entity that is new in deployment
- [ ] patients: group by patient_id, not hospital
- [ ] receipts: a time split, with lines of one receipt kept together
- [ ] sensors: group by machine_id
- [ ] near-identical rows of one entity on both sides inflate the score
