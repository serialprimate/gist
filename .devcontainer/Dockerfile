FROM ubuntu:latest

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Enable strict mode (exit on error, exit on unset variable, error on pipeline)
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# Upgrade packages
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install general packages
# - Freshen CA certificates
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    gnupg \
    jq \
    less \
    lsb-release \
    sudo \
    zip unzip \
    vim \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates --fresh

# Install python development packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install C++ development packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    binutils \
    gcc g++ \
    make \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set required user setup parameters
ARG USERNAME=dev
# Generate with `openssl passwd -1 -stdin <<< '<password>'`
ARG USER_PWCRYPT='$1$O6PU/jrk$o.O1GPhd2hH1qyLVb.1e1.'
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

# Setup the user:
# - Remove any existing user/group with the same UID/GID if they exist
# - Create a new user and group
# - Add user to the docker group
# - Set up sudo permissions for the user
# - Ensure the sudoers file has the correct permissions
RUN if id -u ${USER_UID} >/dev/null 2>&1; then \
    EXISTING_USER=$(getent passwd ${USER_UID} | cut -d: -f1); \
    userdel -r ${EXISTING_USER} || true; \
    fi && \
    if getent group ${USER_GID} >/dev/null 2>&1; then \
    EXISTING_GROUP=$(getent group ${USER_GID} | cut -d: -f1); \
    groupdel ${EXISTING_GROUP} || true; \
    fi && \
    groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --password ${USER_PWCRYPT} ${USERNAME} \
    && echo ${USERNAME} ALL=\(root\) ALL > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# Set the default user
USER ${USERNAME}

# Set the working directory
WORKDIR /code
