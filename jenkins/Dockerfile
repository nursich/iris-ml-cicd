# Jenkins controller with the tools the pipeline needs:
#   - Python 3 + venv  (unit tests, linting, training)
#   - Docker CLI       (talks to the host Docker Engine via the mounted socket)
#   - kubectl          (optional CD stage to Minikube)
# Works on both Apple Silicon (arm64) and Intel/AMD (amd64).
FROM jenkins/jenkins:lts-jdk21

USER root

ARG TARGETARCH
# "stable" = latest stable kubectl release at build time
ARG KUBECTL_VERSION=stable

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip curl ca-certificates gnupg \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
 && chmod a+r /etc/apt/keyrings/docker.asc \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli docker-buildx-plugin \
 && rm -rf /var/lib/apt/lists/*

RUN ARCH="${TARGETARCH:-$(dpkg --print-architecture)}" \
 && VER="${KUBECTL_VERSION}" \
 && if [ "$VER" = "stable" ]; then VER="$(curl -fsSL https://dl.k8s.io/release/stable.txt)"; fi \
 && curl -fsSL -o /usr/local/bin/kubectl \
      "https://dl.k8s.io/release/${VER}/bin/linux/${ARCH}/kubectl" \
 && chmod +x /usr/local/bin/kubectl

USER jenkins

# Pre-install the plugins the pipeline uses
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt
