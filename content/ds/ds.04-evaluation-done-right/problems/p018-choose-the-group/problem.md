# Choose the group

Chapter section 6. The right group for a split is the **entity the model will meet as new** in deployment. For each dataset below, name the column you would group by (or say that a time split is needed as well) and explain why in one or two sentences.

1. **Patients' visits**: one row per hospital visit; columns `patient_id`, `hospital_id`, `visit_date`, lab values; target: complication within 30 days. The model will be used on **new patients** at the same hospitals.
2. **Shop receipts**: one row per receipt line; columns `receipt_id`, `customer_id`, `store_id`, `product`, `amount`; target: was the product returned? The model will run on **future receipts** from **existing** customers.
3. **Sensor readings**: one reading per minute; columns `machine_id`, `timestamp`, vibration, temperature; target: failure in the next hour. The model will be installed on **new machines** of the same type.

Write your answer in `answer.md`.

## After you answer

Compare with the model answer and tick the checklist for the points you made.
