FROM minizinc/minizinc:latest

ENV AMPL_LICENSE="e69fc5e3-52d1-49b8-83b7-f1048bd93eda"

COPY . /src

WORKDIR /src

RUN apt-get update \
    && apt-get install -y python3 python3-venv python3-pip

RUN python3 -m venv venv
ENV PATH="/src/venv/bin:$PATH"

RUN python3 -m pip install --no-cache-dir -r requirements.txt

RUN python3 -m amplpy.modules install highs --no-cache-dir

CMD python3 ./mcp.py $instance $method $solver $time
