pipeline {
    agent any

    triggers {
        pollSCM('H/10 * * * *')
    }

    environment {
        DOCKER_IMAGE = 'keply186/hashx4'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/AlexanderYanuchkovskiy/hash_x4.git'
            }
        }

        stage('Verify Files') {
            steps {
                script {
                    echo "Проверка файлов..."
                    sh '''
                        ls -la
                        echo "Содержимое репозитория:"
                        find . -type f -name "*.py" | head -20
                    '''
                }
            }
        }

        stage('Build Docker Image - Simple') {
            steps {
                script {
                    // Простая сборка без сложных операций
                    sh '''
                        docker --version
                        echo "Сборка образа..."
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        echo "Образ собран: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    '''
                }
            }
        }

        stage('Test Image') {
            steps {
                script {
                    sh '''
                        echo "Тестирование образа..."
                        docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} python --version
                        echo "Тест завершен успешно"
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-login',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                            docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                            docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                            docker push ${DOCKER_IMAGE}:latest
                            echo "Образ успешно загружен в Docker Hub"
                        '''
                    }
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    sh '''
                        echo "Очистка..."
                        docker image prune -f
                        docker container prune -f
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Сборка успешно завершена!"
            echo "📦 Образ: ${DOCKER_IMAGE}:${DOCKER_TAG}"
        }
        failure {
            echo "❌ Сборка завершилась с ошибкой"
        }
    }
}
