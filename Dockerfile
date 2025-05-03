# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the entire project into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose ports for Streamlit and FastAPI
EXPOSE 8501 8000

# Run both Streamlit and FastAPI using a process manager
CMD ["bash", "-c", "uvicorn server:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
