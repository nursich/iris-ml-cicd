// CI/CD pipeline for the Iris classifier research project.
//
// CI: checkout -> lint -> unit tests -> train (quality gate) -> docker build -> smoke test
// CD: push to Docker Hub -> deploy to a test server (Docker) -> deploy to Kubernetes (Minikube)
//
// Jenkins credentials used (Manage Jenkins -> Credentials):
//   dockerhub            Username + password (Docker Hub username + access token)
//   kubeconfig-minikube  Secret file (kubeconfig created by scripts/make-jenkins-kubeconfig.sh)

pipeline {
    agent any

    parameters {
        booleanParam(name: 'PUSH_IMAGE', defaultValue: true,
                     description: 'Push the image to Docker Hub')
        booleanParam(name: 'DEPLOY_K8S', defaultValue: true,
                     description: 'Deploy to Kubernetes (Minikube)')
    }

    // Check GitHub for new commits every 2 minutes and build each new commit.
    // (A local Jenkins cannot receive GitHub webhooks without a public URL.)
    triggers {
        pollSCM('H/2 * * * *')
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'iris-classifier'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        CI_NETWORK = 'ci-net'
        VENV       = "${env.WORKSPACE}/.venv"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                }
                echo "Building commit ${env.GIT_SHORT} (build #${env.BUILD_NUMBER})"
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv "$VENV"
                    . "$VENV/bin/activate"
                    pip install --quiet --upgrade pip
                    pip install --quiet -r requirements-dev.txt
                    python --version
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '. "$VENV/bin/activate" && flake8 src tests'
            }
        }

        stage('Unit tests') {
            steps {
                sh '. "$VENV/bin/activate" && mkdir -p reports && pytest'
            }
            post {
                always {
                    junit 'reports/junit.xml'
                    archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
                }
            }
        }

        stage('Train model (quality gate)') {
            steps {
                sh '''
                    . "$VENV/bin/activate"
                    PYTHONPATH=src python -m iris_classifier.train --out models --min-accuracy 0.90
                '''
                archiveArtifacts artifacts: 'models/metrics.json'
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                    docker build \
                      --build-arg VCS_REF="$GIT_SHORT" \
                      --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
                      -t "$IMAGE_NAME:$IMAGE_TAG" \
                      -t "$IMAGE_NAME:latest" .
                    docker image ls "$IMAGE_NAME"
                '''
            }
        }

        stage('Smoke test container') {
            steps {
                sh '''
                    NAME="iris-smoke-$BUILD_NUMBER"
                    docker rm -f "$NAME" >/dev/null 2>&1 || true
                    docker run -d --name "$NAME" --network "$CI_NETWORK" "$IMAGE_NAME:$IMAGE_TAG"

                    for i in $(seq 1 30); do
                      curl -fs "http://$NAME:8000/health" && break
                      sleep 1
                    done

                    echo "--- /health"
                    curl -fs "http://$NAME:8000/health"
                    echo
                    echo "--- /predict (sample 1 of the UCI dataset, expected Iris-setosa)"
                    curl -fs -X POST "http://$NAME:8000/predict" \
                      -H "Content-Type: application/json" \
                      -d '{"sepal_length_cm":5.1,"sepal_width_cm":3.5,"petal_length_cm":1.4,"petal_width_cm":0.2}' \
                      | tee smoke.json
                    echo
                    grep -q "Iris-setosa" smoke.json
                '''
            }
            post {
                always {
                    sh 'docker rm -f "iris-smoke-$BUILD_NUMBER" >/dev/null 2>&1 || true'
                }
            }
        }

        stage('Push to Docker Hub') {
            when { expression { params.PUSH_IMAGE } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_TOKEN')]) {
                    sh '''
                        echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
                        docker tag "$IMAGE_NAME:$IMAGE_TAG" "$DH_USER/$IMAGE_NAME:$IMAGE_TAG"
                        docker tag "$IMAGE_NAME:$IMAGE_TAG" "$DH_USER/$IMAGE_NAME:latest"
                        docker push "$DH_USER/$IMAGE_NAME:$IMAGE_TAG"
                        docker push "$DH_USER/$IMAGE_NAME:latest"
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to test server') {
            steps {
                sh '''
                    docker rm -f iris-test >/dev/null 2>&1 || true
                    docker run -d --name iris-test --restart unless-stopped \
                      --network "$CI_NETWORK" -p 8081:8000 "$IMAGE_NAME:$IMAGE_TAG"
                    for i in $(seq 1 30); do
                      curl -fs http://iris-test:8000/health && break
                      sleep 1
                    done
                    echo
                    curl -fs http://iris-test:8000/info
                    echo
                    echo "Test server is running at http://localhost:8081"
                '''
            }
        }

        stage('Deploy to Kubernetes (Minikube)') {
            when { expression { params.DEPLOY_K8S && params.PUSH_IMAGE } }
            steps {
                withCredentials([
                    file(credentialsId: 'kubeconfig-minikube', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'dockerhub',
                                     usernameVariable: 'DH_USER',
                                     passwordVariable: 'DH_TOKEN')
                ]) {
                    sh '''
                        IMAGE="$DH_USER/$IMAGE_NAME:$IMAGE_TAG"
                        sed "s|IMAGE_PLACEHOLDER|$IMAGE|" k8s/deployment.yaml | kubectl apply -f -
                        kubectl apply -f k8s/service.yaml
                        kubectl rollout status deployment/iris-classifier --timeout=180s
                        kubectl get deployment,pods,svc -l app=iris-classifier -o wide
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded: image $IMAGE_NAME:$IMAGE_TAG (commit $GIT_SHORT)"
        }
        failure {
            echo 'Pipeline failed. Check the stage logs above.'
        }
        always {
            sh 'rm -f smoke.json || true'
        }
    }
}
