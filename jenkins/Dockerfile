FROM jenkins/jenkins:lts-jdk17

USER root

# ---------------------------------------------------
# Install prerequisites (Docker, gcloud, kubectl)
# ---------------------------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    lsb-release \
    unzip \
    sudo \
    && apt-get clean

# -----------------------------
# Install Docker CLI (safe way)
# -----------------------------
RUN curl -fsSL https://get.docker.com | sh

# ------------------------------------------
# Add Jenkins user to root group which with GID 0 (docker.sock)
# ------------------------------------------
RUN usermod -aG root jenkins

# ---------------------------------------------------
# Install Google Cloud SDK (gcloud CLI)
# ---------------------------------------------------
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-sdk

# ---------------------------------------------------
# Install kubectl
# ---------------------------------------------------
RUN KUBECTL_VERSION="v1.30.1" && \
    curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl

USER jenkins
