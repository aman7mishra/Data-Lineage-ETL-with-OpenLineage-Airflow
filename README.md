# **Data Lineage ETL with OpenLineage & Airflow**

## **Overview**
This project demonstrates a complete **ETL pipeline with data lineage tracking** using **OpenLineage**, **Apache Airflow**, **PostgreSQL**, and **Marquez**. It extracts, transforms, and loads NYC Taxi data while tracking data movement across stages.

## **Technologies Used**
- **Apache Airflow** - Orchestrates ETL workflow
- **OpenLineage** - Tracks data lineage
- **PostgreSQL** - Stores processed data
- **Marquez** - UI for lineage visualization
- **Docker** - Containerized services
- **Pandas** - Data transformation

## **Project Structure**
```
data-lineage-etl/
├── dags/
│   ├── nyc_taxi_lineage.py  # Airflow DAG with OpenLineage
├── docker-compose.yml       # PostgreSQL and Marquez setup
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── .env                     # Environment variables
```

## **Setup Instructions**
### **1. Clone the repository**
```bash
git clone https://github.com/aman7mishra/Data-Lineage-ETL-with-OpenLineage-Airflow.git
cd Data-Lineage-ETL-with-OpenLineage-Airflow
```

### **2. Start PostgreSQL & Marquez with Docker**
```bash
docker-compose up -d
```

### **3. Install Python dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure Environment Variables**
Create a `.env` file:
```bash
OPENLINEAGE_URL=http://localhost:5000
AIRFLOW__OPENLINEAGE__TRANSPORT=http
AIRFLOW__OPENLINEAGE__URL=$OPENLINEAGE_URL
```

### **5. Start Airflow**
```bash
airflow standalone
```

### **6. Trigger the DAG**
```bash
airflow dags trigger nyc_taxi_lineage
```

### **7. Check Data in PostgreSQL**
```bash
docker exec -it postgres psql -U airflow -d nyc_taxi -c "SELECT * FROM nyc_taxi LIMIT 5;"
```

### **8. Visualize Data Lineage in Marquez**
- Open `http://localhost:5000`
- See the lineage graph
