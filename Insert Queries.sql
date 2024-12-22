-- Insert Patients
INSERT INTO Patient (FirstName, LastName, DateOfBirth, Gender, Address, PhoneNumber, Email, InsuranceProvider, InsurancePolicyNumber, EmergencyContactName, EmergencyContactPhone) VALUES
('John', 'Doe', '1985-06-15', 'Male', '123 Elm St, Springfield', '555-1234', 'john.doe@example.com', 'Health Insurance Co.', 'HIC123456', 'Jane Doe', '555-5678'),
('Jane', 'Smith', '1990-02-20', 'Female', '456 Oak St, Springfield', '555-5678', 'jane.smith@example.com', 'Wellness Insurance', 'WI987654', 'Alice Smith', '555-8765'),
('Alice', 'Johnson', '1975-11-30', 'Female', '789 Pine St, Springfield', '555-8765', 'alice.johnson@example.com', 'CarePlus', 'CP54321', 'Bob Johnson', '555-4321'),
('Bob', 'Brown', '2000-01-01', 'Male', '321 Maple St, Springfield', '555-4321', 'bob.brown@example.com', 'Family Health', 'FH654321', 'Charlie Brown', '555-3456');

-- Insert Doctors
INSERT INTO Doctor (FirstName, LastName, Specialty, PhoneNumber, Email, LicenseNumber, YearsOfExperience) VALUES
('Emily', 'Clark', 'Cardiology', '555-1111', 'emily.clark@example.com', 'LIC12345', 10),
('Michael', 'Wilson', 'Neurology', '555-2222', 'michael.wilson@example.com', 'LIC23456', 8),
('Sarah', 'Davis', 'Pediatrics', '555-3333', 'sarah.davis@example.com', 'LIC34567', 5),
('David', 'Martinez', 'Orthopedics', '555-4444', 'david.martinez@example.com', 'LIC45678', 12);

-- Insert Appointments
INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime, Notes, Status) VALUES
(1, 1, '2023-10-01', '09:00:00', 'Routine check-up', 'Completed'),
(2, 2, '2023-10-02', '10:00:00', 'Follow-up on treatment', 'Completed'),
(3, 3, '2023-10-03', '11:00:00', 'Consultation for headache', 'Scheduled'),
(4, 4, '2023-10-04', '14:00:00', 'Knee pain evaluation', 'Completed');

-- Insert Rooms
INSERT INTO Room (RoomType, PricePerDay) VALUES
('Single', 100.00),
('Double', 150.00),
('Suite', 250.00);

-- Insert Stays
INSERT INTO Stay (AppointmentID, RoomID, DaysStayed) VALUES
(2, 1, 3),  -- 3 days in Room 1
(2, 2, 5),  -- 5 days in Room 2
(3, 1, 2),  -- 2 days in Room 1
(4, 3, 4);  -- 4 days in Room 3

-- Insert Diagnoses
INSERT INTO Diagnosis (AppointmentID, DiagnosisDate, DiagnosisDescription) VALUES
(1, '2023-10-01', 'Hypertension'),
(2, '2023-10-02', 'Migraine'),
(3, '2023-10-03', 'Flu'),
(4, '2023-10-04', 'Knee Injury');

-- Insert Medicines
INSERT INTO Medicine (MedicineName, MethodOfAdmin, Manufacturer, Price) VALUES
('Aspirin', 'Oral', 'Pharma Co.', 0.10),
('Ibuprofen', 'Oral', 'Health Corp.', 0.15),
('Amoxicillin', 'Oral', 'MediPharm', 0.20),
('Paracetamol', 'Oral', 'Wellness Inc.', 0.05);

-- Insert Prescriptions
INSERT INTO Prescription (AppointmentID, MedicineID, Dosage, Frequency, Quantity, StartDate, EndDate) VALUES
(1, 1, '500mg', 'Twice a Day', 14, '2023-10-01', '2023-10-15'),  -- Aspirin for 14 days
(2,  2, '500mg', 'Once a Day', 10, '2023-10-02', '2023-10-12'),  -- Ibuprofen for 10 days
(3, 3, '250mg', 'Three Times a Day', 21, '2023-10-03', '2023-10-24'),  -- Amoxicillin for 21 days
(4, 4, '500mg', 'Once a Day', 6, '2023-10-04', '2023-10-10');  -- Paracetamol for 6 days

-- Insert Treatments
INSERT INTO Treatment (DiagnosisID, TreatmentDescription, TreatmentDate, DoctorID, Price, Status) VALUES
(1, 'Lifestyle changes and medication', '2023-10-01', 1, 150.00, 'Completed'),
(2, 'Prescribed rest and hydration', '2023-10-02', 2, 100.00, 'Ongoing'),
(3, 'Antiviral medication and rest', '2023-10-03', 3, 200.00, 'Ongoing'),
(4, 'Physical therapy and pain management', '2023-10-04', 4, 250.00, 'Ongoing');

-- Insert Billings
INSERT INTO Billing (AppointmentID, TotalAmount, PaymentDate, PaymentMethod, Status) VALUES
(1, 300.00, '2023-10-01', 'Insurance', 'Paid'),
(2, 450.00, '2023-10-02', 'Card', 'Pending'),
(3, 200.00, '2023-10-03', 'Cash', 'Pending'),
(4, 600.00, '2023-10-04', 'Insurance', 'Paid');

-- Insert Receipts
INSERT INTO Receipt (BillingID, ReceiptDate, TotalAmount, TreatmentDetails, MedicineDetails) VALUES
(1, '2023-10-01', 300.00, 'Lifestyle changes and medication', 'Aspirin: 14, Ibuprofen: 10'),
(2, '2023-10-02', 450.00, 'Prescribed rest and hydration', 'Ibuprofen: 10'),
(3, '2023-10-03', 200.00, 'Antiviral medication and rest', 'Amoxicillin: 21'),
(4, '2023-10-04', 600.00, 'Physical therapy and pain management', 'Paracetamol: 6');