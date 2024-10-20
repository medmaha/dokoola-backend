### **1. Approval Matrix**

The **Approval Matrix** determines which approvers are needed based on factors like department, unit, or requisition amount.

#### **Who Creates the Approval Matrix?**

- **System Administrators**: They will initially set up the matrix, defining the rules and criteria for approval.
- **Department Heads/Managers**: They may provide input on the specific approval needs for their departments, ensuring the matrix reflects the actual decision-making process.

#### **How is the Approval Matrix Created?**

1. **Step 1**: The admin or manager defines the criteria for approvals (e.g., department, unit, requisition value).
2. **Step 2**: The rules for each criterion are entered into the system. For example:
   - Requisitions under D5,000 may only need unit-level approval.
   - Requisitions above D5,000 might require both unit and finance department approval.
   - Certain departments may have specialized approvers.
3. **Step 3**: The system will use this matrix to automatically assign approvers whenever a requisition is submitted.

---

### **Sample Approval Matrix**

| Department  | Requisition Amount | Unit Approver       | Department Approver | Finance Approver |
| ----------- | ------------------ | ------------------- | ------------------- | ---------------- |
| IT          | <D5,000            | IT Unit Head        | None                | Finance Officer  |
| IT          | ≥D5,000            | IT Unit Head        | IT Department Head  | Finance Manager  |
| Marketing   | <D10,000           | Marketing Unit Head | None                | Finance Officer  |
| Marketing   | ≥D10,000           | Marketing Manager   | Marketing Director  | Finance Manager  |
| Procurement | Any amount         | Procurement Officer | Procurement Manager | Finance Officer  |

---

### **2. Approval Workflows**

An **Approval Workflow** is the specific sequence of approval steps that a requisition follows, based on the **Approval Matrix**.

#### **Who Creates the Approval Workflow?**

- **System Administrators or Workflow Designers**: These individuals will design the workflows based on the approval requirements specified in the **Approval Matrix**.
- **Department Heads/Managers**: They collaborate with admins to ensure that the workflows accurately reflect the necessary approval process within their department.

#### **How are the Workflows Created?**

1. **Step 1**: Define each step in the approval process for a requisition type. This includes identifying all the necessary approvers (e.g., Unit Head, Department Head, Finance, Procurement).
2. **Step 2**: Specify the order in which approvals should occur (e.g., Department Head first, then Finance).
3. **Step 3**: Assign approval permissions to the appropriate users or roles (e.g., specific managers, heads of departments).
4. **Step 4**: The system will follow this workflow every time a requisition matching the criteria is submitted.

---

### **Sample Approval Workflows**

#### **IT Department Workflow** (For requisitions under D5,000)

1. **Step 1**: Requisition submitted by IT staff.
2. **Step 2**: IT Unit Head reviews and approves.
3. **Step 3**: Finance Officer reviews for budget and approves.
4. **Final Step**: Requisition approved and finalized.

#### **Marketing Department Workflow** (For requisitions over D10,000)

1. **Step 1**: Requisition submitted by Marketing staff.
2. **Step 2**: Marketing Manager reviews and approves.
3. **Step 3**: Marketing Director reviews and approves.
4. **Step 4**: Finance Manager reviews for budget and approves.
5. **Final Step**: Requisition approved and finalized.

#### **Procurement Workflow** (Any amount)

1. **Step 1**: Requisition submitted by Procurement staff.
2. **Step 2**: Procurement Officer reviews and approves.
3. **Step 3**: Procurement Manager reviews and approves.
4. **Step 4**: Finance Officer reviews for budget and approves.
5. **Final Step**: Requisition approved and finalized.

---

### **Summary of Roles**:

- **System Administrators**: They set up and manage the overall Approval Matrix and Workflows.
- **Department Heads/Managers**: They provide input and feedback to ensure that workflows reflect their department’s needs.
- **Approvers (e.g., Unit Heads, Finance)**: These are the individuals identified in the workflows who will approve requisitions at various stages.

---

This format is suitable for copying directly into Google Docs and is now enhanced with sample approval matrices and workflows to illustrate how the system works in practice.
