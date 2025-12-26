# 🩺 Smart Wellness Management System

### A Real-Time, Personalized Health Monitoring Web Application

A modern, real-time web application that monitors user health data, manages daily wellness routines, detects abnormal conditions, and provides personalized alerts using user-provided data stored securely in a database.

---

## 📌 Problem Statement

Modern healthcare systems are primarily **reactive**, responding to diseases only after symptoms become severe. Existing digital health platforms often lack real-time personalization, continuous monitoring, and customizable alert mechanisms. Many systems fail to store and update individual health data dynamically, resulting in poor medication adherence, delayed alerts, and limited caregiver awareness.

There is a strong need for a **real-time, personalized, and user-driven wellness management system** that continuously tracks health parameters, visualizes trends, detects abnormal conditions early, and provides timely alerts to improve overall health outcomes.

---

## 🎯 Project Objectives

* To design a real-time wellness monitoring system using user-provided health data
* To enable secure login and personalized health profile management
* To track medication schedules with digital time-based reminders
* To visualize health trends using modern charts
* To calculate a health risk score based on user data
* To detect abnormal health conditions and generate alerts
* To store and update all data persistently using a database

---

## 🧠 System Description

The Smart Wellness Management System is a **user-centric health companion** that allows individuals to enter, edit, and monitor their health data in real time. The system provides:

* A **digital clock–enabled dashboard**
* Editable health profiles
* Medication reminders using real-time system time
* Dynamic health charts
* Risk score calculation
* Customizable alert thresholds


---

## 📂 Dataset Description (Real-Time User Dataset)

### Data Source

* **Primary Source:** Real-time data entered by users through the web application
* **Secondary Source:** Simulated realistic data for testing and demonstration

### Data Collected

**Personal & Physical Data**

* Age, gender
* Height, weight (BMI calculated automatically)

**Medical History**

* Diabetes status
* Blood pressure issues
* Heart-related conditions

**Lifestyle & Exercise Data**

* Sleep duration
* Stress level
* Water intake
* Exercise type (walking, yoga, cardio, strength training)
* Exercise duration and frequency

**Health Metrics**

* Heart rate
* Blood pressure
* Blood sugar levels


---

## ⚙️ Technologies Used

* **Frontend:**

  * HTML5
  * Tailwind CSS
  * JavaScript
  * Chart.js / ApexCharts

* **Backend:**

  * Python
  * Flask (REST APIs)
  * Flask-JWT-Extended

* **Utilities:**

  * Digital time picker
  * System real-time clock

---

## 🖥️ Web Application Features

### 🔐 Authentication

* Secure user registration and login
* JWT-based authentication
* User-specific data isolation

### ⏰ Real-Time Dashboard

* Live digital clock (HH:MM:SS)
* User greeting and navigation hub

### 🧍 Health Profile Management

* Detailed health and lifestyle data entry
* Edit and update profile with confirmation
* Persistent data storage

### 💊 Medication Reminder

* Digital time picker for medication timings
* Real-time countdown
* Taken/missed tracking

### 📊 Health Charts

* Modern animated charts
* Heart rate, BP, sugar trends
* Daily / weekly / monthly views

### ⚠️ Health Risk Score

* Score range: 0–100
* Color-coded risk levels
* Historical score comparison

### 🚨 Abnormal Alert System

* Customizable alert thresholds
* Severity levels (normal, warning, critical)
* Alert history with timestamps

---

## 🔄 System Algorithm

1. User logs into the system using secure authentication.
2. The dashboard displays a real-time digital clock.
3. User enters or updates health profile details.
4. Health metrics and lifestyle data are saved in MongoDB.
5. Medication reminders are scheduled using real-time system time.
6. Health data is continuously evaluated.
7. Charts are updated dynamically from the database.
8. Health risk score is calculated based on latest data.
9. Abnormal conditions are detected using user-defined thresholds.
10. Alerts are generated and stored with timestamps.
11. Updated results are displayed instantly to the user.

---

## 🚀 How to Run the Project

### Step 1: Clone the Repository

```bash
git clone https://github.com/JIDHESHP/INTEGRATED_HEALTH_COMPANION/
cd smart_wellness_system
```

### Step 2: Run the Application

```bash

python app.py
```

### Step 3: Open the Browser

```
http://127.0.0.1:5000
```

---

## 📊 Results

* Real-time health data is captured and stored successfully
* Health charts update instantly upon new data entry
* Risk scores change dynamically based on user inputs
* Alerts are generated accurately for abnormal values
* Profile updates persist across sessions

---

## 🧪 Sample Test Cases

| Test Case ID | Input Data        | Expected Output        |
| ------------ | ----------------- | ---------------------- |
| TC-01        | Normal vitals     | Low risk score         |
| TC-02        | High BP           | Alert generated        |
| TC-03        | Missed medication | Reminder alert         |
| TC-04        | Profile update    | Data saved & reflected |

---

## 🔍 Code Review

* Flask handles backend logic and APIs
* JWT ensures secure authentication
* Chart.js renders modern visualizations
* Modular structure improves maintainability

---

## ⚠️ Disclaimer

This project is developed for **educational and academic purposes only**.
It does not replace professional medical advice or diagnosis.
Users should consult healthcare professionals for medical decisions.

---

## ⭐ References

* Flask Documentation
* Chart.js Documentation
* JWT Authentication Guide
* Health Informatics Research Papers

---

## 📌 Conclusion

The Smart Wellness Management System successfully demonstrates how real-time user data, modern UI design, and persistent storage can be combined to build an intelligent and personalized health monitoring platform. The project provides a strong foundation for future enhancements such as IoT integration and advanced predictive analytics.

---


Just tell me 👍
