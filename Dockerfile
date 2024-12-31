FROM minizinc/minizinc:latest

ENV AMPL_LICENSE=""

COPY . /src

WORKDIR /src

RUN apt-get update \
    && apt-get install -y python3 python3-venv python3-pip

RUN python3 -m venv venv
ENV PATH="/src/venv/bin:$PATH"

RUN python3 -m pip install --no-cache-dir -r requirements.txt

RUN python3 -m amplpy.modules install highs cbc scip gcg --no-cache-dir

CMD python3 ./mcp.py $instance $method $model $solver $time
