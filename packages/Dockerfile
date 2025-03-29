FROM continuumio/miniconda3
WORKDIR /app
COPY environment.yml .
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]
COPY . .
CMD ["conda", "run", "-n", "myenv", "python", "app.py"]