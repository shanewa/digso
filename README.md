# digso

"Dig out *.so libs" - Show all shared libraries used by executables in Linux.  
  
You can use this tool to find all dependency shared libraries.  
Then, copy them to anther container without installations.

# Quick Start
- `python3 ./digso.py -p /lib64/libc.so.6 -d 10`
- `python3 ./digso.py -f /lib64/ -d 10`

# Applycations

Significantly reduce the size of the docker image in this way. (From 355MB to 80MB.)
```
# docker >= 17.05 suppports multi-stages build.

# 1st stage: Temporary image for build purpose.
FROM python:3.7-alpine AS tmp_build
LABEL maintainer="Wang, Shane"
RUN apk add --no-cache python3-dev \
    && apk add --no-cache musl-dev \
    && apk add --no-cache linux-headers \
    && apk add --no-cache gcc \
    && apk add --no-cache jpeg-dev \
    && apk add --no-cache zlib-dev \
    && apk add --no-cache libjpeg
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# 2nd stage: Build the web image.
FROM python:3.7-alpine
LABEL maintainer="Wang, Shane"
# Use digso to find all dependency shared libraries. Then, copy them to a clean build.
# In tmp_build, python /tmp/digso.py -f /usr/local/lib/python3.7/site-packages -o /tmp/digso.log -d 10  
COPY --from=tmp_build /lib/libz.so.1 /lib/libz.so.1
COPY --from=tmp_build /usr/local/lib/libpython3.7m.so.1.0 /usr/local/lib/libpython3.7m.so.1.0
COPY --from=tmp_build /lib/ld-musl-x86_64.so.1 /lib/ld-musl-x86_64.so.1
COPY --from=tmp_build /usr/lib/libjpeg.so.8 /usr/lib/libjpeg.so.8
COPY patch/smtp.py /usr/local/lib/python3.7/site-packages/django/core/mail/backends/smtp.py
COPY patch/hashers.py /usr/local/lib/python3.7/site-packages/django/contrib/auth/hashers.py

```
