pipeline {
    agent any
    
    environment {
        // Переменные окружения для проекта
        APP_NAME = "fastapi-docker-watch-demo"
        DOCKER_REGISTRY = 
        IMAGE_NAME = "${DOCKER_REGISTRY}/${APP_NAME}"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1'
                
                // Настройка переменных окружения для ветки
                script {
                    env.GIT_BRANCH_NAME = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
                    env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    // if (env.GIT_BRANCH_NAME == 'master') {
                    //     env.DEPLOY_ENV = 'production'
                    //     env.IMAGE_TAG = "prod-${env.BUILD_NUMBER}"
                    // } else if (env.GIT_BRANCH_NAME == 'develop') {
                    //     env.DEPLOY_ENV = 'staging'
                    //     env.IMAGE_TAG = "staging-${env.BUILD_NUMBER}"
                    // } else {
                    if (env.GIT_BRANCH_NAME){
                        env.DEPLOY_ENV = 'development'
                        env.IMAGE_TAG = "dev-${env.GIT_COMMIT_SHORT}"
                    }
                }
            }
        }
        
        stage('Lint') {
            steps {
                // Проверка Python кода с помощью flake8
                sh '''
                python3 -m pip install flake8
                flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }
        
        stage('Build') {
            steps {
                // Сборка Docker образов
                sh "docker-compose build"
                
                sh "docker tag fastapi_app:latest ${IMAGE_NAME}-app:${IMAGE_TAG}"
                sh "docker tag fastapi_nginx:latest ${IMAGE_NAME}-nginx:${IMAGE_TAG}"
            }
        }
        
        stage('Test') {
            steps {
                // Запуск контейнеров для тестирования
                sh "docker-compose up -d"
                
                // Проверка доступности сервисов
                sh "sleep 5"  // Даем время на запуск
                sh "curl -s --retry 5 --retry-delay 5 --retry-connrefused http://localhost:8000/ > /dev/null"
                sh "curl -s --retry 5 --retry-delay 5 --retry-connrefused http://localhost:8070/ > /dev/null"
                
                // Здесь можно добавить запуск интеграционных/юнит тестов
                // sh "docker exec fastapi_app python -m pytest"
            }
            post {
                always {
                    // Остановка контейнеров после тестов
                    sh "docker-compose down"
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                expression { 
                    return env.GIT_BRANCH_NAME == 'main' || 
                           env.GIT_BRANCH_NAME == 'master' || 
                           env.GIT_BRANCH_NAME == 'develop'
                }
            }
            steps {
                // Авторизация в Docker registry (используйте Jenkins credentials)
                withCredentials([usernamePassword(credentialsId: 'docker-registry-credentials', 
                                 passwordVariable: 'DOCKER_PASSWORD', 
                                 usernameVariable: 'DOCKER_USERNAME')]) {
                    sh "echo $DOCKER_PASSWORD | docker login $DOCKER_REGISTRY -u $DOCKER_USERNAME --password-stdin"
                }
                
                // Отправка образов в registry
                sh "docker push ${IMAGE_NAME}-app:${IMAGE_TAG}"
                sh "docker push ${IMAGE_NAME}-nginx:${IMAGE_TAG}"
                
                // Для веток main/master создаем также тег latest
                script {
                    if (env.GIT_BRANCH_NAME == 'main' || env.GIT_BRANCH_NAME == 'master') {
                        sh "docker tag ${IMAGE_NAME}-app:${IMAGE_TAG} ${IMAGE_NAME}-app:latest"
                        sh "docker tag ${IMAGE_NAME}-nginx:${IMAGE_TAG} ${IMAGE_NAME}-nginx:latest"
                        sh "docker push ${IMAGE_NAME}-app:latest"
                        sh "docker push ${IMAGE_NAME}-nginx:latest"
                    }
                }
            }
            post {
                always {
                    // Выход из Docker registry
                    sh "docker logout ${DOCKER_REGISTRY}"
                }
            }
        }
        
        stage('Deploy') {

        }
    }
    
    post {
        always {
            // Очистка ресурсов
            sh "docker system prune -f"
        }
    }
}