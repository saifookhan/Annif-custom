FROM python:3.7-slim-buster AS builder

LABEL maintainer="Juho Inkinen <juho.inkinen@helsinki.fi>"

## Install optional dependencies:
RUN apt-get update \
	## Voikko:
	&& apt-get install -y --no-install-recommends \
		libvoikko1 \
		voikko-fi \
	&& pip install --no-cache-dir \
		voikko \
	## fasttext:
	&& apt-get install -y --no-install-recommends \
		build-essential \
	&& pip install --no-cache-dir \
		fasttext==0.9.2 \
	## Vowpal Wabbit
	&& apt-get install -y --no-install-recommends \
		libboost-program-options-dev \
		zlib1g-dev \
		libboost-python-dev \
		cmake \
		libboost-system-dev \
		libboost-thread-dev \
		libboost-test-dev \
	&& ln -sf /usr/lib/x86_64-linux-gnu/libboost_python-py35.a \
		/usr/lib/x86_64-linux-gnu/libboost_python3.a \
	&& ln -sf /usr/lib/x86_64-linux-gnu/libboost_python-py35.so \
		/usr/lib/x86_64-linux-gnu/libboost_python3.so \
	&& pip install --no-cache-dir \
		vowpalwabbit==8.8.1 \
        ## LMDB
        && pip install --no-cache-dir lmdb==1.0.0
	



FROM python:3.7-slim-buster

COPY --from=builder /usr/local/lib/python3.7 /usr/local/lib/python3.7

## Dependencies needed at runtime:
RUN apt-get update \
	# Voikko dependencies:
	&& apt-get install -y --no-install-recommends \
		libvoikko1 \
		voikko-fi \
		nodejs \
		npm \
	# Vowpal Wabbit dependencies:
	&& apt-get install -y --no-install-recommends \
		libboost-program-options1.67.0 \
		libboost-python1.67.0 \
		libboost-system1.67.0 \
	&& pip install --no-cache-dir \
		voikko \
		vowpalwabbit==8.8.1 \
		tensorflow-cpu==2.3.1 \
		omikuji==0.3.* \
	# For Docker healthcheck:
	&& apt-get install -y --no-install-recommends curl \
	# Clean up:
	&& rm -rf /var/lib/apt/lists/* /usr/include/* \
	&& rm -rf /root/.cache/pip*/*


## Install Annif (including development packages and making the installation editable):

COPY setup.py README.md LICENSE.txt projects.cfg.dist /Annif/
COPY annif /Annif/annif
COPY tests /Annif/tests
WORKDIR /Annif

RUN pip install .[dev] --no-cache-dir \
	&& pip install -e . \
	# Download nltk data (handle occasional timeout in with 3 tries)
	&& for i in 1 2 3; do python -m nltk.downloader punkt -d /usr/share/nltk_data && break || sleep 1; done


WORKDIR /annif-projects

# Switch user to non-root:
RUN groupadd -g 998 annif_user \
    && useradd -r -u 998 -g annif_user annif_user \
    && chown -R annif_user:annif_user /annif-projects
USER annif_user


CMD annif
