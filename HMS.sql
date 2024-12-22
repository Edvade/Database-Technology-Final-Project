CREATE TABLE Patient (
    PatientID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Address TEXT,
    PhoneNumber VARCHAR(15),
    Email VARCHAR(255),
    InsuranceProvider VARCHAR(255),
    InsurancePolicyNumber VARCHAR(255),
    EmergencyContactName VARCHAR(255),
    EmergencyContactPhone VARCHAR(15)
);

CREATE TABLE Doctor (
    DoctorID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Specialty VARCHAR(255),
    PhoneNumber VARCHAR(15),
    Email VARCHAR(255),
    LicenseNumber VARCHAR(255),
    YearsOfExperience INT
);

CREATE TABLE Appointment (
    AppointmentID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    AppointmentDate DATE NOT NULL,
    AppointmentTime TIME NOT NULL,
    Notes TEXT,
    Status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
);

CREATE TABLE Room (
    RoomID INT PRIMARY KEY AUTO_INCREMENT,
    RoomType VARCHAR(255) NOT NULL,
    PricePerDay DECIMAL(10, 2) NOT NULL
);

CREATE TABLE Stay (
    StayID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    RoomID INT NOT NULL,
    DaysStayed INT NOT NULL,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

CREATE TABLE Diagnosis (
    DiagnosisID INT PRIMARY KEY AUTO_INCREMENT,
    AppointmentID INT NOT NULL,
    DiagnosisDate DATE NOT NULL,
    DiagnosisDescription TEXT NOT NULL,
    FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID)
);

CREATE TABLE Medicine (
    MedicineID INT PRIMARY KEY AUTO_INCREMENT,
    MedicineName VARCHAR(255) NOT NULL,
    MethodOfAdmin VARCHAR(255), -- e.g., Oral, IV, Topical
    Manufacturer VARCHAR(255),
    Price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE Prescription (
    PrescriptionID INT PRIMARY KEY AUTO_INCREMENT,
    AppointmentID INT NOT NULL,
    MedicineID INT NOT NULL,
    Dosage VARCHAR(255), -- e.g., "500mg"
    Frequency VARCHAR(255), -- e.g., "Twice a Day"
    Quantity INT NOT NULL,
    StartDate DATE,
    EndDate DATE,
    FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID),
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID)
);

CREATE TABLE Treatment (
    TreatmentID INT PRIMARY KEY AUTO_INCREMENT,
    DiagnosisID INT NOT NULL,
    TreatmentDescription TEXT NOT NULL,
    TreatmentDate DATE NOT NULL,
    DoctorID INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    Status ENUM('Ongoing', 'Completed') DEFAULT 'Ongoing',
    FOREIGN KEY (DiagnosisID) REFERENCES Diagnosis(DiagnosisID),
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
);

CREATE TABLE Billing (
    BillingID INT PRIMARY KEY AUTO_INCREMENT,
    AppointmentID INT NOT NULL,
    StayID INT,
    TotalAmount DECIMAL(10, 2),
    PaymentDate DATE,
    PaymentMethod ENUM('Cash', 'Card', 'Insurance'),
    Status ENUM('Pending', 'Paid') DEFAULT 'Pending',
    FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID),
    FOREIGN KEY (StayID) REFERENCES Stay(StayID)
);

CREATE TABLE Receipt (
    ReceiptID INT PRIMARY KEY AUTO_INCREMENT,
    BillingID INT NOT NULL,
    ReceiptDate DATE NOT NULL,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    TreatmentDetails TEXT,
    MedicineDetails TEXT,
    FOREIGN KEY (BillingID) REFERENCES Billing(BillingID)
);
